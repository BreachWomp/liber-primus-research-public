"""Independent source, score, inverse mapping and final-neighborhood E083 audit."""
from collections import Counter
import itertools
import json
import random
import time
from verify_terminated_benchmark import Reference,ROOT,load,sha,to_indices
from liberprimus.alphabet import transliterate


def main():
    tick=time.perf_counter();v=Reference();plan=load('experiments/long_substitution_controls_plan.json')
    complete=load('checkpoints/phase30_controls_complete.json');assert len(complete['outputs'])==15
    assert sha(plan['benchmark_validation'])==plan['benchmark_validation_sha256']
    events=[json.loads(s) for s in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    by_output={e['output']:e for e in events if e['status']=='completed' and e['experiment'].startswith('E083-')}
    assert set(by_output)==set(complete['outputs'])
    fixtures={f['id']:f for f in load('known_solutions/fixtures.json')}
    layouts={r['fixture']:r['segment_ends'] for r in load('results/E026-boundary-audit-314198a84563.json')['controls']}
    counts=Counter();controls=[];nulls=[];entries=[]
    def check_score(p,ends,s):
        assert time.perf_counter()-tick<600
        assert abs(v.score(p,ends)-s)<1e-9;counts['independent_candidate_scores']+=1
    for path in complete['outputs']:
        e=by_output[path];assert sha(path)==e['output_sha256']
        for p,h in e['input_dependencies'].items():assert sha(p)==h,p
        r=load(path);assert r['parameters']==plan and r['training']==v.training
        i=r['index'];s=r['source']
        ch=('X','XI','XII')[i%3];block=i//3;minimum=(200,300,500,729)[block]
        source=[q for q in v.rows if q['chapter']==ch and sum(map(len,q['words']))>=760][2+block]
        assert (s['chapter'],s['paragraph'],s['minimum_runes'],s['eligible_paragraph_index'])==(ch,source['paragraph'],minimum,2+block)
        allp,allends=v.source_window(s,len(source['words']))
        end=next(x for x in allends if x>=minimum);truth=allp[:end];ends=[x for x in allends if x<=end]
        assert s['word_count']==len(ends)
        permutation=list(range(29));random.Random(3301083+i).shuffle(permutation)
        assert s['plaintext_indices']==truth and s['segment_ends']==ends and s['permutation_plain_to_cipher']==permutation
        original=[permutation[x] for x in truth];assert original==s['ciphertext_indices']
        cipher=original[:]
        if r['kind']=='null':
            assert i==0 and r['replicate'] in range(3)
            random.Random(3302083+r['replicate']).shuffle(cipher)
        else:assert r['kind']=='control' and r['replicate']==0
        assert cipher==r['ciphertext_indices'];counts['verified_source_inputs']+=1
        result=r['result'];assert 1<=len(result['restarts'])<=24
        assert len(result['restarts'])==len(result['warmup']['restarts'])
        for final,warm in zip(result['restarts'],result['warmup']['restarts']):
            assert final['restart']==warm['restart']
            key=final['mapping_cipher_to_plain'];assert sorted(key)==list(range(29))
            plain=[key[x] for x in cipher];assert plain==to_indices(final['plaintext_runes'])
            assert transliterate(plain)==final['transliteration'];check_score(plain,ends,final['score'])
            inverse=[key.index(x) for x in range(29)];assert [inverse[x] for x in plain]==cipher
            counts['reencryptions']+=1
            wkey=warm['mapping_cipher_to_plain'];assert sorted(wkey)==list(range(29))
            wp=[wkey[x] for x in cipher];assert wp==to_indices(warm['plaintext_runes'])
            assert abs(v.old.character_model.score(wp)-warm['score'])<1e-9
            assert final['score']>=v.score(wp,ends)-1e-9
            steps=final['word_accepted_swaps'];assert 0<=steps<=40
            assert final['word_evaluations']==1+406*(steps+int(steps<40))
            if steps<40:
                for a,b in itertools.combinations(range(29),2):
                    trial=key[:];trial[a],trial[b]=trial[b],trial[a]
                    q=[trial[x] for x in cipher]
                    assert v.score(q,ends)<=final['score']+1e-9
                    counts['independent_final_neighbor_scores']+=1
        top=max(result['restarts'],key=lambda x:x['score']);assert result['top']==top
        found=to_indices(top['plaintext_runes'])
        if r['kind']=='control':
            exact=found==truth;correct=sum(a==b for a,b in zip(found,truth))
            assert exact==r['exact'] and correct==r['correct_positions'];check_score(truth,ends,r['truth_score'])
            key=top['mapping_cipher_to_plain'];assert exact==all(key[permutation[x]]==x for x in set(truth))
            mismatches=[{'position':j,'truth':a,'found':b} for j,(a,b) in enumerate(zip(truth,found)) if a!=b]
            words=[];begin=0
            for end in ends:
                a,b=tuple(truth[begin:end]),tuple(found[begin:end])
                if a!=b:words.append({'rune_range':[begin,end],'truth':transliterate(a),'found':transliterate(b),
                    'truth_logword':v.word(a),'found_logword':v.word(b),'training_truth_count':v.words.get(a,0),'training_found_count':v.words.get(b,0)})
                begin=end
            controls.append({'index':i,'runes':len(truth),'exact':exact,'correct_positions':correct,
                'truth_score':r['truth_score'],'found_score':top['score'],'wrong_outscores_truth':not exact and top['score']>r['truth_score']+1e-12,
                'mismatches':mismatches,'changed_words':words,'output':path})
        else:nulls.append({'replicate':r['replicate'],'score':top['score'],'output':path})
        entries.append({'id':e['experiment'],'output':path,'sha256':sha(path),'fingerprint':e['fingerprint']})
        print({'verified':e['experiment'],'seconds':time.perf_counter()-tick},flush=True)
    assert [r['index'] for r in controls]==list(range(12)) and [r['replicate'] for r in nulls]==list(range(3))
    gate=all(r['exact'] for r in controls);assert gate==complete['full_gate_passed']
    assert sum(r['exact'] for r in controls)==complete['exact_controls']
    assert [r['score'] for r in nulls]==complete['null_scores']
    result={'full_gate_passed':gate,'controls':controls,'nulls':nulls,'validation':dict(counts),'entries':entries,
        'seconds':sum(e['wall_seconds'] for e in by_output.values()),'validation_seconds':time.perf_counter()-tick,
        'verifier_sha256':sha('scripts/verify_long_substitution_controls.py'),
        'limits':'Independent final scores/neighborhoods/source/inverse mappings; intermediate optimizer trajectory and initialization code not independently reimplemented.',
        'unknown_pages_searched':0,'new_decryptions':[]}
    (ROOT/'results/phase30_controls_validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print({k:v for k,v in result.items() if k not in ('controls','nulls','entries')})


if __name__=='__main__':main()
