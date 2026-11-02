"""Exact finite two-lag ciphertext-filter search in bounded NumPy blocks."""
import argparse
import random
import time
import numpy as np
from attack_support import load,to_indices,to_runes,top_unique
from registry import registered
from external_language import external_model
from ngram_arrays import dense_tables,array_scores
from conditional_attack_null import conditional_shuffle
from liberprimus.cipher_filter import encrypt_suffix
from liberprimus.alphabet import transliterate

PLAN='experiments/cipher_filter_plan.json'


def search(values,lookup,deadline,keep=3,grid=None):
    if not 3<=len(values)<=1024:raise ValueError('Cipher length outside bound')
    values=np.asarray(values,dtype=np.int32);top=[];best=-float('inf');recipes=0
    # Enumeration: d fastest, then b, then c; a outermost.
    aa,bb,cc,dd=grid or (range(1,29),range(29),range(1,29),range(29))
    triples=np.array([(b,c,d) for c in cc for b in bb for d in dd],dtype=np.int32)
    for a in aa:
        allowed=triples[~((triples[:,0]==0)&(triples[:,2]==0)&np.isin(triples[:,1],[1,28]))] if a in (1,28) else triples
        for start in range(0,len(allowed),2048):
            if time.perf_counter()>deadline:raise TimeoutError('E033 deadline')
            block=allowed[start:start+2048];b,c,d=block.T
            plain=(a*values[None,2:]+b[:,None]*values[None,1:-1]+c[:,None]*values[None,:-2]+d[:,None])%29
            scores=array_scores(plain,lookup);recipes+=len(plain);best=max(best,float(scores.max()))
            if keep:
                for i in np.argsort(scores,kind='stable')[-keep:]:
                    p=plain[i].tolist();params=[int(x) for x in [a,b[i],c[i],d[i]]]
                    iv=values[:2].tolist();assert encrypt_suffix(p,*params,iv)==values.tolist()
                    top=top_unique(top+[{'score':float(scores[i]),'plaintext_runes':to_runes(p),'transliteration':transliterate(p),
                        'recipe':dict(zip(('a','b','c','d'),params))|{'iv':iv,'unrecovered_prefix_runes':2,'F_policy':'none'},
                        'reencryption_verified':True}],keep=keep)
    if grid is None:assert recipes==659340
    return best,top,recipes


def run(args):
    tick=time.perf_counter();deadline=tick+180;plan=load(PLAN);lookup=dense_tables(external_model(4))
    result={'experiment':'E033-cipher-filter','parameters':vars(args),'new_decryptions':[]}
    if args.mode=='controls':
        fixtures={f['id']:f for f in load('known_solutions/fixtures.json')};rng=random.Random(plan['control_seed']);rows=[]
        for ident,a,b,c,d in plan['controls']:
            iv=[rng.randrange(29) for _ in range(2)];f=fixtures[ident];plain=to_indices(f['plaintext_runes'])
            cipher=encrypt_suffix(plain,a,b,c,d,iv);_,top,count=search(cipher,lookup,deadline)
            rows.append({'fixture':ident,'injected':[a,b,c,d],'iv':iv,'ciphertext_indices':cipher,
                         'top':top,'exact':top[0]['plaintext_runes']==f['plaintext_runes'],'recipes':count})
            print({'control':ident,'exact':rows[-1]['exact'],'seconds':time.perf_counter()-tick},flush=True)
        result.update(controls=rows,gate_passed=all(r['exact'] for r in rows))
    else:
        page=next(p for p in load('transcriptions/pages.json') if p['id']==args.page)
        assert page['edition']=='LP2' and page['page']<56 and page['page']!=50
        values=to_indices(page['runes']);proposals=None
        if args.mode=='null':
            selection=load('experiments/cipher_filter_selection.json')
            assert args.page==selection['selected_page'] and 0<=args.replicate<19
            values,proposals=conditional_shuffle(values,random.Random(plan['null_seed']+args.replicate),deadline=deadline)
        score,top,count=search(values,lookup,deadline,keep=3 if args.mode=='page' else 1)
        result.update(page=page['id'],ciphertext_indices=values,top=top,score=score,recipes=count,shuffle_proposals=proposals)
    result['wall_seconds']=time.perf_counter()-tick
    return result


DEPS=['experiments/cipher_filter_attack.py',PLAN,'src/liberprimus/cipher_filter.py',
      'experiments/external_language.py','experiments/external_model_plan.json','experiments/ngram_arrays.py',
      'experiments/attack_support.py','experiments/conditional_attack_null.py','src/liberprimus/alphabet.py',
      'src/liberprimus/ciphers.py','src/liberprimus/decoding.py','known_solutions/fixtures.json',
      'transcriptions/pages.json','sources/emerson_manifest.json','data/raw/gutenberg/pg2944.txt']

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--mode',choices=['controls','page','null'],required=True)
    parser.add_argument('--page',default='LP2-00');parser.add_argument('--replicate',type=int,default=0);args=parser.parse_args()
    ident='E033-'+args.mode+('' if args.mode=='controls' else '-'+args.page)+(f'-{args.replicate:02}' if args.mode=='null' else '')
    registered(ident,{**vars(args),'numpy':np.__version__,'seconds':180},
               DEPS+(['experiments/cipher_filter_selection.json'] if args.mode=='null' else []),lambda:run(args))
