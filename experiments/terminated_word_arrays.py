"""Optional vector scoring of the BOS/EOS word model, no altered objective."""
from collections import defaultdict
import math
import numpy as np
from liberprimus.terminated_words import BOS,EOS


class TerminatedArrays:
    def __init__(self,model):
        self.model=model;self.indices={}
        p=np.zeros(31)
        targets=list(range(29))+[EOS]
        p[targets]=[(model.events[()].get(i,0)+model.alpha)/(model.totals[()]+30*model.alpha) for i in targets]
        for length in range(1,4):
            current=np.broadcast_to(p,(31,)+p.shape).copy()
            for context,counts in model.events.items():
                if len(context)!=length:continue
                total=model.totals[context]
                current[context]*=model.strength/(total+model.strength)
                for symbol,count in counts.items():current[context+(symbol,)]+=count/(total+model.strength)
            p=current
        with np.errstate(divide='ignore'):self.table=np.log(p)
        lengths=defaultdict(list)
        for word,count in model.counts.items():
            if len(word)<=12:
                code=0
                for x in word:code=29*code+x
                lengths[len(word)].append((code,count))
        for length,rows in lengths.items():
            rows.sort();self.indices[length]=(np.array([r[0] for r in rows],dtype=np.int64),np.array([r[1] for r in rows],dtype=float))

    def score(self,rows,ends):
        rows=np.asarray(rows)
        if rows.ndim!=2 or not 1<=rows.shape[1]<=1024:raise ValueError('Bounded nonempty rows required')
        if not ends or ends[-1]!=rows.shape[1]:raise ValueError('Final endpoint mismatch')
        groups=defaultdict(list);start=0
        for end in ends:
            if type(end) is not int or not 0<end-start<=32:raise ValueError('Invalid segment length')
            groups[end-start].append(list(range(start,end)));start=end
        total=np.zeros(len(rows))
        for length,positions in groups.items():
            words=rows[:,np.array(positions)].reshape(-1,length)
            padded=np.full((len(words),length+4),BOS,dtype=np.int16)
            padded[:,3:3+length]=words;padded[:,-1]=EOS
            logq=np.zeros(len(words))
            for i in range(length+1):logq+=self.table[tuple(padded[:,i+j] for j in range(4))]
            if length<=12 and length in self.indices:
                code=words@np.array([29**i for i in range(length-1,-1,-1)],dtype=np.int64)
                keys,counts=self.indices[length];where=np.searchsorted(keys,code);safe=np.minimum(where,len(keys)-1)
                observed=np.where((where<len(keys))&(keys[safe]==code),counts[safe],0)
            elif length<=12:observed=np.zeros(len(words))
            else:observed=np.fromiter((self.model.counts.get(tuple(w),0) for w in words),float,count=len(words))
            logcount=np.where(observed>0,np.log(np.maximum(observed,1)),-np.inf)
            scores=np.logaddexp(logcount,math.log(self.model.tau)+logq)-math.log(self.model.word_total+self.model.tau)
            total+=scores.reshape(len(rows),len(positions)).sum(axis=1)
        return total/rows.shape[1]
