"""Externally trained word probability conditioned on observed segment length."""
from collections import Counter
from functools import lru_cache
import math
import time
from .alphabet import validate_indices
from .boundaries import segments
from .decoding import Decoded

class WordModel:
    def __init__(self,counts,character_model,tau=20):
        if not math.isfinite(tau) or tau<=0:raise ValueError('Positive finite tau required')
        self.counts={tuple(validate_indices(word)):count for word,count in counts.items()}
        if any(not word or type(count) is not int or count<=0 for word,count in self.counts.items()):
            raise ValueError('Positive counts of nonempty words required')
        self.totals=Counter()
        for word,count in self.counts.items():self.totals[len(word)]+=count
        self.character_model=character_model;self.tau=tau
        self.logword=lru_cache(maxsize=100000)(self._logword)

    def _logword(self,word):
        if not word:raise ValueError('Empty segment')
        logq=len(word)*self.character_model.score(word)
        observed=self.counts.get(word,0)
        # Stable log(count + tau*Q), without underflow for long unseen words.
        backoff=math.log(self.tau)+logq
        numerator=backoff if not observed else max(math.log(observed),backoff)+math.log1p(math.exp(-abs(math.log(observed)-backoff)))
        return numerator-math.log(self.totals[len(word)]+self.tau)

    def score(self,values,ends):
        values=validate_indices(values)
        if not values:raise ValueError('Empty sequence')
        return sum(self.logword(tuple(word)) for word in segments(values,ends))/len(values)

def word_selective_decode(values,ends,key,model,*,repeating=True,starts=(0,),
                          cipher_sign=1,key_sign=-1,deadline=None,max_states=200000):
    values=validate_indices(values);segments(values,ends);key=list(key);starts=list(starts)
    if not values or not key or not starts:raise ValueError('Nonempty cipher, key, starts required')
    if any(type(x) is not int for x in key) or any(type(s) is not int or s<0 for s in starts):raise ValueError('Invalid key/cursor')
    if cipher_sign not in (-1,1) or key_sign not in (-1,1):raise ValueError('Invalid signs')
    if not repeating and max(starts)+len(values)>len(key):raise ValueError('Insufficient key stream')
    starts=sorted(set(s%len(key) if repeating else s for s in starts))
    # Word scores have no cross-segment context, so cursor is sufficient between words.
    states={s:(0.0,b'',(),s) for s in starts};transitions=0;maximum=len(states);begin=0
    for end in ends:
        active={(cursor,b''):row for cursor,row in states.items()}
        for i in range(begin,end):
            if deadline is not None and time.perf_counter()>deadline:raise TimeoutError('Word DP deadline')
            following={}
            for (cursor,word),(score,path,skips,start) in active.items():
                p=(cipher_sign*values[i]+key_sign*key[cursor])%29
                nxt=(cursor+1)%len(key) if repeating else cursor+1
                options=[(p,nxt,skips)]
                if values[i]==0:options.append((0,cursor,skips+(i,)))
                for symbol,newcursor,newskips in options:
                    transitions+=1;index=(newcursor,word+bytes([symbol]));previous=following.get(index)
                    if previous is None or score>previous[0]:following[index]=(score,path+bytes([symbol]),newskips,start)
            active=following;maximum=max(maximum,len(active))
            if len(active)>max_states:raise MemoryError('Exact DP state bound exceeded; no pruning allowed')
        states={}
        for (cursor,word),(score,path,skips,start) in active.items():
            score+=model.logword(tuple(word));previous=states.get(cursor)
            if previous is None or score>previous[0]:states[cursor]=(score,path,skips,start)
        begin=end
    best=max(states.values(),key=lambda row:row[0])
    return Decoded(best[0]/len(values),list(best[1]),list(best[2]),best[3],transitions,maximum)
