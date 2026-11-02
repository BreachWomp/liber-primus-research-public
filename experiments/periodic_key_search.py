"""Bounded repeating-key search with exact local factor updates."""
import math
import random
import time
import numpy as np
from attack_support import to_runes,top_unique
from ngram_arrays import array_scores
from liberprimus.periodic_key import primitive,schedule,encrypt
from liberprimus.alphabet import transliterate


def factors_at(rows,positions,lookup):
    rows=np.asarray(rows);positions=np.asarray(positions,dtype=np.int32)
    answer=np.empty((len(rows),len(positions)));order=len(lookup)
    for depth in range(order):
        chosen=np.flatnonzero(np.minimum(positions,order-1)==depth)
        if not len(chosen):continue
        ends=positions[chosen]
        answer[:,chosen]=lookup[depth][tuple(rows[:,ends-depth+j] for j in range(depth+1))]
    return answer


def coordinate(plain,signed,positions,slot,key,lookup,factors):
    rows=np.tile(plain,(29,1))
    rows[:,positions]=(signed[positions][None,:]+np.arange(29)[:,None])%29
    affected=np.unique(np.concatenate([positions+j for j in range(len(lookup))]))
    affected=affected[affected<len(plain)]
    new=factors_at(rows,affected,lookup)
    delta=new.sum(axis=1)-factors[affected].sum();choice=int(delta.argmax())
    if float(delta[choice])<=1e-12:return plain,factors,False
    key[slot]=choice;following=factors.copy();following[affected]=new[choice]
    return rows[choice].copy(),following,True


def search(values,lookup,deadline,seed=3303038,oracle_skips=None,periods=range(1,17)):
    if not 1<=len(values)<=1024:raise ValueError('Bounded nonempty cipher required')
    policies=[('oracle',list(oracle_skips))] if oracle_skips is not None else [
        ('none',[]),('all_F',[i for i,x in enumerate(values) if x==0])]
    top=[];families=[];coordinates=0
    cipher=np.array(values,dtype=np.int32)
    for si,sign in enumerate((1,-1)):
        signed=sign*cipher
        for pi,(policy,skips) in enumerate(policies):
            for length in periods:
                slots=np.array(schedule(values,length,skips))
                columns=[np.flatnonzero(slots==j) for j in range(length)]
                if any(not len(col) for col in columns):continue
                base=[]
                for col in columns:
                    scores=lookup[0][(signed[col][None,:]+np.arange(29)[:,None])%29].sum(axis=1)
                    base.append(int(scores.argmax()))
                rng=random.Random(seed+1000*si+100*pi+length);perturbed=base[:]
                for j in rng.sample(range(length),(length+1)//2):perturbed[j]=rng.randrange(29)
                starts=[base,perturbed]+[[rng.randrange(29) for _ in range(length)] for _ in range(2)]
                best=None
                for restart,start in enumerate(starts):
                    key=start[:];plain=np.where(slots<0,0,(signed+np.array(key)[np.maximum(slots,0)])%29)
                    accepted=0;sweeps=0
                    for tables in (lookup[:2],lookup):
                        factors=factors_at(plain[None,:],np.arange(len(plain)),tables)[0]
                        for _ in range(12):
                            if time.perf_counter()>deadline:raise TimeoutError('Repeating-key search deadline')
                            changed=False;sweeps+=1
                            for slot,col in enumerate(columns):
                                plain,factors,moved=coordinate(plain,signed,col,slot,key,tables,factors)
                                coordinates+=1;accepted+=moved;changed|=moved
                            if not changed:break
                    actual=primitive(key);language=float(array_scores(plain[None,:],lookup)[0])
                    score=language-len(actual)*math.log(29)/len(values)
                    row={'score':score,'language_score':language,'nominal_period':length,'key':actual,
                         'sign':sign,'policy':policy,'restart':restart,'sweeps':sweeps,'accepted_coordinates':accepted}
                    if best is None or score>best['score']:best=row
                families.append(best)
                key=best['key'];active=np.array(schedule(values,len(key),skips))
                plain=np.where(active<0,0,(signed+np.array(key)[np.maximum(active,0)])%29).tolist()
                assert encrypt(plain,key,sign,skips)==list(values)
                top=top_unique(top+[best|{'skip_positions':skips,'plaintext_runes':to_runes(plain),
                                        'transliteration':transliterate(plain)}],keep=3)
    return {'top':top,'families':families,'coordinate_evaluations':coordinates,
            'neighbor_evaluations':29*coordinates,'starts_per_family':4}
