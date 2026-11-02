"""Heldout periodic-IC scan under a fitted symmetric Markov null.

This tests unskipped page-local streams only. It cannot exclude repeating keys
with selective interruptions, transposition or section-dependent alignment.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"experiments"))
sys.path.insert(0,str(ROOT/"src"))
from markov_followup import rune_indices,simulate_pages,symmetric_max_t
from liberprimus.ciphers import vigenere


def periodic_rows(rows,period):
    """Pooled IC over residue columns, using exact comparable-pair denominator."""
    batch,n=rows.shape
    lengths=np.bincount(np.arange(n)%period,minlength=period)
    denominator=int(np.sum(lengths*(lengths-1)))
    if denominator==0:
        return np.full(batch,np.nan),0
    offsets=(np.arange(batch)[:,None]*period+np.arange(n)[None,:]%period)*29
    counts=np.bincount((offsets+rows).ravel(),minlength=batch*period*29).reshape(batch,period,29)
    return np.sum(counts*(counts-1),axis=(1,2))/denominator,denominator


def run(root,replicates=9999,seed=3301005,timeout_seconds=180):
    start=time.perf_counter()
    raw=(root/"transcriptions/pages.json").read_bytes()
    fixture_raw=(root/"known_solutions/fixtures.json").read_bytes()
    pages=[p for p in json.loads(raw) if p["edition"]=="LP2" and p["page"]<=55 and p["runes"]]
    pages.sort(key=lambda p:p["page"])
    train=[rune_indices(p["runes"]) for p in pages if p["page"]%4!=0]
    held=[p for p in pages if p["page"]%4==0]
    q=sum(int(np.sum(x[:-1]==x[1:])) for x in train)/sum(len(x)-1 for x in train)
    rng=np.random.default_rng(seed)
    observed_parts,simulated_parts,features=[],[],[]
    for page in held:
        values=rune_indices(page["runes"])
        periods=[]
        observed=[]
        for period in range(2,33):
            score,pairs=periodic_rows(values[None,:],period)
            if pairs>=100:
                periods.append(period);observed.append(float(score[0]))
                features.append({"page_id":page["id"],"period":period,"ordered_pairs":pairs,"ic":float(score[0])})
        simulated=np.zeros((replicates,len(periods)))
        for first in range(0,replicates,128):
            if time.perf_counter()-start>timeout_seconds:
                raise TimeoutError("Period scan exceeded wall-time budget")
            last=min(first+128,replicates)
            chains=simulate_pages(len(values),last-first,q,rng)
            for j,period in enumerate(periods):
                simulated[first:last,j]=periodic_rows(chains,period)[0]
        observed_parts.extend(observed)
        simulated_parts.append(simulated)
    simulated=np.concatenate(simulated_parts,axis=1)
    test=symmetric_max_t(np.array(observed_parts),simulated)
    for j,feature in enumerate(features):
        feature.update(p_maxT=test["adjusted_p_plugin"][j],abs_z=test["observed_abs_z"][j])
    # Inject a known period with no interrupts; no language-model fitting involved.
    control=next(f for f in json.loads(fixture_raw) if f["id"]=="LP1-03_04_divinity")
    plain=rune_indices(control["plaintext_runes"]).tolist()
    cipher=np.array(vigenere(plain,control["key_indices"],decrypt=False),dtype=np.int16)
    observed=float(periodic_rows(cipher[None,:],8)[0][0])
    draws=[]
    for first in range(0,replicates,128):
        if time.perf_counter()-start>timeout_seconds:
            raise TimeoutError("Period scan positive control exceeded wall-time budget")
        batch=min(128,replicates-first)
        draws.extend(periodic_rows(simulate_pages(len(cipher),batch,q,rng),8)[0].tolist())
    control_p=(1+sum(value>=observed for value in draws))/(replicates+1)
    if control_p>0.01:
        raise AssertionError("Injected period-8 positive control failed")
    return {"experiment":"E005-heldout-period-scan","input_sha256":hashlib.sha256(raw).hexdigest(),
        "fixtures_sha256":hashlib.sha256(fixture_raw).hexdigest(),
        "parameters":{"replicates":replicates,"seed":seed,"timeout_seconds":timeout_seconds,"periods":[2,32],
                      "minimum_ordered_pairs":100,"batch":128,"q_training":q,
                      "split":"training page%4!=0, heldout page%4==0","heldout_ids":[p["id"] for p in held]},
        "family_size":len(features),"global_p_plugin":test["global_p_plugin"],
        "features":sorted(features,key=lambda f:f["abs_z"],reverse=True),
        "positive_control":{"source_fixture":control["id"],"construction":"Re-encrypt known plaintext under DIVINITY with no interrupts",
                            "length":len(cipher),"period":8,"ic":observed,"p_upper_plugin":control_p},
        "limitations":["Plug-in q uncertainty not propagated; uniform marginals rather than count conditioning.",
            "Computational split reused from E002; global E002/E005 p-values require joint correction if used inferentially.",
            "MaxT corrects all eligible heldout page/period features; no effect-size or power guarantee for weaker alternatives.",
            "No selective interrupter search, no section key alignment, no transposition. Non-rejection cannot eliminate Vigenere.",
            "Positive control is an injected unskipped period, not a recovered unknown key."],
        "wall_seconds":time.perf_counter()-start,"numpy":np.__version__,"new_decryptions":[]}


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root",type=Path,default=ROOT)
    p.add_argument("--replicates",type=int,default=9999)
    p.add_argument("--seed",type=int,default=3301005)
    p.add_argument("--timeout-seconds",type=float,default=180)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    if args.replicates<99 or args.timeout_seconds<=0:p.error("Require >=99 replicates and positive timeout")
    result=run(args.root,args.replicates,args.seed,args.timeout_seconds)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:result[k] for k in ["experiment","family_size","global_p_plugin","positive_control","wall_seconds"]}))

