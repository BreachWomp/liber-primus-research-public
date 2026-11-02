"""Optional NumPy acceleration of the standard-library backoff language model."""
import numpy as np


def dense_tables(model):
    probabilities=[]
    unigram=np.array([model.counts[()].get(i,0) for i in range(29)],dtype=float)
    unigram=(unigram+model.alpha)/(unigram.sum()+29*model.alpha)
    probabilities.append(unigram)
    for length in range(1,model.order):
        current=np.broadcast_to(probabilities[-1],(29,)+probabilities[-1].shape).copy()
        for context,count in model.counts.items():
            if len(context)!=length:continue
            total=model.totals[context]
            current[context]*=model.strength/(total+model.strength)
            for symbol,n in count.items():current[context+(symbol,)]+=n/(total+model.strength)
        probabilities.append(current)
    return [np.log(p) for p in probabilities]


def array_scores(rows,lookup):
    n=rows.shape[1];order=len(lookup)
    if not n:raise ValueError("empty rows")
    total=np.zeros(len(rows))
    for i in range(min(order-1,n)):
        total+=lookup[i][tuple(rows[:,j] for j in range(i+1))]
    if n>=order:
        total+=lookup[-1][tuple(rows[:,j:n-order+j+1] for j in range(order))].sum(axis=1)
    return total/n
