"""Source-preserving long-stream controls before any unknown section scan."""
import random
import time
import numpy as np
from attack_support import load,to_indices,to_runes,digest
from periodic_key_controls import models
from joint_skip_external import DEPS as JOINT_DEPS
from section_key_support import join_pages,artificial_spans,page_null
from section_key_search import search
from liberprimus.periodic_key import encrypt,decrypt
from ngram_arrays import dense_tables
from registry import registered

PLAN='experiments/section_key_plan.json'
HISTORICAL='results/E040-joint-key-skip-controls-17a783e45d76.json'


def external_streams(external):
    results=[]
    for chapter,limit in (('X',3316),('XI',1200),('XII',1200)):
        values=[];ranges=[]
        for row in external:
            if row['chapter']!=chapter:continue
            piece=[x for w in row['words'] for x in w];take=min(limit-len(values),len(piece))
            if take:
                ranges.append({'source_character_range':row['source_character_range'],'paragraph':row['paragraph'],
                               'runes_consumed':take});values.extend(piece[:take])
            if len(values)==limit:break
        assert len(values)==limit
        results.append((chapter,values,ranges))
    return results


def run():
    tick=time.perf_counter();deadline=tick+180;model,external,training=models();lookup=dense_tables(model)
    fixtures={f['id']:f for f in load('known_solutions/fixtures.json')};reused=[]
    history=load(HISTORICAL);assert history['gate_passed']
    for record in history['controls']:
        f=fixtures[record['fixture']];cipher,spans=join_pages(f['page_ids'])
        assert cipher==to_indices(f['ciphertext_runes'])==record['ciphertext_indices']
        top=record['result']['top'][0]
        assert to_runes(decrypt(cipher,top['key'],top['sign'],top['skip_positions']))==f['plaintext_runes']
        reused.append({'fixture':f['id'],'page_spans':spans,'source_output':HISTORICAL,
                       'source_sha256':digest(HISTORICAL),'search_rerun':False,'exact':True})
    group=next(s for s in load('experiments/section_plan.json')['sections'] if s['id']=='LP2-40_55')
    _,template=join_pages(group['page_ids']);lengths=[r['runes'] for r in template]
    rng=random.Random(3301043);controls=[]
    for j,(chapter,plain,ranges) in enumerate(external_streams(external)):
        key=[rng.randrange(1,29) for _ in range((5,8,13)[j])];sign=(1,-1,1)[j]
        skips=[i for i,x in enumerate(plain) if x==0][::2]
        cipher=encrypt(plain,key,sign,skips)
        spans=artificial_spans(lengths if j==0 else [197,263,311,429],chapter)
        assert spans[-1]['end']==len(cipher)
        result=search(cipher,model,lookup,deadline);top=result['top'][0]
        checks={'plaintext_exact':top['plaintext_runes']==to_runes(plain),
                'key_exact':top['key']==key and top['sign']==sign,'mask_exact':top['skip_positions']==skips}
        controls.append({'chapter':chapter,'source_ranges':ranges,'truth_runes':to_runes(plain),
            'injected_key':key,'injected_sign':sign,'injected_skips':skips,'ciphertext_indices':cipher,
            'page_spans':spans,'result':result,'checks':checks,'exact':all(checks.values())})
        print({'chapter':chapter,'runes':len(cipher),'checks':checks,'seconds':time.perf_counter()-tick},flush=True)
    source=controls[1];sample,proposals=page_null(source['ciphertext_indices'],source['page_spans'],3302043,deadline)
    null={'control_index':1,'ciphertext_indices':sample,'page_spans':source['page_spans'],
          'page_proposals':proposals,'result':search(sample,model,lookup,deadline)}
    return {'experiment':'E043-section-key-controls','parameters':load(PLAN),'training':training,
        'reused_historical':reused,'controls':controls,'nulls':[null],
        'gate_passed':all(r['exact'] for r in controls+reused),'unknown_sections_searched':0,
        'wall_seconds':time.perf_counter()-tick,'new_decryptions':[]}


DEPS=JOINT_DEPS+[PLAN,'experiments/section_key_controls.py','experiments/section_key_search.py',
                'experiments/section_key_support.py','experiments/section_plan.json','transcriptions/pages.json']
if __name__=='__main__':registered('E043-section-key-controls',load(PLAN)|{'numpy':np.__version__},DEPS,run)
