"""Source-anchored multi-page number streams, with arbitrary F interruptions."""
import argparse
import time
import numpy as np
from attack_support import ROOT,load,to_indices,to_runes,model_without,stream_catalog,candidate,top_unique
from liberprimus.decoding import selective_decode,replay
from liberprimus.ciphers import keystream
from markov_followup import simulate_pages
from registry import registered

SIGNS=((1,-1),(1,1),(-1,-1),(-1,1))


def assemble(section):
    pages={p["id"]:p for p in load("transcriptions/pages.json")}
    values=[];spans=[]
    for ident in section["page_ids"]:
        p=pages[ident];start=len(values);values+=to_indices(p["runes"])
        spans.append({"page":ident,"start":start,"end":len(values),"non_rune":not bool(p["runes"]),
                      "layout":p["text_with_layout"]})
    return values,spans


def search(values,model,deadline,keep=3):
    streams=stream_catalog(len(values)+256);top=[];best=-float("inf");transitions=0
    for family,key in streams.items():
        for cs,ks in SIGNS:
            result=selective_decode(values,key,model,repeating=False,starts=range(256),cipher_sign=cs,key_sign=ks,deadline=deadline)
            best=max(best,result.score);transitions+=result.transitions
            if keep:
                row=candidate(result,values,key,{"family":family,"cipher_sign":cs,"key_sign":ks},False)
                top=top_unique(top+[row],keep=keep)
    return best,top,transitions


def control(seconds):
    tick=time.perf_counter();fixture=next(f for f in load("known_solutions/fixtures.json") if f["id"]=="LP1-14_15_circumference")
    plain=to_indices(fixture["plaintext_runes"]);key=stream_catalog(len(plain)+256)["prime_totient"]
    skips=[i for i,v in enumerate(plain) if v==0][::2];start=17
    cipher=keystream(plain,key[start:],decrypt=False,skip_positions=skips)
    expected=replay(cipher,key,repeating=False,start=start,skip_positions=skips)
    assert expected==plain
    cuts=[0,len(plain)//3,2*len(plain)//3,len(plain)]
    parts=[cipher[a:b] for a,b in zip(cuts,cuts[1:])]
    rebuilt=[];cursor=start
    for a,b in zip(cuts,cuts[1:]):
        local_skips=[i-a for i in skips if a<=i<b]
        rebuilt+=replay(cipher[a:b],key,repeating=False,start=cursor,skip_positions=local_skips)
        cursor+=(b-a)-len(local_skips)
    assert rebuilt==plain
    _,top,_=search(cipher,model_without(fixture["id"]),tick+seconds)
    exact=top[0]["plaintext_runes"]==fixture["plaintext_runes"]
    return {"experiment":"E012-section-control","status":"completed","fixture":fixture["id"],
            "ciphertext_indices":cipher,"page_cuts":cuts,"known_recipe":{"family":"prime_totient","start":start,"skip_positions":skips},
            "exact_independent_page_continuation":rebuilt==plain,"training_excludes_fixture":True,
            "exact_top_one":exact,"character_accuracy":sum(a==b for a,b in zip(to_indices(top[0]["plaintext_runes"]),plain))/len(plain),
            "top":top,"wall_seconds":time.perf_counter()-tick,"new_decryptions":[]}


def attack(ident,seconds,replicates,seed):
    tick=time.perf_counter();deadline=tick+seconds
    plan=load("experiments/section_plan.json");section=next(s for s in plan["sections"] if s["id"]==ident)
    values,spans=assemble(section);model=model_without()
    best,top,transitions=search(values,model,deadline)
    for row in top:
        plain=to_indices(row["plaintext_runes"])
        row["page_outputs"]=[{"page":span["page"],"plaintext_runes":to_runes(plain[span["start"]:span["end"]]),
                              "rune_count":span["end"]-span["start"]} for span in spans]
    result={"experiment":"E012-section-streams","status":"completed","section":section,
            "ciphertext_runes":to_runes(values),"page_spans":spans,"top":top,"dp_transitions":transitions,
            "parameters":{"offsets":[0,255],"signs":SIGNS,"number_families":["prime_totient","prime","integer_totient"],
                          "F_masks":"all subsets, exact DP","language_context":"continuous across page boundaries",
                          "non_rune_page_consumption":0,"seconds":seconds,"replicates":replicates,"seed":seed},
            "limits":["Source partitions are community hypotheses, not authenticated cipher boundaries.",
                      "Numeric page retained but modeled as consuming no key; no statement about its actual cipher role.",
                      "Sparse language scorer cannot certify decryption; preserve complete outputs."],"new_decryptions":[]}
    if replicates:
        pages=[p for p in load("transcriptions/pages.json") if p["edition"]=="LP2" and p["page"]<=55 and p["runes"] and p["page"]%4!=0]
        arrays=[to_indices(p["runes"]) for p in pages]
        q=sum(sum(a==b for a,b in zip(v,v[1:])) for v in arrays)/sum(len(v)-1 for v in arrays)
        rng=np.random.default_rng(seed);null=[]
        for i in range(replicates):
            # Original page boundaries start independent chains; concatenate only after simulation.
            sample=[]
            for span in spans:
                sample+=simulate_pages(span["end"]-span["start"],1,q,rng)[0].tolist()
            score,_,_=search(sample,model,deadline,keep=0);null.append(score)
            if (i+1)%5==0:print({"null_replicates":i+1,"seconds":time.perf_counter()-tick},flush=True)
        p=(1+sum(v>=best for v in null))/(replicates+1)
        result["null_calibration"]={"q_plugin":q,"null_maxima":null,"monte_carlo_p_plugin":p,
            "bonferroni_10_sections":min(1,10*p),"selection":"Full offset/sign/F search in each replicate; ten-section Bonferroni after maximum-score section selection.",
            "limits":"Plug-in symmetric Markov null does not fix marginal counts; q uncertainty not propagated; exploratory reused data."}
    result["wall_seconds"]=time.perf_counter()-tick
    return result


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--section",required=True)
    p.add_argument("--seconds",type=float,default=180);p.add_argument("--replicates",type=int,default=0)
    p.add_argument("--seed",type=int,default=3301012);args=p.parse_args()
    deps=["experiments/section_stream_attack.py","experiments/section_plan.json","experiments/attack_support.py",
          "experiments/markov_followup.py","src/liberprimus/decoding.py","src/liberprimus/alphabet.py","src/liberprimus/ciphers.py",
          "transcriptions/pages.json","known_solutions/fixtures.json","sources/manifest.json",
          "data/raw/iddqd/liber-primus__index/liber-primus__index.txt"]
    if args.section=="control":
        registered("E012-section-control",vars(args),deps,lambda:control(args.seconds))
    else:
        registered("E012-"+("null-" if args.replicates else "section-")+args.section,vars(args),deps,
                   lambda:attack(args.section,args.seconds,args.replicates,args.seed))
