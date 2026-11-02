"""Bounded general-feedback screening and exact no-skip trigram factors."""
import time
import numpy as np
from liberprimus.general_feedback import affine_chain


def screen(values, unigram, deadline):
    result=[]
    for m in range(4,33):
        rows=[]
        for a in (1,-1):
            for b in range(1,29):
                if time.perf_counter()>deadline:raise TimeoutError('Family screening deadline')
                base,coeff=affine_chain(values,m,a,b)
                variants=(np.arange(29)[:,None]*np.array(coeff)+np.array(base))%29
                score=float(sum(unigram[variants[:,r::m]].sum(axis=1).max() for r in range(m)))
                rows.append({'period':m,'cipher_sign':a,'feedback_sign':b,'unigram_max_total':score})
        for rank,row in enumerate(sorted(rows,key=lambda r:r['unigram_max_total'],reverse=True),1):
            result.append(row|{'rank':rank})
    return result


def factor_tables(values,period,cs,ks,lookup):
    base,coeff=map(np.array,affine_chain(values,period,cs,ks))
    grids=[np.arange(29).reshape((29,1,1)),np.arange(29).reshape((1,29,1)),np.arange(29).reshape((1,1,29))]
    factors=np.zeros((period,29,29,29))
    for end in range(len(values)):
        start=max(0,end-2)
        symbols=[(coeff[j]*grids[j-start]+base[j])%29 for j in range(start,end+1)]
        factors[start%period]+=lookup[end-start][tuple(symbols)]
    return factors,0.0,list(range(len(values))),base,coeff
