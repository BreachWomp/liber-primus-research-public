"""Full fixed word/number/affine union under the frozen lexical-segment score."""
import argparse
import random
import time
from attack_support import load,to_indices,to_runes,key_catalog,stream_catalog,candidate,top_unique
from liberprimus.alphabet import transliterate
from liberprimus.word_model import word_selective_decode
from boundary_model_benchmark import make_model,AUDIT,DEPS
from conditional_attack_null import conditional_shuffle
from registry import registered

SIGNS=((1,-1),(1,1),(-1,-1),(-1,1))

def search(values,ends,model,deadline,keep=3):
    top=[];best=-float('inf');tasks=0;keys=key_catalog();assert len(keys)==381
    for a in range(1,29):
        if time.perf_counter()>deadline:raise TimeoutError('Affine word-score deadline')
        for b in range(29):
            plain=[(a*c+b)%29 for c in values];score=model.score(plain,ends);best=max(best,score)
            if keep and (len(top)<keep or score>top[-1]['score']):
                top=top_unique(top+[{'score':score,'plaintext_runes':to_runes(plain),'transliteration':transliterate(plain),
                    'recipe':{'family':'affine','a':a,'b':b},'replay_verified':True}],keep=keep)
    options=[('vigenere',k['indices'],True) for k in keys]+[(name,key,False) for name,key in stream_catalog(len(values)+256).items()]
    for family,key,repeat in options:
        for cs,ks in SIGNS:
            out=word_selective_decode(values,ends,key,model,repeating=repeat,
                starts=range(len(key)) if repeat else range(256),cipher_sign=cs,key_sign=ks,deadline=deadline)
            tasks+=1;best=max(best,out.score)
            if keep and (len(top)<keep or out.score>top[-1]['score']):
                recipe={'family':family,'cipher_sign':cs,'key_sign':ks}
                if repeat:recipe['key_indices']=key
                top=top_unique(top+[candidate(out,values,key,recipe,repeat)],keep=keep)
    assert tasks==1536
    return best,top,tasks

def run(args):
    tick=time.perf_counter();deadline=tick+180;model,_=make_model();audit=load(AUDIT)
    assert load('results/E027-boundary-model-1fc24b4da481.json')['gate_passed']
    layouts={p['page']:p['canonical']['segment_ends'] for p in audit['pages']}
    result={'experiment':'E028-boundary-selective','status':'completed','parameters':vars(args),'new_decryptions':[]}
    if args.mode=='controls':
        fixtures={f['id']:f for f in load('known_solutions/fixtures.json')}
        control_layouts={c['fixture']:c['segment_ends'] for c in audit['controls']};rows=[]
        for ident in load('experiments/boundary_attack_plan.json')['controls']:
            f=fixtures[ident];ends=control_layouts[ident]
            _,top,tasks=search(to_indices(f['ciphertext_runes']),ends,model,deadline)
            rows.append({'fixture':ident,'segment_ends':ends,'top':top,'key_sign_tasks':tasks,
                         'exact':top[0]['plaintext_runes']==f['plaintext_runes']})
            print({'control':ident,'exact':rows[-1]['exact'],'seconds':time.perf_counter()-tick},flush=True)
        result.update(controls=rows,gate_passed=all(r['exact'] for r in rows))
    else:
        pages={p['id']:p for p in load('transcriptions/pages.json')}
        assert args.page in audit['eligible_unknown_pages'] or args.page=='LP2-35'
        values=to_indices(pages[args.page]['runes']);ends=layouts[args.page]
        if args.mode=='page':
            _,top,tasks=search(values,ends,model,deadline)
            result.update(page=args.page,ciphertext_runes=pages[args.page]['runes'],segment_ends=ends,top=top,key_sign_tasks=tasks)
        else:
            selection=load('experiments/boundary_attack_selection.json')
            assert selection['selected_page']==args.page and 0<=args.replicate<19
            sample,proposals=conditional_shuffle(values,random.Random(3301028+args.replicate),deadline=deadline)
            best,_,tasks=search(sample,ends,model,deadline,keep=0)
            result.update(page=args.page,ciphertext_indices=sample,segment_ends=ends,score=best,
                          proposals=proposals,key_sign_tasks=tasks)
    result['wall_seconds']=time.perf_counter()-tick
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--mode',choices=['controls','page','null'],required=True)
    p.add_argument('--page',default='LP2-00');p.add_argument('--replicate',type=int,default=0);args=p.parse_args()
    deps=DEPS+['experiments/boundary_selective_attack.py','experiments/boundary_attack_plan.json',
        'experiments/conditional_attack_null.py','results/E027-boundary-model-1fc24b4da481.json','transcriptions/pages.json']
    from attack_support import ROOT
    deps+=sorted(path.relative_to(ROOT).as_posix() for path in (ROOT/'data/raw/relikd/pages').glob('solved_*.txt'))
    if args.mode=='null':deps.append('experiments/boundary_attack_selection.json')
    ident='E028-'+args.mode+('-'+args.page if args.mode!='controls' else '')+(f'-{args.replicate:02}' if args.mode=='null' else '')
    registered(ident,{**vars(args),'seconds':180,'seed':3301028},deps,lambda:run(args))
