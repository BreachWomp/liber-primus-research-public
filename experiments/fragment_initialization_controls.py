"""One bounded registered control/null per invocation, frozen E052 design."""
import argparse
import random
import time
import numpy as np
from attack_support import load, to_indices, to_runes
from periodic_key_controls import models
from long_key_controls import DEPS as PREVIOUS_DEPS
from fragment_initialization_search import search
from section_key_support import artificial_spans, page_null
from liberprimus.periodic_key import encrypt
from ngram_arrays import dense_tables
from registry import registered

PLAN='experiments/fragment_initialization_plan.json'
OLD='results/E049-long-key-controls-74c0828cc750.json'
DEPS=PREVIOUS_DEPS+[PLAN,OLD,'experiments/fragment_initialization_search.py',
    'experiments/fragment_initialization_controls.py','experiments/pooled_long_key_search.py',
    'experiments/phase_key_search.py','experiments/reset_key_search.py','scripts/run_fragment_initialization_phase.py']


def fresh(rows,index):
    rng=random.Random(3301052)
    for j in range(index+1):key=[rng.randrange(1,29) for _ in range((17,23,31)[j])]
    chapter=('X','XI','XII')[index]; plain=[]; ranges=[]; offset=0
    for row in rows:
        if row['chapter']!=chapter:continue
        piece=[x for word in row['words'] for x in word]; a=max(0,4000-offset); b=min(len(piece),5200-offset)
        if a<b:
            plain+=piece[a:b]
            ranges.append({'source_character_range':row['source_character_range'],'paragraph':row['paragraph'],
                           'paragraph_rune_range':[a,b]})
        offset+=len(piece)
        if offset>=5200:break
    assert len(plain)==1200
    sign=(1,-1,1)[index]; skips=[i for i,c in enumerate(plain) if c==0][::2]
    return {'chapter':chapter,'source_ranges':ranges,'chapter_rune_range':[4000,5200],
            'truth_runes':to_runes(plain),'injected_key':key,'injected_sign':sign,'injected_skips':skips,
            'ciphertext_indices':encrypt(plain,key,sign,skips),'page_spans':artificial_spans([197,263,311,429],chapter)}


def run(kind,index):
    tick=time.perf_counter(); deadline=tick+180; model,rows,training=models(); lookup=dense_tables(model)
    source=fresh(rows,index) if kind in ('fresh','null') else {k:v for k,v in load(OLD)['controls'][index].items() if k not in ('result','checks','exact')}
    if kind=='null':
        sample,proposals=page_null(source['ciphertext_indices'],source['page_spans'],3302052,deadline)
        source={'chapter':source['chapter'],'ciphertext_indices':sample,'page_spans':source['page_spans'],
                'page_proposals':proposals,'source_kind':'fresh','source_index':index}
    result=search(source['ciphertext_indices'],model,lookup,deadline)
    record={'experiment':f'E052-{kind}-{index}','kind':kind,'index':index,'parameters':load(PLAN),
            'training':training,'source':source,'result':result,'unknown_sections_searched':0,'new_decryptions':[]}
    if kind!='null':
        top=result['top'][0]
        record['checks']={'plaintext_exact':top['plaintext_runes']==source['truth_runes'],
                          'key_exact':top['key']==source['injected_key'] and top['sign']==source['injected_sign'],
                          'mask_exact':top['skip_positions']==source['injected_skips']}
        record['exact']=all(record['checks'].values())
        record['correct_runes']=sum(a==b for a,b in zip(to_indices(top['plaintext_runes']),to_indices(source['truth_runes'])))
    record['wall_seconds']=time.perf_counter()-tick
    print({k:record[k] for k in ('experiment','wall_seconds','checks','correct_runes') if k in record},flush=True)
    return record


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('kind',choices=['fresh','regression','null']);parser.add_argument('index',type=int,choices=range(3));args=parser.parse_args()
    if args.kind=='null' and args.index!=2:parser.error('Only fresh XII null preregistered')
    registered(f'E052-{args.kind}-{args.index}',load(PLAN)|{'kind':args.kind,'index':args.index,'numpy':np.__version__},DEPS,lambda:run(args.kind,args.index))
