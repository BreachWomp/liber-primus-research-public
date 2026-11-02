"""Shared keys, independent page phases and exact conditional F masks."""
import math
import time
import numpy as np
from attack_support import cycle_key,to_runes,top_unique
from periodic_key_search import search as fixed_search
from reset_key_search import validate,sources,factors_at
from liberprimus.periodic_key import primitive,schedule,decrypt
from liberprimus.decoding import selective_decode
from liberprimus.alphabet import transliterate


def replay(values,spans,key,sign,skips,phases):
    if len(phases)!=len(spans):raise ValueError('One phase per page required')
    out=[]
    for span,phase in zip(spans,phases):
        a,b=span['start'],span['end'];phase%=len(key)
        out+=decrypt(values[a:b],key[phase:]+key[:phase],sign,[i-a for i in skips if a<=i<b])
    return out


def coordinate_key(values,spans,key,sign,skips,phases,lookup,deadline):
    key=key[:];slots=[];starts=[]
    for s,phase in zip(spans,phases):
        a,b=s['start'],s['end'];slots += [-1 if x<0 else (x+phase)%len(key) for x in schedule(values[a:b],len(key),[i-a for i in skips if a<=i<b])];starts += [a]*(b-a)
    slots=np.array(slots);starts=np.array(starts);signed=sign*np.array(values,dtype=np.int32)
    plain=np.array(replay(values,spans,key,sign,skips,phases));factors=factors_at(plain[None,:],np.arange(len(values)),lookup,starts)[0]
    changes=0
    for _ in range(6):
        changed=False
        for slot in range(len(key)):
            if time.perf_counter()>deadline:raise TimeoutError('Page-phase coordinates deadline')
            col=np.flatnonzero(slots==slot)
            if not len(col):continue
            neighbors=np.tile(plain,(29,1));neighbors[:,col]=(signed[col][None,:]+np.arange(29)[:,None])%29
            affected=[]
            for distance in range(len(lookup)):
                ends=col+distance;valid=ends<len(values);beg=col[valid];ends=ends[valid]
                affected.extend(ends[starts[ends]==starts[beg]])
            affected=np.unique(affected);new=factors_at(neighbors,affected,lookup,starts)
            delta=new.sum(axis=1)-factors[affected].sum();choice=int(delta.argmax())
            if float(delta[choice])>1e-12:
                key[slot]=choice;plain=neighbors[choice].copy();factors[affected]=new[choice];changed=True;changes+=1
        if not changed:break
    return primitive(key),changes


def optimize(values,spans,key,sign,model,deadline):
    key=primitive(key);total=0;skips=[];phases=[];maximum=0;transitions=0
    for span in spans:
        a,b=span['start'],span['end']
        if a==b:phases.append(0);continue
        row=selective_decode(values[a:b],key,model,starts=range(len(key)),cipher_sign=sign,key_sign=1,deadline=deadline)
        phases.append(row.start);total+=row.score*(b-a);skips += [a+i for i in row.skip_positions]
        maximum=max(maximum,row.max_states);transitions+=row.transitions
    assert maximum<=8*len(key)
    first=next(i for i,s in enumerate(spans) if s['end']>s['start']);rotation=phases[first]
    oriented=key[rotation:]+key[:rotation]
    phases=[(p-rotation)%len(key) if s['end']>s['start'] else 0 for p,s in zip(phases,spans)]
    pages=sum(s['end']>s['start'] for s in spans);phase_cost=(pages-1)*math.log(len(key));language=total/len(values)
    return {'key':oriented,'sign':sign,'skip_positions':skips,'page_phases':phases,
        'language_score':language,'score':language-(len(key)*math.log(29)+values.count(0)*math.log(2)+phase_cost)/len(values),
        'phase_cost':phase_cost,'rotation':rotation,'input_period':len(key),
        'dp_max_states':maximum,'dp_transitions':transitions}


def search(values,spans,model,lookup,deadline,seed=3303047):
    validate(values,spans);unique={};stats=[]
    for label,a,b,skips in sources(values,spans):
        found=fixed_search(values[a:b],lookup,deadline,seed=seed,oracle_skips=skips)
        stats.append({'kind':label,'range':[a,b],'families':len(found['families'])})
        for row in found['families']:
            key=cycle_key(row['key']);ident=(row['sign'],key)
            initial={'key':list(key),'sign':row['sign'],'seed_score':row['score'],'source_kind':label,
                'source_range':[a,b],'source_key':row['key'],'source_policy':row['policy']}
            if ident not in unique or row['score']>unique[ident]['seed_score']:unique[ident]=initial
    seeds=sorted(unique.values(),key=lambda r:r['seed_score'],reverse=True)[:12];top=[];restarts=[]
    for index,initial in enumerate(seeds):
        state=optimize(values,spans,initial['key'],initial['sign'],model,deadline);trace=[state]
        for _ in range(3):
            key,changes=coordinate_key(values,spans,state['key'],state['sign'],state['skip_positions'],state['page_phases'],lookup,deadline)
            following=optimize(values,spans,key,state['sign'],model,deadline);following['coordinate_changes']=changes
            assert following['score']>=state['score']-1e-9
            trace.append(following);unchanged=all(following[k]==state[k] for k in ('key','skip_positions','page_phases'));state=following
            if unchanged:break
        plain=replay(values,spans,state['key'],state['sign'],state['skip_positions'],state['page_phases'])
        final=state|{'seed_index':index,'plaintext_runes':to_runes(plain),'transliteration':transliterate(plain)}
        restarts.append({'initial':initial,'trace':trace,'final':final});top=top_unique(top+[final],keep=3)
    return {'top':top,'restarts':restarts,'source_stats':stats,'unique_seed_keys':len(unique)}

