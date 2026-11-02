"""E066: per-period family screening followed by the fixed E062 search budget."""
import random
import time
import numpy as np
from general_feedback_factors import factor_tables, screen
from attack_support import to_runes, top_unique
from ngram_arrays import array_scores
from liberprimus.general_feedback import decode_prefix
from liberprimus.alphabet import transliterate


def local_scores(factors, prefix, residue):
    m=len(prefix);r=residue
    return (factors[r,:,prefix[(r+1)%m],prefix[(r+2)%m]]+
            factors[(r-1)%m,prefix[(r-1)%m],:,prefix[(r+1)%m]]+
            factors[(r-2)%m,prefix[(r-2)%m],prefix[(r-1)%m],:])


def factor_score(factors,prefix):
    m=len(prefix)
    return float(sum(factors[r,prefix[r],prefix[(r+1)%m],prefix[(r+2)%m]] for r in range(m)))


def bounded_beam(factors,deadline):
    m=len(factors);initial=np.array([(a,b) for a in range(29) for b in range(29)],dtype=np.int16)
    found={}
    for cut in (0,m//2):
        paths=initial.copy();scores=np.zeros(len(paths))
        for j in range(2,m):
            if time.perf_counter()>deadline:raise TimeoutError('Beam deadline')
            flat=(scores[:,None]+factors[(cut+j-2)%m,paths[:,-2],paths[:,-1],:]).ravel()
            take=np.argsort(flat,kind='stable')[-128:];parents,symbols=np.divmod(take,29)
            paths=np.column_stack((paths[parents],symbols));scores=flat[take]
        scores+=factors[(cut+m-2)%m,paths[:,-2],paths[:,-1],paths[:,0]]
        scores+=factors[(cut+m-1)%m,paths[:,-1],paths[:,0],paths[:,1]]
        for idx in np.argsort(scores,kind='stable')[-2:]:
            found[tuple(np.roll(paths[idx],cut).tolist())]=float(scores[idx])
    return [list(p) for p in found]


def search(values,lookup,deadline):
    families=[];candidates=[];n=len(values)
    screening=screen(values,lookup[0],deadline)
    for period in range(4,33):
        for selected_family in [r for r in screening if r['period']==period and r['rank']<=4]:
            cs,ks=selected_family['cipher_sign'],selected_family['feedback_sign']
            if time.perf_counter()>deadline:raise TimeoutError('Extended autokey deadline')
            factors,constant,active,base,coeff=factor_tables(values,period,cs,ks,lookup[:3])
            residue=np.arange(n)%period
            variants=(np.arange(29)[:,None]*coeff[None,:]+base[None,:])%29
            unary=np.array([lookup[0][variants[:,residue==r]].sum(axis=1) for r in range(period)])
            ranks=np.argsort(-unary,axis=1,kind='stable')
            rng=random.Random(3303066+56*period+28*(cs==-1)+ks-1);starts=[]
            for start in range(8):
                prefix=[int(ranks[r,start if start<3 else rng.randrange(5)]) for r in range(period)]
                initial=prefix[:];before=factor_score(factors,prefix);converged=False
                for sweep in range(6):
                    changed=False
                    for r in range(period):
                        scores=local_scores(factors,prefix,r);best=int(np.argmax(scores))
                        if scores[best]>scores[prefix[r]]+1e-12:prefix[r]=best;changed=True
                    if not changed:converged=True;break
                starts.append({'initial':initial,'prefix':prefix,'initial_total':before,
                    'final_total':factor_score(factors,prefix),'sweeps':sweep+1,'converged':converged})
            coordinate=sorted(starts,key=lambda r:r['final_total'],reverse=True)[:2]
            beam=bounded_beam(factors,deadline)
            family={'period':period,'cipher_sign':cs,'feedback_sign':ks,'starts':starts,'candidates':[]}
            for origin,prefix in [('coordinate',r['prefix']) for r in coordinate]+[('beam',p) for p in beam]:
                plain=(np.array(prefix)[residue]*coeff+base)%29
                score=float(array_scores(plain[None,:],lookup)[0])
                row={'period':period,'cipher_sign':cs,'feedback_sign':ks,'prefix':prefix[:],
                     'origin':origin,'score':score,'trigram_score':(factor_score(factors,prefix)+constant)/n}
                family['candidates'].append(row);candidates.append(row)
            families.append(family)
    selected=[];seen=set()
    for row in sorted(candidates,key=lambda r:r['score'],reverse=True):
        identity=(row['period'],row['cipher_sign'],row['feedback_sign'],tuple(row['prefix']))
        if identity not in seen:seen.add(identity);selected.append(row)
        if len(selected)==12:break
    refinements=[];top=[]
    for row in selected:
        prefix=row['prefix'][:];cs=row['cipher_sign'];ks=row['feedback_sign'];m=len(prefix)
        plain,key=decode_prefix(values,prefix,cs,ks);current=np.array(plain,dtype=np.int16);trace=[]
        # Changing a prefix symbol changes exactly one residue chain.
        coefficient=np.array([pow(ks,i//m,29) for i in range(n)],dtype=np.int16)
        converged=False
        for sweep in range(6):
            changed=False
            for r in range(m):
                if time.perf_counter()>deadline:raise TimeoutError('Fourgram refinement deadline')
                trial=np.tile(current,(29,1));positions=np.arange(r,n,m)
                trial[:,positions]=(current[positions]+(np.arange(29)[:,None]-prefix[r])*coefficient[positions])%29
                scores=array_scores(trial,lookup);best=int(np.argmax(scores))
                if scores[best]>scores[prefix[r]]+1e-12:
                    prefix[r]=best;current=trial[best].copy();changed=True
            trace.append({'prefix':prefix[:],'score':float(array_scores(current[None,:],lookup)[0])})
            if not changed:converged=True;break
        plain,key=decode_prefix(values,prefix,cs,ks)
        assert plain==current.tolist()
        refinements.append({'initial':row,'trace':trace,'converged':converged})
        top=top_unique(top+[{'score':trace[-1]['score'],'plaintext_runes':to_runes(plain),
            'transliteration':transliterate(plain),'recipe':{'key_indices':key,'cipher_sign':cs,
            'feedback_sign':ks,'skip_positions':[],'skip_policy':'none'}}],keep=3)
    return {'screening':screening,'families':families,'refinements':refinements,'top':top,
        'branch_best_before_refinement':{name:max(r['score'] for r in candidates if r['origin']==name) for name in ('coordinate','beam')}}
