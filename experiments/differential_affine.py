"""First differences followed by all invertible affine maps over Z29."""
import argparse
import time
import numpy as np
from attack_support import load,to_indices,to_runes,model_without
from liberprimus.alphabet import transliterate
from ciphertext_autokey_scan import tables,scores
from markov_followup import simulate_pages
from registry import registered


def recover(cipher,a,b):
    return [(a*(v-u)+b)%29 for u,v in zip(cipher,cipher[1:])]


def encrypt_suffix(plain,a,b,initial):
    out=[initial];inverse=pow(a,-1,29)
    for p in plain:out.append((out[-1]+inverse*(p-b))%29)
    return out


def scan(rows,lookup,deadline,keep=False):
    differences=(rows[:,1:]-rows[:,:-1])%29
    shifts=np.arange(29,dtype=np.int16)[None,:,None]
    best=np.full(len(rows),-np.inf);record=None
    for a in range(1,29):
        if time.perf_counter()>deadline:raise TimeoutError("differential-affine deadline")
        plain=(a*differences[:,None,:]+shifts)%29
        score=scores(plain.reshape(-1,plain.shape[-1]),lookup).reshape(len(rows),29)
        if keep:
            b=int(score[0].argmax())
            if score[0,b]>best[0]:
                values=plain[0,b].tolist()
                record={"score":float(score[0,b]),"plaintext_runes":to_runes(values),"transliteration":transliterate(values),
                        "recipe":{"a":a,"b":b,"initial_cipher_rune":int(rows[0,0]),"unrecovered_prefix_runes":1},
                        "reencryption_verified":encrypt_suffix(values,a,b,int(rows[0,0]))==rows[0].tolist()}
                assert record["reencryption_verified"]
        best=np.maximum(best,score.max(axis=1))
    return best,record


def run(seconds=180,replicates=199,seed=3301015):
    tick=time.perf_counter();deadline=tick+seconds;lookup=tables(model_without());rng=np.random.default_rng(seed)
    pages=[p for p in load("transcriptions/pages.json") if p["edition"]=="LP2" and p["page"]<=55 and p["runes"]]
    train=[to_indices(p["runes"]) for p in pages if p["page"]%4!=0]
    q=sum(sum(a==b for a,b in zip(v,v[1:])) for v in train)/sum(len(v)-1 for v in train)
    rows=[];null=np.full(replicates,-np.inf)
    for page in pages:
        values=np.array(to_indices(page["runes"]),dtype=np.int16)
        _,top=scan(values[None,:],lookup,deadline,keep=True)
        rows.append({"page":page["id"],"ciphertext_runes":page["runes"],"top_suffix":top})
        for first in range(0,replicates,16):
            last=min(first+16,replicates)
            maxima,_=scan(simulate_pages(len(values),last-first,q,rng),lookup,deadline)
            null[first:last]=np.maximum(null[first:last],maxima)
        print({"page":page["id"],"score":top["score"],"seconds":time.perf_counter()-tick},flush=True)
    observed=max(r["top_suffix"]["score"] for r in rows)
    p=(1+int(np.sum(null>=observed)))/(replicates+1)
    fixture=next(f for f in load("known_solutions/fixtures.json") if f["id"]=="LP1-14_15_circumference")
    plain=to_indices(fixture["plaintext_runes"]);cipher=encrypt_suffix(plain,11,7,17)
    _,control=scan(np.array([cipher],dtype=np.int16),tables(model_without(fixture["id"])),deadline,keep=True)
    exact=control["plaintext_runes"]==fixture["plaintext_runes"]
    return {"experiment":"E015-differential-affine","status":"completed","parameters":{"seconds":seconds,
                "replicates":replicates,"seed":seed,"a":list(range(1,29)),"b":list(range(29)),"null_batch":16,
                "F_interruption":"none","page_reset":True,"memory":"16nullpages x29shifts, processed one multiplier at a time"},
            "motivation":"If P_i=a(C_i-C_(i-1))+b, equal neighboring ciphertext runes correspond to plaintext rune b; a rare b could explain repeat suppression.",
            "evaluated_recipes":55*812,"pages":rows,"observed_global_max":observed,
            "null_calibration":{"q_plugin":q,"global_p_plugin":p,"null_global_maxima":null.tolist(),
                "selection":"Each simulation maximizes over all55pages and812affine maps.",
                "model":"Symmetric stationary Markov with fixed E002training split; uniform marginals; q uncertainty not propagated."},
            "positive_control":{"fixture":fixture["id"],"excluded_from_training":True,"ciphertext_indices":cipher,
                "injected_a":11,"injected_b":7,"injected_initial_cipher":17,"exact_top_one":exact,"result":control},
            "limits":["This is first-order modular difference plus affine substitution only; no arbitrary substitution or higher-order feedback.",
                      "The first source cipher rune serves as IV; no original plaintext rune is claimed for that position.",
                      "Prior E010covered only two difference slopes and no additive shift; this extends that family, not an independent replication.",
                      "Reused corpus and fitted null; exploratory model diagnostic, not exact permutation inference."],
            "numpy":np.__version__,"wall_seconds":time.perf_counter()-tick,"new_decryptions":[]}


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--seconds",type=float,default=180)
    p.add_argument("--replicates",type=int,default=199);p.add_argument("--seed",type=int,default=3301015);args=p.parse_args()
    deps=["experiments/differential_affine.py","experiments/differential_plan.json","experiments/attack_support.py",
          "experiments/ciphertext_autokey_scan.py","experiments/markov_followup.py","src/liberprimus/alphabet.py",
          "src/liberprimus/ciphers.py","src/liberprimus/decoding.py","known_solutions/fixtures.json","transcriptions/pages.json"]
    registered("E015-differential-affine",{**vars(args),"numpy":np.__version__},deps,lambda:run(args.seconds,args.replicates,args.seed))
