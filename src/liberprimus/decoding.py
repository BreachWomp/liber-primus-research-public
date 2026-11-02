"""Exact finite-context decoding over selective F interruptions.

Merging paths is safe only when key cursor and language context match. This
optimizes a declared score; it does not prove the resulting text is correct.
"""
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import lru_cache
import math
import time
from .alphabet import validate_indices


class BackoffModel:
    """Normalized conditional model with hierarchical Dirichlet smoothing."""
    def __init__(self, sequences, order=3, alpha=0.5, strength=5.0):
        if type(order) is not int or not 1 <= order <= 4:
            raise ValueError("order must be 1..4")
        if not math.isfinite(alpha) or not math.isfinite(strength) or alpha<=0 or strength<=0:
            raise ValueError("smoothing must be finite and positive")
        self.order,self.alpha,self.strength=order,alpha,strength
        self.counts=defaultdict(Counter)
        for sequence in sequences:
            data=validate_indices(sequence)
            for i,symbol in enumerate(data):
                for length in range(min(i,order-1)+1):
                    context=tuple(data[i-length:i]) if length else ()
                    self.counts[context][symbol]+=1
        self.totals={context:sum(counts.values()) for context,counts in self.counts.items()}
        if not self.totals.get((),0):raise ValueError("empty training corpus")
        self.logp=lru_cache(maxsize=100000)(self._logp)

    def _logp(self, context, symbol):
        if symbol not in range(29):raise ValueError("invalid symbol")
        context=tuple(context[-(self.order-1):]) if self.order>1 else ()
        p=(self.counts[()].get(symbol,0)+self.alpha)/(self.totals[()]+29*self.alpha)
        for length in range(1,len(context)+1):
            suffix=context[-length:]
            count=self.counts.get(suffix,{})
            p=(count.get(symbol,0)+self.strength*p)/(self.totals.get(suffix,0)+self.strength)
        return math.log(p)

    def score(self, values):
        data=validate_indices(values)
        if not data:raise ValueError("empty sequence")
        return sum(self.logp(tuple(data[max(0,i-self.order+1):i]),symbol) for i,symbol in enumerate(data))/len(data)


@dataclass
class Decoded:
    score: float
    plaintext: list[int]
    skip_positions: list[int]
    start: int
    transitions: int
    max_states: int


def selective_decode(values, key, model, *, repeating=True, starts=(0,),
                     cipher_sign=1, key_sign=-1, deadline=None):
    """Global score optimum over all F-skip subsets and declared start cursors.

    key is finite even for streams; stream exhaustion raises. Skips copy F
    unchanged and consume no key item. No skip penalty or arbitrary beam prune.
    """
    values,key=validate_indices(values),list(key)
    if not values or not key:raise ValueError("nonempty ciphertext and key required")
    if any(type(x) is not int for x in key):raise ValueError("key values must be integers")
    if cipher_sign not in (-1,1) or key_sign not in (-1,1):raise ValueError("sign must be +/-1")
    starts=list(starts)
    if not starts or any(type(x) is not int or x<0 for x in starts):raise ValueError("invalid starts")
    if not repeating and max(starts)+len(values)>len(key):raise ValueError("stream too short")
    starts=sorted(set(s%len(key) if repeating else s for s in starts))
    # (cursor, context) -> (sum score, output bytes, skip tuple, initial cursor)
    states={(s,()):(0.0,b"",(),s) for s in starts}
    transitions=0;maximum=len(states)
    for i,cipher in enumerate(values):
        if deadline is not None and time.perf_counter()>deadline:raise TimeoutError("decoding deadline")
        following={}
        for (cursor,history),(score,path,skips,start) in states.items():
            plain=(cipher_sign*cipher+key_sign*key[cursor])%29
            nxt=(cursor+1)%len(key) if repeating else cursor+1
            options=[(plain,nxt,skips)]
            if cipher==0:options.append((0,cursor,skips+(i,)))
            for symbol,new_cursor,new_skips in options:
                transitions+=1
                new_history=(history+(symbol,))[-(model.order-1):] if model.order>1 else ()
                index=(new_cursor,new_history)
                candidate=score+model.logp(history,symbol)
                previous=following.get(index)
                if previous is None or candidate>previous[0]:
                    following[index]=(candidate,path+bytes([symbol]),new_skips,start)
        states=following
        maximum=max(maximum,len(states))
    best=max(states.values(),key=lambda value:value[0])
    return Decoded(best[0]/len(values),list(best[1]),list(best[2]),best[3],transitions,maximum)


def replay(values,key,*,repeating=True,start=0,skip_positions=(),cipher_sign=1,key_sign=-1):
    """Independent simple forward replay of a saved recipe."""
    output=[];cursor=start;skips=set(skip_positions)
    for position,value in enumerate(values):
        if position in skips:
            if value!=0:raise ValueError("only ciphertext F can interrupt this family")
            output.append(0)
        else:
            output.append((cipher_sign*value+key_sign*key[cursor])%29)
            cursor=cursor+1
            if repeating:cursor%=len(key)
    return output
