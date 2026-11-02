"""Revisit the registered selective-F grids with independent external4gram scoring."""
import argparse
import random
import time
from attack_support import load,key_catalog,stream_catalog,to_indices,candidate,top_unique
from liberprimus.decoding import selective_decode
from external_language import external_model,paragraphs
from conditional_attack_null import conditional_shuffle
from registry import registered

SIGNS=((1,-1),(1,1),(-1,-1),(-1,1))


def search(values,model,deadline,keep=3):
    keys=key_catalog();streams=stream_catalog(len(values)+256);top=[];best=-float("inf");tasks=0
    options=[("vigenere",k["indices"],True) for k in keys]+[(name,k,False) for name,k in streams.items()]
    for family,key,repeating in options:
        for cs,ks in SIGNS:
            out=selective_decode(values,key,model,repeating=repeating,starts=range(len(key)) if repeating else range(256),
                                 cipher_sign=cs,key_sign=ks,deadline=deadline)
            tasks+=1;best=max(best,out.score)
            if keep and (len(top)<keep or out.score>top[-1]["score"]):
                recipe={"family":family,"cipher_sign":cs,"key_sign":ks}
                if repeating:recipe["key_indices"]=key
                top=top_unique(top+[candidate(out,values,key,recipe,repeating)],keep=keep)
    return best,top,tasks


def run(mode,first,last,seconds,replicates,seed):
    tick=time.perf_counter();deadline=tick+seconds;model=external_model(4)
    result={"experiment":"E018-external-selective-"+mode,"status":"completed","source":paragraphs()[2],
            "parameters":{"mode":mode,"first":first,"last":last,"seconds":seconds,"replicates":replicates,"seed":seed,
                          "key_cycles":381,"number_streams":3,"number_stream_offsets":[0,255],"signs":SIGNS,
                          "F_masks":"all subsets via exactDP","language_order":4,"alpha":0.5,"strength":5.0},"new_decryptions":[]}
    if mode=="controls":
        fixtures={f["id"]:f for f in load("known_solutions/fixtures.json")};rows=[]
        for ident in ("LP1-03_04_divinity","LP1-14_15_circumference","LP2-56_totient_primes"):
            fixture=fixtures[ident];_,top,tasks=search(to_indices(fixture["ciphertext_runes"]),model,deadline)
            exact=top[0]["plaintext_runes"]==fixture["plaintext_runes"]
            rows.append({"fixture":ident,"exact":exact,"top":top,"key_sign_tasks":tasks})
            print({"fixture":ident,"exact":exact,"seconds":time.perf_counter()-tick},flush=True)
        result.update(controls=rows,gate_passed=all(r["exact"] for r in rows))
    else:
        pages=[p for p in load("transcriptions/pages.json") if p["edition"]=="LP2" and first<=p["page"]<=last and p["page"]<=55 and p["runes"]]
        rows=[]
        for page in pages:
            best,top,tasks=search(to_indices(page["runes"]),model,deadline)
            rows.append({"page":page["id"],"ciphertext_runes":page["runes"],"top":top,"key_sign_tasks":tasks})
            print({"page":page["id"],"score":best,"seconds":time.perf_counter()-tick},flush=True)
        result["pages"]=rows
        if mode=="null":
            if len(rows)!=1:raise ValueError("null needs a single selected page")
            values=to_indices(rows[0]["ciphertext_runes"]);rng=random.Random(seed);null=[]
            for i in range(replicates):
                sample,proposals=conditional_shuffle(values,rng,deadline=deadline)
                score,_,_=search(sample,model,deadline,keep=0)
                null.append({"score":score,"ciphertext_indices":sample,"proposals":proposals})
                if (i+1)%5==0:print({"null_replicates":i+1,"seconds":time.perf_counter()-tick},flush=True)
            p=(1+sum(r["score"]>=rows[0]["top"][0]["score"] for r in null))/(replicates+1)
            result["null_calibration"]={"runs":null,"monte_carlo_p":p,"bonferroni_55_pages":min(1,55*p),
                "selection":"Same complete union of word/number grids optimized in each exact count/doublet shuffle; Bonferroni55for selected page."}
    result["limits"]=["This is a changed-score rescan of E007/E008, not a new cipher family or independent discovery.",
                      "External model fixed using previously seen controls; source-independent training is not independent historical validation.",
                      "AllFsubsets covered only in these finite known-key streams; no arbitrary keys, transpositions or across-page continuation.",
                      "B19cannot resolve corrected significance; null calibration is a screen for chance maxima."]
    result["wall_seconds"]=time.perf_counter()-tick
    return result


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--mode",choices=["controls","pages","null"],required=True)
    p.add_argument("--first",type=int,default=0);p.add_argument("--last",type=int,default=55)
    p.add_argument("--seconds",type=float,default=180.0);p.add_argument("--replicates",type=int,default=19)
    p.add_argument("--seed",type=int,default=3301018);args=p.parse_args()
    deps=["experiments/external_selective_attack.py","experiments/external_selective_plan.json","experiments/external_language.py",
          "experiments/external_model_plan.json","experiments/attack_support.py","experiments/conditional_attack_null.py",
          "src/liberprimus/alphabet.py","src/liberprimus/ciphers.py","src/liberprimus/decoding.py","known_solutions/fixtures.json",
          "transcriptions/pages.json","sources/emerson_manifest.json","data/raw/gutenberg/pg2944.txt"]
    from attack_support import ROOT
    deps+=sorted(p.relative_to(ROOT).as_posix() for p in (ROOT/"data/raw/relikd/pages").glob("solved_*.txt"))
    ident="E018-"+args.mode+(f"-LP2-{args.first:02}_{args.last:02}" if args.mode!="controls" else "")
    registered(ident,vars(args),deps,lambda:run(args.mode,args.first,args.last,args.seconds,args.replicates,args.seed))
