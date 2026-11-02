"""All unit multipliers with exact histogram evaluation of unigram screening."""
import time
import numpy as np
from liberprimus.bilinear_feedback import affine_chain


def period_scores(values,m,unigram,deadline):
    # H[r,t,x] counts base1_i+t*coefficient_i=x in residue r.
    # Multiplying the full plaintext by a permutes prefix t bijectively.
    weights=unigram[(np.arange(1,29)[:,None]*np.arange(29)[None,:])%29].T
    offset=(np.arange(len(values))%m)[None,:]*841+np.arange(29)[:,None]*29
    scores=np.empty((28,28))
    for b in range(1,29):
        if time.perf_counter()>deadline:raise TimeoutError('Bilinear screening deadline')
        base,coeff=map(np.array,affine_chain(values,m,1,b))
        symbols=(base[None,:]+np.arange(29)[:,None]*coeff[None,:])%29
        hist=np.bincount((offset+symbols).ravel(),minlength=m*841).reshape(m,29,29)
        scores[:,b-1]=(hist@weights).max(axis=1).sum(axis=0)
    return scores


def screen(values,unigram,deadline):
    result=[]
    for m in range(4,33):
        scores=period_scores(values,m,unigram,deadline)
        rows=[{'period':m,'cipher_sign':a,'feedback_sign':b,'unigram_max_total':float(scores[a-1,b-1]),
            'selection_score':round(float(scores[a-1,b-1]),9)} for a in range(1,29) for b in range(1,29)]
        for rank,row in enumerate(sorted(rows,key=lambda r:r['selection_score'],reverse=True),1):
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
