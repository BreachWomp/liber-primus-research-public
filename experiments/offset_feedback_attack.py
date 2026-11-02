"""Exhaustive affine plaintext feedback with nonzero constant term."""
import argparse
import random
import time
import numpy as np
from attack_support import load,to_indices,to_runes,top_unique
from registry import registered
from external_language import external_model
from ngram_arrays import dense_tables,array_scores
from conditional_attack_null import conditional_shuffle
from liberprimus.offset_feedback import basis,encrypt
from liberprimus.alphabet import transliterate

PLAN='experiments/offset_feedback_plan.json'


def search(values,lookup,deadline,keep=3,grid=None):
    if not 1<=len(values)<=1024:raise ValueError('Cipher length outside bound')
    top=[];best=-float('inf');recipes=0
    aa,bb,dd,xx=grid or (range(1,29),range(1,29),range(1,29),range(29))
    triples=np.array([(a,d,x) for a in aa for d in dd for x in xx],dtype=np.int32)
    for b in bb:
        base,power,offset=[np.asarray(v,dtype=np.int32) for v in basis(values,b)]
        for start in range(0,len(triples),2048):
            if time.perf_counter()>deadline:raise TimeoutError('E034 deadline')
            a,d,x=triples[start:start+2048].T
            plain=(a[:,None]*base+x[:,None]*power+d[:,None]*offset)%29
            scores=array_scores(plain,lookup);recipes+=len(plain);best=max(best,float(scores.max()))
            if keep:
                for i in np.argsort(scores,kind='stable')[-keep:]:
                    av,dv,xv=map(int,(a[i],d[i],x[i]))
                    key=pow(b,-1,29)*(xv-av*values[0]-dv)%29;p=plain[i].tolist()
                    assert encrypt(p,av,b,dv,key)==list(values)
                    top=top_unique(top+[{'score':float(scores[i]),'plaintext_runes':to_runes(p),
                        'transliteration':transliterate(p),'recipe':{'a':av,'b':b,'d':dv,'initial_key':key,
                        'initial_plaintext':xv,'F_policy':'none'},'reencryption_verified':True}],keep=keep)
    if grid is None:assert recipes==636608
    return best,top,recipes


def run(args):
    tick=time.perf_counter();deadline=tick+180;plan=load(PLAN);lookup=dense_tables(external_model(4))
    result={'experiment':'E034-offset-feedback','parameters':vars(args),'new_decryptions':[]}
    if args.mode=='controls':
        fixtures={f['id']:f for f in load('known_solutions/fixtures.json')};rng=random.Random(plan['control_seed']);rows=[]
        for ident,a,b,d in plan['controls']:
            key=rng.randrange(29);f=fixtures[ident];plain=to_indices(f['plaintext_runes'])
            cipher=encrypt(plain,a,b,d,key);_,top,count=search(cipher,lookup,deadline)
            rows.append({'fixture':ident,'injected':[a,b,d],'initial_key':key,'ciphertext_indices':cipher,
                         'top':top,'exact':top[0]['plaintext_runes']==f['plaintext_runes'],'recipes':count})
            print({'control':ident,'exact':rows[-1]['exact'],'seconds':time.perf_counter()-tick},flush=True)
        result.update(controls=rows,gate_passed=all(r['exact'] for r in rows))
    else:
        page=next(p for p in load('transcriptions/pages.json') if p['id']==args.page)
        assert page['edition']=='LP2' and page['page']<56 and page['page']!=50
        values=to_indices(page['runes']);proposals=None
        if args.mode=='null':
            selection=load('experiments/offset_feedback_selection.json')
            assert args.page==selection['selected_page'] and 0<=args.replicate<19
            values,proposals=conditional_shuffle(values,random.Random(plan['null_seed']+args.replicate),deadline=deadline)
        score,top,count=search(values,lookup,deadline,keep=3 if args.mode=='page' else 1)
        result.update(page=page['id'],ciphertext_indices=values,top=top,score=score,recipes=count,shuffle_proposals=proposals)
    result['wall_seconds']=time.perf_counter()-tick
    return result


DEPS=['experiments/offset_feedback_attack.py',PLAN,'src/liberprimus/offset_feedback.py',
      'experiments/external_language.py','experiments/external_model_plan.json','experiments/ngram_arrays.py',
      'experiments/attack_support.py','experiments/conditional_attack_null.py','src/liberprimus/alphabet.py',
      'src/liberprimus/ciphers.py','src/liberprimus/decoding.py','known_solutions/fixtures.json',
      'transcriptions/pages.json','sources/emerson_manifest.json','data/raw/gutenberg/pg2944.txt']

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--mode',choices=['controls','page','null'],required=True)
    parser.add_argument('--page',default='LP2-00');parser.add_argument('--replicate',type=int,default=0);args=parser.parse_args()
    ident='E034-'+args.mode+('' if args.mode=='controls' else '-'+args.page)+(f'-{args.replicate:02}' if args.mode=='null' else '')
    registered(ident,{**vars(args),'numpy':np.__version__,'seconds':180},
               DEPS+(['experiments/offset_feedback_selection.json'] if args.mode=='null' else []),lambda:run(args))
