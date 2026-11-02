"""Exact delay-two affine feedback search in bounded NumPy batches."""
import argparse
import random
import time
import numpy as np
from attack_support import load,to_indices,to_runes,top_unique
from liberprimus.alphabet import transliterate
from liberprimus.feedback import basis,encrypt
from external_language import external_model
from ngram_arrays import dense_tables,array_scores
from conditional_attack_null import conditional_shuffle
from registry import registered

def search(values,lookup,deadline,keep=3):
    n=len(values)
    if not 2<=n<=1024: raise ValueError('Page length outside registered bound')
    top=[];best=-float('inf');recipes=0;residues=np.arange(n)%2
    for b in range(1,29):
        aa=np.array([a for a in range(1,29) if not(a in (1,28) and b in (1,28))],dtype=np.int16)
        base,powers=map(lambda x:np.asarray(x,dtype=np.int16),basis(values,b,2))
        for first in range(0,len(aa)*841,2048):
            if time.perf_counter()>deadline: raise TimeoutError('periodic feedback deadline')
            ids=np.arange(first,min(first+2048,len(aa)*841));a=aa[ids//841]
            xx=np.stack([(ids%841)//29,ids%29],axis=1).astype(np.int16)
            plain=(a[:,None]*base[None,:]+powers[None,:]*xx[:,residues])%29
            scores=array_scores(plain,lookup);recipes+=len(plain);best=max(best,float(scores.max()))
            if keep:
                for idx in np.argsort(scores,kind='stable')[-keep:]:
                    p=plain[idx].tolist();av=int(a[idx]);x=xx[idx].tolist()
                    seed=[int((x[r]-av*values[r])*pow(b,-1,29)%29) for r in range(2)]
                    assert encrypt(p,av,b,seed)==list(values)
                    top=top_unique(top+[{'score':float(scores[idx]),'plaintext_runes':to_runes(p),
                        'transliteration':transliterate(p),'recipe':{'delay':2,'a':av,'b':b,'initial_key':seed,
                        'initial_plaintext':x,'F_policy':'none'},'reencryption_verified':True}],keep=keep)
    assert recipes==655980
    return best,top,recipes

def run(args):
    tick=time.perf_counter();deadline=tick+180;lookup=dense_tables(external_model(4))
    plan=load('experiments/periodic_feedback_plan.json')
    result={'experiment':'E025-periodic-feedback','status':'completed','parameters':vars(args),'new_decryptions':[]}
    if args.mode=='controls':
        fixtures={f['id']:f for f in load('known_solutions/fixtures.json')};rng=random.Random(3301025);rows=[]
        for ident,a,b in plan['controls']:
            seed=[rng.randrange(29) for _ in range(2)];expected=fixtures[ident]['plaintext_runes']
            cipher=encrypt(to_indices(expected),a,b,seed);_,top,count=search(cipher,lookup,deadline)
            rows.append({'fixture':ident,'a':a,'b':b,'initial_key':seed,'ciphertext_indices':cipher,
                         'exact':top[0]['plaintext_runes']==expected,'top':top,'recipes':count})
            print({'control':ident,'exact':rows[-1]['exact'],'seconds':time.perf_counter()-tick},flush=True)
        result.update(controls=rows,gate_passed=all(row['exact'] for row in rows))
    else:
        pages=[p for p in load('transcriptions/pages.json') if p['edition']=='LP2' and args.first<=p['page']<=min(args.last,55) and p['runes']]
        rows=[]
        for page in pages:
            values=to_indices(page['runes'])
            if args.mode=='null':
                assert len(pages)==1
                values,proposals=conditional_shuffle(values,random.Random(3301025+args.replicate),deadline=deadline)
                best,top,count=search(values,lookup,deadline,keep=0)
                rows.append({'page':page['id'],'score':best,'ciphertext_indices':values,'proposals':proposals,'recipes':count})
            else:
                _,top,count=search(values,lookup,deadline)
                rows.append({'page':page['id'],'ciphertext_runes':page['runes'],'top':top,'recipes':count})
                print({'page':page['id'],'score':top[0]['score'],'seconds':time.perf_counter()-tick},flush=True)
        result['pages']=rows
    result['wall_seconds']=time.perf_counter()-tick
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--mode',choices=['controls','pages','null'],required=True)
    parser.add_argument('--first',type=int,default=0);parser.add_argument('--last',type=int,default=55)
    parser.add_argument('--replicate',type=int,default=0);args=parser.parse_args()
    deps=['experiments/periodic_feedback.py','experiments/periodic_feedback_plan.json','src/liberprimus/feedback.py',
        'experiments/external_language.py','experiments/external_model_plan.json','experiments/ngram_arrays.py',
        'experiments/attack_support.py','experiments/conditional_attack_null.py','src/liberprimus/alphabet.py',
        'src/liberprimus/ciphers.py','src/liberprimus/decoding.py','known_solutions/fixtures.json',
        'transcriptions/pages.json','sources/emerson_manifest.json','data/raw/gutenberg/pg2944.txt']
    ident='E025-'+args.mode+(f'-LP2-{args.first:02}_{args.last:02}' if args.mode!='controls' else '')+(f'-{args.replicate:02}' if args.mode=='null' else '')
    registered(ident,{**vars(args),'numpy':np.__version__,'seconds':180},deps,lambda:run(args))
