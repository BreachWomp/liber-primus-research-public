"""Page-local phases and F schedules after page-bounded pooled initialization."""
import math
import random
import time
import numpy as np
from attack_support import cycle_key, to_runes, top_unique
from reset_key_search import validate
from phase_key_search import optimize, replay
from fragment_initialization_search import phase_fit, unigram_key, check_time
from phase_key_search import coordinate_key
from reset_key_search import factors_at
from liberprimus.alphabet import transliterate


def page_fragments(values, page_spans):
    runs=[]
    for span in page_spans:
        a,b=span['start'],span['end'];begin=a
        for i in range(a,b+1):
            if i==b or values[i]==0:
                if i-begin>=16:runs.append((begin,i))
                begin=i+1
    runs.sort(key=lambda ab:(-(ab[1]-ab[0]),ab[0]))
    ranges=[(a,min(b,a+256)) for a,b in runs[:12]];pool=[];spans=[]
    for j,(a,b) in enumerate(ranges):
        start=len(pool);pool+=values[a:b]
        spans.append({'page_id':f'fragment-{j:02}','start':start,'end':len(pool),'runes':b-a,'zero_rune_page':False})
    return pool,spans,ranges


def search(values, page_spans, model, lookup, deadline, seed=3303052):
    validate(values,page_spans)
    if not 512 <= len(values) <= 4096:
        raise ValueError('Input bound512..4096')
    pool, spans, ranges = page_fragments(values,page_spans)
    if not pool:
        raise ValueError('No eligible fragment')
    families=[]; start_records=[]
    for sign_index, sign in enumerate((1,-1)):
        for period in range(17,33):
            rng=random.Random(seed+1000*sign_index+period); unique={}
            for start in range(16):
                check_time(deadline)
                if start==0: phases=[0]*len(spans)
                elif start==1: phases=[a%period for a,b in ranges]
                elif start==2: phases=[(a-values[:a].count(0)//2)%period for a,b in ranges]
                else: phases=[rng.randrange(period) for _ in spans]
                key=unigram_key(pool,spans,phases,period,sign,lookup)
                state=phase_fit(pool,spans,key,sign,lookup[:1],deadline); steps=0
                for _ in range(20):
                    key=unigram_key(pool,spans,state['page_phases'],len(state['key']),sign,lookup)
                    following=phase_fit(pool,spans,key,sign,lookup[:1],deadline); steps+=1
                    assert following['score']>=state['score']-1e-9
                    same=all(following[k]==state[k] for k in ('key','page_phases'))
                    state=following
                    if same: break
                row=state|{'nominal_period':period,'start':start,'unigram_steps':steps}
                start_records.append(row); ident=cycle_key(state['key'])
                if ident not in unique or row['score']>unique[ident]['score']: unique[ident]=row
            candidates=[]
            for initial in sorted(unique.values(),key=lambda r:r['score'],reverse=True)[:2]:
                state=initial; trace=[]
                for order in (2,4):
                    state=phase_fit(pool,spans,state['key'],sign,lookup[:order],deadline)
                    trace.append(state)
                    for _ in range(3):
                        key,changes=coordinate_key(pool,spans,state['key'],sign,[],state['page_phases'],lookup[:order],deadline)
                        following=phase_fit(pool,spans,key,sign,lookup[:order],deadline)
                        following['coordinate_changes']=changes
                        assert following['score']>=state['score']-1e-9
                        trace.append(following); state=following
                candidates.append({'initial':initial,'pool_trace':trace,'state':state,'nominal_period':period})
            families.append({'nominal_period':period,'sign':sign,'candidates':candidates,
                             'winner':max(range(len(candidates)),key=lambda i:candidates[i]['state']['score'])})
            if period in (24,32): print({'stage':'pool','sign':sign,'through_period':period},flush=True)
    winners=[f['candidates'][f['winner']] for f in families]
    selected=[]
    for period in range(17,33):
        selected.append(max((r for r in winners if r['nominal_period']==period),key=lambda r:r['state']['score']))
    remaining=[r for r in winners if all(r is not s for s in selected)]
    selected+=sorted(remaining,key=lambda r:r['state']['score'],reverse=True)[:4]
    restarts=[]; top=[]
    for i,chosen in enumerate(selected):
        pooled=chosen['state']; state=optimize(values,page_spans,pooled['key'],pooled['sign'],model,deadline); trace=[state]
        for _ in range(3):
            key,changes=coordinate_key(values,page_spans,state['key'],state['sign'],state['skip_positions'],state['page_phases'],lookup,deadline)
            following=optimize(values,page_spans,key,state['sign'],model,deadline); following['coordinate_changes']=changes
            assert following['score']>=state['score']-1e-9
            same=all(following[k]==state[k] for k in ('key','skip_positions','page_phases'))
            trace.append(following); state=following
            if same: break
        plain=replay(values,page_spans,state['key'],state['sign'],state['skip_positions'],state['page_phases'])
        final=state|{'seed_index':i,'plaintext_runes':to_runes(plain),'transliteration':transliterate(plain)}
        restarts.append({'nominal_period':chosen['nominal_period'],'pool_start':chosen['initial']['start'],
                         'pool_state':pooled,'trace':trace,'final':final})
        top=top_unique(top+[final],keep=3)
    return {'top':top,'restarts':restarts,'families':families,'unigram_starts':start_records,
            'pool_ciphertext':pool,'pool_spans':spans,'pool_source_ranges':[list(r) for r in ranges]}
