"""Bounded cyclic-factor beam search for arbitrary plaintext-autokey seeds."""
import time
import numpy as np
from short_seed_autokey import affine_chain
from plaintext_autokey_attack import invert
from attack_support import to_runes,top_unique
from liberprimus.alphabet import transliterate
from ngram_arrays import array_scores

SIGNS=((1,-1),(1,1),(-1,-1),(-1,1))


def factor_tables(values,period,cs,ks,skip_all_f,lookup):
    """Sum all trigram terms into ring factors over three adjacent seed residues."""
    active=[i for i,v in enumerate(values) if not skip_all_f or v!=0]
    cipher=[values[i] for i in active]
    if len(cipher)<period:raise ValueError("not enough active runes")
    base,coefficient=affine_chain(cipher,period,cs,ks)
    ordinal={pos:j for j,pos in enumerate(active)}
    grids=[np.arange(29).reshape((29,1,1)),np.arange(29).reshape((1,29,1)),np.arange(29).reshape((1,1,29))]
    factors=np.zeros((period,29,29,29));constant=0.0
    for i in range(len(values)):
        positions=list(range(max(0,i-2),i+1))
        ordinals=[ordinal[pos] for pos in positions if pos in ordinal]
        if not ordinals:
            constant+=float(lookup[len(positions)-1][(0,)*len(positions)]);continue
        first=ordinals[0];symbols=[]
        for pos in positions:
            if pos not in ordinal:symbols.append(0)
            else:
                j=ordinal[pos]
                symbols.append((coefficient[j]*grids[j-first]+base[j])%29)
        factors[first%period]+=lookup[len(positions)-1][tuple(symbols)]
    return factors,constant,active,base,coefficient


def cycle_beam(factors,width=512,keep=16):
    """Search every cyclic cut; this finite beam is heuristic, not exhaustive."""
    period,alphabet=factors.shape[:2];found={}
    initial=np.array([(a,b) for a in range(alphabet) for b in range(alphabet)],dtype=np.int16)
    for cut in range(period):
        paths=initial.copy();score=np.zeros(len(paths))
        for j in range(2,period):
            candidate=score[:,None]+factors[(cut+j-2)%period,paths[:,-2],paths[:,-1],:]
            flat=candidate.ravel();take=np.argsort(flat,kind="stable")[-min(width,len(flat)):]
            parents,symbols=np.divmod(take,alphabet)
            paths=np.column_stack((paths[parents],symbols));score=flat[take]
        score+=factors[(cut+period-2)%period,paths[:,-2],paths[:,-1],paths[:,0]]
        score+=factors[(cut+period-1)%period,paths[:,-1],paths[:,0],paths[:,1]]
        for idx in np.argsort(score,kind="stable")[-keep:]:
            unrotated=np.roll(paths[idx],cut)
            found[tuple(unrotated.tolist())]=float(score[idx])
    return sorted(found.items(),key=lambda item:item[1],reverse=True)


def search(values,lookup3,lookup4,deadline,periods=range(4,13),width=512,keep_per_cut=16):
    top=[];tasks=0;generated=0
    for period in periods:
        for skip in (False,True):
            for cs,ks in SIGNS:
                if time.perf_counter()>deadline:raise TimeoutError("autokey beam deadline")
                factors,constant,active,base,coeff=factor_tables(values,period,cs,ks,skip,lookup3)
                candidates=cycle_beam(factors,width,keep_per_cut)
                prefixes=np.array([key for key,score in candidates],dtype=np.int16)
                output=np.zeros((len(prefixes),len(values)),dtype=np.int16)
                output[:,active]=(prefixes[:,np.arange(len(active))%period]*coeff+base)%29
                scores3=array_scores(output,lookup3)
                expected=np.array([(s+constant)/len(values) for _,s in candidates])
                if not np.allclose(scores3,expected,rtol=0,atol=1e-10):raise AssertionError("factor score mismatch")
                scores4=array_scores(output,lookup4);generated+=len(candidates);tasks+=1
                for idx in np.argsort(scores4)[-3:]:
                    plain=output[idx].tolist()
                    key=[(ks*(int(prefixes[idx,j])-cs*values[active[j]]))%29 for j in range(period)]
                    skips=[i for i,v in enumerate(values) if skip and v==0]
                    if invert(plain,key,cs,ks,skips)!=values:raise AssertionError("candidate reencryption failed")
                    record={"score":float(scores4[idx]),"trigram_score":float(scores3[idx]),
                            "plaintext_runes":to_runes(plain),"transliteration":transliterate(plain),
                            "recipe":{"key_indices":key,"cipher_sign":cs,"feedback_sign":ks,
                                      "skip_positions":skips,"skip_policy":"all_F" if skip else "none"},
                            "reencryption_verified":True}
                    top=top_unique(top+[record])
    return top,{"period_sign_policy_tasks":tasks,"generated_candidates":generated,"beam_width":width,
                "keep_per_cut":keep_per_cut,"cyclic_cuts":"all period positions","periods":list(periods)}
