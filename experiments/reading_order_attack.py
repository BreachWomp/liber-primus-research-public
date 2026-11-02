"""Image-audited ragged-row routes followed by a fixed finite cipher union."""
import argparse
import random
import time
import numpy as np
from attack_support import load,to_indices,to_runes,stream_catalog,candidate,top_unique
from liberprimus.alphabet import transliterate
from liberprimus.decoding import selective_decode
from liberprimus.layout import row_permutations,permute,scatter
from external_language import external_model
from ngram_arrays import dense_tables,array_scores
from conditional_attack_null import conditional_shuffle
from registry import registered

SIGNS=((1,-1),(1,1),(-1,-1),(-1,1))

def search(values,lengths,model,lookup,deadline,keep=3):
    fixtures={f['id']:f for f in load('known_solutions/fixtures.json')}
    options=[('vigenere',fixtures[k]['key_indices'],True) for k in ('LP1-03_04_divinity','LP1-14_15_circumference')]
    options += [(name,key,False) for name,key in stream_catalog(len(values)+256).items()]
    a=np.repeat(np.arange(1,29),29);b=np.tile(np.arange(29),28)
    top=[];best=-float('inf');route_scores=[]
    for route in row_permutations(lengths):
        if time.perf_counter()>deadline:raise TimeoutError('reading-order deadline')
        ordered=permute(values,route['indices']);affine=(a[:,None]*np.array(ordered)[None,:]+b[:,None])%29
        scores=array_scores(affine,lookup);route_best=float(scores.max());best=max(best,route_best)
        if keep:
            for idx in np.argsort(scores,kind='stable')[-keep:]:
                plain=affine[idx].tolist()
                top=top_unique(top+[{'score':float(scores[idx]),'plaintext_runes':to_runes(plain),'transliteration':transliterate(plain),
                    'recipe':{'family':'affine','a':int(a[idx]),'b':int(b[idx]),'route':route},'source_replay_verified':True}],keep=keep)
        for family,key,repeating in options:
            for cs,ks in SIGNS:
                out=selective_decode(ordered,key,model,repeating=repeating,starts=range(len(key)) if repeating else range(256),
                    cipher_sign=cs,key_sign=ks,deadline=deadline)
                route_best=max(route_best,out.score);best=max(best,out.score)
                if keep and (len(top)<keep or out.score>top[-1]['score']):
                    r={'family':family,'cipher_sign':cs,'key_sign':ks,'route':route}
                    if repeating:r['key_indices']=key
                    top=top_unique(top+[candidate(out,ordered,key,r,repeating)],keep=keep)
        route_scores.append({'route':route['name'],'score':route_best})
    return best,top,route_scores

def run(mode,page,batch,seconds,seed):
    tick=time.perf_counter();deadline=tick+seconds;model=external_model(4);lookup=dense_tables(model)
    audit={p['page_id']:p for p in load('sources/layout_audit.json')['pages']}
    pages={p['id']:p for p in load('transcriptions/pages.json')}
    result={'experiment':'E021-reading-order-'+mode,'status':'completed','parameters':{'mode':mode,'page':page,'batch':batch,'seconds':seconds,'seed':seed},'new_decryptions':[]}
    if mode=='controls':
        fixtures={f['id']:f for f in load('known_solutions/fixtures.json')};rows=[]
        f=fixtures['LP2-56_totient_primes'];values=to_indices(f['ciphertext_runes']);lengths=audit['LP2-56']['row_lengths']
        for route in row_permutations(lengths):
            stored=scatter(values,route['indices']);_,top,scores=search(stored,lengths,model,lookup,deadline)
            rows.append({'fixture':f['id'],'injected_route':route,'stored_ciphertext_indices':stored,'row_lengths':lengths,
                'exact':top[0]['plaintext_runes']==f['plaintext_runes'],'top':top,'route_scores':scores})
            print({'control':route['name'],'exact':rows[-1]['exact'],'seconds':time.perf_counter()-tick},flush=True)
        f=fixtures['LP2-57_direct'];values=to_indices(f['ciphertext_runes']);lengths=audit['LP2-57']['row_lengths']
        _,top,scores=search(values,lengths,model,lookup,deadline)
        rows.append({'fixture':f['id'],'injected_route':row_permutations(lengths)[0],'stored_ciphertext_indices':values,'row_lengths':lengths,
            'exact':top[0]['plaintext_runes']==f['plaintext_runes'],'top':top,'route_scores':scores})
        result.update(controls=rows,gate_passed=all(r['exact'] for r in rows))
    elif mode=='page':
        assert page in load('experiments/reading_order_plan.json')['unknown_pages']
        values=to_indices(pages[page]['runes']);lengths=audit[page]['row_lengths'];best,top,scores=search(values,lengths,model,lookup,deadline)
        result.update(page=page,ciphertext_runes=pages[page]['runes'],row_lengths=lengths,top=top,route_scores=scores)
    else:
        plan=load('experiments/reading_order_null_plan.json');assert page==plan['selected_page'] and 0<=batch<19
        values=to_indices(pages[page]['runes']);lengths=audit[page]['row_lengths'];rng=random.Random(seed+batch)
        sample,proposals=conditional_shuffle(values,rng,deadline=deadline)
        score,_,scores=search(sample,lengths,model,lookup,deadline,keep=0)
        result.update(page=page,row_lengths=lengths,ciphertext_indices=sample,proposals=proposals,score=score,route_scores=scores)
    result['wall_seconds']=time.perf_counter()-tick
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--mode',choices=['controls','page','null'],required=True)
    p.add_argument('--page',default='LP2-00');p.add_argument('--batch',type=int,default=0)
    p.add_argument('--seconds',type=float,default=180.0);p.add_argument('--seed',type=int,default=3301021);args=p.parse_args()
    deps=['experiments/reading_order_attack.py','experiments/reading_order_plan.json','sources/layout_audit.json','sources/layout_images_manifest.json',
        'src/liberprimus/layout.py','src/liberprimus/alphabet.py','src/liberprimus/ciphers.py','src/liberprimus/decoding.py',
        'experiments/external_language.py','experiments/external_model_plan.json','experiments/ngram_arrays.py',
        'experiments/attack_support.py','experiments/conditional_attack_null.py','known_solutions/fixtures.json','transcriptions/pages.json',
        'sources/emerson_manifest.json','data/raw/gutenberg/pg2944.txt']
    deps += [p['image_path'] for p in load('sources/layout_audit.json')['pages']]
    if args.mode=='null':deps.append('experiments/reading_order_null_plan.json')
    ident='E021-'+args.mode+('-'+args.page if args.mode!='controls' else '')+(f'-{args.batch:02}' if args.mode=='null' else '')
    registered(ident,{**vars(args),'numpy':np.__version__},deps,lambda:run(args.mode,args.page,args.batch,args.seconds,args.seed))
