"""Concrete attacks on unsolved LP2 with globally optimized F interruptions."""
import argparse
import itertools
import json
import math
import random
import time
from pathlib import Path

from attack_support import (ROOT,load,model_without,training_fixtures,key_catalog,stream_catalog,
                           to_indices,to_runes,digest,candidate,top_unique,BackoffModel)
from liberprimus.decoding import selective_decode,replay

SIGNS=((1,-1),(1,1),(-1,-1),(-1,1))


def controls(timeout=180):
    started=time.perf_counter();deadline=started+timeout;rows=[]
    rng=random.Random(3301006)
    fixtures=load("known_solutions/fixtures.json")
    for fixture in training_fixtures():
        expected=to_indices(fixture["plaintext_runes"])
        model=model_without(fixture["id"])
        correct=model.score(expected)
        scores=[]
        for width in (1,5):
            for repeat in range(100):
                modified=list(expected);first=rng.randrange(len(modified)-width+1)
                for i in range(first,first+width):modified[i]=(modified[i]+rng.randrange(1,29))%29
                scores.append({"width":width,"score":model.score(modified)})
        row={"fixture":fixture["id"],"evaluation":"leave-one-section-out",
             "correct_score":correct,"corruption_comparisons":len(scores),
             "correct_strictly_better":sum(correct>x["score"] for x in scores),
             "mutation_scores":scores}
        if fixture["cipher"]=="vigenere":
            values=to_indices(fixture["ciphertext_runes"]);key=fixture["key_indices"]
            decoded=selective_decode(values,key,model,starts=range(len(key)),deadline=deadline)
            row["known_key_decoding"]={**candidate(decoded,values,key,{"family":"vigenere","key_indices":key,"cipher_sign":1,"key_sign":-1},True),
                "exact":decoded.plaintext==expected,"character_accuracy":sum(a==b for a,b in zip(expected,decoded.plaintext))/len(expected),
                "true_skip_positions":fixture["skip_positions"]}
        rows.append(row)
    model=model_without()
    fixture=next(f for f in fixtures if f["id"]=="LP2-56_totient_primes")
    values=to_indices(fixture["ciphertext_runes"]);key=stream_catalog(len(values)+32)["prime_totient"]
    decoded=selective_decode(values,key,model,repeating=False,starts=range(29),deadline=deadline)
    regression={**candidate(decoded,values,key,{"family":"prime_totient","cipher_sign":1,"key_sign":-1},False),
                "exact":decoded.plaintext==fixture["expected_indices"],"role":"seen regression, never a fresh holdout"}
    return {"experiment":"E006-selective-control-benchmark","model":{"order":3,"alpha":0.5,"strength":5},
        "seed":3301006,"rows":rows,"LP2_56_seen_regression":regression,
        "total_mutations":sum(row["corruption_comparisons"] for row in rows),
        "correct_strictly_better":sum(row["correct_strictly_better"] for row in rows),
        "limits":["Mutation scores are correlated and are descriptive; no p-value or independent sample count claimed.",
                  "Parameters frozen before this benchmark; language score never certifies decryption.",
                  "Control plaintext is not included in its own training fold."],
        "wall_seconds":time.perf_counter()-started,"new_decryptions":[]}


def attack(mode,timeout=180,first=0,last=55,max_offset=255,output=None):
    started=time.perf_counter();deadline=started+timeout
    model=model_without();keys=key_catalog();streams=stream_catalog(1500+max_offset)
    pages=[p for p in load("transcriptions/pages.json") if p["edition"]=="LP2" and first<=p["page"]<=last and p["runes"]]
    rows=[];transitions=0;tasks=0
    for page in sorted(pages,key=lambda p:p["page"]):
        values=to_indices(page["runes"]);top=[];page_tasks=0;page_transitions=0
        options=[("vigenere",row["indices"]) for row in keys] if mode=="dictionary" else list(streams.items())
        for family,key in options:
            repeating=mode=="dictionary"
            starts=range(len(key)) if repeating else range(max_offset+1)
            for cs,ks in SIGNS:
                decoded=selective_decode(values,key,model,repeating=repeating,starts=starts,cipher_sign=cs,key_sign=ks,deadline=deadline)
                recipe={"family":family,"cipher_sign":cs,"key_sign":ks}
                if repeating:recipe["key_indices"]=key
                row=candidate(decoded,values,key,recipe,repeating)
                top=top_unique(top+[row]);page_transitions+=decoded.transitions;page_tasks+=1
        rows.append({"page":page["id"],"ciphertext_runes":page["runes"],"rune_count":len(values),
                     "f_count":values.count(0),"evaluated_key_sign_tasks":page_tasks,"dp_transitions":page_transitions,"top":top})
        transitions+=page_transitions;tasks+=page_tasks
        print(json.dumps({"page":page["id"],"mode":mode,"best_score":top[0]["score"],"seconds":time.perf_counter()-started}),flush=True)
        if output:
            partial={"status":"partial_not_complete","mode":mode,"pages":rows,"new_decryptions":[]}
            output.with_suffix(".partial.json").write_text(json.dumps(partial,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return {"experiment":"E007-selective-dictionary" if mode=="dictionary" else "E008-selective-streams",
        "status":"completed","parameters":{"mode":mode,"page_range":[first,last],"max_offset":max_offset,
            "signs":SIGNS,"model":{"order":3,"alpha":0.5,"strength":5},
            "all_initial_key_phases":True,"F_masks":"all subsets, optimized exactly by dynamic programming",
            "training_ids":[f["id"] for f in training_fixtures()],"timeout_seconds":timeout},
        "key_catalog":keys if mode=="dictionary" else None,"stream_families":list(streams) if mode=="streams" else None,
        "input_sha256":digest("transcriptions/pages.json"),"fixtures_sha256":digest("known_solutions/fixtures.json"),
        "pages":rows,"evaluated_key_sign_tasks":tasks,"dp_transitions":transitions,
        "limits":["DP finds the global optimum under this finite-context score, not the correct plaintext by guarantee.",
                  "No deleted nulls, transpositions, changing alphabets, or cross-page keys in this family.",
                  "Scores are selected over keys/phases/signs/F masks; uncalibrated maxima are not evidence of decryption.",
                  "Distinct keys are reduced by primitive period and rotation; reverse spellings are also included.",
                  "A negative result only concerns this finite family and scorer."],
        "wall_seconds":time.perf_counter()-started,"new_decryptions":[]}


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mode",choices=["controls","dictionary","streams"],required=True)
    p.add_argument("--first",type=int,default=0);p.add_argument("--last",type=int,default=55)
    p.add_argument("--max-offset",type=int,default=255)
    p.add_argument("--timeout-seconds",type=float,default=180)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    if args.timeout_seconds<=0 or not 0<=args.first<=args.last<=55 or args.max_offset<0:p.error("invalid budget/range")
    args.output.parent.mkdir(parents=True,exist_ok=True)
    result=controls(args.timeout_seconds) if args.mode=="controls" else attack(args.mode,args.timeout_seconds,args.first,args.last,args.max_offset,args.output)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"experiment":result["experiment"],"wall_seconds":result["wall_seconds"],"new_decryptions":0}),flush=True)
