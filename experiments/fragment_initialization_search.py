"""Ciphertext-only pooled phases, staged language order, diversified long keys."""
import math
import random
import time
import numpy as np
from attack_support import cycle_key, to_runes, top_unique
from pooled_long_key_search import pooled_fragments
from phase_key_search import coordinate_key
from reset_key_search import factors_at
from joint_skip_search import fixed_schedule_key, optimize_schedule
from liberprimus.periodic_key import primitive, decrypt, encrypt
from liberprimus.alphabet import transliterate


def check_time(deadline):
    if time.perf_counter() > deadline:
        raise TimeoutError('Fragment initialization deadline')


def phase_fit(values, spans, key, sign, lookup, deadline):
    """Exact independent fragment phases; vectorized enumeration, no F allowed."""
    if not values or 0 in values:
        raise ValueError('Nonempty F-free pool required')
    key = primitive(list(key)); m = len(key); total = 0.; phases = []
    for span in spans:
        check_time(deadline)
        part = np.asarray(values[span['start']:span['end']], dtype=np.int32)
        indices = (np.arange(m)[:, None] + np.arange(len(part))[None, :]) % m
        plain = (sign * part[None, :] + np.asarray(key)[indices]) % 29
        scores = factors_at(plain, np.arange(len(part)), lookup, np.zeros(len(part), dtype=int)).sum(axis=1)
        phase = int(scores.argmax()); phases.append(phase); total += float(scores[phase])
    rotation = phases[0]
    return {'key': key[rotation:] + key[:rotation], 'sign': sign,
            'page_phases': [(p-rotation) % m for p in phases], 'order': len(lookup),
            'language_score': total/len(values),
            'score': (total-m*math.log(29)-(len(spans)-1)*math.log(m))/len(values)}


def unigram_key(values, spans, phases, period, sign, lookup):
    slots = np.concatenate([(np.arange(s['end']-s['start'])+p) % period for s,p in zip(spans,phases)])
    counts = np.zeros((period,29), dtype=np.int32)
    np.add.at(counts, (slots, np.asarray(values)), 1)
    scores = counts @ lookup[0][(sign*np.arange(29)[:,None]+np.arange(29)[None,:])%29]
    return scores.argmax(axis=1).tolist()


def search(values, model, lookup, deadline, seed=3303052):
    if not 512 <= len(values) <= 4096:
        raise ValueError('Input bound512..4096')
    pool, spans, ranges = pooled_fragments(values)
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
        pooled=chosen['state']; state=optimize_schedule(values,pooled['key'],pooled['sign'],model,deadline); trace=[state]
        for _ in range(3):
            key,changes=fixed_schedule_key(values,state['key'],state['sign'],state['skip_positions'],lookup,deadline)
            following=optimize_schedule(values,key,state['sign'],model,deadline); following['coordinate_changes']=changes
            assert following['score']>=state['score']-1e-9
            same=all(following[k]==state[k] for k in ('key','skip_positions'))
            trace.append(following); state=following
            if same: break
        plain=decrypt(values,state['key'],state['sign'],state['skip_positions'])
        assert encrypt(plain,state['key'],state['sign'],state['skip_positions'])==list(values)
        final=state|{'seed_index':i,'plaintext_runes':to_runes(plain),'transliteration':transliterate(plain)}
        restarts.append({'nominal_period':chosen['nominal_period'],'pool_start':chosen['initial']['start'],
                         'pool_state':pooled,'trace':trace,'final':final})
        top=top_unique(top+[final],keep=3)
    return {'top':top,'restarts':restarts,'families':families,'unigram_starts':start_records,
            'pool_ciphertext':pool,'pool_spans':spans,'pool_source_ranges':[list(r) for r in ranges]}
