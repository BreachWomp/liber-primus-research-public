"""Full-search calibration on selected pages, with explicit selection correction.

Uniform shuffles conditional on exact rune counts AND adjacent-equality count
are obtained by rejection, not by an accepted-move Markov chain.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random
import time

from attack_support import ROOT, load, model_without, key_catalog, stream_catalog, to_indices, digest
from liberprimus.decoding import selective_decode

SIGNS=((1,-1),(1,1),(-1,-1),(-1,1))


def doubles(values):
    return sum(a==b for a,b in zip(values,values[1:]))


def conditional_shuffle(values,rng,max_proposals=100000,deadline=None):
    target=doubles(values)
    for proposal in range(1,max_proposals+1):
        if deadline is not None and time.perf_counter()>deadline:
            raise TimeoutError("conditional shuffle deadline")
        shuffled=list(values);rng.shuffle(shuffled)
        if doubles(shuffled)==target:
            return shuffled,proposal
    raise TimeoutError("conditional rejection proposal cap")


def search(values,model,keys,streams,deadline):
    best=-float("inf")
    for key in keys:
        for cs,ks in SIGNS:
            result=selective_decode(values,key,model,starts=range(len(key)),cipher_sign=cs,key_sign=ks,deadline=deadline)
            best=max(best,result.score)
    for key in streams.values():
        for cs,ks in SIGNS:
            result=selective_decode(values,key,model,repeating=False,starts=range(256),cipher_sign=cs,key_sign=ks,deadline=deadline)
            best=max(best,result.score)
    return best


def run(page_id,replicates,seed,seconds):
    started=time.perf_counter();deadline=started+seconds
    page=next(p for p in load("transcriptions/pages.json") if p["id"]==page_id)
    values=to_indices(page["runes"]);model=model_without()
    keys=[r["indices"] for r in key_catalog()];streams=stream_catalog(1755)
    rng=random.Random(seed);observed=search(values,model,keys,streams,deadline)
    rows=[]
    for i in range(replicates):
        sample,proposals=conditional_shuffle(values,rng,deadline=deadline)
        assert Counter(sample)==Counter(values) and doubles(sample)==doubles(values)
        score=search(sample,model,keys,streams,deadline)
        rows.append({"replicate":i,"max_score":score,"proposals":proposals,
                     "ciphertext_indices":sample})
        if (i+1)%10==0:print(json.dumps({"page":page_id,"replicates":i+1,"seconds":time.perf_counter()-started}),flush=True)
    exceed=sum(r["max_score"]>=observed for r in rows)
    p=(1+exceed)/(1+replicates)
    return {"experiment":"E009-conditional-full-search-null","status":"completed","page":page_id,
            "seed":seed,"replicates":replicates,"observed_max_score":observed,
            "null_exceedances":exceed,"monte_carlo_p":p,"bonferroni_55_pages":min(1,p*55),
            "null":"Uniform permutations conditional on exact page rune counts and stream adjacent-equality count.",
            "method":"Independent rejection shuffles; each labeled permutation equally likely, constant multiplicity per distinct string.",
            "selection":"Union of dictionary and stream grids is maximized in every replicate; Bonferroni 55 covers page selection. Unrun pages assigned p=1.",
            "parameters":{"keys":len(keys),"signs":SIGNS,"stream_offsets":[0,255],"F_masks":"all subsets","max_shuffle_proposals":100000,"timeout_seconds":seconds},
            "limits":["Post-screen calibration, registered before null sampling; no new holdout plaintext.",
                      "39 replicates cannot resolve significance after 55-page correction; designed to reject casual promotion, not certify a discovery.",
                      "This conditional exchangeability null does not preserve word layout or other possible ciphertext structure."],
            "null_runs":rows,"wall_seconds":time.perf_counter()-started,"new_decryptions":[]}


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--page",required=True);p.add_argument("--replicates",type=int,default=39)
    p.add_argument("--seed",type=int,required=True);p.add_argument("--seconds",type=float,default=180)
    args=p.parse_args()
    if args.replicates<1 or args.seconds<=0:p.error("positive counts/budget required")
    deps=["experiments/conditional_attack_null.py","experiments/attack_support.py","experiments/phase2_null_plan.json",
          "src/liberprimus/decoding.py","src/liberprimus/alphabet.py","src/liberprimus/ciphers.py",
          "transcriptions/pages.json","known_solutions/fixtures.json"]
    deps+=sorted(p.relative_to(ROOT).as_posix() for p in (ROOT/"data/raw/relikd/pages").glob("solved_*.txt"))
    dependencies={f:digest(f) for f in deps}
    fingerprint=hashlib.sha256(json.dumps({"dependencies":dependencies,"args":vars(args)},sort_keys=True).encode()).hexdigest()
    output=f"results/E009-null-{args.page}-{fingerprint[:12]}.json"
    history=[json.loads(line) for line in (ROOT/"experiment_log.jsonl").read_text(encoding="utf-8").splitlines()]
    previous=next((r for r in reversed(history) if r.get("fingerprint")==fingerprint and r.get("status")=="completed"),None)
    if previous and (ROOT/previous["output"]).exists() and digest(previous["output"])==previous["output_sha256"]:
        print(json.dumps({"status":"skipped_completed","output":previous["output"]}))
        raise SystemExit(0)
    row={"experiment":"E009-null-"+args.page,"fingerprint":fingerprint,"input_dependencies":dependencies,
         "parameters":vars(args),"started_at":datetime.now(timezone.utc).isoformat(),"status":"started","output":output}
    def append(record):
        with (ROOT/"experiment_log.jsonl").open("a",encoding="utf-8") as f:f.write(json.dumps(record,sort_keys=True)+"\n")
    append(row);tick=time.perf_counter()
    try:
        result=run(args.page,args.replicates,args.seed,args.seconds)
        (ROOT/output).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        row.update(status="completed",output_sha256=digest(output))
        print(json.dumps({k:result[k] for k in ["page","monte_carlo_p","bonferroni_55_pages","wall_seconds"]}))
    except Exception as exc:
        row.update(status="failed",error=repr(exc));raise
    finally:
        row.update(finished_at=datetime.now(timezone.utc).isoformat(),wall_seconds=time.perf_counter()-tick)
        append(row)
