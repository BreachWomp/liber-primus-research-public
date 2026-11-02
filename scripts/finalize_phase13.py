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
    if (ROOT/'checkpoints/phase14_complete.json').exists():raise RuntimeError('Newer checkpoint exists')
    complete=load('checkpoints/phase13_joint_complete.json')
    tests=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,
                         capture_output=True,text=True,encoding='utf-8',timeout=60)
    output=tests.stdout+tests.stderr;(ROOT/'results/validation_phase13.txt').write_text(output,encoding='utf-8')
    if tests.returncode:raise RuntimeError(output)
    count=int(re.search(r'Ran (\d+) tests',output)[1]);now=datetime.now(timezone.utc).isoformat()
    events=[json.loads(line) for line in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    done=[e for e in events if e['status']=='completed'];latest={e['experiment']:e for e in done}
    phase={k:e for k,e in latest.items() if k.startswith(('E040-','E041-','E042-'))};assert len(phase)==76
    for event in phase.values():
        assert sha(event['output'])==event['output_sha256'] and event['wall_seconds']<180
        for path,digest in event['input_dependencies'].items():assert sha(path)==digest,path
    data={k:load(e['output']) for k,e in phase.items()}
    historical=data['E040-joint-key-skip-controls'];external_control=data['E041-joint-key-skip-external']
    assert historical['gate_passed'] and external_control['gate_passed']
    rows=corpus();raw=(ROOT/'data/raw/gutenberg/pg2944.txt').read_bytes().decode('utf-8-sig')
    training=[r for r in rows if r['chapter'] in ('I','III','IV','V','VI','VII','VIII','IX')]
    ranges=[r['source_character_range'] for r in training]
    model=BackoffModel([[x for w in tokenize(raw[a:b])[0] for x in w] for a,b in ranges],order=4,alpha=.5,strength=5)
    assert historical['training']==external_control['training']
    assert ranges==historical['training']['training_source_ranges']
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
        expected=[('whole',[0,len(cipher)])]+[('non_F_run',[a,min(b,a+256)]) for a,b in intervals]
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
    fixtures={f['id']:f for f in load('known_solutions/fixtures.json')};controls_summary=[]
    assert len(historical['controls'])==2 and len(external_control['controls'])==6
    for record in historical['controls']:
        f=fixtures[record['fixture']];cipher=to_indices(f['ciphertext_runes']);top=record['result']['top'][0]
        assert cipher==record['ciphertext_indices']
        verify_result(cipher,record['result'])
        assert top['plaintext_runes']==f['plaintext_runes'] and top['skip_positions']==f['skip_positions']
        assert top['sign']==1 and canonical(top['key'])==canonical([(-x)%29 for x in f['key_indices']])
        assert record['exact'] and all(record['checks'].values())
        controls_summary.append({'fixture':record['fixture'],'exact':True,'key_length':len(top['key']),
                                  'skips':len(top['skip_positions']),'oracle_used':False})
    eligible=[]
    for chapter in ('X','XI','XII'):
        candidates=[]
        for row in rows:
            if row['chapter']!=chapter:continue
            values=[x for w in row['words'] for x in w]
            if len(values)>=350 and values[:350].count(0)>=2:candidates.append(row)
        eligible+=candidates[:2]
    rng=random.Random(3301041)
    for i,(src,record) in enumerate(zip(eligible,external_control['controls'])):
        a,b=record['source_character_range'];assert [a,b]==src['source_character_range']
        assert all(b<=x or a>=y for x,y in ranges)
        plain=[x for w in tokenize(raw[a:b])[0] for x in w][:350]
        assert to_runes(plain)==record['truth_runes']
        key=[rng.randrange(1,29) for _ in range((5,13)[i%2])];sign=(1,-1)[i%2]
        skips=[j for j,x in enumerate(plain) if x==0][::2];cursor=0;cipher=[]
        for j,p in enumerate(plain):
            if j in skips:cipher.append(0)
            else:cipher.append(sign*(p-key[cursor%len(key)])%29);cursor+=1
        assert key==record['injected_key'] and sign==record['injected_sign'] and skips==record['injected_skips']
        assert cipher==record['ciphertext_indices']
        verify_result(cipher,record['result']);top=record['result']['top'][0]
        assert top['plaintext_runes']==record['truth_runes'] and top['key']==key and top['sign']==sign and top['skip_positions']==skips
        assert record['exact'] and all(record['checks'].values())
        controls_summary.append({'chapter':record['chapter'],'paragraph':record['paragraph'],'exact':True,
                                 'key_length':len(key),'skips':len(skips),'oracle_used':False})
    doublets=lambda v:sum(a==b for a,b in zip(v,v[1:]))
    def verify_null(source,row,seed):
        rng=random.Random(seed)
        for proposal in range(1,100001):
            sample=source[:];rng.shuffle(sample)
            if doublets(sample)==doublets(source):break
        else:raise AssertionError('Null replay exhausted')
        assert sample==row['ciphertext_indices'] and Counter(sample)==Counter(source)
        assert proposal==row.get('proposals',row.get('shuffle_proposals'))
        verify_result(sample,row['result'])
    assert len(historical['nulls'])==2 and len(external_control['nulls'])==3
    for row in historical['nulls']:
        j=row['control_index'];verify_null(historical['controls'][j]['ciphertext_indices'],row,3302040+j)
    for row in external_control['nulls']:
        verify_null(external_control['controls'][0]['ciphertext_indices'],row,3302041+row['replicate'])
    pages=[r for k,r in data.items() if k.startswith('E042-page-')]
    assert len(pages)==55 and {p['page'] for p in pages}=={f'LP2-{i:02}' for i in range(56) if i!=50}
    canonical_pages={r['id']:r for r in load('transcriptions/pages.json')}
    for page in pages:
        assert page['ciphertext_indices']==to_indices(canonical_pages[page['page']]['runes'])
        assert page['training']==historical['training'] and page['score']==page['result']['top'][0]['score']
        verify_result(page['ciphertext_indices'],page['result'])
    winner=max(pages,key=lambda r:r['score']);selection=load('experiments/joint_skip_selection.json')
    assert selection['selected_page']==winner['page']==complete['selected_page']
    assert selection['observed_score']==winner['score'] and len(selection['source_outputs'])==56
    assert selection['search_seed']==3303040 and selection['null_seed']==3301042 and selection['replicates']==19
    assert sha('experiments/joint_skip_selection.json')==complete['selection_sha256']
    for path,digest in selection['source_outputs'].items():assert sha(path)==digest
    nulls=[r for k,r in data.items() if k.startswith('E042-null-')];assert len(nulls)==19
    for row in nulls:
        verify_null(winner['ciphertext_indices'],row,3301042+row['parameters']['replicate'])
        assert row['score']==row['result']['top'][0]['score']
    exceed=sum(r['score']>=winner['score'] for r in nulls);p=(exceed+1)/20
    assert exceed==complete['exceedances'] and p==complete['raw_p']
    seconds=sum(e['wall_seconds'] for e in phase.values())
    assert seconds<900 and complete['seconds']+complete['prior_seconds']<650
    summary={'created_at':now,'selected_page':winner['page'],'top':winner['result']['top'][0],
        'unknown_pages':55,'controls_exact':8,'oracle_used':False,'controls':controls_summary,
        'raw_p':p,'bonferroni55':min(1,55*p),'null_exceedances':exceed,'null_replicates':19,
        'pending_larger_calibration':exceed==0,'candidate_records_recomputed':verified,
        'seed_records_recomputed':seeds_checked,'restart_traces_checked':traces_checked,
        'independent_schedule_optima':optima,'tests_passed':count,'successful_tasks':len(phase),
        'seconds':seconds,'family_accounted_seconds':complete['seconds']+complete['prior_seconds'],'new_decryptions':[]}
    save('results/phase13_summary.json',summary);finish(summary,phase,done,now)


def finish(summary,phase,done,now):
    s=summary;exceed=s['null_exceedances'];top=s['top']
    status='thirteenth_batch_complete_no_new_decryption' if exceed else 'thirteenth_batch_candidate_requires_larger_null'
    entries=[{'id':k,'fingerprint':e['fingerprint'],'output':e['output'],'sha256':e['output_sha256']} for k,e in phase.items()]
    queue=([{'id':'E042-larger-null','priority':0,'task':'Preserve frozen E042 candidate and preregister larger fresh full-optimizer matched-null calibration; no claim from zero of19 exceedances.'}] if not exceed else [])+[
        {'id':'H035','priority':1,'task':'Direct continuous-section key attack: reuse pinned E012 page groupings as explicit hypotheses, not authenticated cipher boundaries. Test a shared repeating key with selective F interruptions across page joins, with multifile historical and source-excluded controls. Freeze max length, source spans, seeds and full null reoptimization before execution.'},
        {'id':'H031','priority':2,'task':'Keep general substitution deferred until independently justified score repair; no control-specific tuning.'},
        {'id':'H023','priority':3,'task':'Keep delay3 feedback deferred pending feasible calibrated reduction.'}]
    state=load('research_state.json');known={e['fingerprint'] for e in state['completed_experiments']}
    state['completed_experiments'] += [e for e in entries if e['fingerprint'] not in known]
    state.update(status=status,updated_at=now,latest_report='reports/attack_phase13_report.md',
        next_experiments=[r['id'] for r in queue],
        promising_candidates=[] if exceed else [{'page':s['selected_page'],'status':'screen_maximum_requires_larger_null'}],
        validation={'tests_passed':s['tests_passed'],'path':'results/validation_phase13.txt',
                    'phase13_candidate_records_recomputed':s['candidate_records_recomputed'],
                    'phase13_seed_records_recomputed':s['seed_records_recomputed'],
                    'phase13_independent_schedule_optima':s['independent_schedule_optima']},
        session_budget={'phase':'thirteenth bounded joint key and F-schedule queue','max_compute_wall_seconds':900,
                        'max_experiment_wall_seconds':180,'workers':1,'background_jobs':False},
        scoring_gate='E040 both actual historical ciphertexts recover exact text,key and skip mask without oracle. E041 all6 source-excluded synthetic selective-skip controls exact in all3 criteria.',
        notes=['No previously unknown plaintext confirmed.','Direct solving only; no community-claim audits.',
               'Selective F-schedule and unknown periodic key can now be jointly recovered on8controls without oracle masks.',
               'Fixed-key F-schedule optimization is exact; candidate-key search and top12 seed selection remain heuristic.',
               'E042 all55unknown rune pages tested with full matched optimizer on19selected-page nulls.',
               'All source bytes and canonical transcriptions retained. No research process remains running.'])
    state['resources'].update(recorded_successful_experiment_runs=len(done),
        recorded_experiment_subprocess_wall_seconds=sum(e['wall_seconds'] for e in done),phase13_wall_seconds=s['seconds'])
    message=f'E042 joint unknown repeating key/selective F mask on55pages: {s["selected_page"]}, rawp={s["raw_p"]}, adjusted={s["bonferroni55"]}; no supported plaintext.'
    if exceed and message not in state['failed_approaches']:state['failed_approaches'].append(message)
    save('research_state.json',state)
    hypotheses=load('hypotheses.json');old=next(h for h in hypotheses['hypotheses'] if h['id']=='H034')
    old.update(status='bounded_heuristic_screen_complete' if exceed else 'larger_null_required',
        experiments=['E040','E041','E042'],result=s,
        parameters='Longest3non-F runs plus whole-page fixed-schedule seeds;12deduplicated cyclic keys; exact all-phase schedule DP and up to3coordinate/schedule alternations.',
        limits='All8controls recover text,key and mask without oracle. Key search remains heuristic; exactness applies only to schedules conditional on key. No unknown plaintext validated by selection-corrected matched nulls.')
    hypotheses['hypotheses']=[h for h in hypotheses['hypotheses'] if h['id']!='H035']+[
        {'id':'H035','claim':'A repeating key and selective F schedule may continue across multiple LP2 pages within a pinned source grouping.',
         'status':'queued','basis':'Historical DIVINITY/CIRCUMFERENCE fixtures span multiple pages. E042 assumes a separate page-local key and ranks short-page maxima; continuity provides additional shared-key constraints. E012 tested only named numerical streams across its groups.',
         'mechanism':'Concatenate rune streams in explicit page order; one periodic key and cursor with selective F skips across joins. Preserve all page boundaries and offsets.',
         'parameters':'Use existing pinned E012 group definitions as hypotheses only; separately preregister bounds, controls, score and null design.',
         'cost':'Benchmark longer inputs before unknown groups; require complete shared-key optimization in every null within a fixed budget.',
         'success_criterion':'Source-aligned historical and external controls recover exact key/masks; unknown candidate reproduces across page boundaries and survives selection-corrected matched nulls.',
         'rejection_criterion':'Failed controls, unsupported boundary assumptions or unaffordable calibration prevents escalation.',
         'limits':'Source grouping is not authenticated cipher structure; continuity, language model and bounded key search are hypotheses, not established facts.'}]
    hypotheses.update(status=status,updated_at=now,next_queue=queue);save('hypotheses.json',hypotheses)
    report=f'''# Dreizehnte Forschungsserie: Schlüssel und F-Unterbrechungen gemeinsam finden

Stand (UTC): {now}. **Keine neue Entschlüsselung bestätigt.**

## Fortschritt an überprüfbaren Kontrollen

E040 rekonstruiert die tatsächlichen Chiffren der bekannten Abschnitte
LP1-03/04 (DIVINITY) und LP1-14/15 (CIRCUMFERENCE) vollständig:
**Klartext, Schlüssel und dokumentierte F-Unterbrechungen stimmen exakt.**
Weder Schlüssel noch Unterbrechungspositionen wurden dem Solver übergeben.
Die Eingaben sind dieselben auf die Quellen zurückgeführten Chiffren wie zuvor.
Das ist eine verbesserte Replikation bekannter Lösungen, keine neue
historische Entschlüsselung.

E041 prüft denselben unveränderten Solver an sechs externen Texten aus
Emerson X, XI, XII, je 350 Runen. Zufällige Schlüssel der Längen 5 und 13,
beide Vorzeichen; jede zweite Klartext-F-Rune wird kopiert und verbraucht
keinen Schlüsselwert. Alle anderen Positionen werden regulär verschlüsselt.
Diese Regel dient nur der kontrollierten Herstellung der Chiffre; der
Solver erhält weder Regel, Klartext, Schlüssel noch Zeitplan.
**Alle sechs Texte, Schlüssel und Unterbrechungsmasken exakt.**
Nichtnullige eingesetzte Schlüsselwerte vermeiden hier die Mehrdeutigkeit
zwischen einem kopierten F und einer normal verschlüsselten F-Chiffrenrune.

Training weiter ausschließlich auf I, III–IX: 207.030 Runen, keine LP-Texte
und keine Kapitel X, XI, XII. Die Quellen waren in früheren Forschungsserien
bereits vorhanden; keine Behauptung einer historisch neuen Blindprüfung.
Zwei historische und drei externe Kontroll-Nulltexte durchlaufen ebenfalls
den vollständigen Optimierer, als Fähigkeitsdiagnose ohne Entdeckungs-p-Wert.

[Historischer Kontrollplan](../experiments/joint_skip_plan.json),
[externer Kontrollplan](../experiments/joint_skip_external_plan.json).

## Wie die gemeinsame Suche funktioniert

Regel: `P_i = s*C_i + K_j mod29`, s=+1 oder −1. An einer Chiffrenrune F=0
darf alternativ F kopiert werden, ohne j weiterzuschalten.
Jede Quellrune bleibt im bewerteten Text erhalten.

Schlüsselstarts stammen aus dem ganzen Text unter den zwei einfachen
Zeitplänen sowie aus den drei längsten maximalen F-freien Abschnitten
mit mindestens 32 Runen, jeweils auf höchstens 256 Runen begrenzt.
In einem F-freien Abschnitt kann kein solcher Skip auftreten.
Perioden 1–16 und beide Vorzeichen werden geprüft; primitive Schlüssel
werden unter zyklischer Rotation dedupliziert, zwölf Starts behalten.
Die Rangfolge benutzt die feste Sprachwertung mit Schlüssellängenabzug.
Das ist keine Garantie, dass der richtige Schlüssel unter diesen zwölf ist.

Für jeden festen Schlüssel findet dynamische Programmierung den global
besten F-Zeitplan und die beste Anfangsphase. Zusammenführen darf sie nur
Zustände mit gleichem Schlüsselcursor und gleichem Sprachkontext.
Bei einem Viergramm-Modell reichen höchstens acht Zustände je Cursor:
Die letzten drei binären F-Entscheidungen und der Cursor bestimmen den
Kontext. Die gemessenen Zustandszahlen wurden gegen diese Schranke geprüft.

Danach wechseln sich höchstens drei Runden aus Schlüsselverbesserung
bei festem Zeitplan und erneuter exakter Zeitplanoptimierung ab.
Je Schlüsselrunde höchstens sechs Koordinatendurchläufe, jeweils alle
29 Werte pro Schlüsselstelle. **Die Schlüsselsuche bleibt heuristisch;
exakt ist die Zeitplanoptimierung bei festem Schlüssel.**

Endbewertung:
`(Summe logp − primitive Schlüssellänge*ln29 − Anzahl Chiffren-F*ln2)/Runenzahl`.
Der letzte Term rechnet eine binäre Entscheidung je möglicher F-Stelle an;
er ist innerhalb derselben Seite konstant. Keine gefittete Skip-Wahrscheinlichkeit.
Dies ist ein Beschreibungslängen-Kriterium, keine Wahrscheinlichkeit,
dass ein Suchtreffer richtig ist.

## E042: Angriff auf alle 55 unbekannten Runenseiten

Der unveränderte Solver wurde auf LP2-00 bis LP2-55 angewandt; die Zahlenseite
LP2-50 bleibt erhalten und wird nicht als Runenchiffre behandelt.
Keine Kandidatenanpassung der Parameter, keine vorgegebenen Klartextwörter.
Seiten werden in diesem Versuch einzeln mit eigenem Cursor behandelt.

Stärkster Suchtreffer: **{s['selected_page']}**,
Bewertungswert {top['score']:.6f}, reine Sprachwertung {top['language_score']:.6f}.
Vorzeichen {top['sign']}, Schlüsselindizes `{top['key']}`.
Kopierte F-Positionen (nullbasierte Runenoffsets): `{top['skip_positions']}`.
Die Rückverschlüsselung ist an aktiven Stellen
`C_i=s*(P_i-K_j) mod29`; an den gespeicherten Skip-Positionen bleibt F stehen.

```text
{top['transliteration']}
```

Unveränderte Suchausgabe, **kein bestätigter Klartext**.
Die Seite und alle Quellergebnis-Prüfsummen wurden vor Nullgenerierung
eingefroren. 19 unabhängige Zufallstexte erhalten exakt Runenhäufigkeiten
und die Zahl gleicher Nachbarpaare. Jeder sucht seine eigenen F-freien
Abschnitte, Schlüsselstarts, Phasen und Unterbrechungsmasken mit demselben
vollständigen Optimierer.

**{exceed}/19** erreichen mindestens den beobachteten Wert.
Plus-eins-p={s['raw_p']:.3f}, Bonferroni55={s['bonferroni55']:.3f}.
{'Eine größere frische Kalibrierung bleibt erforderlich; noch keine Signifikanzbehauptung.' if not exceed else 'Der Treffer wird dadurch nicht als Lösung gestützt.'}
19 Replikate können korrigierte Signifikanz nicht auflösen. Die Seitenkorrektur
ist keine projektweite Korrektur über alle bisherigen explorativen Familien.
Ein negativer Befund widerlegt keine beliebigen Schlüssel oder andere
Unterbrechungszeichen.

[Angriffsplan](../experiments/joint_skip_unknown_plan.json),
[eingefrorene Auswahl](../experiments/joint_skip_selection.json).

## Unabhängige Prüfung und weitere Richtung

**{s['tests_passed']} Tests bestanden.**
{s['candidate_records_recomputed']} gespeicherte Zwischen-/Endkandidaten
und {s['seed_records_recomputed']} Schlüsselstarts wurden durch skalare
Entschlüsselung, Rückverschlüsselung und Neubewertung geprüft.
{s['restart_traces_checked']} Suchverläufe haben konsistente, nicht fallende Scores.
Für die Sieger aller {s['independent_schedule_optima']} Suchausgaben wurde
das globale Zeitplanmaximum mit einem separaten, nur Scores speichernden
Viterbi-Prüfer erneut berechnet. Kleine Tests vergleichen alle Phasen und
Skip-Teilmengen vollständig durch Enumeration.

Externe Klartexte wurden auf Original-Quellbereiche zurückgeführt,
Trainingsüberschneidungen ausgeschlossen und alle Schlüssel,
Kontrollmasken sowie 24 Zufallsfolgen aus den festen Seeds reproduziert.
Alle Ergebnis- und Abhängigkeitshashes stimmen.
{s['successful_tasks']} Aufgaben, {s['seconds']:.3f} Sekunden erfolgreiche
Experimentzeit. E042 einschließlich Ablaufaufwand
{s['family_accounted_seconds']:.3f} Sekunden unter 650;
Phasenbudget 900, maximal 180 je Aufgabe, ein Prozess.
Keine neuen Fremdquellen oder Lösungsmeldungen, keine verbleibenden Hintergrundjobs.

Als nächste direkte Hypothese ist ein gemeinsamer Schlüssel über
Seitengrenzen vorgesehen. Die historischen Kontrolltexte erstrecken sich
ebenfalls über mehrere Seiten. Bereits gepinnte E012-Gruppierungen können
dafür explizite Prüfhypothesen liefern; sie sind keine authentifizierten
Chiffregrenzen. Längere Eingaben, Kontrollen und vollständige Nulloptimierung
müssen vor dem Angriff separat begrenzt und festgelegt werden.

[Checkpoint](../checkpoints/phase13_complete.json),
[Messübersicht](../results/phase13_summary.json).
'''
    (ROOT/'reports/attack_phase13_report.md').write_text(report,encoding='utf-8')
    save('checkpoints/phase13_complete.json',{'created_at':now,'status':status,'summary':'results/phase13_summary.json',
        'summary_sha256':sha('results/phase13_summary.json'),'experiments':entries})
    print(json.dumps({k:v for k,v in s.items() if k!='top'},ensure_ascii=True))


if __name__=='__main__':main()
