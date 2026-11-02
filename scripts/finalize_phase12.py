"""Independent scalar verification of repeating-key controls and searches."""
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


def main():
    if (ROOT/'checkpoints/phase13_complete.json').exists():raise RuntimeError('Newer checkpoint exists')
    complete=load('checkpoints/phase12_periodic_complete.json')
    tests=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,
                         capture_output=True,text=True,encoding='utf-8',timeout=60)
    output=tests.stdout+tests.stderr;(ROOT/'results/validation_phase12.txt').write_text(output,encoding='utf-8')
    if tests.returncode:raise RuntimeError(output)
    test_count=int(re.search(r'Ran (\d+) tests',output)[1]);now=datetime.now(timezone.utc).isoformat()
    events=[json.loads(line) for line in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    done=[e for e in events if e['status']=='completed'];latest={e['experiment']:e for e in done}
    phase={k:e for k,e in latest.items() if k.startswith(('E038-','E039-'))};assert len(phase)==75
    for event in phase.values():
        assert sha(event['output'])==event['output_sha256']
        for path,digest in event['input_dependencies'].items():assert sha(path)==digest,path
        assert event['wall_seconds']<180
    data={k:load(e['output']) for k,e in phase.items()};control=data['E038-periodic-key-controls']
    assert control['gate_passed'] and len(control['controls'])==8 and control['unknown_pages_searched']==0
    # Rebuild the training model from source ranges rather than the runner's model function.
    raw=(ROOT/'data/raw/gutenberg/pg2944.txt').read_bytes().decode('utf-8-sig')
    external=corpus();train=[r for r in external if r['chapter'] in ('I','III','IV','V','VI','VII','VIII','IX')]
    training_ranges=[r['source_character_range'] for r in train]
    assert training_ranges==control['training']['training_source_ranges']
    sequences=[[x for word in tokenize(raw[a:b])[0] for x in word] for a,b in training_ranges]
    model=BackoffModel(sequences,order=4,alpha=.5,strength=5)
    assert sum(map(len,sequences))==control['training']['training_runes']==207030
    assert sha('data/raw/gutenberg/pg2944.txt')==control['training']['source_sha256']
    verified=0;results_verified=0
    def verify_result(cipher,result,oracle=None):
        nonlocal verified,results_verified
        policies=('oracle',) if oracle is not None else ('none','all_F')
        expected={(sign,policy,size) for sign in (1,-1) for policy in policies for size in range(1,17)}
        assert {(r['sign'],r['policy'],r['nominal_period']) for r in result['families']}==expected
        assert len(result['families'])==len(expected) and result['starts_per_family']==4
        assert result['neighbor_evaluations']==29*result['coordinate_evaluations']
        assert result['top'][0]['score']==max(r['score'] for r in result['families'])
        for row in result['families']+result['top']:
            key=row['key'];sign=row['sign'];period=row['nominal_period'];policy=row['policy']
            assert sign in (1,-1) and all(type(x) is int and 0<=x<29 for x in key)
            assert 1<=len(key)<=period<=16 and period%len(key)==0
            assert not any(len(key)%n==0 and key[:n]*(len(key)//n)==key for n in range(1,len(key)))
            skips=list(oracle) if policy=='oracle' else [i for i,x in enumerate(cipher) if x==0] if policy=='all_F' else []
            assert policy in policies and all(cipher[i]==0 for i in skips)
            cursor=0;plain=[];encoded=[]
            for i,x in enumerate(cipher):
                if i in skips:plain.append(0);encoded.append(0)
                else:
                    p=(sign*x+key[cursor%len(key)])%29;plain.append(p)
                    encoded.append(sign*(p-key[cursor%len(key)])%29);cursor+=1
            assert encoded==cipher
            language=model.score(plain);penalty=len(key)*math.log(29)/len(cipher)
            assert abs(language-row['language_score'])<1e-9
            assert abs(language-penalty-row['score'])<1e-9
            assert 0<=row['restart']<4 and 2<=row['sweeps']<=24
            assert 0<=row['accepted_coordinates']<=row['sweeps']*period
            if 'plaintext_runes' in row:
                assert to_runes(plain)==row['plaintext_runes'] and skips==row['skip_positions']
            verified+=1
        results_verified+=1
    fixtures={f['id']:f for f in load('known_solutions/fixtures.json')};diagnostics=[]
    for record in control['controls'][:2]:
        fixture=fixtures[record['fixture']]
        assert record['kind']=='historical_oracle_skips'
        assert record['ciphertext_indices']==to_indices(fixture['ciphertext_runes'])
        assert record['oracle_skips']==fixture['skip_positions'] and record['truth_runes']==fixture['plaintext_runes']
        verify_result(record['ciphertext_indices'],record['result'],record['oracle_skips'])
        assert record['exact'] and record['result']['top'][0]['plaintext_runes']==record['truth_runes']
        assert record['result']['top'][0]['key']==[(-x)%29 for x in fixture['key_indices']]
        assert record['result']['top'][0]['sign']==1
        diagnostics.append({'fixture':record['fixture'],'exact':True,'oracle_skips':True,
                            'recovered_key':record['result']['top'][0]['key']})
    eligible=[r for chapter in ('X','XI','XII') for r in
              [s for s in external if s['chapter']==chapter and sum(map(len,s['words']))>=200][:2]]
    rng=random.Random(3301038)
    for index,(src,record) in enumerate(zip(eligible,control['controls'][2:])):
        a,b=record['source_character_range'];assert [a,b]==src['source_character_range']
        assert record['chapter']==src['chapter'] and record['paragraph']==src['paragraph']
        assert all(b<=x or a>=y for x,y in training_ranges)
        truth=[x for w in tokenize(raw[a:b])[0] for x in w][:200]
        assert to_runes(truth)==record['truth_runes']
        length=(5,13)[index%2];sign=(1,-1)[index%2]
        key=[rng.randrange(29) for _ in range(length)]
        assert key==record['injected_key'] and sign==record['injected_sign']
        cipher=[sign*(p-key[i%length])%29 for i,p in enumerate(truth)]
        assert cipher==record['ciphertext_indices']
        verify_result(cipher,record['result'])
        assert record['exact'] and record['result']['top'][0]['plaintext_runes']==record['truth_runes']
        diagnostics.append({'chapter':record['chapter'],'paragraph':record['paragraph'],'exact':True,
                            'injected_period':length,'injected_sign':sign,'oracle_skips':False})
    doublets=lambda v:sum(a==b for a,b in zip(v,v[1:]))
    def verify_null(source,record,seed):
        rng=random.Random(seed)
        for proposal in range(1,100001):
            sample=source[:];rng.shuffle(sample)
            if doublets(sample)==doublets(source):break
        else:raise AssertionError('Null rejection exhausted')
        assert sample==record['ciphertext_indices']
        assert Counter(sample)==Counter(source)
        assert proposal==record.get('proposals',record.get('shuffle_proposals'))
        verify_result(sample,record['result'])
    assert len(control['nulls'])==3
    for record in control['nulls']:verify_null(control['controls'][2]['ciphertext_indices'],record,3302038+record['replicate'])
    pages=[r for k,r in data.items() if k.startswith('E039-page-')]
    assert len(pages)==55 and {r['page'] for r in pages}=={f'LP2-{i:02}' for i in range(56) if i!=50}
    canonical={p['id']:p for p in load('transcriptions/pages.json')}
    for page in pages:
        assert page['training']==control['training'] and page['ciphertext_indices']==to_indices(canonical[page['page']]['runes'])
        assert page['score']==page['result']['top'][0]['score']
        verify_result(page['ciphertext_indices'],page['result'])
    winner=max(pages,key=lambda r:r['score']);selection=load('experiments/periodic_key_selection.json')
    assert selection['selected_page']==winner['page']==complete['selected_page']
    assert selection['observed_score']==winner['score'] and len(selection['source_outputs'])==56
    assert selection['null_seed']==3301039 and selection['search_seed']==3303038 and selection['replicates']==19
    assert sha('experiments/periodic_key_selection.json')==complete['selection_sha256']
    for path,digest in selection['source_outputs'].items():assert sha(path)==digest
    nulls=[r for k,r in data.items() if k.startswith('E039-null-')];assert len(nulls)==19
    for row in nulls:
        verify_null(winner['ciphertext_indices'],row,3301039+row['parameters']['replicate'])
        assert row['score']==row['result']['top'][0]['score']
    exceed=sum(r['score']>=winner['score'] for r in nulls);p=(exceed+1)/20
    assert exceed==complete['exceedances'] and p==complete['raw_p']
    seconds=sum(e['wall_seconds'] for e in phase.values())
    assert seconds<900 and complete['seconds']+complete['prior_seconds']<650
    summary={'created_at':now,'selected_page':winner['page'],'top':winner['result']['top'][0],
        'unknown_pages':55,'families_per_page':64,'starts_per_family':4,'keys_exhaustively_enumerated':False,
        'controls':diagnostics,'controls_exact':8,'raw_p':p,'bonferroni55':min(1,55*p),
        'null_exceedances':exceed,'null_replicates':19,'pending_larger_calibration':exceed==0,
        'candidate_records_recomputed':verified,'search_outputs_recomputed':results_verified,
        'tests_passed':test_count,'successful_tasks':len(phase),'seconds':seconds,
        'family_accounted_seconds':complete['seconds']+complete['prior_seconds'],'new_decryptions':[]}
    save('results/phase12_summary.json',summary)
    finish(summary,phase,done,now)


def finish(summary,phase,done,now):
    s=summary;exceed=s['null_exceedances'];top=s['top']
    entries=[{'id':k,'fingerprint':e['fingerprint'],'output':e['output'],'sha256':e['output_sha256']} for k,e in phase.items()]
    status='twelfth_batch_complete_no_new_decryption' if exceed else 'twelfth_batch_candidate_requires_larger_null'
    queue=([{'id':'E039-larger-null','priority':0,'task':'Preserve frozen E039 candidate and preregister fresh larger full-optimizer matched-null calibration. No plaintext claim from zero of19 exceedances.'}] if not exceed else [])+[
        {'id':'H034','priority':1,'task':'Direct selective-interruption attack: jointly infer repeating key AND arbitrary F skips. Benchmark a bounded beam or alternating key/Viterbi solver on actual DIVINITY/CIRCUMFERENCE ciphertext without oracle skips, plus source-excluded synthetic controls. Freeze objective, seeds, budgets and matched-null search before unknown scans.'},
        {'id':'H031','priority':2,'task':'Keep general substitution deferred: both frozen objectives prefer incorrect short control output. No tuning to the erroneous rune.'},
        {'id':'H023','priority':3,'task':'Keep delay3 feedback deferred until a feasible independently calibrated reduction exists.'}]
    state=load('research_state.json');known={r['fingerprint'] for r in state['completed_experiments']}
    state['completed_experiments'] += [e for e in entries if e['fingerprint'] not in known]
    state.update(status=status,updated_at=now,latest_report='reports/attack_phase12_report.md',
        next_experiments=[r['id'] for r in queue],
        promising_candidates=[] if exceed else [{'page':s['selected_page'],'status':'screen_maximum_requires_larger_null'}],
        validation={'tests_passed':s['tests_passed'],'path':'results/validation_phase12.txt',
                    'phase12_candidate_records_recomputed':s['candidate_records_recomputed'],
                    'phase12_search_outputs_recomputed':s['search_outputs_recomputed']},
        session_budget={'phase':'twelfth bounded arbitrary repeating-key queue','max_compute_wall_seconds':900,
                        'max_experiment_wall_seconds':180,'workers':1,'background_jobs':False},
        scoring_gate='E038 all8 exact:2 historical keys recovered with ORACLE skip positions,6 training-excluded external synthetic keys recovered without oracle. E039 same optimizer, no arbitrary skip inference.',
        notes=['No previously unknown plaintext confirmed.','Direct solving only; no community-claim audits.',
               'Arbitrary rune keys now searched, beyond the381literal-key catalogue; heuristic coordinate search, not exhaustive29^period.',
               'E039 scans all55unknown rune pages with periods1..16, both signs and none/all_F policies. Oracle skips used only for the2 historical controls.',
               'Training excludes chaptersX/XI/XII in current model; these sources were seen in earlier phases, so not a historically blind evaluation.',
               'No research process remains running.'])
    state['resources'].update(recorded_successful_experiment_runs=len(done),
        recorded_experiment_subprocess_wall_seconds=sum(e['wall_seconds'] for e in done),phase12_wall_seconds=s['seconds'])
    message=f'E039 arbitrary periodic keys1..16, signs+/- and none/all_F on55pages: {s["selected_page"]}, rawp={s["raw_p"]}, adjusted={s["bonferroni55"]}; no supported plaintext.'
    if exceed and message not in state['failed_approaches']:state['failed_approaches'].append(message)
    save('research_state.json',state)
    hypotheses=load('hypotheses.json');old=next(h for h in hypotheses['hypotheses'] if h['id']=='H033')
    old.update(status='bounded_heuristic_screen_complete' if exceed else 'larger_null_required',
        experiments=['E038','E039'],result=s,
        parameters='Periods1..16, signs+/-1, none/all_F,4starts,12bigram then12fourgram coordinate sweeps. Primitive-key description-length penalty.',
        limits='Heuristic finite-budget search, not exhaustive29^period. All8controls exact, but2historical controls use oracle skip positions. None/all_F unknown policies do not test selective interruptions. Selection-corrected matched nulls, no new historical plaintext.')
    hypotheses['hypotheses']=[h for h in hypotheses['hypotheses'] if h['id']!='H034']+[
        {'id':'H034','claim':'Joint inference of unknown repeating keys and selective F interruptions may recover an unknown page.',
         'status':'queued','basis':'Both actual historical cyclic-key controls contain F symbols that are skipped and F symbols that consume a key; E038 recovered their keys only with oracle skip schedules.',
         'mechanism':'At each sourceF choose copied0/no cursor advance or normal keyed symbol/advance, while learning the cyclic key.',
         'parameters':'Preregister a bounded joint beam or alternating key/exact-schedule optimizer and controls before execution; no unknown-text-driven tuning.',
         'cost':'Prototype within180seconds; require full matched-optimizer null budget before broad scan.',
         'success_criterion':'Recover both historical plaintexts, keys and skip masks without oracle plus source-excluded external synthetic controls. Unknown candidates need source replay and corrected full-search null evidence.',
         'rejection_criterion':'Failed no-oracle controls or infeasible full null calibration prevents escalation.',
         'limits':'Potential large search/overfitting cost; model comparisons must include flexible skip selection in every null.'}]
    hypotheses.update(status=status,updated_at=now,next_queue=queue);save('hypotheses.json',hypotheses)
    report=f'''# Zwölfte Forschungsserie: beliebige wiederholte Runenschlüssel

Stand (UTC): {now}. **Keine neue Entschlüsselung bestätigt.**

## Was der neue Angriff abdeckt

Die bisherigen 381 Schlüsselwörter begrenzten die Schlüsselwerte auf einen
Katalog. E038/E039 lernen stattdessen jeden Schlüsselwert direkt aus den
Runen: `P_i = s*C_i + K_j mod29`, s=+1 oder −1. Der Schlüsselcursor j läuft
zyklisch. Geprüft werden Perioden 1–16, wobei 1 als einfache Vergleichsvariante
enthalten ist. Keine Wörter oder Klartextanfänge werden vorgegeben.

Zwei feste Regeln für F=0: keine Unterbrechung oder jedes F kopieren und den
Schlüsselcursor dort nicht weiterschalten. Das ist noch keine Suche über
beliebige F-Teilmengen. Alle Quellrunen bleiben im bewerteten Text erhalten.
Die Rückverschlüsselung lautet für aktive Positionen
`C_i = s*(P_i-K_j) mod29`; kopierte Positionen bleiben F.

Je Vorzeichen, F-Regel und Periode vier Starts: Spaltenmaximum unter dem
Unigramm-Modell, ein gestörter Start und zwei Zufallsstarts.
Je Start höchstens 12 Koordinatendurchläufe mit Bigrammen und anschließend
12 mit Viergrammen. Pro Koordinate werden alle 29 Schlüsselwerte geprüft.
Die lokalen Score-Änderungen umfassen alle betroffenen Kontextfaktoren,
auch diejenigen neben kopierten F-Runen, und sind mathematisch exakt.
Die globale Schlüsselsuche bleibt **heuristisch**, kein Durchsuchen von
29^Periode.

Endgültige Bewertung:
`(Summe der Viergramm-Logwahrscheinlichkeiten − primitive Schlüssellänge*ln29)/Runenzahl`.
Der feste Längenabzug vermindert den Vorteil längerer, flexiblerer Schlüssel.
Er ist ein Beschreibungslängen-Kriterium, keine Wahrscheinlichkeit dafür,
dass ein Text richtig ist. Kürzere primitive Wiederholungen werden erkannt.
Die Suche innerhalb einer festen Periode optimiert die Sprachwertung;
der Längenabzug wird auf die endgültigen Kandidaten angewandt.

## E038: acht Kontrollen exakt

Die tatsächlichen Chiffren der bekannten Abschnitte LP1-03/04 (DIVINITY) und
LP1-14/15 (CIRCUMFERENCE) werden samt Schlüssel exakt wiedergewonnen.
**Ihre dokumentierten F-Unterbrechungen wurden dabei vorgegeben.**
Dies prüft unbekannte Schlüssel bei bekanntem Zeitplan; es beweist keine
Wiedergewinnung der Unterbrechungspositionen.

Sechs weitere Kontrollen: die ersten zwei geeigneten Absätze aus Emerson
X, XI, XII, jeweils die ersten 200 Runen, mit zufälligen Schlüsseln der
Länge 5 beziehungsweise 13 und beiden Vorzeichen. Bei diesen Kontrollen
werden Schlüssel, Periode, Vorzeichen und F-Regel gesucht. Alle sechs
Texte werden ohne vorgegebene Unterbrechungen exakt gefunden.

Training ausschließlich auf I, III–IX: **207.030 Runen**, keine LP-Texte
und keine Kapitel X, XI, XII. Die Quellen wurden schon in früheren Serien
verwendet; dies ist eine aktuelle Trainingstrennung, kein historisch neuer
Blindtest. Das Wortmodell aus E036 wird hier nicht verwendet.

Drei zusätzliche, vollständig optimierte Kontroll-Nulltexte erhalten
Runenhäufigkeiten und die Zahl gleicher Nachbarpaare. Sie dienen nur als
Fähigkeitsdiagnose, ohne Entdeckungs-p-Wert.

[Kontrollplan](../experiments/periodic_key_plan.json).

## E039: alle 55 unbekannten Runenseiten

Pro Seite 64 Kombinationen aus Vorzeichen, F-Regel und nominaler Periode,
je vier Starts. LP2-50 bleibt als Zahlenseite erhalten.
Keine Quellenänderung, keine vorgegebenen Schlüssel und keine
Unterbrechungs-Orakel bei den unbekannten Seiten.

Stärkster Suchtreffer: **{s['selected_page']}**.
Bewertungswert mit Längenabzug {top['score']:.6f},
reine Sprachwertung {top['language_score']:.6f}.
Vorzeichen {top['sign']}, F-Regel `{top['policy']}`,
primitive Schlüssellänge {len(top['key'])}.
Schlüssel als Runenindizes: `{top['key']}`.

```text
{top['transliteration']}
```

Dies ist eine unveränderte Suchausgabe, **kein bestätigter Klartext**.
Seitenauswahl und Ergebnisprüfsummen wurden vor den Nullversuchen eingefroren.
19 unabhängige Zufallstexte erhalten genau die Runenhäufigkeiten und die Zahl
gleicher Nachbarpaare dieser Seite. Jeder durchläuft wieder alle 64 Familien
und vier Starts; die F-Positionen werden aus jedem Zufallstext neu bestimmt.
So werden auch die flexible Schlüsselwahl und die F-Regel ausgewählt.

**{exceed}/19** erreichen mindestens den beobachteten Bewertungswert.
Plus-eins-p={s['raw_p']:.3f}, Bonferroni55={s['bonferroni55']:.3f}.
{'Eine größere frische Kalibrierung bleibt erforderlich; keine Signifikanzbehauptung.' if not exceed else 'Der Treffer ist dadurch nicht als Lösung gestützt.'}
19 Replikate können korrigierte Signifikanz nicht auflösen.
Die Seitenkorrektur ist keine projektweite Bestätigung über alle früheren
Versuchsfamilien. Der Befund widerlegt weder beliebige wiederholte Schlüssel
noch selektiv unterbrochene Schlüsselströme.

[Angriffsplan](../experiments/periodic_key_unknown_plan.json),
[eingefrorene Auswahl](../experiments/periodic_key_selection.json).

## Unabhängige Prüfung und nächster Schritt

**{s['tests_passed']} Tests bestanden.**
Alle **{s['candidate_records_recomputed']} gespeicherten Familienmaxima und
Top-Kandidaten** aus {s['search_outputs_recomputed']} Suchausgaben wurden
mit einem skalaren Prüfer rückverschlüsselt und neu bewertet, einschließlich
Schlüsselperioden, F-Zeitplan und Längenabzug. Die lokalen Faktoränderungen
wurden durch Tests gegen vollständiges Neuberechnen sämtlicher 29
Nachbarschlüssel geprüft.
Alle Kontrolltexte sind auf Quellpositionen zurückgeführt; externe
Trainingsbereiche und Prüffenster überschneiden sich nicht. Die sechs
Verschlüsselungen und alle 22 Zufallsfolgen wurden aus ihren Seeds
unabhängig reproduziert. Ergebnis- und Abhängigkeitshashes stimmen.

{s['successful_tasks']} registrierte Aufgaben,
{s['seconds']:.3f} Sekunden erfolgreiche Experimentzeit.
E039 einschließlich Ablaufaufwand {s['family_accounted_seconds']:.3f} Sekunden,
unter dem Familienbudget von 650 Sekunden; Gesamtbudget 900,
maximal 180 je Aufgabe, ein Prozess. Keine Hintergrundjobs bleiben aktiv.

Der nächste direkte Ansatz ist die gemeinsame Suche nach Schlüssel
**und** selektiven F-Unterbrechungen. Die beiden tatsächlichen historischen
Chiffren liefern dafür strenge Kontrollen: Beide enthalten sowohl
übersprungene als auch normal verschlüsselte F-Runen. Ein neuer Solver muss
die Texte samt Zeitplan ohne vorgegebene Skip-Positionen wiedergewinnen,
bevor er auf unbekannte Seiten angesetzt wird.

[Checkpoint](../checkpoints/phase12_complete.json),
[Messübersicht](../results/phase12_summary.json).
'''
    (ROOT/'reports/attack_phase12_report.md').write_text(report,encoding='utf-8')
    save('checkpoints/phase12_complete.json',{'created_at':now,'status':status,'summary':'results/phase12_summary.json',
        'summary_sha256':sha('results/phase12_summary.json'),'experiments':entries})
    print(json.dumps({k:v for k,v in s.items() if k!='top'},ensure_ascii=True))


if __name__=='__main__':main()
