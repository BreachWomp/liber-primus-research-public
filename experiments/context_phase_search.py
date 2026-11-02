"""Exact page-phase/F decoding with language history carried across pages."""
import math
import time
import numpy as np
from attack_support import to_runes
from reset_key_search import validate,factors_at
from phase_key_search import replay
from liberprimus.periodic_key import primitive,schedule,encrypt


def optimize(values,spans,key,sign,model,deadline):
    validate(values,spans)
    if any(0<s['end']-s['start']<4 for s in spans):raise ValueError('Nonempty pages require>=4runes')
    key=primitive(list(key));m=len(key)
    if not 1<=m<=32 or sign not in (-1,1):raise ValueError('Key/sign bound')
    # (cursor,last symbols) -> (logscore,plaintext bytes,skip tuple,raw page phases)
    states={(0,()):(0.,b'',(),())};maximum=1;transitions=0;boundary_counts=[]
    def bounded():
        if time.perf_counter()>deadline:raise TimeoutError('Coupled page context deadline')
        if len(states)>16*m*m:raise RuntimeError('Exact-state bound exceeded')
    for span in spans:
        bounded();a,b=span['start'],span['end']
        if a==b:
            states={k:(v[0],v[1],v[2],v[3]+(0,)) for k,v in states.items()}
            boundary_counts.append(0);continue
        histories={}
        for (_,history),row in states.items():
            if history not in histories or row[0]>histories[history][0]:histories[history]=row
        boundary_counts.append(len(histories))
        states={(p,h):(row[0],row[1],row[2],row[3]+(p,)) for h,row in histories.items() for p in range(m)}
        maximum=max(maximum,len(states));bounded()
        for i in range(a,b):
            bounded();following={};cipher=values[i]
            for (cursor,history),(old,path,skips,phases) in states.items():
                options=[((sign*cipher+key[cursor])%29,(cursor+1)%m,skips)]
                if cipher==0:options.append((0,cursor,skips+(i,)))
                for symbol,nxt,mask in options:
                    h=(history+(symbol,))[-(model.order-1):] if model.order>1 else ()
                    ident=(nxt,h);score=old+model.logp(history,symbol);transitions+=1
                    if ident not in following or score>following[ident][0]:
                        following[ident]=(score,path+bytes([symbol]),mask,phases)
            states=following;maximum=max(maximum,len(states));bounded()
    best=max(states.values(),key=lambda row:row[0]);first=next(i for i,s in enumerate(spans) if s['end']>s['start'])
    rotation=best[3][first];oriented=key[rotation:]+key[:rotation]
    phases=[(p-rotation)%m if s['end']>s['start'] else 0 for p,s in zip(best[3],spans)]
    plain=replay(values,spans,oriented,sign,list(best[2]),phases)
    assert plain==list(best[1]) and abs(model.score(plain)-best[0]/len(values))<1e-9
    phase_cost=(sum(s['end']>s['start'] for s in spans)-1)*math.log(m)
    return {'key':oriented,'sign':sign,'skip_positions':list(best[2]),'page_phases':phases,
        'language_score':best[0]/len(values),'score':(best[0]-m*math.log(29)-values.count(0)*math.log(2)-phase_cost)/len(values),
        'phase_cost':phase_cost,'rotation':rotation,'input_period':m,'dp_max_states':maximum,
        'dp_transitions':transitions,'boundary_context_counts':boundary_counts}


def coordinate_key(values,spans,key,sign,skips,phases,lookup,deadline):
    key=key[:];slots=[]
    for s,p in zip(spans,phases):
        a,b=s['start'],s['end']
        slots += [-1 if x<0 else (x+p)%len(key) for x in schedule(values[a:b],len(key),[i-a for i in skips if a<=i<b])]
    slots=np.asarray(slots);starts=np.zeros(len(values),dtype=int);signed=sign*np.asarray(values,dtype=np.int32)
    plain=np.asarray(replay(values,spans,key,sign,skips,phases));factors=factors_at(plain[None,:],np.arange(len(values)),lookup,starts)[0]
    changes=0
    for _ in range(6):
        changed=False
        for slot in range(len(key)):
            if time.perf_counter()>deadline:raise TimeoutError('Coupled context coordinates deadline')
            col=np.flatnonzero(slots==slot)
            if not len(col):continue
            neighbors=np.tile(plain,(29,1));neighbors[:,col]=(signed[col][None,:]+np.arange(29)[:,None])%29
            affected=np.unique(np.concatenate([col+d for d in range(len(lookup))]));affected=affected[affected<len(values)]
            new=factors_at(neighbors,affected,lookup,starts);delta=new.sum(axis=1)-factors[affected].sum();choice=int(delta.argmax())
            if float(delta[choice])>1e-12:
                key[slot]=choice;plain=neighbors[choice].copy();factors[affected]=new[choice];changed=True;changes+=1
        if not changed:break
    return primitive(key),changes


def alternatives(values,spans,row,model):
    """Keep each nonfirst leading-F alternative, irrespective of its score."""
    key=row['key'];m=len(key);sign=row['sign'];first=next(i for i,s in enumerate(spans) if s['end']>s['start']);out=[]
    baseline=replay(values,spans,key,sign,row['skip_positions'],row['page_phases'])
    penalty=(m*math.log(29)+values.count(0)*math.log(2)+(sum(s['end']>s['start'] for s in spans)-1)*math.log(m))/len(values)
    for j,s in enumerate(spans):
        a,b=s['start'],s['end']
        if a==b or j==first or values[a]!=0:continue
        skips=sorted(set(row['skip_positions'])^{a});phases=row['page_phases'][:]
        phases[j]=(phases[j]+(-1 if a in row['skip_positions'] else 1))%m
        plain=replay(values,spans,key,sign,skips,phases);encoded=[]
        for span,p in zip(spans,phases):
            x,y=span['start'],span['end']
            encoded+=encrypt(plain[x:y],key[p:]+key[:p],sign,[i-x for i in skips if x<=i<y])
        assert encoded==list(values)
        changed=[i for i,(x,y) in enumerate(zip(plain,baseline)) if x!=y];assert changed in ([],[a])
        out.append({'page_index':j,'position':a,'key':key,'sign':sign,'skip_positions':skips,
            'page_phases':phases,'plaintext_runes':to_runes(plain),'score':model.score(plain)-penalty,
            'changed_positions':changed,'ciphertext_identical':True})
    return out
