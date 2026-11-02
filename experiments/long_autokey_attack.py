"""Registered control and unknown-page runs for the fixed autokey beam search."""
import argparse
import random
import time
import numpy as np
from attack_support import load,to_indices
from liberprimus.ciphers import autokey
from external_language import external_model,paragraphs
from ngram_arrays import dense_tables
from autokey_beam import search
from conditional_attack_null import conditional_shuffle
from registry import registered


def run(mode,first=0,last=55,seconds=180.0,replicates=19,seed=3301017):
    tick=time.perf_counter();deadline=tick+seconds
    lookup3=dense_tables(external_model(3));lookup4=dense_tables(external_model(4))
    result={"experiment":"E017-long-autokey-"+mode,"status":"completed","parameters":{"first":first,"last":last,
        "seconds":seconds,"seed":seed,"replicates":replicates,"periods":[4,12],"beam_width":512,"keep_per_cut":16,
        "language":"external3gram candidate generation, external4gram ranking","F_policies":["none","all_F"],
        "signs":[[1,-1],[1,1],[-1,-1],[-1,1]]},"source":paragraphs()[2],"new_decryptions":[]}
    if mode=="controls":
        rng=random.Random(seed);rows=[]
        fixtures={f["id"]:f for f in load("known_solutions/fixtures.json")}
        for ident in ("LP1-03_04_divinity","LP1-14_15_circumference"):
            plain=to_indices(fixtures[ident]["plaintext_runes"])
            for period in (4,8,12):
                key=[rng.randrange(29) for _ in range(period)]
                cipher=autokey(plain,key,decrypt=False,feedback="plaintext")
                top,stats=search(cipher,lookup3,lookup4,deadline)
                exact=top[0]["plaintext_runes"]==fixtures[ident]["plaintext_runes"]
                rows.append({"fixture":ident,"injected_key":key,"injected_period":period,"ciphertext_indices":cipher,
                             "exact":exact,"top":top,"search":stats})
                print({"fixture":ident,"period":period,"exact":exact,"seconds":time.perf_counter()-tick},flush=True)
        result.update(controls=rows,passed=sum(r["exact"] for r in rows),gate_passed=all(r["exact"] for r in rows))
    else:
        pages=[p for p in load("transcriptions/pages.json") if p["edition"]=="LP2" and first<=p["page"]<=last and p["page"]<=55 and p["runes"]]
        rows=[]
        for page in pages:
            values=to_indices(page["runes"]);top,stats=search(values,lookup3,lookup4,deadline)
            rows.append({"page":page["id"],"ciphertext_runes":page["runes"],"top":top,"search":stats})
            print({"page":page["id"],"score":top[0]["score"],"seconds":time.perf_counter()-tick},flush=True)
        result["pages"]=rows
        if mode=="null":
            if len(rows)!=1:raise ValueError("null calibration requires exactly one page")
            row=rows[0];values=to_indices(row["ciphertext_runes"]);rng=random.Random(seed);null=[]
            for i in range(replicates):
                sample,proposals=conditional_shuffle(values,rng,deadline=deadline)
                top,stats=search(sample,lookup3,lookup4,deadline)
                null.append({"score":top[0]["score"],"ciphertext_indices":sample,"proposals":proposals,"search":stats})
                if (i+1)%5==0:print({"null_replicates":i+1,"seconds":time.perf_counter()-tick},flush=True)
            p=(1+sum(n["score"]>=row["top"][0]["score"] for n in null))/(replicates+1)
            result["null_calibration"]={"runs":null,"monte_carlo_p":p,"bonferroni_55_pages":min(1,55*p),
                "selection":"Highest mean4gram score across55pages; same full optimizer on every exact count/doublet conditional shuffle."}
    result["limitations"]=["Beam search is heuristic; all finite paths are not enumerated. Negative result does not exclude this cipher family.",
        "All cyclic cuts are tried; top16percut generated under trigram are reranked by a4gram model. Null replicates repeat this selection.",
        "External-only training, but LP controls were previously inspected; not fresh blind validation.",
        "Seed lengths4..12 only; no arbitrary F subset or cross-page key."]
    result["wall_seconds"]=time.perf_counter()-tick
    return result


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--mode",choices=["controls","pages","null"],required=True)
    p.add_argument("--first",type=int,default=0);p.add_argument("--last",type=int,default=55)
    p.add_argument("--seconds",type=float,default=180.0);p.add_argument("--replicates",type=int,default=19)
    p.add_argument("--seed",type=int,default=3301017);args=p.parse_args()
    deps=["experiments/long_autokey_attack.py","experiments/long_autokey_plan.json","experiments/autokey_beam.py",
        "experiments/ngram_arrays.py","experiments/external_language.py","experiments/external_model_plan.json",
        "experiments/short_seed_autokey.py","experiments/plaintext_autokey_attack.py","experiments/conditional_attack_null.py",
        "experiments/attack_support.py","src/liberprimus/alphabet.py","src/liberprimus/ciphers.py","src/liberprimus/decoding.py",
        "known_solutions/fixtures.json","transcriptions/pages.json","sources/emerson_manifest.json","data/raw/gutenberg/pg2944.txt"]
    ident="E017-"+args.mode+(f"-LP2-{args.first:02}_{args.last:02}" if args.mode!="controls" else "")
    registered(ident,{**vars(args),"numpy":np.__version__},deps,
               lambda:run(args.mode,args.first,args.last,args.seconds,args.replicates,args.seed))
