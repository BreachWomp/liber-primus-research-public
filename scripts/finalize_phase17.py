"""Independent source replay, schedule optimum checks and joint-search checkpoint."""
from collections import Counter
from datetime import datetime,timezone
import hashlib
import json
import math
from pathlib import Path
import random
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'experiments'))
from attack_support import to_indices,to_runes
from heldout_language import corpus,tokenize
from liberprimus.decoding import BackoffModel

def load(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))
def save(path,value):(ROOT/path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def canonical(key):
    for n in range(1,len(key)+1):
        if len(key)%n==0 and key[:n]*(len(key)//n)==key:
            key=key[:n];break
    return min(key[i:]+key[:i] for i in range(len(key)))


def scalar_replay(cipher,key,sign,skips):
    assert sign in (-1,1) and key and all(type(x) is int and 0<=x<29 for x in key)
    assert skips==sorted(set(skips)) and all(0<=i<len(cipher) and cipher[i]==0 for i in skips)
    plain=[];encoded=[];cursor=0
    for i,c in enumerate(cipher):
        if i in skips:plain.append(0);encoded.append(0)
        else:
            p=(sign*c+key[cursor%len(key)])%29;plain.append(p)
            encoded.append(sign*(p-key[cursor%len(key)])%29);cursor+=1
    assert encoded==cipher
    return plain


def schedule_optimum(cipher,key,sign,model):
    """Independent score-only Viterbi, no stored path and no search-module call."""
    states={(phase,()):0.0 for phase in range(len(key))}
    for c in cipher:
        following={}
        for (phase,h),old in states.items():
            options=[((sign*c+key[phase])%29,(phase+1)%len(key))]
            if c==0:options.append((0,phase))
            for symbol,nxt in options:
                index=(nxt,(h+(symbol,))[-3:]);value=old+model.logp(h,symbol)
                if value>following.get(index,-float('inf')):following[index]=value
        states=following
    return max(states.values())/len(cipher)


def main():
    if (ROOT/'checkpoints/phase18_complete.json').exists():raise RuntimeError('Newer checkpoint exists')
    tests=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=60)
    output=tests.stdout+tests.stderr;(ROOT/'results/validation_phase17.txt').write_text(output,encoding='utf-8')
    if tests.returncode:raise RuntimeError(output)
    count=int(re.search(r'Ran (\d+) tests',output)[1]);now=datetime.now(timezone.utc).isoformat()
    events=[json.loads(line) for line in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    done=[e for e in events if e['status']=='completed'];latest={e['experiment']:e for e in done}
    phase={k:e for k,e in latest.items() if k.startswith(('E049-','E050-','E051-'))};assert len(phase)==3
    for event in phase.values():
        assert sha(event['output'])==event['output_sha256'] and event['wall_seconds']<180
        for path,digest in event['input_dependencies'].items():assert sha(path)==digest,path
    data={k:load(e['output']) for k,e in phase.items()};control=data['E049-long-key-controls'];assert not control['gate_passed']
    rows=corpus();raw=(ROOT/'data/raw/gutenberg/pg2944.txt').read_bytes().decode('utf-8-sig')
    training=[r for r in rows if r['chapter'] in ('I','III','IV','V','VI','VII','VIII','IX')]
    ranges=[r['source_character_range'] for r in training]
    model=BackoffModel([[x for w in tokenize(raw[a:b])[0] for x in w] for a,b in ranges],order=4,alpha=.5,strength=5)
    assert ranges==control['training']['training_source_ranges']
    verified=0;optima=0;seeds_checked=0;traces_checked=0;pool_records=0
    def verify_row(cipher,row):
        nonlocal verified
        key=row['key'];assert 1<=len(key)<=32
        assert len(canonical(key))==len(key)
        plain=scalar_replay(cipher,key,row['sign'],row['skip_positions'])
        language=model.score(plain)
        assert abs(language-row['language_score'])<1e-9
        score=language-(len(key)*math.log(29)+cipher.count(0)*math.log(2))/len(cipher)
        assert abs(score-row['score'])<1e-9
        assert 0<=row['selected_phase']<row['input_period']<=32
        assert 1<=row['dp_max_states']<=8*row['input_period']
        if 'plaintext_runes' in row:assert to_runes(plain)==row['plaintext_runes']
        verified+=1
    def verify_pool(cipher,result,trace):
        nonlocal pool_records
        intervals=[];begin=0
        for i,c in enumerate(cipher+[0]):
            if c==0:
                if i-begin>=16:intervals.append((begin,i))
                begin=i+1
        intervals=sorted(intervals,key=lambda ab:(-(ab[1]-ab[0]),ab[0]))[:12]
        ranges=[[a,min(b,a+256)] for a,b in intervals]
        assert ranges==result['pool_source_ranges'];pool=[];spans=[]
        for j,(a,b) in enumerate(ranges):
            start=len(pool);pool+=cipher[a:b]
            spans.append({'page_id':f'fragment-{j:02}','start':start,'end':len(pool),'runes':b-a,'zero_rune_page':False})
        assert pool==result['pool_ciphertext'] and spans==result['pool_spans'] and 0 not in pool
        assert len(trace)==3
        for row in trace:
            key=row['key'];phases=row['page_phases'];assert row['skip_positions']==[]
            assert 1<=len(key)<=32 and len(canonical(key))==len(key)
            assert len(phases)==len(spans) and phases[0]==0 and all(0<=p<len(key) for p in phases)
            total=0;optimum=0
            for span,offset in zip(spans,phases):
                piece=pool[span['start']:span['end']];oriented=key[offset:]+key[:offset]
                plain=scalar_replay(piece,oriented,row['sign'],[])
                total+=model.score(plain)*len(piece)
                optimum+=schedule_optimum(piece,key,row['sign'],model)*len(piece)
            phase_cost=(len(spans)-1)*math.log(len(key))
            assert abs(total/len(pool)-row['language_score'])<1e-9 and abs(optimum-total)<1e-7
            assert abs(row['phase_cost']-phase_cost)<1e-12
            assert abs(row['score']-(total-len(key)*math.log(29)-phase_cost)/len(pool))<1e-9
            assert row['input_period']==len(key) and row['dp_max_states']<=8*len(key)
            pool_records+=1
        assert all(y['score']>=x['score']-1e-9 for x,y in zip(trace,trace[1:]))

    def verify_result(cipher,result):
        nonlocal optima,seeds_checked,traces_checked
        intervals=[];start=0
        for i,c in enumerate(cipher+[0]):
            if c==0:
                if i-start>=64:intervals.append((start,i))
                start=i+1
        intervals=sorted(intervals,key=lambda ab:(-(ab[1]-ab[0]),ab[0]))[:3]
        expected=([('whole',[0,len(cipher)])] if len(cipher)<=1024 else [('prefix',[0,1024]),('suffix',[len(cipher)-1024,len(cipher)])])+[('non_F_run',[a,min(b,a+512)]) for a,b in intervals]
        assert [(r['kind'],r['range']) for r in result['source_stats']]==expected
        assert len(result['restarts'])==min(12,result['unique_seed_keys'])
        keys_seen=set();seed_scores=[];finals=[]
        for restart in result['restarts']:
            initial=restart['initial'];a,b=initial['source_range'];source=cipher[a:b]
            assert 17<=initial['nominal_period']<=32
            assert (initial['source_kind'],[a,b]) in expected
            key=initial['source_key'];policy=initial['source_policy']
            skips=[i for i,x in enumerate(source) if x==0] if policy=='all_F' else []
            if initial['source_kind']=='non_F_run':assert 0 not in source and policy=='oracle'
            plain=scalar_replay(source,key,initial['sign'],skips)
            assert abs(model.score(plain)-len(key)*math.log(29)/len(source)-initial['seed_score'])<1e-9
            assert canonical(key)==initial['key']
            ident=(initial['sign'],tuple(initial['key']));assert ident not in keys_seen;keys_seen.add(ident)
            seed_scores.append(initial['seed_score']);seeds_checked+=1
            trace=restart['trace'];assert 2<=len(trace)<=4
            if 'pool_trace' in restart:
                verify_pool(cipher,result,restart['pool_trace'])
                assert trace[0]['input_period']==len(restart['pool_trace'][-1]['key'])
            else:assert trace[0]['input_period']==len(initial['key'])
            for row in trace:verify_row(cipher,row)
            assert all(y['score']>=x['score']-1e-9 for x,y in zip(trace,trace[1:]))
            for field,value in trace[-1].items():assert restart['final'][field]==value
            verify_row(cipher,restart['final']);finals.append(restart['final']);traces_checked+=1
        assert seed_scores==sorted(seed_scores,reverse=True)
        ranked=[];seen=set()
        for row in sorted(finals,key=lambda r:r['score'],reverse=True):
            if row['plaintext_runes'] not in seen:
                ranked.append(row);seen.add(row['plaintext_runes'])
        assert result['top']==ranked[:3]
        winner=result['top'][0]
        assert abs(schedule_optimum(cipher,winner['key'],winner['sign'],model)-winner['language_score'])<1e-9
        optima+=1
    catalog={p['id']:p for p in load('transcriptions/pages.json')}
    def source_stream(ids,spans):
        assert [s['page_id'] for s in spans]==ids
        out=[]
        for ident,span in zip(ids,spans):
            piece=to_indices(catalog[ident]['runes'])
            assert span=={'page_id':ident,'start':len(out),'end':len(out)+len(piece),
                'runes':len(piece),'source_refs':catalog[ident]['source_refs'],'zero_rune_page':not bool(piece)}
            out+=piece
        return out
    assert len(control['controls'])==3
    rng=random.Random(3301049)
    for j,record in enumerate(control['controls']):
        chapter=('X','XI','XII')[j];limit=(3316,1200,1200)[j];plain=[];source_ranges=[]
        for src in rows:
            if src['chapter']!=chapter:continue
            a,b=src['source_character_range'];assert all(b<=x or a>=y for x,y in ranges)
            piece=[x for w in tokenize(raw[a:b])[0] for x in w];take=min(limit-len(plain),len(piece))
            if take:
                source_ranges.append({'source_character_range':[a,b],'paragraph':src['paragraph'],'runes_consumed':take})
                plain+=piece[:take]
            if len(plain)==limit:break
        assert source_ranges==record['source_ranges'] and to_runes(plain)==record['truth_runes']
        key=[rng.randrange(1,29) for _ in range((17,23,31)[j])];sign=(1,-1,1)[j]
        skips=[i for i,x in enumerate(plain) if x==0][::2];cipher=[];cursor=0
        for i,p in enumerate(plain):
            if i in skips:cipher.append(0)
            else:cipher.append(sign*(p-key[cursor%len(key)])%29);cursor+=1
        assert key==record['injected_key'] and sign==record['injected_sign'] and skips==record['injected_skips']
        assert cipher==record['ciphertext_indices']
        lengths=([len(to_indices(catalog[f'LP2-{i:02}']['runes'])) for i in range(40,56)] if j==0 else [197,263,311,429])
        offset=0
        for k,(span,length) in enumerate(zip(record['page_spans'],lengths)):
            assert span=={'page_id':f'external-{chapter}-{k:02}','start':offset,'end':offset+length,'runes':length,'zero_rune_page':length==0}
            offset+=length
        assert len(record['page_spans'])==len(lengths) and offset==limit
        verify_result(cipher,record['result']);top=record['result']['top'][0]
        expected_checks={'plaintext_exact':top['plaintext_runes']==record['truth_runes'],
            'key_exact':top['key']==key and top['sign']==sign,'mask_exact':top['skip_positions']==skips}
        assert record['checks']==expected_checks and record['exact']==all(expected_checks.values())
    doublets=lambda v:sum(a==b for a,b in zip(v,v[1:]))
    def verify_null(source,row,seed):
        out=[];records=[]
        for j,span in enumerate(row['page_spans']):
            assert span['start']==len(out);piece=source[span['start']:span['end']]
            if len(piece)<=2:sample=piece[:];proposal=0
            else:
                rng=random.Random(seed+j)
                for proposal in range(1,100001):
                    interior=piece[1:-1];rng.shuffle(interior);sample=piece[:1]+interior+piece[-1:]
                    if doublets(sample)==doublets(piece):break
                else:raise AssertionError('Null replay exhausted')
            assert Counter(sample)==Counter(piece) and doublets(sample)==doublets(piece)
            assert not piece or (sample[0],sample[-1])==(piece[0],piece[-1])
            out+=sample;records.append({'page_id':span['page_id'],'seed':seed+j,'proposals':proposal})
        assert out==row['ciphertext_indices'] and Counter(out)==Counter(source) and doublets(out)==doublets(source)
        assert records==row['page_proposals'];verify_result(out,row['result'])
    assert len(control['nulls'])==1
    assert control['nulls'][0]['page_spans']==control['controls'][1]['page_spans']
    verify_null(control['controls'][1]['ciphertext_indices'],control['nulls'][0],3302049)
    diagnosis=data['E050-long-key-diagnostic'];assert diagnosis['oracle_diagnosis_only']
    assert diagnosis['training']==control['training'] and len(diagnosis['controls'])==3
    for src,d in zip(control['controls'],diagnosis['controls']):
        cipher=src['ciphertext_indices'];truth=to_indices(src['truth_runes']);key=src['injected_key'];top=src['result']['top'][0]
        truth_language=model.score(truth);truth_score=truth_language-(len(key)*math.log(29)+cipher.count(0)*math.log(2))/len(cipher)
        assert abs(d['truth_language_score']-truth_language)<1e-12 and abs(d['truth_score']-truth_score)<1e-12
        assert d['found_score']==top['score'] and abs(d['truth_minus_found']-(truth_score-top['score']))<1e-12
        assert d['correct_runes']==sum(a==b for a,b in zip(truth,to_indices(top['plaintext_runes'])))
        target=(src['injected_sign'],canonical(key))
        for name,field in (('true_initial_seed_indices','initial'),('true_final_key_indices','final')):
            expected=[i for i,r in enumerate(src['result']['restarts']) if (r[field]['sign'],canonical(r[field]['key']))==target]
            assert d[name]==expected
        if not src['exact']:
            known=d['known_key_oracle'];verify_row(cipher,known['result'])
            assert known['mask_exact']==(known['result']['skip_positions']==src['injected_skips'])
            assert known['key_exact']==(known['result']['key']==key)
            assert abs(schedule_optimum(cipher,key,src['injected_sign'],model)-known['result']['language_score'])<1e-9
            oracle=d['known_period_mask_oracle'];prefix=cipher[:1024];skips=[i for i in src['injected_skips'] if i<1024]
            assert oracle['period']==len(key) and oracle['mask']==skips and oracle['range']==[0,1024]
            for row in oracle['result']['families']+oracle['result']['top']:
                plain=scalar_replay(prefix,row['key'],row['sign'],skips);language=model.score(plain)
                assert abs(language-row['language_score'])<1e-9
                assert abs(row['score']-(language-len(row['key'])*math.log(29)/1024))<1e-9
                if 'plaintext_runes' in row:assert to_runes(plain)==row['plaintext_runes']
            winner=oracle['result']['top'][0]
            assert oracle['key_exact']==(winner['key']==key and winner['sign']==src['injected_sign'])
            assert oracle['plaintext_exact']==(winner['plaintext_runes']==src['truth_runes'][:1024])
    repair=data['E051-pooled-long-key-diagnostic'];target=control['controls'][2]
    assert repair['ciphertext_indices']==target['ciphertext_indices'] and repair['page_spans']==target['page_spans']
    assert repair['adaptive_control_probe'] and not repair['gate_for_unknown'] and repair['training']==control['training']
    verify_result(repair['ciphertext_indices'],repair['result']);best=repair['result']['top'][0]
    checks={'plaintext_exact':best['plaintext_runes']==target['truth_runes'],
        'key_exact':best['key']==target['injected_key'] and best['sign']==target['injected_sign'],
        'mask_exact':best['skip_positions']==target['injected_skips']}
    assert checks==repair['checks'] and repair['exact']==all(checks.values())
    assert repair['null']['page_spans']==target['page_spans']
    verify_null(target['ciphertext_indices'],repair['null'],3302051)
    assert all(r['unknown_sections_searched']==0 and r['new_decryptions']==[] for r in (control,diagnosis,repair))
    seconds=sum(e['wall_seconds'] for e in phase.values());assert seconds<900
    summary={'created_at':now,'unknown_sections':0,'control_gate_passed':False,
        'original_controls':[{'chapter':r['chapter'],'key_length':len(r['injected_key']),'runes':len(r['ciphertext_indices']),
            'exact':r['exact'],'checks':r['checks']} for r in control['controls']],
        'diagnosis':diagnosis['controls'],'adaptive_repair_exact':repair['exact'],
        'repair_correct_runes':sum(a==b for a,b in zip(best['plaintext_runes'],target['truth_runes'])),
        'repair_score':best['score'],'repair_null_score':repair['null']['result']['top'][0]['score'],
        'pool_fragments':len(repair['result']['pool_spans']),'pool_runes':len(repair['result']['pool_ciphertext']),
        'candidate_records_recomputed':verified,'seed_records_recomputed':seeds_checked,
        'restart_traces_checked':traces_checked,'pool_records_recomputed':pool_records,
        'independent_schedule_optima':optima,'tests_passed':count,'successful_tasks':len(phase),
        'seconds':seconds,'new_decryptions':[]}
    # Keep diagnostic search arrays in their source artifact, not duplicated in summary.
    for row in summary['diagnosis']:
        for name in ('known_key_oracle','known_period_mask_oracle'):
            if name in row:row[name]={k:v for k,v in row[name].items() if k not in ('result','mask')}
    save('results/phase17_summary.json',summary);finish(summary,phase,done,now)


def finish(s,phase,done,now):
    status='seventeenth_batch_controls_failed_search_bottleneck'
    entries=[{'id':k,'fingerprint':e['fingerprint'],'output':e['output'],'sha256':e['output_sha256']} for k,e in phase.items()]
    queue=[{'id':'H039','priority':1,'task':'Develop phase-aware pooled-fragment initialization for long keys using several deterministic starts and a preregistered unigram-to-fourgram schedule. E051 showed that refining the same12 weak seeds does not suffice. Test on fresh source-excluded controls plus all old regressions before any unknown scan; do not tune to the failed31-key plaintext.'},
        {'id':'H031','priority':2,'task':'General substitution remains deferred pending independently justified scoring repair.'},
        {'id':'H023','priority':3,'task':'Delay3 feedback remains deferred pending feasible calibrated reduction.'}]
    state=load('research_state.json');known={e['fingerprint'] for e in state['completed_experiments']}
    state['completed_experiments'] += [e for e in entries if e['fingerprint'] not in known]
    state.update(status=status,updated_at=now,latest_report='reports/attack_phase17_report.md',
        next_experiments=[q['id'] for q in queue],promising_candidates=[],
        validation={'tests_passed':s['tests_passed'],'path':'results/validation_phase17.txt',
            'phase17_candidate_records_recomputed':s['candidate_records_recomputed'],
            'phase17_pool_records_recomputed':s['pool_records_recomputed'],
            'phase17_independent_schedule_optima':s['independent_schedule_optima']},
        session_budget={'phase':'seventeenth bounded long-key controls and repair diagnosis','max_compute_wall_seconds':900,
            'max_experiment_wall_seconds':180,'workers':1,'background_jobs':False},
        scoring_gate='E04917/23-key controls exact;31-key control failed. E050 oracle diagnostics identify search failure, not objective rejection. E051 adaptive pooled-fragment repair remains unvalidated.',
        notes=['No previously unknown plaintext confirmed.','Direct cryptanalysis only; no unsupported claim audits.',
            'No unknown ciphertexts searched in phase17 because long-key control gate failed.',
            'True31-key plaintext scores higher than failed search result; explicit oracle runs are diagnostic only.',
            'E051 is an adaptive probe on a known failed control, not independent validation.',
            'All source bytes and historical results retained. No research process remains running.'])
    state['resources'].update(recorded_successful_experiment_runs=len(done),
        recorded_experiment_subprocess_wall_seconds=sum(e['wall_seconds'] for e in done),phase17_wall_seconds=s['seconds'])
    message='E049 nominal17..32 joint key/F search:17 and23 exact,31 failed59/1200 despite higher truth score; E051 pooled-fragment seed refinement also fails. No unknown scan.'
    if message not in state['failed_approaches']:state['failed_approaches'].append(message)
    save('research_state.json',state)
    hypotheses=load('hypotheses.json');h=next(h for h in hypotheses['hypotheses'] if h['id']=='H038')
    h.update(status='control_gate_failed_search_bottleneck',experiments=['E049','E050','E051'],result=s,
        limits='No evidence against long-key encryption from a failed heuristic control. Oracle diagnoses do not count as blind recovery. No unknown ciphertext tested.')
    hypotheses['hypotheses']=[r for r in hypotheses['hypotheses'] if r['id']!='H039']+[
        {'id':'H039','claim':'Long-key initialization may improve by jointly inferring phases across F-free fragments before full-stream schedule refinement.',
         'status':'queued','basis':'E04931-key initialization misses truth; supplied key or mask/period permits exact recovery. All12 retained seeds originate in one65-rune fragment. E051 pooling those same seeds still fails, so new initialization requires separate calibration.',
         'mechanism':'Several deterministic initializations per nominal period; pool fragment unigram likelihood with unknown phases, then higher-order refinement, then full-stream exact F schedules.',
         'parameters':'Preregister starts, phase optimization, score schedule, caps and fresh source ranges before execution. No truth-dependent key or mask in candidate search.',
         'success_criterion':'Fresh source-excluded controls and all prior regressions recover exact keys,text and masks; only then unknown attack with matched nulls.',
         'rejection_criterion':'Further failed controls or uncontrolled cost blocks unknown escalation.',
         'limits':'Algorithmic hypothesis prompted by a known control failure, not independent evidence of the actual LP cipher.'}]
    hypotheses.update(status=status,updated_at=now,next_queue=queue);save('hypotheses.json',hypotheses)
    d=s['diagnosis'][2];table='\n'.join(f'| {r["chapter"]} | {r["key_length"]} | {r["runes"]} | {"exakt" if r["exact"] else "fehlgeschlagen"} |' for r in s['original_controls'])
    report=f'''# Siebzehnte Forschungsserie: Lange Schlüssel und ein nachgewiesener Suchengpass

Stand (UTC): {now}. **Keine neue Entschlüsselung bestätigt.**
Die neue Suche wurde wegen eines verfehlten Kontrollkriteriums nicht auf
unbekannte Liber-Primus-Seiten angewandt.

## E049: Schlüssel mit nominell 17–32 Runen

Regel unverändert: `P_i=s*C_i+K_j mod29`, s=±1, selektive Chiffren-F-Kopie
ohne Cursorverbrauch. Schlüssel und Sprachkontext laufen durch den gesamten
Text. Der Kandidatenscore bleibt `mean(logp4)-(m*ln29+F_count*ln2)/N`.
Nominelle Perioden 17–32; keine neue nominelle Suche über 1–16.
Kürzere primitive Teiler können bei der Optimierung entstehen.

Startfenster: ganzer Text bis1024 Runen, sonst erste/letzte1024, dazu drei
längste F-freie Abschnitte ab64 Runen, begrenzt auf512. Vier E038-Starts
pro Familie, zwölf zyklisch deduplizierte Schlüsselstarts. Exakte F-Suche
über alle Phasen bei festem Schlüssel; bis zu drei Runden aus sechs
Koordinatendurchläufen und erneuter Zeitplanoptimierung.
Eingaben512–4096 Runen, maximal32 Schlüsselstellen und256 DP-Zustände.

| Kapitel | Schlüssellänge | Runen | Text, Schlüssel und F-Maske |
|---|---:|---:|---|
{table}

Kontrolltexte und Quellbereiche stammen aus E043; neue nichtnullige
Zufallsschlüssel, Vorzeichen+1,−1,+1; jede zweite Klartext-F wird kopiert.
Training weiterhin Emerson I,III–IX, Kontrollen X,XI,XII, disjunkte
Originalbereiche. Bereits bekannte Kapitel, keine historisch blinde Prüfung.
Ein XI-Nulltext durchläuft den vollständigen Solver mit erhaltenen
seitenweisen Runenhäufigkeiten, Randrunen und gleichen Nachbarpaaren.

## E050: Ursache unterscheiden

Bei der 31-Runen-Kontrolle sind nur **{d['correct_runes']}/1200 Runen** richtig.
Der tatsächliche Klartext hat Score **{d['truth_score']:.6f}**, der gefundene
Kandidat **{d['found_score']:.6f}**: ein Unterschied von
**{d['truth_minus_found']:.6f} zugunsten des richtigen Textes**.
Der echte Schlüssel ist weder unter den zwölf Startschlüsseln noch unter
deren Endschlüsseln. Alle zwölf Starts stammen aus demselben nur65 Runen
langen F-freien Abschnitt. Bei den erfolgreichen17/23-Kontrollen entsteht
der genaue Schlüssel ebenfalls erst durch die nachfolgenden Verbesserungen.

Zwei ausdrücklich mit Lösungswissen unterstützte Diagnosen:

* Vorgegebener Schlüssel samt Vorzeichen: exakte F-Maske wiedergefunden.
* Vorgegebene Länge31 und richtige F-Maske der ersten1024 Runen:
  Schlüsselwerte und Präfixtext exakt gefunden.

Diese Oracle-Versuche sind **keine eigenständige Entschlüsselung**.
Sie zeigen, dass die richtige Ausgabe besser bewertet wird und die
Teiloptimierer mit den genannten Hilfen funktionieren. Der blinde
Suchlauf findet den Schlüssel dennoch nicht; daraus folgt kein Ausschluss
langer Schlüssel als tatsächlicher Chiffre.

## E051: Begrenzter Reparaturversuch

Vor dem Lauf separat registrierte, ausdrücklich adaptive Änderung:
zwölf längste F-freie Fragmente ab16 Runen, je maximal256, gemeinsam auswerten.
Jedes Fragment darf bei einer anderen Schlüsselphase beginnen. Die bisherigen
zwölf Starts werden durch zwei Runden gemeinsamer Koordinaten- und exakter
Phasenoptimierung verbessert, danach erfolgt die bisherige vollständige
F-Zeitplansuche auf dem Originaltext. Keine korrekten Schlüsselwerte oder
Masken an den Solver. Auswahl und Parameter wurden aber nach Kenntnis des
E049-Fehlers festgelegt; das ist keine unabhängige Kontrollprüfung.

{s['pool_fragments']} Fragmente, zusammen{s['pool_runes']} Runen.
Reparatur exakt: **{s['adaptive_repair_exact']}**;
{s['repair_correct_runes']}/1200 richtige Runen, Score{s['repair_score']:.6f}.
Ein passender Nulltext mit vollständiger Neuoptimierung hat
Score{s['repair_null_score']:.6f}. Diese einzelne Diagnose erhält keinen p-Wert.
Der Reparaturversuch erfüllt die Voraussetzung für unbekannte Seiten nicht.

## Validierung und nächste Richtung

{s['tests_passed']} Tests bestanden. {s['candidate_records_recomputed']} Zwischen-/Endkandidaten,
{s['seed_records_recomputed']} Starts und {s['restart_traces_checked']} Suchverläufe skalar
nachgerechnet und rückverschlüsselt. Zusätzlich{s['pool_records_recomputed']}
Fragmentzustände einschließlich Phasen, Bewertungen und bedingten Maxima
geprüft; {s['independent_schedule_optima']} vollständige Suchausgaben mit separatem
Score-Viterbi bestätigt. Kontrolltexte, neue Schlüssel und beide Nulltexte
aus Originalbereichen beziehungsweise Seeds reproduziert. Alle Ergebnis-
und Abhängigkeitshashes stimmen.

{s['successful_tasks']} Experimente, {s['seconds']:.3f} Sekunden erfolgreiche Experimentzeit;
je maximal180, Phasenbudget900, ein Worker. Keine Quellbytes verändert,
keine alten Ergebnisse überschrieben, keine Hintergrundprozesse.

Nächster Ansatz ist eine andere Initialisierung der langen Schlüssel:
mehrere deterministische Starts pro Periode, zunächst gemeinsame
Einzelrunen-Häufigkeiten und unbekannte Fragmentphasen, danach Viergramme.
Das muss an frischen Kontrollbereichen und den bisherigen Regressionen
bestehen. Weitere Anpassung nur an denselben fehlgeschlagenen Klartext
wäre kein belastbarer Fortschritt.

[E049-Plan](../experiments/long_key_plan.json),
[Oracle-Diagnoseplan](../experiments/long_key_diagnostic_plan.json),
[Reparaturplan](../experiments/pooled_long_key_plan.json),
[Messübersicht](../results/phase17_summary.json),
[Checkpoint](../checkpoints/phase17_complete.json).
'''
    for a,b in {'bis1024':'bis 1.024','erste/letzte1024':'erste/letzte 1.024','ab64':'ab 64','auf512':'auf 512',
        'Eingaben512':'Eingaben 512','maximal32':'maximal 32','und256':'und 256','Vorzeichen+1,−1,+1':'Vorzeichen +1, −1, +1',
        'I,III–IX':'I, III–IX','X,XI,XII':'X, XI, XII','nur65':'nur 65','erfolgreichen17/23':'erfolgreichen 17/23',
        'Länge31':'Länge 31','ersten1024':'ersten 1.024','ab16':'ab 16','maximal256':'maximal 256',
        'zusammen'+str(s['pool_runes']):'zusammen '+str(s['pool_runes']),'Score'+f'{s["repair_score"]:.6f}':'Score '+f'{s["repair_score"]:.6f}',
        'Score'+f'{s["repair_null_score"]:.6f}':'Score '+f'{s["repair_null_score"]:.6f}',
        'Zusätzlich'+str(s['pool_records_recomputed']):'Zusätzlich '+str(s['pool_records_recomputed']),
        'maximal180':'maximal 180','Phasenbudget900':'Phasenbudget 900'}.items():report=report.replace(a,b)
    (ROOT/'reports/attack_phase17_report.md').write_text(report,encoding='utf-8')
    save('checkpoints/phase17_complete.json',{'created_at':now,'status':status,'summary':'results/phase17_summary.json',
        'summary_sha256':sha('results/phase17_summary.json'),'experiments':entries})
    print(json.dumps({k:v for k,v in s.items() if k not in ('diagnosis',)},ensure_ascii=True))


if __name__=='__main__':main()
