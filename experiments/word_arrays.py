"""NumPy evaluation of the existing scalar WordModel, without score changes."""
from collections import Counter,defaultdict
import math
import numpy as np
from ngram_arrays import dense_tables,array_scores


class WordArrays:
    def __init__(self,model):
        self.counts=model.counts;self.totals=model.totals;self.tau=model.tau
        self.lookup=dense_tables(model.character_model);self.indices={}
        lengths=defaultdict(list)
        for word,count in self.counts.items():
            if len(word)<=12:
                code=0
                for symbol in word:code=29*code+symbol
                lengths[len(word)].append((code,count))
        for length,rows in lengths.items():
            rows.sort();self.indices[length]=(np.array([r[0] for r in rows],dtype=np.int64),
                                              np.array([r[1] for r in rows],dtype=float))

    def score(self,rows,ends):
        rows=np.asarray(rows)
        if rows.ndim!=2 or not 1<=rows.shape[1]<=1024:raise ValueError('Nonempty bounded row matrix required')
        if not ends or ends[-1]!=rows.shape[1]:raise ValueError('Final endpoint must match length')
        groups=defaultdict(list);begin=0
        for end in ends:
            if type(end) is not int or not 0<end-begin<=32:raise ValueError('Invalid segment length')
            groups[end-begin].append(list(range(begin,end)));begin=end
        total=np.zeros(len(rows))
        for length,positions in groups.items():
            words=rows[:,np.asarray(positions)].reshape(-1,length)
            logq=length*array_scores(words,self.lookup)
            if length<=12 and length in self.indices:
                codes=words@np.array([29**i for i in range(length-1,-1,-1)],dtype=np.int64)
                keys,counts=self.indices[length];where=np.searchsorted(keys,codes)
                safe=np.minimum(where,len(keys)-1)
                observed=np.where((where<len(keys))&(keys[safe]==codes),counts[safe],0)
            elif length<=12:observed=np.zeros(len(words))
            else:observed=np.fromiter((self.counts.get(tuple(w),0) for w in words),float,count=len(words))
            logcount=np.where(observed>0,np.log(np.maximum(observed,1)),-np.inf)
            scores=np.logaddexp(logcount,math.log(self.tau)+logq)-math.log(self.totals[length]+self.tau)
            total+=scores.reshape(len(rows),len(positions)).sum(axis=1)
        return total/rows.shape[1]
