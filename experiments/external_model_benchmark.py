"""Frozen external-only scoring benchmark; no unknown-page selection."""
import argparse
import random
import time
from attack_support import load,to_indices,to_runes,stream_catalog,candidate
from liberprimus.decoding import selective_decode
from external_language import external_model,paragraphs
from registry import registered


def run(seconds=180,seed=3301016):
    tick=time.perf_counter();deadline=tick+seconds;rng=random.Random(seed)
    fixtures=[f for f in load("known_solutions/fixtures.json") if f.get("eligible_language_training")]
    corruptions={}
    for f in fixtures:
        plain=to_indices(f["plaintext_runes"]);samples=[]
        for width in (1,5):
            for _ in range(100):
                sample=list(plain);first=rng.randrange(len(plain)-width+1)
                for i in range(first,first+width):sample[i]=(sample[i]+rng.randrange(1,29))%29
                samples.append({"width":width,"indices":sample})
        corruptions[f["id"]]=samples
    results=[]
    for order in (3,4):
        model=external_model(order);rows=[];decoded=[]
        for f in fixtures:
            plain=to_indices(f["plaintext_runes"]);truth=model.score(plain)
            null=[model.score(s["indices"]) for s in corruptions[f["id"]]]
            rows.append({"fixture":f["id"],"correct_score":truth,"better_than_mutations":sum(truth>s for s in null),
                         "mutation_scores":null,"comparisons":len(null)})
            if f["cipher"]=="vigenere":
                key=f["key_indices"];repeat=True;starts=range(len(key));family="vigenere"
            elif f["id"]=="LP2-56_totient_primes":
                key=stream_catalog(len(plain)+256)["prime_totient"];repeat=False;starts=range(256);family="prime_totient"
            else:continue
            values=to_indices(f["ciphertext_runes"])
            out=selective_decode(values,key,model,repeating=repeat,starts=starts,deadline=deadline)
            record=candidate(out,values,key,{"family":family,"key_indices":key if repeat else None,"cipher_sign":1,"key_sign":-1},repeat)
            record.update(fixture=f["id"],exact=out.plaintext==plain,
                          character_accuracy=sum(a==b for a,b in zip(out.plaintext,plain))/len(plain),expected_skip_positions=f["skip_positions"])
            decoded.append(record)
        results.append({"order":order,"rows":rows,"known_key_decodings":decoded,
                        "correct_strictly_better":sum(r["better_than_mutations"] for r in rows),
                        "comparisons":sum(r["comparisons"] for r in rows)})
        print({"order":order,"exact_controls":sum(r["exact"] for r in decoded),"controls":len(decoded),"seconds":time.perf_counter()-tick},flush=True)
    return {"experiment":"E016-external-model-benchmark","status":"completed","source":paragraphs()[2],
            "parameters":{"orders":[3,4],"alpha":0.5,"strength":5.0,"seed":seed,"seconds":seconds},
            "results":results,"corruptions":corruptions,
            "limits":["All LP controls have been inspected in earlier phases; source-independent training is not a fresh blind evaluation.",
                      "Order3and4 fixed before testing, with no parameter tuning on unknown ciphertext; comparisons across orders are exploratory.",
                      "Corruption samples overlap and are correlated; descriptive counts, not binomial inference.",
                      "Passing known-key controls never validates an unknown decryption."],
            "wall_seconds":time.perf_counter()-tick,"new_decryptions":[]}


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--seconds",type=float,default=180.0);p.add_argument("--seed",type=int,default=3301016)
    args=p.parse_args()
    deps=["experiments/external_model_benchmark.py","experiments/external_language.py","experiments/external_model_plan.json",
          "experiments/attack_support.py","src/liberprimus/decoding.py","src/liberprimus/alphabet.py","src/liberprimus/ciphers.py",
          "known_solutions/fixtures.json","sources/emerson_manifest.json","data/raw/gutenberg/pg2944.txt"]
    registered("E016-external-language",vars(args),deps,lambda:run(args.seconds,args.seed))
