"""Word-token model with explicit beginning/end events; standard library only."""
from collections import Counter,defaultdict
from functools import lru_cache
import math
from .alphabet import validate_indices
from .boundaries import segments

BOS=29
EOS=30
TARGETS=tuple(range(29))+(EOS,)


class TerminatedWords:
    def __init__(self,words,alpha=.5,strength=5.,tau=20.):
        if any(not math.isfinite(x) or x<=0 for x in (alpha,strength,tau)):
            raise ValueError('Positive finite smoothing required')
        self.alpha,self.strength,self.tau=alpha,strength,tau
        self.counts=Counter(tuple(validate_indices(w)) for w in words)
        if not self.counts or () in self.counts:raise ValueError('Nonempty words required')
        self.events=defaultdict(Counter)
        for word,count in self.counts.items():
            history=(BOS,)*3
            for symbol in word+(EOS,):
                for k in range(4):self.events[history[-k:] if k else ()][symbol]+=count
                history=(history+(symbol,))[-3:]
        self.totals={h:sum(c.values()) for h,c in self.events.items()}
        self.word_total=sum(self.counts.values())
        self.logp=lru_cache(maxsize=100000)(self._logp)
        self.logword=lru_cache(maxsize=100000)(self._logword)

    def _logp(self,context,symbol):
        if symbol not in TARGETS:raise ValueError('BOS cannot be emitted')
        context=tuple(context[-3:])
        if any(type(x) is not int or not 0<=x<=BOS for x in context):raise ValueError('Invalid context')
        p=(self.events[()].get(symbol,0)+self.alpha)/(self.totals[()]+30*self.alpha)
        for k in range(1,len(context)+1):
            h=context[-k:]
            p=(self.events.get(h,{}).get(symbol,0)+self.strength*p)/(self.totals.get(h,0)+self.strength)
        return math.log(p)

    def logq(self,word):
        word=tuple(validate_indices(word));history=(BOS,)*3;total=0.
        for symbol in word+(EOS,):
            total+=self.logp(history,symbol);history=(history+(symbol,))[-3:]
        return total

    def _logword(self,word):
        if not word:raise ValueError('Empty observed word')
        backoff=math.log(self.tau)+self.logq(word);count=self.counts.get(word,0)
        total=backoff if not count else max(math.log(count),backoff)+math.log1p(math.exp(-abs(math.log(count)-backoff)))
        return total-math.log(self.word_total+self.tau)

    def score(self,values,ends):
        values=validate_indices(values)
        if not values:raise ValueError('Empty sequence')
        return sum(self.logword(tuple(w)) for w in segments(values,ends))/len(values)
