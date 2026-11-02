"""Shared key with page-local cursor/context resets; bounded heuristic keys."""
import math
import time
import numpy as np
from attack_support import cycle_key,to_runes,top_unique
from periodic_key_search import search as fixed_search
from joint_skip_search import seed_ranges
from liberprimus.periodic_key import primitive,schedule,decrypt
from liberprimus.decoding import selective_decode
from liberprimus.alphabet import transliterate


def validate(values,spans):
    cursor=0
    if not 1<=len(values)<=4096 or not 1<=len(spans)<=16:raise ValueError('Reset search bound')
    for s in spans:
        if s['start']!=cursor or s['end']<cursor:raise ValueError('Invalid page spans')
        cursor=s['end']
    if cursor!=len(values):raise ValueError('Incomplete page spans')


def replay(values,spans,key,sign,skips):
    out=[]
    for span in spans:
        a,b=span['start'],span['end']
        out+=decrypt(values[a:b],key,sign,[i-a for i in skips if a<=i<b])
    return out


def sources(values,spans):
    pages=sorted([(s['start'],s['end']) for s in spans if s['end']>s['start']],key=lambda ab:(-(ab[1]-ab[0]),ab[0]))[:2]
    result=[('page',a,min(a+1024,b),None) for a,b in pages]
    runs=[]
    for s in spans:
        a,b=s['start'],s['end']
        # Rank by full run length before capping, matching the declared rule.
        begin=a
        for i in range(a,b+1):
            if i==b or values[i]==0:
                if i-begin>=32:runs.append((begin,i))
                begin=i+1
    runs.sort(key=lambda ab:(-(ab[1]-ab[0]),ab[0]))
    return result+[('non_F_run',a,min(a+256,b),[]) for a,b in runs[:3]]


def factors_at(rows,positions,lookup,page_starts):
    positions=np.asarray(positions,dtype=np.int32);answer=np.empty((len(rows),len(positions)))
    depths=np.minimum(positions-page_starts[positions],len(lookup)-1)
    for d in range(len(lookup)):
        chosen=np.flatnonzero(depths==d);ends=positions[chosen]
        if len(chosen):answer[:,chosen]=lookup[d][tuple(rows[:,ends-d+j] for j in range(d+1))]
    return answer


def coordinate_key(values,spans,key,sign,skips,lookup,deadline):
    key=key[:];slots=[];starts=[]
    for s in spans:
        a,b=s['start'],s['end'];slots+=schedule(values[a:b],len(key),[i-a for i in skips if a<=i<b]);starts += [a]*(b-a)
    slots=np.array(slots);starts=np.array(starts);signed=sign*np.array(values,dtype=np.int32)
    plain=np.array(replay(values,spans,key,sign,skips));factors=factors_at(plain[None,:],np.arange(len(values)),lookup,starts)[0]
    changes=0
    for _ in range(6):
        changed=False
        for slot in range(len(key)):
            if time.perf_counter()>deadline:raise TimeoutError('Reset coordinates deadline')
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


def optimize(values,spans,key,sign,model,deadline,all_phases=False):
    best=None
    for phase in (range(len(key)) if all_phases else (0,)):
        total=0;skips=[];maximum=0;transitions=0
        for span in spans:
            a,b=span['start'],span['end']
            if a==b:continue
            row=selective_decode(values[a:b],key,model,starts=(phase,),cipher_sign=sign,key_sign=1,deadline=deadline)
            total+=row.score*(b-a);skips += [a+i for i in row.skip_positions]
            maximum=max(maximum,row.max_states);transitions+=row.transitions
        assert maximum<=8*len(key)
        rotated=primitive(key[phase:]+key[:phase]);language=total/len(values)
        result={'key':rotated,'sign':sign,'skip_positions':skips,'language_score':language,
            'score':language-(len(rotated)*math.log(29)+values.count(0)*math.log(2))/len(values),
            'selected_phase':phase,'input_period':len(key),'all_phases':all_phases,
            'dp_max_states':maximum,'dp_transitions':transitions}
        if best is None or result['score']>best['score']:best=result
    return best


def search(values,spans,model,lookup,deadline,seed=3303045):
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
        state=optimize(values,spans,initial['key'],initial['sign'],model,deadline,True);trace=[state]
        for _ in range(3):
            key,changes=coordinate_key(values,spans,state['key'],state['sign'],state['skip_positions'],lookup,deadline)
            following=optimize(values,spans,key,state['sign'],model,deadline);following['coordinate_changes']=changes
            assert following['score']>=state['score']-1e-9
            trace.append(following);unchanged=following['key']==state['key'] and following['skip_positions']==state['skip_positions'];state=following
            if unchanged:break
        plain=replay(values,spans,state['key'],state['sign'],state['skip_positions'])
        final=state|{'seed_index':index,'plaintext_runes':to_runes(plain),'transliteration':transliterate(plain)}
        restarts.append({'initial':initial,'trace':trace,'final':final});top=top_unique(top+[final],keep=3)
    return {'top':top,'restarts':restarts,'source_stats':stats,'unique_seed_keys':len(unique)}
