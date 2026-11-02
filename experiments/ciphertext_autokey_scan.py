"""Seed-free ciphertext-autokey suffix scan, bounded and globally calibrated."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
import platform
import time
import numpy as np

from attack_support import ROOT,load,digest,model_without,to_indices,to_runes
from liberprimus.alphabet import transliterate
from liberprimus.ciphers import autokey
from markov_followup import simulate_pages

SIGNS=((1,-1),(1,1),(-1,-1),(-1,1))


def tables(model):
    if model.order!=3:raise ValueError("trigram model required")
    return (np.array([model.logp((),a) for a in range(29)]),
            np.array([[model.logp((a,),b) for b in range(29)] for a in range(29)]),
            np.array([[[model.logp((a,b),c) for c in range(29)] for b in range(29)] for a in range(29)]))


def scores(rows,lookup):
    one,two,three=lookup
    if rows.shape[1]<3:raise ValueError("need >=3 runes")
    return (one[rows[:,0]]+two[rows[:,0],rows[:,1]]+
            three[rows[:,:-2],rows[:,1:-1],rows[:,2:]].sum(axis=1))/rows.shape[1]


def scan(rows,lookup,max_period=64,min_tail=60,deadline=None,keep=False):
    best=np.full(len(rows),-np.inf);record=None;tasks=0
    for period in range(1,min(max_period,rows.shape[1]-min_tail)+1):
        if deadline is not None and time.perf_counter()>deadline:raise TimeoutError("autokey deadline")
        for cs,ks in SIGNS:
            plain=(cs*rows[:,period:]+ks*rows[:,:-period])%29
            score=scores(plain,lookup)
            if keep and score[0]>best[0]:
                record={"score":float(score[0]),"period":period,"cipher_sign":cs,"feedback_sign":ks,
                        "plaintext_indices":plain[0].tolist(),"plaintext_runes":to_runes(plain[0].tolist()),
                        "transliteration":transliterate(plain[0].tolist()),"unrecovered_prefix_runes":period}
            best=np.maximum(best,score);tasks+=1
    return best,record,tasks


def run(replicates=999,seed=3301010,seconds=180):
    tick=time.perf_counter();deadline=tick+seconds;rng=np.random.default_rng(seed)
    pages=[p for p in load("transcriptions/pages.json") if p["edition"]=="LP2" and p["page"]<=55 and p["runes"]]
    train=[to_indices(p["runes"]) for p in pages if p["page"]%4!=0]
    q=sum(sum(a==b for a,b in zip(v,v[1:])) for v in train)/sum(len(v)-1 for v in train)
    lookup=tables(model_without());observed=[];null=np.full(replicates,-np.inf);tasks=0
    for page in pages:
        values=np.array(to_indices(page["runes"]),dtype=np.int16)
        maximum,top,count=scan(values[None,:],lookup,deadline=deadline,keep=True)
        # Simple scalar replay is independent of vectorized candidate construction.
        p=top["period"];cs=top["cipher_sign"];ks=top["feedback_sign"]
        assert [(cs*int(values[i])+ks*int(values[i-p]))%29 for i in range(p,len(values))]==top["plaintext_indices"]
        observed.append({"page":page["id"],"ciphertext_runes":page["runes"],"tasks":count,"top_suffix":top});tasks+=count
        for first in range(0,replicates,128):
            last=min(first+128,replicates)
            sample=simulate_pages(len(values),last-first,q,rng)
            maxima,_,_=scan(sample,lookup,deadline=deadline)
            null[first:last]=np.maximum(null[first:last],maxima)
        print(json.dumps({"page":page["id"],"best_score":top["score"],"seconds":time.perf_counter()-tick}),flush=True)
    best=max(row["top_suffix"]["score"] for row in observed)
    p=(1+int(np.sum(null>=best)))/(replicates+1)
    fixture=next(f for f in load("known_solutions/fixtures.json") if f["id"]=="LP1-03_04_divinity")
    plain=to_indices(fixture["plaintext_runes"]);key=[(7*i+3)%29 for i in range(8)]
    cipher=autokey(plain,key,decrypt=False,feedback="ciphertext")
    _,control,_=scan(np.array([cipher],dtype=np.int16),tables(model_without(fixture["id"])),deadline=deadline,keep=True)
    exact=control["period"]==8 and control["plaintext_indices"]==plain[8:]
    if not exact:raise AssertionError("ciphertext-autokey positive control not recovered")
    return {"experiment":"E010-ciphertext-autokey-suffix","status":"completed","parameters":{
                "replicates":replicates,"seed":seed,"seconds":seconds,"periods":[1,64],"minimum_suffix_runes":60,
                "signs":SIGNS,"F_interruption":"none","batch":128,"q_plugin":q,
                "memory":"At most 128 page-sized simulation rows at once; fixed 29^3 score table; no key enumeration."},
            "mechanism":"For i>=period, P_i=(cipher_sign*C_i+feedback_sign*C_(i-period)) mod29. The prefix seed is not recovered.",
            "evaluated_page_period_sign_tasks":tasks,"pages":observed,"observed_global_max":best,
            "null_global_maxima":null.tolist(),"global_p_plugin":p,"bonferroni_3_diagnostic_families":min(1,3*p),
            "selection_correction":"Every replicate maximizes over all 55 pages, eligible periods, and four signs; additionally show Bonferroni3 with two E009 diagnostics.",
            "positive_control":{"fixture":fixture["id"],"excluded_from_training":True,"seed_key":key,
                                "ciphertext_indices":cipher,"exact_suffix_recovered":exact,"result":control},
            "limits":["Stationary symmetric Markov null approximates repeat suppression; uniform marginal counts, plug-in q uncertainty not propagated.",
                      "All unknown pages were previously seen; this is exploratory, not a fresh blind holdout.",
                      "No selective F interruptions, plaintext feedback, transposition, or cross-page stream in this grid.",
                      "Scoring begins at the suffix boundary; a promising suffix would still require recovery and validation of the prefix."],
            "numpy":np.__version__,"python":platform.python_version(),"wall_seconds":time.perf_counter()-tick,"new_decryptions":[]}


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--replicates",type=int,default=999);p.add_argument("--seed",type=int,default=3301010)
    p.add_argument("--seconds",type=float,default=180);args=p.parse_args()
    if args.replicates<99 or args.seconds<=0:p.error("need >=99 replicates and positive budget")
    deps=["experiments/ciphertext_autokey_scan.py","experiments/attack_support.py","experiments/markov_followup.py",
          "experiments/autokey_plan.json","src/liberprimus/alphabet.py","src/liberprimus/ciphers.py",
          "src/liberprimus/decoding.py","transcriptions/pages.json","known_solutions/fixtures.json"]
    dependencies={f:digest(f) for f in deps}
    fingerprint=hashlib.sha256(json.dumps({"dependencies":dependencies,"args":vars(args),"numpy":np.__version__,"python":platform.python_version()},sort_keys=True).encode()).hexdigest()
    output=f"results/E010-autokey-{fingerprint[:12]}.json"
    history=[json.loads(line) for line in (ROOT/"experiment_log.jsonl").read_text(encoding="utf-8").splitlines()]
    previous=next((r for r in reversed(history) if r.get("fingerprint")==fingerprint and r.get("status")=="completed"),None)
    if previous and (ROOT/previous["output"]).exists() and digest(previous["output"])==previous["output_sha256"]:
        print(json.dumps({"status":"skipped_completed","output":previous["output"]}));raise SystemExit(0)
    row={"experiment":"E010-autokey","fingerprint":fingerprint,"input_dependencies":dependencies,"parameters":vars(args),
         "started_at":datetime.now(timezone.utc).isoformat(),"status":"started","output":output}
    def append(record):
        with (ROOT/"experiment_log.jsonl").open("a",encoding="utf-8") as f:f.write(json.dumps(record,sort_keys=True)+"\n")
    append(row);tick=time.perf_counter()
    try:
        result=run(args.replicates,args.seed,args.seconds)
        (ROOT/output).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        row.update(status="completed",output_sha256=digest(output))
        print(json.dumps({k:result[k] for k in ["global_p_plugin","evaluated_page_period_sign_tasks","wall_seconds"]}))
    except Exception as exc:row.update(status="failed",error=repr(exc));raise
    finally:
        row.update(finished_at=datetime.now(timezone.utc).isoformat(),wall_seconds=time.perf_counter()-tick);append(row)
