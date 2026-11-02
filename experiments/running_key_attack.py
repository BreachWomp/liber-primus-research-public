"""Running-key scan of one pinned literary text with explicit rune conventions."""
import argparse
import hashlib
import json
import re
import random
import time
import numpy as np

from attack_support import ROOT,load,digest,model_without,to_indices,to_runes,top_unique
from liberprimus.alphabet import latin_to_indices,transliterate
from ciphertext_autokey_scan import tables,scores
from conditional_attack_null import conditional_shuffle
from registry import registered

SIGNS=((1,-1),(1,1),(-1,-1),(-1,1))


def source_keys():
    raw=(ROOT/"data/raw/gutenberg/pg2944.txt").read_bytes()
    if hashlib.sha256(raw).hexdigest()!=load("sources/emerson_manifest.json")["sha256"]:
        raise ValueError("key source checksum mismatch")
    text=raw.decode("utf-8-sig")
    first=re.search(r"(?m)^II\.\r?\nSELF-RELIANCE\r?$",text)
    last=re.search(r"(?m)^III\.\r?\nCOMPENSATION\r?$",text)
    if not first or not last or first.end()>=last.start():raise ValueError("chapter markers changed")
    section=text[first.end():last.start()]
    words=re.findall(r"[A-Za-z]+",section)
    streams={}
    for convention in ("Q_to_C","QU_to_CW_Q_to_C"):
        values=[]
        for word in words:
            word=word.upper()
            if convention=="QU_to_CW_Q_to_C":word=word.replace("QU","CW")
            values+=latin_to_indices(word.replace("Q","C"))
        streams[convention]=values
    return streams,{"source_sha256":hashlib.sha256(raw).hexdigest(),"decoded_character_range":[first.end(),last.start()],
                    "section":"Self-Reliance, after chapter heading and before III.Compensation; includes epigraph and repeated essay title",
                    "tokenization":"ASCII letter words only; punctuation/numbers omitted; greedy GP encoding within each word, never across words",
                    "non_ascii_letters":sorted(set(c for c in section if c.isalpha() and not c.isascii())),
                    "stream_hashes":{k:hashlib.sha256(bytes(v)).hexdigest() for k,v in streams.items()},
                    "stream_lengths":{k:len(v) for k,v in streams.items()}}


def scan(values,streams,lookup,deadline,keep=3,batch=512):
    top=[];best=-float("inf");tasks=0;n=len(values)
    for label,key in streams.items():
        key=np.array(key,dtype=np.int16)
        for skip in (False,True):
            active=np.array([i for i,v in enumerate(values) if not skip or v!=0],dtype=np.int64)
            if len(active)==0:raise ValueError("all-F data not supported by this experiment")
            if len(key)<len(active):raise ValueError("running key shorter than page")
            windows=np.lib.stride_tricks.sliding_window_view(key,len(active))
            cipher=np.array(values,dtype=np.int16)[active]
            for cs,ks in SIGNS:
                for first in range(0,len(windows),batch):
                    if time.perf_counter()>deadline:raise TimeoutError("running-key deadline")
                    block=windows[first:first+batch]
                    plain=np.zeros((len(block),n),dtype=np.int16)
                    plain[:,active]=(cs*cipher[None,:]+ks*block)%29
                    score=scores(plain,lookup);tasks+=len(block);best=max(best,float(score.max()))
                    if keep:
                        for i in np.argsort(score)[-keep:][::-1]:
                            if len(top)==keep and float(score[i])<=top[-1]["score"]:continue
                            output=plain[i].tolist();offset=first+int(i)
                            # Scalar re-encryption, independent of array broadcasting.
                            actual=list(values);cursor=offset
                            for pos in active:
                                actual[int(pos)]=(cs*(output[int(pos)]-ks*int(key[cursor])))%29;cursor+=1
                            assert actual==values
                            row={"score":float(score[i]),"plaintext_runes":to_runes(output),"transliteration":transliterate(output),
                                 "recipe":{"key_stream":label,"start":offset,"cipher_sign":cs,"key_sign":ks,
                                           "skip_policy":"all_F" if skip else "none","skip_positions":[j for j,v in enumerate(values) if skip and v==0]},
                                 "reencryption_verified":True}
                            top=top_unique(top+[row],keep=keep)
    return best,top,tasks


def run(seconds=180,replicates=39,seed=3301013):
    tick=time.perf_counter();deadline=tick+seconds;streams,provenance=source_keys();lookup=tables(model_without())
    pages=[p for p in load("transcriptions/pages.json") if p["edition"]=="LP2" and p["page"]<=55 and p["runes"]]
    rows=[];tasks=0
    for page in pages:
        values=to_indices(page["runes"]);best,top,count=scan(values,streams,lookup,deadline)
        rows.append({"page":page["id"],"ciphertext_runes":page["runes"],"top":top,"recipes":count});tasks+=count
        print(json.dumps({"page":page["id"],"score":best,"seconds":time.perf_counter()-tick}),flush=True)
    chosen=max(rows,key=lambda r:r["top"][0]["score"]);values=to_indices(chosen["ciphertext_runes"])
    rng=random.Random(seed);null=[]
    for i in range(replicates):
        sample,proposals=conditional_shuffle(values,rng,deadline=deadline)
        score,_,_=scan(sample,streams,lookup,deadline,keep=0)
        null.append({"score":score,"ciphertext_indices":sample,"proposals":proposals})
        if (i+1)%10==0:print(json.dumps({"null_replicates":i+1,"seconds":time.perf_counter()-tick}),flush=True)
    p=(1+sum(r["score"]>=chosen["top"][0]["score"] for r in null))/(replicates+1)
    fixture=next(f for f in load("known_solutions/fixtures.json") if f["id"]=="LP1-14_15_circumference")
    plain=to_indices(fixture["plaintext_runes"]);start=123;key=streams["QU_to_CW_Q_to_C"]
    cipher=[(v+key[start+i])%29 for i,v in enumerate(plain)]
    _,control,_=scan(cipher,streams,tables(model_without(fixture["id"])),deadline)
    exact=control[0]["plaintext_runes"]==fixture["plaintext_runes"]
    return {"experiment":"E013-emerson-running-key","status":"completed","parameters":{"seconds":seconds,
                "replicates":replicates,"seed":seed,"batch":512,"signs":SIGNS,"skip_policies":["none","all_F"],
                "offsets":"all starts for which the full active page fits within the chapter","source_direction":"forward only"},
            "source":provenance,"evaluated_recipes":tasks,"pages":rows,
            "null_calibration":{"page":chosen["page"],"monte_carlo_p":p,"bonferroni_55_pages":min(1,55*p),"runs":null,
                                "model":"Exact rune counts and stream doublets, independent rejection shuffles; full key/offset/sign/skip scan in each draw."},
            "positive_control":{"fixture":fixture["id"],"excluded_from_training":True,"ciphertext_indices":cipher,
                                "injected_start":123,"injected_key_stream":"QU_to_CW_Q_to_C","exact_top_one":exact,"top":control},
            "limits":["One selected essay and digital edition, two explicit encoding conventions; no other text, backward key or arbitrary F mask is tested.",
                      "The essay is a speculative thematic candidate; no source claims it is an established Cicada key.",
                      "Non-ASCII Latin letters are excluded from ASCII-word tokenization and explicitly inventoried in source metadata.",
                      "39 null draws cannot establish significance after55page correction; scores alone never certify decryption."],
            "numpy":np.__version__,"wall_seconds":time.perf_counter()-tick,"new_decryptions":[]}


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--seconds",type=float,default=180)
    p.add_argument("--replicates",type=int,default=39);p.add_argument("--seed",type=int,default=3301013);args=p.parse_args()
    deps=["experiments/running_key_attack.py","experiments/running_key_plan.json","experiments/attack_support.py",
          "experiments/ciphertext_autokey_scan.py","experiments/conditional_attack_null.py","experiments/markov_followup.py",
          "src/liberprimus/alphabet.py","src/liberprimus/ciphers.py","src/liberprimus/decoding.py","transcriptions/pages.json",
          "known_solutions/fixtures.json","sources/emerson_manifest.json","data/raw/gutenberg/pg2944.txt"]
    registered("E013-running-key",{**vars(args),"numpy":np.__version__},deps,lambda:run(args.seconds,args.replicates,args.seed))
