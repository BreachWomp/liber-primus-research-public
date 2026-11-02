"""Exhaustive short plaintext-autokey seeds via affine residue chains."""
import argparse
import random
import time
import numpy as np
from attack_support import load,to_indices,to_runes,model_without,top_unique
from liberprimus.alphabet import transliterate
from liberprimus.ciphers import autokey
from ciphertext_autokey_scan import tables,scores
from plaintext_autokey_attack import invert
from conditional_attack_null import conditional_shuffle
from registry import registered

SIGNS=((1,-1),(1,1),(-1,-1),(-1,1))


def affine_chain(values,period,cs,ks):
    """P_i = coefficient_i * P_(i mod period) + base_i, modulo29."""
    n=len(values);base=np.zeros(n,dtype=np.int16);coefficient=np.ones(n,dtype=np.int16)
    for i in range(period,n):
        base[i]=(cs*values[i]+ks*int(base[i-period]))%29
        coefficient[i]=ks*int(coefficient[i-period])
    return base,coefficient


def prefix_block(first,last,period):
    ids=np.arange(first,last,dtype=np.int32)
    return np.column_stack([(ids//(29**j))%29 for j in range(period)]).astype(np.int16)


def scan(values,lookup,deadline,keep=3,batch=1024,max_period=3):
    best=-float("inf");top=[];tasks=0;n=len(values)
    for skip in (False,True):
        active=[i for i,v in enumerate(values) if not skip or v!=0]
        cipher=[values[i] for i in active];skips=[i for i,v in enumerate(values) if skip and v==0]
        for period in range(1,min(max_period,len(cipher))+1):
            residue=np.arange(len(cipher))%period
            for cs,ks in SIGNS:
                base,coefficient=affine_chain(cipher,period,cs,ks)
                for first in range(0,29**period,batch):
                    if time.perf_counter()>deadline:raise TimeoutError("short-seed deadline")
                    prefix=prefix_block(first,min(first+batch,29**period),period)
                    output=np.zeros((len(prefix),n),dtype=np.int16)
                    output[:,active]=(prefix[:,residue]*coefficient[None,:]+base[None,:])%29
                    score=scores(output,lookup);tasks+=len(prefix);best=max(best,float(score.max()))
                    if keep:
                        for i in np.argsort(score)[-keep:][::-1]:
                            if len(top)==keep and float(score[i])<=top[-1]["score"]:continue
                            plain=output[i].tolist()
                            key=[(ks*(int(prefix[i,j])-cs*cipher[j]))%29 for j in range(period)]
                            assert invert(plain,key,cs,ks,skips)==values
                            row={"score":float(score[i]),"plaintext_runes":to_runes(plain),"transliteration":transliterate(plain),
                                 "recipe":{"key_indices":key,"cipher_sign":cs,"feedback_sign":ks,"skip_positions":skips,
                                           "skip_policy":"all_F" if skip else "none"},"reencryption_verified":True}
                            top=top_unique(top+[row],keep=keep)
    return best,top,tasks


def run(seconds=180,replicates=39,seed=3301014):
    tick=time.perf_counter();deadline=tick+seconds;lookup=tables(model_without())
    pages=[p for p in load("transcriptions/pages.json") if p["edition"]=="LP2" and p["page"]<=55 and p["runes"]]
    rows=[];tasks=0
    for page in pages:
        values=to_indices(page["runes"]);best,top,count=scan(values,lookup,deadline)
        rows.append({"page":page["id"],"ciphertext_runes":page["runes"],"top":top,"recipes":count});tasks+=count
        print({"page":page["id"],"score":best,"seconds":time.perf_counter()-tick},flush=True)
    chosen=max(rows,key=lambda row:row["top"][0]["score"]);values=to_indices(chosen["ciphertext_runes"])
    rng=random.Random(seed);null=[]
    for _ in range(replicates):
        sample,proposals=conditional_shuffle(values,rng,deadline=deadline)
        score,_,_=scan(sample,lookup,deadline,keep=0)
        null.append({"score":score,"ciphertext_indices":sample,"proposals":proposals})
    p=(1+sum(r["score"]>=chosen["top"][0]["score"] for r in null))/(replicates+1)
    fixture=next(f for f in load("known_solutions/fixtures.json") if f["id"]=="LP1-14_15_circumference")
    plain=to_indices(fixture["plaintext_runes"]);key=[7,11,23]
    cipher=autokey(plain,key,decrypt=False,feedback="plaintext")
    _,control,_=scan(cipher,tables(model_without(fixture["id"])),deadline)
    exact=control[0]["plaintext_runes"]==fixture["plaintext_runes"]
    return {"experiment":"E014-exhaustive-short-plaintext-autokey","status":"completed",
            "parameters":{"seconds":seconds,"replicates":replicates,"seed":seed,"batch":1024,"seed_lengths":[1,2,3],
                          "seed_space":"all29^1+29^2+29^3 keys","signs":SIGNS,"F_policies":["none","all_F"]},
            "evaluated_recipes":tasks,"pages":rows,
            "null_calibration":{"page":chosen["page"],"monte_carlo_p":p,"bonferroni_55_pages":min(1,55*p),"runs":null,
                                "model":"Independent exact count/doublet conditional shuffle; all seeds, lengths, signs and policies searched in each draw."},
            "positive_control":{"fixture":fixture["id"],"excluded_from_training":True,"key_indices":key,
                                "ciphertext_indices":cipher,"exact_top_one":exact,"top":control},
            "limits":["Only seed lengths1..3, no arbitrary selective interruptions or page continuation.",
                      "Prefix plaintext enumeration is bijective with keys for every sign choice; affine residue recurrence is checked against scalar autokey.",
                      "B39 cannot resolve significance after55page correction; a zero-exceedance candidate would need a larger registered follow-up.",
                      "Sparse language model and these negative screens cannot exclude general plaintext autokey."],
            "numpy":np.__version__,"wall_seconds":time.perf_counter()-tick,"new_decryptions":[]}


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--seconds",type=float,default=180)
    p.add_argument("--replicates",type=int,default=39);p.add_argument("--seed",type=int,default=3301014);args=p.parse_args()
    deps=["experiments/short_seed_autokey.py","experiments/short_seed_plan.json","experiments/attack_support.py",
          "experiments/ciphertext_autokey_scan.py","experiments/plaintext_autokey_attack.py","experiments/conditional_attack_null.py",
          "experiments/markov_followup.py","src/liberprimus/alphabet.py","src/liberprimus/ciphers.py","src/liberprimus/decoding.py",
          "transcriptions/pages.json","known_solutions/fixtures.json"]
    registered("E014-short-autokey",{**vars(args),"numpy":np.__version__},deps,lambda:run(args.seconds,args.replicates,args.seed))
