"""F-free key seeds followed by alternating key and exact schedule inference."""
import math
import time
import numpy as np
from attack_support import cycle_key,to_runes,top_unique
from periodic_key_search import search as fixed_search,coordinate,factors_at
from liberprimus.periodic_key import primitive,schedule,decrypt,encrypt
from liberprimus.decoding import selective_decode
from liberprimus.alphabet import transliterate


def seed_ranges(values):
    runs=[];begin=0
    for i,x in enumerate(list(values)+[0]):
        if x==0:
            if i-begin>=32:runs.append((begin,i))
            begin=i+1
    runs.sort(key=lambda ab:(-(ab[1]-ab[0]),ab[0]))
    return [(a,min(b,a+256)) for a,b in runs[:3]]


def make_seeds(values,lookup,deadline,seed):
    sources=[('whole',0,len(values),None)]+[('non_F_run',a,b,[]) for a,b in seed_ranges(values)]
    unique={};source_stats=[]
    for label,a,b,skips in sources:
        found=fixed_search(values[a:b],lookup,deadline,seed=seed,oracle_skips=skips)
        source_stats.append({'kind':label,'range':[a,b],'families':len(found['families']),
                             'coordinate_evaluations':found['coordinate_evaluations']})
        for row in found['families']:
            canonical=cycle_key(row['key']);index=(row['sign'],canonical)
            candidate={'key':list(canonical),'sign':row['sign'],'seed_score':row['score'],
                'source_kind':label,'source_range':[a,b],'source_key':row['key'],
                'source_policy':row['policy'],'nominal_period':row['nominal_period']}
            if index not in unique or row['score']>unique[index]['seed_score']:unique[index]=candidate
    selected=sorted(unique.values(),key=lambda r:r['seed_score'],reverse=True)[:12]
    return selected,source_stats,len(unique)


def fixed_schedule_key(values,key,sign,skips,lookup,deadline):
    key=key[:];slots=np.array(schedule(values,len(key),skips));signed=sign*np.array(values,dtype=np.int32)
    plain=np.array(decrypt(values,key,sign,skips));factors=factors_at(plain[None,:],np.arange(len(values)),lookup)[0]
    changes=0
    for _ in range(6):
        if time.perf_counter()>deadline:raise TimeoutError('Joint key update deadline')
        changed=False
        for slot in range(len(key)):
            col=np.flatnonzero(slots==slot)
            if not len(col):continue
            plain,factors,moved=coordinate(plain,signed,col,slot,key,lookup,factors)
            changes+=moved;changed|=moved
        if not changed:break
    return primitive(key),changes


def optimize_schedule(values,key,sign,model,deadline):
    result=selective_decode(values,key,model,starts=range(len(key)),cipher_sign=sign,key_sign=1,deadline=deadline)
    assert result.max_states<=8*len(key)
    rotated=key[result.start:]+key[:result.start];rotated=primitive(rotated)
    assert decrypt(values,rotated,sign,result.skip_positions)==result.plaintext
    return {'key':rotated,'sign':sign,'skip_positions':result.skip_positions,'language_score':result.score,
            'score':result.score-(len(rotated)*math.log(29)+values.count(0)*math.log(2))/len(values),
            'selected_phase':result.start,'dp_transitions':result.transitions,'dp_max_states':result.max_states,
            'input_period':len(key)}


def search(values,model,lookup,deadline,seed=3303040):
    if not 1<=len(values)<=1024:raise ValueError('Bounded nonempty input required')
    seeds,source_stats,unique=make_seeds(values,lookup,deadline,seed)
    top=[];restarts=[]
    for index,initial in enumerate(seeds):
        state=optimize_schedule(values,initial['key'],initial['sign'],model,deadline);trace=[state]
        for _ in range(3):
            key,changes=fixed_schedule_key(values,state['key'],state['sign'],state['skip_positions'],lookup,deadline)
            following=optimize_schedule(values,key,state['sign'],model,deadline)
            following['coordinate_changes']=changes
            assert following['score']>=state['score']-1e-9
            trace.append(following)
            unchanged=following['key']==state['key'] and following['skip_positions']==state['skip_positions']
            state=following
            if unchanged:break
        plain=decrypt(values,state['key'],state['sign'],state['skip_positions'])
        assert encrypt(plain,state['key'],state['sign'],state['skip_positions'])==list(values)
        row=state|{'seed_index':index,'plaintext_runes':to_runes(plain),'transliteration':transliterate(plain)}
        restarts.append({'initial':initial,'trace':trace,'final':row})
        top=top_unique(top+[row],keep=3)
    return {'top':top,'restarts':restarts,'source_stats':source_stats,'unique_seed_keys':unique}
