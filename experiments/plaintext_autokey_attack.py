"""Bounded plaintext-feedback autokey attack with literal LP1-word seed keys."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
import random
import time

from attack_support import ROOT,load,digest,key_catalog,model_without,to_indices,to_runes,top_unique
from liberprimus.alphabet import transliterate
from liberprimus.ciphers import autokey
from conditional_attack_null import conditional_shuffle

SIGNS=((1,-1),(1,1),(-1,-1),(-1,1))


def literal_keys():
    # Primitive-period reduction is valid for repeating Vigenere, not autokey.
    # Recover original literal tokens from preserved evidence instead.
    keys=set()
    for row in key_catalog():
        for evidence in row["evidence"]:
            key=tuple(to_indices(evidence["original_runes"]))
            keys.add(key[::-1] if evidence["reversed"] else key)
    return sorted(keys)


def transform(values,key,cs=1,ks=-1,skip_all_f=False):
    stream=list(key);cursor=0;out=[];skips=[]
    for i,value in enumerate(values):
        if skip_all_f and value==0:
            out.append(0);skips.append(i)
        else:
            plain=(cs*value+ks*stream[cursor])%29
            out.append(plain);stream.append(plain);cursor+=1
    return out,skips


def invert(plain,key,cs,ks,skips):
    stream=list(key);cursor=0;out=[];skips=set(skips)
    for i,value in enumerate(plain):
        if i in skips:
            if value!=0:raise ValueError("interrupter must be F")
            out.append(0)
        else:
            out.append((cs*(value-ks*stream[cursor]))%29)
            stream.append(value);cursor+=1
    return out


def score_table(model):
    one=[model.logp((),a) for a in range(29)]
    two=[model.logp((a,),b) for a in range(29) for b in range(29)]
    three=[model.logp((a,b),c) for a in range(29) for b in range(29) for c in range(29)]
    return one,two,three


def fast_score(values,lookup):
    one,two,three=lookup
    return (one[values[0]]+two[values[0]*29+values[1]]+
            sum(three[a*841+b*29+c] for a,b,c in zip(values,values[1:],values[2:])))/len(values)


def search(values,keys,lookup,deadline,keep=3):
    top=[];best=-float("inf");tasks=0
    for key in keys:
        if time.perf_counter()>deadline:raise TimeoutError("plaintext-autokey deadline")
        for skip in (False,True):
            for cs,ks in SIGNS:
                plain,skips=transform(values,key,cs,ks,skip)
                score=fast_score(plain,lookup);tasks+=1;best=max(best,score)
                if keep and (len(top)<keep or score>top[-1]["score"]):
                    assert invert(plain,key,cs,ks,skips)==values
                    row={"score":score,"plaintext_runes":to_runes(plain),"transliteration":transliterate(plain),
                         "recipe":{"key_indices":list(key),"cipher_sign":cs,"feedback_sign":ks,
                                   "skip_positions":skips,"skip_policy":"all_F" if skip else "none"},
                         "reencryption_verified":True}
                    top=top_unique(top+[row],keep=keep)
    return best,top,tasks


def run(seconds=180,replicates=39,seed=3301011):
    tick=time.perf_counter();deadline=tick+seconds;keys=literal_keys();lookup=score_table(model_without())
    pages=[p for p in load("transcriptions/pages.json") if p["edition"]=="LP2" and p["page"]<=55 and p["runes"]]
    rows=[];tasks=0
    for page in pages:
        values=to_indices(page["runes"])
        best,top,count=search(values,keys,lookup,deadline)
        rows.append({"page":page["id"],"ciphertext_runes":page["runes"],"top":top,"tasks":count});tasks+=count
        print(json.dumps({"page":page["id"],"best_score":best,"seconds":time.perf_counter()-tick}),flush=True)
    # Frozen selection rule: two highest page maxima, exact conditional shuffle null.
    rng=random.Random(seed);calibration=[]
    for row in sorted(rows,key=lambda r:r["top"][0]["score"],reverse=True)[:2]:
        values=to_indices(row["ciphertext_runes"]);null=[]
        for i in range(replicates):
            sample,proposals=conditional_shuffle(values,rng,deadline=deadline)
            best,_,_=search(sample,keys,lookup,deadline,keep=0)
            null.append({"max_score":best,"proposals":proposals,"ciphertext_indices":sample})
        p=(1+sum(r["max_score"]>=row["top"][0]["score"] for r in null))/(replicates+1)
        calibration.append({"page":row["page"],"monte_carlo_p":p,"bonferroni_55_pages":min(1,55*p),"null_runs":null})
        print(json.dumps({"null_page":row["page"],"p":p,"seconds":time.perf_counter()-tick}),flush=True)
    fixture=next(f for f in load("known_solutions/fixtures.json") if f["id"]=="LP1-03_04_divinity")
    plain=to_indices(fixture["plaintext_runes"]);key=fixture["key_indices"]
    cipher=autokey(plain,key,decrypt=False,feedback="plaintext")
    _,control,_=search(cipher,keys,score_table(model_without(fixture["id"])),deadline)
    exact=control[0]["plaintext_runes"]==fixture["plaintext_runes"]
    if not exact:raise AssertionError("plaintext autokey positive control failed")
    return {"experiment":"E011-plaintext-autokey-dictionary","status":"completed","parameters":{
                "seconds":seconds,"replicates":replicates,"seed":seed,"key_count":len(keys),"signs":SIGNS,
                "F_policies":["none","all_F"],"phases":"literal word seeds, no rotations or period reduction",
                "memory":"One candidate and one null page at a time, 29^3 score table, top3 per page."},
            "key_indices":[list(k) for k in keys],"evaluated_recipes":tasks,"pages":rows,"null_calibration":calibration,
            "positive_control":{"fixture":fixture["id"],"excluded_from_training":True,"ciphertext_indices":cipher,
                                "exact_top_one":exact,"top":control},
            "limits":["Only literal declared seed keys; no arbitrary-key inference, selective F masks, transposition, or across-page continuation.",
                      "Exact conditional null preserves counts and doublets; all key/sign/F policies searched in each replicate.",
                      "Bonferroni55 accounts for selecting pages; B39 cannot attain corrected significance. No global success claim across sequential experiments.",
                      "Scorer still fails the separate LP2-56 top-one regression; negative screens do not rule out these cipher families."],
            "wall_seconds":time.perf_counter()-tick,"new_decryptions":[]}


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--seconds",type=float,default=180)
    p.add_argument("--replicates",type=int,default=39);p.add_argument("--seed",type=int,default=3301011);args=p.parse_args()
    if args.seconds<=0 or args.replicates<1:p.error("positive budget and sample size required")
    deps=["experiments/plaintext_autokey_attack.py","experiments/plaintext_autokey_plan.json","experiments/attack_support.py",
          "experiments/conditional_attack_null.py","src/liberprimus/alphabet.py","src/liberprimus/ciphers.py",
          "src/liberprimus/decoding.py","transcriptions/pages.json","known_solutions/fixtures.json"]
    deps+=sorted(p.relative_to(ROOT).as_posix() for p in (ROOT/"data/raw/relikd/pages").glob("solved_*.txt"))
    dependencies={f:digest(f) for f in deps}
    fingerprint=hashlib.sha256(json.dumps({"dependencies":dependencies,"args":vars(args)},sort_keys=True).encode()).hexdigest()
    output=f"results/E011-autokey-{fingerprint[:12]}.json"
    history=[json.loads(line) for line in (ROOT/"experiment_log.jsonl").read_text(encoding="utf-8").splitlines()]
    previous=next((r for r in reversed(history) if r.get("fingerprint")==fingerprint and r.get("status")=="completed"),None)
    if previous and (ROOT/previous["output"]).exists() and digest(previous["output"])==previous["output_sha256"]:
        print(json.dumps({"status":"skipped_completed","output":previous["output"]}));raise SystemExit(0)
    row={"experiment":"E011-autokey","fingerprint":fingerprint,"input_dependencies":dependencies,"parameters":vars(args),
         "started_at":datetime.now(timezone.utc).isoformat(),"status":"started","output":output}
    def append(record):
        with (ROOT/"experiment_log.jsonl").open("a",encoding="utf-8") as f:f.write(json.dumps(record,sort_keys=True)+"\n")
    append(row);tick=time.perf_counter()
    try:
        result=run(args.seconds,args.replicates,args.seed)
        (ROOT/output).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        row.update(status="completed",output_sha256=digest(output))
        print(json.dumps({"recipes":result["evaluated_recipes"],"seconds":result["wall_seconds"],"new_decryptions":0}))
    except Exception as exc:row.update(status="failed",error=repr(exc));raise
    finally:
        row.update(finished_at=datetime.now(timezone.utc).isoformat(),wall_seconds=time.perf_counter()-tick);append(row)
