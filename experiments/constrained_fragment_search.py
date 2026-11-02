"""Constrained fragment phases with coupled full-text context."""
import math
import random
import time
import numpy as np
from attack_support import cycle_key, to_runes, top_unique
from reset_key_search import validate
from phase_key_search import replay
from context_phase_search import optimize,coordinate_key as context_coordinates,alternatives
from fragment_initialization_search import unigram_key, check_time
from liberprimus.fragment_constraints import build_chains, maximize, seed_phases
from liberprimus.periodic_key import primitive
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


def search(values, page_spans, model, lookup, deadline, seed=3303058):
    validate(values,page_spans)
    if not 512 <= len(values) <= 4096:
        raise ValueError('Input bound512..4096')
    pool, spans, ranges = page_fragments(values,page_spans)
    if not pool:
        raise ValueError('No eligible fragment')
    chains=build_chains(values,page_spans,ranges)
    def phase_fit(pool, spans, key, sign, tables, deadline):
        key=primitive(list(key));m=len(key);costs=[]
        for span in spans:
            check_time(deadline)
            part=np.asarray(pool[span['start']:span['end']],dtype=np.int32)
            indices=(np.arange(m)[:,None]+np.arange(len(part))[None,:])%m
            plain=(sign*part[None,:]+np.asarray(key)[indices])%29
            costs.append(factors_at(plain,np.arange(len(part)),tables,np.zeros(len(part),dtype=int)).sum(axis=1).tolist())
        total,phases=maximize(costs,chains,deadline);rotation=phases[0]
        return {'key':key[rotation:]+key[:rotation],'sign':sign,'page_phases':[(p-rotation)%m for p in phases],
                'order':len(tables),'language_score':total/len(pool),
                'score':(total-m*math.log(29)-(len(spans)-1)*math.log(m))/len(pool)}
    starts_count=64 if len(values)<=1024 else 16
    retained=4 if len(values)<=1024 else 2
    families=[]; start_records=[]
    for sign_index, sign in enumerate((1,-1)):
        for period in range(17,33):
            rng=random.Random(seed+1000*sign_index+period); unique={}
            for start in range(starts_count):
                check_time(deadline)
                phases=seed_phases(chains,period,start,rng)
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
            for initial in sorted(unique.values(),key=lambda r:r['score'],reverse=True)[:retained]:
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
            key,changes=context_coordinates(values,page_spans,state['key'],state['sign'],state['skip_positions'],state['page_phases'],lookup,deadline)
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
    return {'phase_chains':chains,'top':top,'restarts':restarts,'starts_per_family':starts_count,'retained_per_family':retained,
            'alternatives':alternatives(values,page_spans,top[0],model),'families':families,'unigram_starts':start_records,
            'pool_ciphertext':pool,'pool_spans':spans,'pool_source_ranges':[list(r) for r in ranges]}
