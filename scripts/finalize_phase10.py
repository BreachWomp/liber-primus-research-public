"""Independent scalar validation and checkpoint for the offset-feedback attack."""
from collections import Counter
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import random
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'experiments'))
from attack_support import to_indices
from external_language import external_model

def load(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))
def save(path,data):(ROOT/path).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def main():
    if (ROOT/'checkpoints/phase11_complete.json').exists():raise RuntimeError('Newer checkpoint exists')
    complete=load('checkpoints/phase10_offset_complete.json')
    tests=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,
        capture_output=True,encoding='utf-8',text=True,timeout=60)
    output=tests.stdout+tests.stderr;(ROOT/'results/validation_phase10.txt').write_text(output,encoding='utf-8')
    if tests.returncode:raise RuntimeError(output)
    count=int(re.search(r'Ran (\d+) tests',output)[1]);now=datetime.now(timezone.utc).isoformat()
    events=[json.loads(line) for line in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    done=[e for e in events if e['status']=='completed'];latest={e['experiment']:e for e in done}
    phase={k:e for k,e in latest.items() if k.startswith(('E034-','E035-'))};assert len(phase)==76
    for e in phase.values():
        assert sha(e['output'])==e['output_sha256']
        for path,digest in e['input_dependencies'].items():assert sha(path)==digest,path
        assert e['wall_seconds']<180
    data={k:load(e['output']) for k,e in phase.items()};controls=data['E034-controls']
    assert controls['gate_passed'] and len(controls['controls'])==3
    fixtures={f['id']:f for f in load('known_solutions/fixtures.json')}
    model=external_model(4);verified=0
    def verify(cipher,row):
        nonlocal verified
        recipe=row['recipe'];plain=to_indices(row['plaintext_runes']);assert len(plain)==len(cipher)
        a,b,d=[recipe[k] for k in ('a','b','d')];key=recipe['initial_key']
        assert all(1<=x<=28 for x in (a,b,d)) and 0<=key<29 and recipe['F_policy']=='none'
        recovered=[];previous=key;encoded=[]
        for symbol in cipher:
            previous=(a*symbol+b*previous+d)%29;recovered.append(previous)
        previous=key;inv=pow(a,-1,29)
        for symbol in plain:
            encoded.append(inv*(symbol-b*previous-d)%29);previous=symbol
        assert recovered==plain and encoded==cipher and recipe['initial_plaintext']==plain[0]
        assert abs(model.score(plain)-row['score'])<1e-9
        verified+=1
    for control in controls['controls']:
        truth=to_indices(fixtures[control['fixture']]['plaintext_runes'])
        assert control['exact'] and control['top'][0]['plaintext_runes']==fixtures[control['fixture']]['plaintext_runes']
        a,b,d=control['injected'];previous=control['initial_key'];expected=[]
        for symbol in truth:
            expected.append(pow(a,-1,29)*(symbol-b*previous-d)%29);previous=symbol
        assert expected==control['ciphertext_indices'] and control['recipes']==636608
        for row in control['top']:verify(expected,row)
    pages=[r for k,r in data.items() if k.startswith('E034-page-')];assert len(pages)==55
    assert {r['page'] for r in pages}=={f'LP2-{n:02}' for n in range(56) if n!=50}
    canonical={p['id']:p for p in load('transcriptions/pages.json')}
    for page in pages:
        assert page['ciphertext_indices']==to_indices(canonical[page['page']]['runes']) and page['recipes']==636608
        assert page['score']==page['top'][0]['score']
        for row in page['top']:verify(page['ciphertext_indices'],row)
    winner=max(pages,key=lambda r:r['score']);selection=load('experiments/offset_feedback_selection.json')
    assert sha('experiments/offset_feedback_selection.json')==complete['selection_sha256']
    assert winner['page']==selection['selected_page']==complete['selected_page'] and winner['score']==selection['observed_score']
    assert len(selection['source_outputs'])==56
    for path,digest in selection['source_outputs'].items():assert sha(path)==digest
    nulls=[r for k,r in data.items() if k.startswith('E034-null-')];assert len(nulls)==19
    doublets=lambda v:sum(a==b for a,b in zip(v,v[1:]));cipher=winner['ciphertext_indices']
    for null in nulls:
        assert Counter(null['ciphertext_indices'])==Counter(cipher)
        assert doublets(null['ciphertext_indices'])==doublets(cipher) and null['recipes']==636608
        assert null['score']==null['top'][0]['score']
        # Independent rejection replay verifies the fixed seed and first acceptance.
        rng=random.Random(3301034+null['parameters']['replicate'])
        for proposal in range(1,100001):
            sample=cipher[:];rng.shuffle(sample)
            if doublets(sample)==doublets(cipher):break
        else:raise AssertionError('Null replay exhausted')
        assert sample==null['ciphertext_indices'] and proposal==null['shuffle_proposals']
        verify(sample,null['top'][0])
    exceed=sum(r['score']>=winner['score'] for r in nulls);p=(exceed+1)/20
    assert exceed==complete['exceedances'] and p==complete['raw_p']
    prototype=data['E035-substitution-prototype'];sub_verified=0;sub_diagnostics=[]
    assert prototype['unknown_pages_searched']==0 and not prototype['gate_passed']
    injection_rng=random.Random(3301035)
    for j,control in enumerate(prototype['controls']):
        truth=to_indices(fixtures[control['fixture']]['plaintext_runes'])
        perm=list(range(29));injection_rng.shuffle(perm)
        assert perm==control['permutation_plain_to_cipher']
        source=[perm[x] for x in truth];assert source==control['ciphertext_indices']
        assert control['search_seed']==3303035+100*j
        cases=[(source,control['result'])]
        for null in control['nulls']:
            sample=source[:];random.Random(3302035+100*j+null['replicate']).shuffle(sample)
            assert sample==null['ciphertext_indices'] and Counter(sample)==Counter(source)
            cases.append((sample,null['result']))
        for sample,result in cases:
            assert 1<=len(result['restarts'])<=24
            assert result['top']==max(result['restarts'],key=lambda r:r['score'])
            assert result['evaluations']==sum(r['evaluations'] for r in result['restarts'])
            for row in result['restarts']:
                mapping=row['mapping_cipher_to_plain'];assert sorted(mapping)==list(range(29))
                recovered=[mapping[x] for x in sample];plain=to_indices(row['plaintext_runes'])
                assert recovered==plain and [mapping.index(x) for x in plain]==sample
                assert abs(model.score(plain)-row['score'])<1e-9
                assert 0<=row['accepted_swaps']<=40 and row['evaluations']<=1+40*406
                sub_verified+=1
        found=to_indices(control['result']['top']['plaintext_runes'])
        assert control['exact']==(found==truth) and control['correct_positions']==sum(a==b for a,b in zip(found,truth))
        sub_diagnostics.append({'fixture':control['fixture'],'exact':control['exact'],'runes':len(truth),
            'correct_positions':control['correct_positions'],'truth_score':model.score(truth),
            'best_score':control['result']['top']['score'],
            'wrong_plaintext_outscores_truth':found!=truth and control['result']['top']['score']>model.score(truth)+1e-12,
            'mismatches':[{'offset':i,'truth_index':a,'found_index':b} for i,(a,b) in enumerate(zip(truth,found)) if a!=b]})
    assert sum(r['exact'] for r in sub_diagnostics)==2 and sub_diagnostics[-1]['wrong_plaintext_outscores_truth']
    seconds=sum(e['wall_seconds'] for e in phase.values());assert seconds<900
    attack_seconds=sum(e['wall_seconds'] for k,e in phase.items() if k.startswith('E034-'));assert attack_seconds<750
    assert complete['prior_seconds']+complete['seconds']<750
    summary={'created_at':now,'selected_page':winner['page'],'top':winner['top'][0],
        'unknown_pages':55,'rules_per_page':636608,'unknown_rules_evaluated':55*636608,
        'controls_exact':3,'raw_p':p,'bonferroni55':min(1,55*p),'null_exceedances':exceed,
        'null_replicates':19,'pending_larger_calibration':exceed==0,'candidate_records_recomputed':verified,
        'tests_passed':count,'successful_tasks':len(phase),'seconds':seconds,'attack_seconds':attack_seconds,
        'substitution_candidate_records_recomputed':sub_verified,'substitution_controls':sub_diagnostics,
        'substitution_gate_passed':False,'substitution_unknown_pages_searched':0,
        'orchestration_seconds':complete['seconds'],'preexisting_seconds':complete['prior_seconds'],
        'family_budget_seconds':750,'new_decryptions':[]}
    save('results/phase10_summary.json',summary)
    entries=[{'id':k,'fingerprint':e['fingerprint'],'output':e['output'],'sha256':e['output_sha256']} for k,e in phase.items()]
    status='tenth_batch_complete_no_new_decryption' if exceed else 'tenth_batch_candidate_requires_larger_null'
    queue=([{'id':'E034-larger-null','priority':0,'task':'Freeze E034 candidate and preregister larger fresh full-grid matched null calibration.'}] if not exceed else [])+[
        {'id':'H031','priority':1,'task':'Direct solving: repair substitution ranking using a separately preregistered externally trained boundary-aware objective. E035 recovers both long controls but its frozen4gram prefers a wrong short plaintext. More search alone cannot fix this. Require exact controls and external heldout discrimination before unknown scan; budget full null optimization.'},
        {'id':'H023','priority':2,'task':'Keep delay3 plaintext feedback deferred until a justified reduction makes full control/null calibration feasible.'}]
    state=load('research_state.json');known={r['fingerprint'] for r in state['completed_experiments']}
    state['completed_experiments'] += [e for e in entries if e['fingerprint'] not in known]
    state.update(status=status,updated_at=now,latest_report='reports/attack_phase10_report.md',
        next_experiments=[r['id'] for r in queue],
        promising_candidates=[] if exceed else [{'page':winner['page'],'status':'screen_maximum_requires_larger_null'}],
        validation={'tests_passed':count,'path':'results/validation_phase10.txt','phase10_candidate_records_recomputed':verified,
                    'phase10_substitution_candidate_records_recomputed':sub_verified},
        session_budget={'phase':'tenth bounded offset-feedback queue','max_compute_wall_seconds':900,
                        'max_experiment_wall_seconds':180,'workers':1,'background_jobs':False},
        scoring_gate='E034 all3 synthetic controls exact. E035 general substitution2/3 exact; frozen4gram prefers a wrong short control, so no E035 unknown scan authorized by its gate.',
        notes=['No previously unknown plaintext confirmed.','Direct solving remains the priority; no community-claim audits.',
               'E034 exhausts nonzero constant one-step affine plaintext feedback, preserving every rune position.',
               'Prior zero-constant rules excluded; original source bytes and canonical transcriptions unchanged.',
               'E035 recovers515/515 and319/319 runes; short control93/95. Wrong short plaintext scores above truth, so ranking rather than search budget must change before escalation.',
               'No research process remains running.'])
    state['resources'].update(recorded_successful_experiment_runs=len(done),
        recorded_experiment_subprocess_wall_seconds=sum(e['wall_seconds'] for e in done),phase10_wall_seconds=seconds)
    message=f'E034 nonzero-constant plaintext feedback on55pages: {winner["page"]}, rawp={p}, adjusted={min(1,55*p)}; no supported plaintext.'
    if exceed and message not in state['failed_approaches']:state['failed_approaches'].append(message)
    save('research_state.json',state)
    hypotheses=load('hypotheses.json')
    hypotheses['hypotheses']=[r for r in hypotheses['hypotheses'] if r['id'] not in ('H030','H031')]+[
        {'id':'H030','claim':'One-step affine plaintext feedback with a nonzero constant may recover an unknown page.',
         'experiments':['E034'],'status':'finite_screen_complete' if exceed else 'larger_null_required','result':summary,
         'limits':'Finite exploratory family, not fresh blind historical validation; no nonlinear or interrupted updates; no broad feedback exclusion.'},
        {'id':'H031','claim':'A non-affine rune substitution consistent with observed lexical equality patterns may reveal plaintext.',
         'experiments':['E035'],'status':'control_gate_failed_short_text_score','result':sub_diagnostics,
         'basis':'Affine scans cover only a small subset of bijections; preserved repeated-rune word patterns constrain general substitutions.',
         'mechanism':'Single29-symbol bijection, source lexical endpoints fixed; external word patterns constrain admissible mappings.',
         'parameters':'E035 fixed dictionary pattern seeds, up to24 starts,40 exhaustive406-swap sweeps. No unknown-candidate tuning.',
         'cost':'Completed prototype within180seconds; no unknown-page scan.',
         'success_criterion':'Exact control recovery before unknown scan; any candidate needs reversible mapping, source replay and selection-corrected null evidence.',
         'rejection_criterion':'Failed control or infeasible calibration prevents escalation; dictionary incompatibility alone cannot rule out unseen words or a different language.',
         'limits':'Two controls recovered exactly, short control score misspecified. Nine count-preserving diagnostic nulls did not condition doublets. No unknown-page or historical decryption claim.'}]
    hypotheses.update(status=status,updated_at=now,next_queue=queue);save('hypotheses.json',hypotheses)
    report=f'''# Zehnte Forschungsserie: Rückkopplung und allgemeine Runen-Ersetzung

Stand (UTC): {now}. **Keine neue Entschlüsselung bestätigt.**

## E034: Eine bisher offene Erweiterung vollständig geprüft

Die Regel lautet `P_i = a*C_i + b*P_(i-1) + d mod 29`, mit einem unbekannten
Anfangswert `P_-1 = K`. a, b und d durchlaufen jeweils 1–28, K alle 29 Werte.
**636.608 Regeln je Seite; 35.013.440 Regeln auf allen 55 ungelösten Runenseiten.**
LP2-50 bleibt als reine Zahlenseite erhalten. Jede Rune einschließlich der ersten
wird bewertet. Kein F-Skip, keine Umordnung und keine seitenübergreifende Fortsetzung.

E019 hatte den konstanten Term explizit ausgeschlossen. `d=0` bleibt daher hier
ausgespart; seine Koeffizientenfälle wurden in E019 und E014 behandelt. Für b≠1
kann d durch eine Klartextverschiebung absorbiert werden, für b=1 kumuliert es.
Das motiviert die endliche Erweiterung, liefert aber keinen historischen Schlüssel.

Mit x=P0 berechnet die Suche die Basisfolgen
`S0=0, q0=1, t0=0`, danach
`S_i=C_i+b*S_(i-1), q_i=b*q_(i-1), t_i=1+b*t_(i-1)`.
Dann ist `P_i=a*S_i+q_i*x+d*t_i`. Der Schlüssel
`K=b^-1*(x-a*C0-d)` ist für feste a,b,d bijektiv zu x.
Diese Formel funktioniert auch für b=1; es gibt keine Division durch b−1.
Die Rückverschlüsselung `C_i=a^-1*(P_i-b*P_(i-1)-d)` ist eindeutig.

Drei synthetisch verschlüsselte bekannte Texte werden im vollständigen Suchraum
jeweils exakt als bestes Ergebnis zurückgewonnen; eine Kontrolle verwendet b=1.
Kontrollen sind Funktionsprüfungen, keine historische Entschlüsselung.
Der externe Viergramm-Score von E016 bleibt unverändert; keine LP-Texte im
Training und keine Anpassung an unbekannte Ausgaben.

[Festgelegter Plan](../experiments/offset_feedback_plan.json).

## Ergebnis und Zufallsvergleich

Stärkster Suchtreffer: **{winner['page']}**, Score {winner['score']:.6f}.
Unveränderte Transliteration:

```text
{winner['top'][0]['transliteration']}
```

Regel: `{json.dumps(winner['top'][0]['recipe'])}`.
Dies ist ein gespeicherter Suchtreffer, **kein bestätigter Klartext**.

Vor Beginn der Zufallsversuche wurden Seitenauswahl und alle Ergebnisprüfsummen
eingefroren. 19 unabhängige Zufallstexte erhalten exakt die Runenhäufigkeiten
und die Anzahl gleicher Nachbarpaare der gewählten Seite. Jeder durchläuft
denselben vollständigen Suchraum von 636.608 Regeln.

**{exceed}/19** erreichen mindestens den beobachteten Score.
Plus-eins-p={p:.3f}; Bonferroni über 55 Seiten={min(1,55*p):.3f}.
19 Replikate können korrigierte Signifikanz nicht auflösen.
{'Eine größere vorab registrierte Kalibrierung ist erforderlich und vorgemerkt.' if not exceed else 'Dieser Befund begründet keine größere Kalibrierung des Treffers.'}
Die Untersuchung folgt früheren explorativen Familien; der Seitenfaktor ist
keine projektweite Bestätigungskorrektur und das Korpus kein frischer Blindtest.

[Eingefrorene Auswahl](../experiments/offset_feedback_selection.json).

## E035: Allgemeine Runen-Ersetzung – zwei Kontrolltexte exakt

Zusätzlich wurde ein begrenzter Prototyp für beliebige bijektive Ersetzungen der
29 Runen geprüft. Anders als affine Abbildungen kann er auch nichtlineare
Permutationen darstellen. Wörter mit gleichem Wiederholungsmuster liefern
Startbelegungen aus dem unveränderten externen Wörterbuch. Diese sind Suchstarts,
keine behaupteten Klartextwörter oder erzwungenen Lösungen.

Höchstens 24 deduplizierte Starts, je höchstens 40 Verbesserungsschritte; pro
Schritt werden alle 406 Vertauschungen zweier Schlüsselwerte bewertet.
Dies ist eine begrenzte heuristische Suche, keine vollständige Prüfung von 29!.
Kein Test auf unbekannten Seiten.

| Kontrolltext | Korrekte Runen | Vollständig |
|---|---:|---|
| LP1-03/04, bekannte DIVINITY-Lösung, neu zufällig substituiert | 515/515 | ja |
| LP1-14/15, bekannte CIRCUMFERENCE-Lösung, neu zufällig substituiert | 319/319 | ja |
| LP2-57, bekannter Direkttext, neu zufällig substituiert | 93/95 | nein |

Beim kurzen Kontrolltext bewertet das feste Viergramm-Modell die falsche Ausgabe
mit {sub_diagnostics[-1]['best_score']:.6f} sogar höher als den korrekten Text
({sub_diagnostics[-1]['truth_score']:.6f}). Betroffen sind Runenoffsets 25 und 80.
Damit liegt nachweislich eine Grenze des Ranking-Scores vor. Mehr Laufzeit allein
kann den richtigen Text unter diesem unveränderten Ziel nicht zum Maximum machen.
**Exaktes Kontroll-Gate verfehlt, deshalb keine unbekannte Seite mit E035 gesucht.**

Je Kontrolltext wurden drei zufällige Vergleichstexte mit identischen
Runenhäufigkeiten und Segmentendpunkten durch denselben Optimierer verarbeitet.
Diese neun Fähigkeitsdiagnosen konditionieren ausdrücklich **nicht** auf gleiche
Nachbarpaare und tragen keinen Entdeckungs-p-Wert. Ein späterer Angriff braucht
eine vorab festgelegte, stärkere vollständige Nullkalibrierung.
Die bekannten Kontrolltexte wurden früher bereits betrachtet; keine blinde
historische Validierung und keine neue Entschlüsselung.

[Prototyp-Plan](../experiments/substitution_prototype_plan.json).

## Unabhängige Prüfung und Rechenbudget

**{count} Tests bestanden.** Der skalare Prüfer reproduziert alle **{verified}
gespeicherten E034-Kandidaten** durch Entschlüsselung und Rückverschlüsselung und
berechnet ihre Scores erneut. Die Testfälle vergleichen die vektorisierte
Suche mit vollständiger unabhängiger Enumeration eines kleinen Gitters.
Basisformeln und Invertierbarkeit werden für alle nichtnulligen Koeffizienten
geprüft. Zusätzlich wurden alle {sub_verified} gespeicherten E035-Startläufe als
vollständige Bijektionen, durch Rückverschlüsselung und durch skalare Neubewertung
kontrolliert. Alle 19 E034-Zufallstexte wurden aus den festgelegten Seeds unabhängig
bis zur ersten akzeptierten Permutation reproduziert.

Alle Ergebnis- und Abhängigkeitshashes stimmen. Historische Ergebnisse bleiben
erhalten, das Experimentprotokoll wurde ausschließlich ergänzt. Keine neuen
Fremdquellen oder Lösungsmeldungen untersucht.

76 Aufgaben, {seconds:.3f} Sekunden protokollierte Experimentzeit, E034 davon
{attack_seconds:.3f} Sekunden.
Queue {complete['seconds']:.3f} Sekunden plus {complete['prior_seconds']:.3f}
Sekunden bereits abgeschlossener Kontrolllauf, unter 750 Sekunden Familienbudget.
180 Sekunden je Aufgabe, ein Prozess; höchstens 2048 Kandidatenzeilen gleichzeitig.
Kein Hintergrundprozess bleibt aktiv.

## Nächster direkter Ansatz

{'Zunächst die größere E034-Nullkalibrierung; danach ' if not exceed else ''}Den E035-Substitutionsprototyp
mit einem separat festgelegten externen Wortgrenzen-Score weiterprüfen.
Die zwei längeren Kontrollen zeigen, dass der Ansatz praktisch ganze Texte
zurückgewinnen kann; die kurze Kontrolle verhindert derzeit die Eskalation.
Wörterbuchlücken dürfen nicht als Widerlegung ausgegeben werden.
Ein vollständiger Zufallsvergleich muss vor einer größeren Seitensuche finanzierbar
sein. Abstand-drei-Rückkopplung bleibt wegen des höheren Aufwands zurückgestellt.

[Checkpoint](../checkpoints/phase10_complete.json), [Messübersicht](../results/phase10_summary.json).
'''
    (ROOT/'reports/attack_phase10_report.md').write_text(report,encoding='utf-8')
    save('checkpoints/phase10_complete.json',{'created_at':now,'status':status,'summary':'results/phase10_summary.json',
        'summary_sha256':sha('results/phase10_summary.json'),'experiments':entries})
    print(json.dumps({k:v for k,v in summary.items() if k!='top'},ensure_ascii=True))


if __name__=='__main__':main()
