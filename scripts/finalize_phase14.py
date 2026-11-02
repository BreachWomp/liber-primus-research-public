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
    if (ROOT/'checkpoints/phase15_complete.json').exists():raise RuntimeError('Newer checkpoint exists')
    complete=load('checkpoints/phase14_section_complete.json')
    tests=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=60)
    output=tests.stdout+tests.stderr;(ROOT/'results/validation_phase14.txt').write_text(output,encoding='utf-8')
    if tests.returncode:raise RuntimeError(output)
    count=int(re.search(r'Ran (\d+) tests',output)[1]);now=datetime.now(timezone.utc).isoformat()
    events=[json.loads(line) for line in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    done=[e for e in events if e['status']=='completed'];latest={e['experiment']:e for e in done}
    phase={k:e for k,e in latest.items() if k.startswith(('E043-','E044-'))};assert len(phase)==30
    for event in phase.values():
        assert sha(event['output'])==event['output_sha256'] and event['wall_seconds']<180
        for path,digest in event['input_dependencies'].items():assert sha(path)==digest,path
    data={k:load(e['output']) for k,e in phase.items()};control=data['E043-section-key-controls'];assert control['gate_passed']
    rows=corpus();raw=(ROOT/'data/raw/gutenberg/pg2944.txt').read_bytes().decode('utf-8-sig')
    training=[r for r in rows if r['chapter'] in ('I','III','IV','V','VI','VII','VIII','IX')]
    ranges=[r['source_character_range'] for r in training]
    model=BackoffModel([[x for w in tokenize(raw[a:b])[0] for x in w] for a,b in ranges],order=4,alpha=.5,strength=5)
    assert ranges==control['training']['training_source_ranges']
    verified=0;optima=0;seeds_checked=0;traces_checked=0
    def verify_row(cipher,row):
        nonlocal verified
        key=row['key'];assert 1<=len(key)<=16
        assert len(canonical(key))==len(key)
        plain=scalar_replay(cipher,key,row['sign'],row['skip_positions'])
        language=model.score(plain)
        assert abs(language-row['language_score'])<1e-9
        score=language-(len(key)*math.log(29)+cipher.count(0)*math.log(2))/len(cipher)
        assert abs(score-row['score'])<1e-9
        assert 0<=row['selected_phase']<row['input_period']<=16
        assert 1<=row['dp_max_states']<=8*row['input_period']
        if 'plaintext_runes' in row:assert to_runes(plain)==row['plaintext_runes']
        verified+=1
    def verify_result(cipher,result):
        nonlocal optima,seeds_checked,traces_checked
        intervals=[];start=0
        for i,c in enumerate(cipher+[0]):
            if c==0:
                if i-start>=32:intervals.append((start,i))
                start=i+1
        intervals=sorted(intervals,key=lambda ab:(-(ab[1]-ab[0]),ab[0]))[:3]
        expected=([('whole',[0,len(cipher)])] if len(cipher)<=1024 else [('prefix',[0,1024]),('suffix',[len(cipher)-1024,len(cipher)])])+[('non_F_run',[a,min(b,a+256)]) for a,b in intervals]
        assert [(r['kind'],r['range']) for r in result['source_stats']]==expected
        assert len(result['restarts'])==min(12,result['unique_seed_keys'])
        keys_seen=set();seed_scores=[];finals=[]
        for restart in result['restarts']:
            initial=restart['initial'];a,b=initial['source_range'];source=cipher[a:b]
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
            assert trace[0]['input_period']==len(initial['key'])
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
    fixtures={f['id']:f for f in load('known_solutions/fixtures.json')}
    assert len(control['reused_historical'])==2 and len(control['controls'])==3
    for reused in control['reused_historical']:
        assert sha(reused['source_output'])==reused['source_sha256'] and not reused['search_rerun'] and reused['exact']
        f=fixtures[reused['fixture']];cipher=source_stream(f['page_ids'],reused['page_spans'])
        original=next(r for r in load(reused['source_output'])['controls'] if r['fixture']==f['id'])
        assert cipher==original['ciphertext_indices']==to_indices(f['ciphertext_runes'])
        verify_result(cipher,original['result'])
        assert original['result']['top'][0]['plaintext_runes']==f['plaintext_runes']
    rng=random.Random(3301043)
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
        key=[rng.randrange(1,29) for _ in range((5,8,13)[j])];sign=(1,-1,1)[j]
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
        assert top['plaintext_runes']==record['truth_runes'] and top['key']==key and top['sign']==sign and top['skip_positions']==skips
        assert record['exact'] and all(record['checks'].values())
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
    verify_null(control['controls'][1]['ciphertext_indices'],control['nulls'][0],3302043)
    groups=load('experiments/section_plan.json')['sections']
    sections=[r for k,r in data.items() if k.startswith('E044-section-')]
    assert len(sections)==10 and {s['section'] for s in sections}=={g['id'] for g in groups}
    for row in sections:
        group=next(g for g in groups if g['id']==row['section']);assert row['group']==group
        assert row['ciphertext_indices']==source_stream(group['page_ids'],row['page_spans'])
        assert row['training']==control['training'] and row['score']==row['result']['top'][0]['score']
        verify_result(row['ciphertext_indices'],row['result'])
    winner=max(sections,key=lambda r:r['score']);selection=load('experiments/section_key_selection.json')
    assert winner['section']==selection['selected_section']==complete['selected_section']
    assert selection['observed_score']==winner['score'] and len(selection['source_outputs'])==11
    assert selection['search_seed']==3303040 and selection['null_seed']==3301044 and selection['replicates']==19
    for path,digest in selection['source_outputs'].items():assert sha(path)==digest
    assert sha('experiments/section_key_selection.json')==complete['selection_sha256']
    nulls=[r for k,r in data.items() if k.startswith('E044-null-')];assert len(nulls)==19
    for row in nulls:
        assert row['page_spans']==winner['page_spans'] and row['section']==winner['section']
        verify_null(winner['ciphertext_indices'],row,3301044+100*row['parameters']['replicate'])
        assert row['score']==row['result']['top'][0]['score'] and row['training']==control['training']
    exceed=sum(r['score']>=winner['score'] for r in nulls);p=(exceed+1)/20
    assert exceed==complete['exceedances'] and p==complete['raw_p'] and min(1,10*p)==complete['bonferroni10']
    seconds=sum(e['wall_seconds'] for e in phase.values())
    assert seconds<900 and complete['seconds']+complete['prior_seconds']<650
    s={'created_at':now,'selected_section':winner['section'],'top':winner['result']['top'][0],
       'unknown_groups':10,'controls_exact':5,'new_controls':3,'reused_historical_controls':2,
       'raw_p':p,'bonferroni10':min(1,10*p),'null_exceedances':exceed,'null_replicates':19,
       'pending_larger_calibration':exceed==0,'candidate_records_recomputed':verified,
       'seed_records_recomputed':seeds_checked,'restart_traces_checked':traces_checked,
       'independent_schedule_optima':optima,'tests_passed':count,'successful_tasks':len(phase),
       'seconds':seconds,'family_accounted_seconds':complete['seconds']+complete['prior_seconds'],
       'section_scores':[{'section':r['section'],'runes':len(r['ciphertext_indices']),'score':r['score']} for r in sections],
       'new_decryptions':[]}
    save('results/phase14_summary.json',s);finish(s,phase,done,now)


def finish(s,phase,done,now):
    status='fourteenth_batch_complete_no_new_decryption' if s['null_exceedances'] else 'fourteenth_batch_candidate_requires_larger_null'
    entries=[{'id':k,'fingerprint':e['fingerprint'],'output':e['output'],'sha256':e['output_sha256']} for k,e in phase.items()]
    queue=([{'id':'E044-larger-null','priority':0,'task':'Preserve frozen E044 candidate; preregister larger fresh full-optimizer matched-null calibration. No significance claim from zero of19.'}] if not s['null_exceedances'] else [])+[
        {'id':'H036','priority':1,'task':'Test a shared repeating key across the same pinned groups with cursor reset at each page. Develop bounded shared-coordinate updates and pagewise exact F-schedule DP; calibrate on external controls before unknown pages. Keep page phase fixed at zero rather than fitting independent phases. Preserve numeric pages.'},
        {'id':'H031','priority':2,'task':'General substitution remains deferred pending independently justified score repair; no control-specific tuning.'},
        {'id':'H023','priority':3,'task':'Delay3 feedback remains deferred pending feasible calibrated reduction.'}]
    state=load('research_state.json');known={e['fingerprint'] for e in state['completed_experiments']}
    state['completed_experiments'] += [e for e in entries if e['fingerprint'] not in known]
    state.update(status=status,updated_at=now,latest_report='reports/attack_phase14_report.md',
        next_experiments=[r['id'] for r in queue],
        promising_candidates=[] if s['null_exceedances'] else [{'section':s['selected_section'],'status':'screen_maximum_requires_larger_null'}],
        validation={'tests_passed':s['tests_passed'],'path':'results/validation_phase14.txt',
            'phase14_candidate_records_recomputed':s['candidate_records_recomputed'],
            'phase14_seed_records_recomputed':s['seed_records_recomputed'],
            'phase14_independent_schedule_optima':s['independent_schedule_optima']},
        session_budget={'phase':'fourteenth bounded continuous section key queue','max_compute_wall_seconds':900,
                        'max_experiment_wall_seconds':180,'workers':1,'background_jobs':False},
        scoring_gate='E043 all3 long source-excluded controls exact text,key,mask; E040 two source-replayed historical controls reused without repeated search.',
        notes=['No previously unknown plaintext confirmed.','Direct solving only; no community-claim audits.',
            '10 explicit source group hypotheses tested with continuous key and selective F cursor across page joins.',
            'Page boundaries and numeric LP2-50 spans preserved; zero numeric key consumption is an assumption.',
            'Key search remains heuristic; exact schedule optimization is conditional on a key.',
            'All source bytes retained. No research process remains running.'])
    state['resources'].update(recorded_successful_experiment_runs=len(done),
        recorded_experiment_subprocess_wall_seconds=sum(e['wall_seconds'] for e in done),phase14_wall_seconds=s['seconds'])
    message=f'E044 continuous shared keys on10groups: {s["selected_section"]}, rawp={s["raw_p"]}, adjusted={s["bonferroni10"]}; no supported plaintext.'
    if s['null_exceedances'] and message not in state['failed_approaches']:state['failed_approaches'].append(message)
    save('research_state.json',state)
    hypotheses=load('hypotheses.json');old=next(h for h in hypotheses['hypotheses'] if h['id']=='H035')
    old.update(status='bounded_heuristic_screen_complete' if s['null_exceedances'] else 'larger_null_required',
        experiments=['E043','E044'],result=s,
        parameters='Continuous stream up to4096runes;prefix/suffix1024 and longest3 non-F seeds;12keys;periods1..16; exact fixed-key selective F DP;3coordinate/schedule rounds.',
        limits='Only specified source groupings and heuristic key search tested. No arbitrary key or cipher-boundary exclusion. No unknown plaintext validated.')
    hypotheses['hypotheses']=[h for h in hypotheses['hypotheses'] if h['id']!='H036']+[
        {'id':'H036','claim':'A shared repeating key may reset to its initial phase at each LP2 page boundary.',
         'status':'queued','basis':'Page-local E042 and continuous E044 impose different constraints; neither enforces one shared key with perpage reset. This is a distinct testable mechanism, not evidence it was used.',
         'mechanism':'One key, both signs, same initial phase at every page; selective F copies without cursor advance; language contexts reset at each page.',
         'parameters':'Preregister fixed groups,period bounds,seeds,shared coordinate search,nulls and budgets before execution.',
         'success_criterion':'External reset controls recover exact text,key,masks; unknown result survives full-search matched nulls and source-anchored independent validation.',
         'rejection_criterion':'Failed controls block unknown scan; null-typical output provides no support.',
         'limits':'Pinned grouping is an unverified boundary hypothesis; key search remains bounded and heuristic.'}]
    hypotheses.update(status=status,updated_at=now,next_queue=queue);save('hypotheses.json',hypotheses)
    top=s['top'];table='\n'.join(f'| {r["section"]} | {r["runes"]} | {r["score"]:.6f} |' for r in s['section_scores'])
    report=f'''# Vierzehnte Forschungsserie: Gemeinsamer Schlüssel über Seitengrenzen

Stand (UTC): {now}. **Keine neue Entschlüsselung bestätigt.**

## Direkter Angriff

E044 prüft zehn bereits gepinnte Seitengruppierungen. Diese sind ausdrücklich
Hypothesen über Chiffregrenzen, keine authentifizierten Abschnitte.
Regel: `P_i=s*C_i+K_j mod29`, s=+1 oder −1; an einer Chiffren-F-Rune kann
alternativ F kopiert werden, ohne den Schlüsselcursor zu erhöhen.
Schlüssel, Cursor und Sprachkontext laufen über die Seitengrenzen weiter.
Alle Seiten und Quellverweise bleiben als exakte Runenoffsets erhalten.
Die Zahlenseite LP2-50 ist als leere Runenspanne enthalten; dass ihre Zahlen
keinen Schlüsselwert verbrauchen, ist eine explizite Modellannahme.

| Gruppe | Runen | Bester penaliserter Score |
|---|---:|---:|
{table}

Für Eingaben bis 1024 Runen bleibt der E040-Solver unverändert. Bei längeren
Eingaben erzeugen die ersten und letzten 1024 Runen sowie die drei längsten
F-freien Abschnitte Schlüsselstarts. Perioden 1–16, beide Vorzeichen,
höchstens zwölf zyklisch deduplizierte Starts. Bis zu drei Runden wechseln
Schlüsselkoordinaten-Verbesserung und exakte F-Zeitplanoptimierung ab.
Alle Endbewertungen verwenden den gesamten Abschnitt.
Die Schlüsselsuche ist heuristisch; exakt ist nur die Zeitplanoptimierung
bei festem Schlüssel. Score unverändert:
`mean(logp4) - (primitive_key_length*ln29 + ciphertext_F_count*ln2)/N`.

## Kontrollen und Zufallsvergleich

E043 rekonstruiert drei externe Kontrolltexte mit 3316, 1200 und 1200 Runen
exakt: Klartext, Schlüssel und F-Masken. Schlüssel zufällig mit Längen 5, 8,
13; kein Schlüssel oder Zeitplan wird dem Solver übergeben. Die erste
Kontrolle verwendet die Seitenlängen von LP2-40 bis LP2-55 einschließlich
der leeren Zahlenseite. Die beiden historischen E040-Ergebnisse werden
gegen kanonische LP1-Seiten erneut reproduziert, ohne identische Suchen
zu wiederholen. Das sind Kontrollen und Replikationen, keine neuen LP-Lösungen.
Training auf Emerson I, III–IX (207030 Runen), Kontrollen aus X, XI, XII;
Quellbereiche sind disjunkt, die Kapitel waren historisch bereits vorhanden.
Ein zusätzlicher Kontroll-Nulltext durchläuft die gesamte Suche.

Stärkster unbekannter Abschnitt: **{s['selected_section']}**, Score
{top['score']:.6f}, Sprachwertung {top['language_score']:.6f}.
Vorzeichen {top['sign']}, Schlüssel `{top['key']}`,
F-Skips (nullbasierte Offsets im gesamten Abschnitt) `{top['skip_positions']}`.
Die Rückverschlüsselung lautet `C_i=s*(P_i-K_j) mod29`, an Skips F.

```text
{top['transliteration']}
```

**Suchausgabe, kein bestätigter Klartext.** Auswahl und Ergebnis-Prüfsummen
wurden vor den Nullversuchen eingefroren. Jeder Nulltext erhält pro Seite
Runenhäufigkeiten, die Zahl gleicher Nachbarpaare und die beiden Randrunen.
Damit bleiben auch Gleichheiten an Seitenübergängen erhalten. Innenpositionen
werden unabhängig gleichverteilt permutiert und bis zur passenden
Nachbarpaarzahl verworfen; maximal 100000 Versuche je Seite.
Jeder Nulltext sucht seine eigenen Fenster, Schlüssel, Phasen und Masken.

**{s['null_exceedances']}/19** Nulltexte erreichen mindestens den beobachteten
Score. Plus-eins-p={s['raw_p']:.3f}, Bonferroni10={s['bonferroni10']:.3f}.
{'Größere frische Kalibrierung erforderlich; keine Signifikanzbehauptung.' if not s['null_exceedances'] else 'Der Treffer wird durch diesen Vergleich nicht als Lösung gestützt.'}
19 Replikate reichen nicht zur Auflösung korrigierter Signifikanz.
Die Korrektur gilt für diese Familie mit zehn Gruppen, nicht projektweit.
Überlappende Gruppen sind für die Bonferroni-Schranke zulässig.

## Reproduzierbarkeit und nächster Angriff

{s['tests_passed']} Tests bestanden. {s['candidate_records_recomputed']} Zwischen-/Endkandidaten,
{s['seed_records_recomputed']} Schlüsselstarts und {s['restart_traces_checked']}
Suchverläufe unabhängig skalar geprüft, einschließlich Rückverschlüsselung.
Ein separater Score-Viterbi reproduziert {s['independent_schedule_optima']}
Zeitplanmaxima. Kontrolltexte aus Originalbereichen, Schlüssel und alle
20 neuen Nulltexte aus festen Seeds reproduziert; alle Abhängigkeitshashes stimmen.
{s['successful_tasks']} Aufgaben, {s['seconds']:.3f} Sekunden erfolgreiche Experimentzeit;
E044 mit Ablaufaufwand {s['family_accounted_seconds']:.3f} Sekunden unter 650.
Phasenbudget 900, je Prozess 180 Sekunden, ein Worker, maximal 4096 Runen.
Keine Quellen verändert, keine Lösungsmeldungen fremder Autoren untersucht.

Nächste direkte Hypothese: derselbe Schlüssel in mehreren Seiten, dessen
Cursor an jeder Seite auf den Anfang zurückgesetzt wird. Das unterscheidet
sich sowohl vom kontinuierlichen Schlüssel hier als auch von getrennten
Seitenschlüsseln in E042. Vor dem unbekannten Material werden feste Parameter
und positive Kontrollen mit solchen Seitenresets benötigt.

[Plan](../experiments/section_key_unknown_plan.json),
[eingefrorene Auswahl](../experiments/section_key_selection.json),
[Messübersicht](../results/phase14_summary.json),
[Checkpoint](../checkpoints/phase14_complete.json).
'''
    (ROOT/'reports/attack_phase14_report.md').write_text(report,encoding='utf-8')
    save('checkpoints/phase14_complete.json',{'created_at':now,'status':status,'summary':'results/phase14_summary.json',
        'summary_sha256':sha('results/phase14_summary.json'),'experiments':entries})
    print(json.dumps({k:v for k,v in s.items() if k not in ('top','section_scores')},ensure_ascii=True))


if __name__=='__main__':main()
