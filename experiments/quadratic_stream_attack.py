"""Complete bounded quadratic progressive-key search."""
import argparse
import random
import time
import numpy as np
from attack_support import load,to_indices,to_runes,top_unique
from registry import registered
from external_language import external_model
from ngram_arrays import dense_tables,array_scores
from conditional_attack_null import conditional_shuffle
from liberprimus.quadratic_stream import encrypt
from liberprimus.alphabet import transliterate

PLAN='experiments/quadratic_stream_plan.json'


def search(values,lookup,deadline,keep=3,grid=None):
    if not 1<=len(values)<=1024:raise ValueError('Cipher length outside bound')
    aa,bb,cc,dd=grid or (range(1,29),range(29),range(29),range(29))
    triples=np.array([(b,c,d) for b in bb for c in cc if b or c for d in dd],dtype=np.int32)
    if not len(triples):raise ValueError('Empty progressive grid')
    cipher=np.array(values,dtype=np.int32);index=np.arange(len(values),dtype=np.int32)%29
    square=index*index%29;top=[];best=-float('inf');recipes=0
    for a in aa:
        for start in range(0,len(triples),2048):
            if time.perf_counter()>deadline:raise TimeoutError('E037 deadline')
            b,c,d=triples[start:start+2048].T
            plain=(a*cipher+b[:,None]*square+c[:,None]*index+d[:,None])%29
            scores=array_scores(plain,lookup);recipes+=len(plain);best=max(best,float(scores.max()))
            if keep:
                for j in np.argsort(scores,kind='stable')[-keep:]:
                    bv,cv,dv=map(int,(b[j],c[j],d[j]));p=plain[j].tolist()
                    assert encrypt(p,a,bv,cv,dv)==list(values)
                    top=top_unique(top+[{'score':float(scores[j]),'plaintext_runes':to_runes(p),
                        'transliteration':transliterate(p),'recipe':{'a':a,'b':bv,'c':cv,'d':dv},
                        'reencryption_verified':True}],keep=keep)
    if grid is None:assert recipes==682080
    return best,top,recipes


def run(args):
    tick=time.perf_counter();deadline=tick+180;plan=load(PLAN);lookup=dense_tables(external_model(4))
    result={'experiment':'E037-quadratic-stream','parameters':vars(args),'new_decryptions':[]}
    if args.mode=='controls':
        fixtures={f['id']:f for f in load('known_solutions/fixtures.json')};rows=[]
        for ident,a,b,c,d in plan['controls']:
            f=fixtures[ident];plain=to_indices(f['plaintext_runes']);cipher=encrypt(plain,a,b,c,d)
            _,top,count=search(cipher,lookup,deadline)
            rows.append({'fixture':ident,'injected':[a,b,c,d],'ciphertext_indices':cipher,'top':top,
                         'exact':top[0]['plaintext_runes']==f['plaintext_runes'],'recipes':count})
            print({'control':ident,'exact':rows[-1]['exact'],'seconds':time.perf_counter()-tick},flush=True)
        result.update(controls=rows,gate_passed=all(r['exact'] for r in rows))
    else:
        page=next(p for p in load('transcriptions/pages.json') if p['id']==args.page)
        assert page['edition']=='LP2' and page['page']<56 and page['page']!=50
        values=to_indices(page['runes']);proposals=None
        if args.mode=='null':
            selection=load('experiments/quadratic_stream_selection.json')
            assert args.page==selection['selected_page'] and 0<=args.replicate<19
            values,proposals=conditional_shuffle(values,random.Random(plan['null_seed']+args.replicate),deadline=deadline)
        score,top,count=search(values,lookup,deadline,keep=3 if args.mode=='page' else 1)
        result.update(page=page['id'],ciphertext_indices=values,top=top,score=score,recipes=count,shuffle_proposals=proposals)
    result['wall_seconds']=time.perf_counter()-tick
    return result


DEPS=['experiments/quadratic_stream_attack.py',PLAN,'src/liberprimus/quadratic_stream.py',
      'experiments/external_language.py','experiments/external_model_plan.json','experiments/ngram_arrays.py',
      'experiments/attack_support.py','experiments/conditional_attack_null.py','src/liberprimus/alphabet.py',
      'src/liberprimus/ciphers.py','src/liberprimus/decoding.py','known_solutions/fixtures.json',
      'transcriptions/pages.json','sources/emerson_manifest.json','data/raw/gutenberg/pg2944.txt']

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--mode',choices=['controls','page','null'],required=True)
    parser.add_argument('--page',default='LP2-00');parser.add_argument('--replicate',type=int,default=0);args=parser.parse_args()
    ident='E037-'+args.mode+('' if args.mode=='controls' else '-'+args.page)+(f'-{args.replicate:02}' if args.mode=='null' else '')
    registered(ident,{**vars(args),'numpy':np.__version__,'seconds':180},
               DEPS+(['experiments/quadratic_stream_selection.json'] if args.mode=='null' else []),lambda:run(args))
