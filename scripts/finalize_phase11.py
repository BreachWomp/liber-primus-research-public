"""Independent scalar replay of both phase11 families and persistent checkpoint."""
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
from heldout_language import corpus,make_models,tokenize
from liberprimus.boundaries import segments

def load(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))
def save(path,data):(ROOT/path).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def main():
    if (ROOT/'checkpoints/phase12_complete.json').exists():raise RuntimeError('Newer checkpoint exists')
    complete=load('checkpoints/phase11_quadratic_complete.json')
    tests=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,
        capture_output=True,encoding='utf-8',text=True,timeout=60)
    output=tests.stdout+tests.stderr;(ROOT/'results/validation_phase11.txt').write_text(output,encoding='utf-8')
    if tests.returncode:raise RuntimeError(output)
    count=int(re.search(r'Ran (\d+) tests',output)[1]);now=datetime.now(timezone.utc).isoformat()
    events=[json.loads(line) for line in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    done=[e for e in events if e['status']=='completed'];latest={e['experiment']:e for e in done}
    phase={k:e for k,e in latest.items() if k.startswith(('E036-','E037-'))};assert len(phase)==76
    for e in phase.values():
        assert sha(e['output'])==e['output_sha256']
        for path,digest in e['input_dependencies'].items():assert sha(path)==digest,path
        assert e['wall_seconds']<180
    data={k:load(e['output']) for k,e in phase.items()}
    fixtures={f['id']:f for f in load('known_solutions/fixtures.json')}
    # Independent scalar replay, using the equation directly, not search helpers.
    model=external_model(4);verified=0
    def verify(cipher,row):
        nonlocal verified
        a,b,c,d=[row['recipe'][k] for k in ('a','b','c','d')]
        assert 1<=a<29 and all(0<=x<29 for x in (b,c,d)) and (b or c)
        plain=to_indices(row['plaintext_runes']);assert len(plain)==len(cipher)
        assert plain==[(a*x+b*i*i+c*i+d)%29 for i,x in enumerate(cipher)]
        assert cipher==[(pow(a,-1,29)*(x-b*i*i-c*i-d))%29 for i,x in enumerate(plain)]
        assert abs(model.score(plain)-row['score'])<1e-9
        verified+=1
    controls=data['E037-controls'];assert controls['gate_passed'] and len(controls['controls'])==3
    for ctrl in controls['controls']:
        truth=to_indices(fixtures[ctrl['fixture']]['plaintext_runes']);a,b,c,d=ctrl['injected']
        cipher=[(pow(a,-1,29)*(x-b*i*i-c*i-d))%29 for i,x in enumerate(truth)]
        assert ctrl['ciphertext_indices']==cipher and ctrl['exact'] and ctrl['recipes']==682080
        assert ctrl['top'][0]['plaintext_runes']==fixtures[ctrl['fixture']]['plaintext_runes']
        for row in ctrl['top']:verify(cipher,row)
    pages=[r for k,r in data.items() if k.startswith('E037-page-')];assert len(pages)==55
    assert {r['page'] for r in pages}=={f'LP2-{n:02}' for n in range(56) if n!=50}
    canonical={p['id']:p for p in load('transcriptions/pages.json')}
    for page in pages:
        assert page['ciphertext_indices']==to_indices(canonical[page['page']]['runes']) and page['recipes']==682080
        assert page['score']==page['top'][0]['score']
        for row in page['top']:verify(page['ciphertext_indices'],row)
    winner=max(pages,key=lambda r:r['score']);selection=load('experiments/quadratic_stream_selection.json')
    assert sha('experiments/quadratic_stream_selection.json')==complete['selection_sha256']
    assert winner['page']==selection['selected_page']==complete['selected_page']
    assert winner['score']==selection['observed_score'] and len(selection['source_outputs'])==56
    assert selection['seed']==3301037 and selection['replicates']==19
    for path,digest in selection['source_outputs'].items():assert sha(path)==digest
    nulls=[r for k,r in data.items() if k.startswith('E037-null-')];assert len(nulls)==19
    doublets=lambda v:sum(a==b for a,b in zip(v,v[1:]));cipher=winner['ciphertext_indices']
    for null in nulls:
        assert Counter(null['ciphertext_indices'])==Counter(cipher)
        assert doublets(null['ciphertext_indices'])==doublets(cipher) and null['recipes']==682080
        rng=random.Random(3301037+null['parameters']['replicate'])
        for proposal in range(1,100001):
            sample=cipher[:];rng.shuffle(sample)
            if doublets(sample)==doublets(cipher):break
        else:raise AssertionError('Null rejection exhausted')
        assert sample==null['ciphertext_indices'] and proposal==null['shuffle_proposals']
        assert null['score']==null['top'][0]['score']
        verify(sample,null['top'][0])
    exceed=sum(r['score']>=winner['score'] for r in nulls);p=(exceed+1)/20
    assert exceed==complete['exceedances'] and p==complete['raw_p']
    # Recompute E036 from scalar WordModel. Replay injections, null RNG and both stages.
    external=corpus();words,_,metadata=make_models(external);prototype=data['E036-boundary-substitution-controls']
    assert metadata==prototype['training'] and not prototype['gate_passed'] and prototype['unknown_pages_searched']==0
    assert metadata['training_chapters']==['I','III','IV','V','VI','VII','VIII','IX']
    sub_verified=0;sub_diagnostics=[];injection=random.Random(3301036)
    layouts={r['fixture']:r['segment_ends'] for r in load('results/E026-boundary-audit-314198a84563.json')['controls']}
    for j,ctrl in enumerate(prototype['controls']):
        truth=to_indices(fixtures[ctrl['fixture']]['plaintext_runes']);ends=ctrl['segment_ends']
        assert ends==layouts[ctrl['fixture']]
        perm=list(range(29));injection.shuffle(perm)
        source=[perm[x] for x in truth]
        assert perm==ctrl['permutation_plain_to_cipher'] and source==ctrl['ciphertext_indices']
        assert ctrl['search_seed']==3303036+100*j
        cases=[(source,ctrl['result'])]
        for null in ctrl['nulls']:
            sample=source[:];random.Random(3302036+100*j+null['replicate']).shuffle(sample)
            assert sample==null['ciphertext_indices']
            cases.append((sample,null['result']))
        for sample,result in cases:
            for stage,word_stage in ((result,True),(result['warmup'],False)):
                assert 1<=len(stage['restarts'])<=24
                assert stage['top']==max(stage['restarts'],key=lambda r:r['score'])
                for row in stage['restarts']:
                    mapping=row['mapping_cipher_to_plain'];assert sorted(mapping)==list(range(29))
                    plain=to_indices(row['plaintext_runes'])
                    assert plain==[mapping[x] for x in sample] and sample==[mapping.index(x) for x in plain]
                    score=words.score(plain,ends) if word_stage else words.character_model.score(plain)
                    assert abs(score-row['score'])<1e-9
                    steps=row['word_accepted_swaps'] if word_stage else row['accepted_swaps']
                    evaluations=row['word_evaluations'] if word_stage else row['evaluations']
                    assert 0<=steps<=40 and 1<=evaluations<=1+40*406
                    sub_verified+=1
            assert result['evaluations']==result['warmup']['evaluations']+sum(r['word_evaluations'] for r in result['restarts'])
        found=to_indices(ctrl['result']['top']['plaintext_runes']);truth_score=words.score(truth,ends)
        assert abs(truth_score-ctrl['truth_word_score'])<1e-9
        assert ctrl['exact']==(found==truth) and ctrl['correct_positions']==sum(a==b for a,b in zip(found,truth))
        sub_diagnostics.append({'fixture':ctrl['fixture'],'exact':ctrl['exact'],'runes':len(truth),
            'correct_positions':ctrl['correct_positions'],'truth_score':truth_score,'best_score':ctrl['result']['top']['score'],
            'wrong_plaintext_outscores_truth':found!=truth and ctrl['result']['top']['score']>truth_score+1e-12,
            'mismatches':[{'offset':i,'truth_index':a,'found_index':b} for i,(a,b) in enumerate(zip(truth,found)) if a!=b]})
    assert sum(r['exact'] for r in sub_diagnostics)==2 and sub_diagnostics[-1]['wrong_plaintext_outscores_truth']
    # Source-anchored holdout and identical independently regenerated mutations.
    raw=(ROOT/'data/raw/gutenberg/pg2944.txt').read_bytes().decode('utf-8-sig')
    eligible=[r for chapter in ('X','XI','XII') for r in
              [s for s in external if s['chapter']==chapter and len(s['words'])>=20][:6]]
    assert len(eligible)==len(prototype['heldout'])==18
    rng=random.Random(3304036);wins=[0,0]
    for src,row in zip(eligible,prototype['heldout']):
        assert row['source_character_range']==src['source_character_range'] and row['chapter']==src['chapter']
        a,b=row['source_character_range'];source_words=tokenize(raw[a:b])[0][:20]
        assert list(segments(row['values'],row['segment_ends']))==[list(w) for w in source_words]
        assert all(b<=x or a>=y for x,y in metadata['training_source_ranges'])
        truth_scores=[words.character_model.score(row['values']),words.score(row['values'],row['segment_ends'])]
        assert all(abs(x-y)<1e-9 for x,y in zip(truth_scores,row['truth_scores']))
        for mutation in row['mutations']:
            sample=row['values'][:];pos=rng.randrange(len(sample));replacement=(sample[pos]+rng.randrange(1,29))%29
            assert pos==mutation['position'] and replacement==mutation['replacement'];sample[pos]=replacement
            scores=[words.character_model.score(sample),words.score(sample,row['segment_ends'])]
            assert all(abs(x-y)<1e-9 for x,y in zip(scores,mutation['scores']))
            for k in range(2):wins[k]+=truth_scores[k]>scores[k]+1e-12
    assert wins==prototype['heldout_wins_character_word'] and prototype['heldout_comparisons']==360
    checks={'all_controls_exact':all(r['exact'] for r in sub_diagnostics),
            'heldout_word_rate_at_least_095':wins[1]/360>=.95,
            'heldout_loss_at_most_001':(wins[1]-wins[0])/360>=-.01}
    assert checks==prototype['gate_checks'] and all(checks.values())==prototype['gate_passed']
    seconds=sum(e['wall_seconds'] for e in phase.values())
    assert seconds<900 and complete['prior_seconds']+complete['seconds']<650
    summary={'created_at':now,'selected_page':winner['page'],'top':winner['top'][0],
        'unknown_pages':55,'rules_per_page':682080,'unknown_rules_evaluated':55*682080,
        'controls_exact':3,'raw_p':p,'bonferroni55':min(1,55*p),'null_exceedances':exceed,'null_replicates':19,
        'pending_larger_calibration':exceed==0,'candidate_records_recomputed':verified,
        'substitution_candidate_records_recomputed':sub_verified,'substitution_controls':sub_diagnostics,
        'substitution_gate_passed':False,'substitution_unknown_pages_searched':0,
        'heldout_wins_character_word':wins,'heldout_comparisons':360,'tests_passed':count,
        'successful_tasks':len(phase),'seconds':seconds,'orchestration_seconds':complete['seconds'],
        'preexisting_seconds_including_reserve':complete['prior_seconds'],
        'family_accounted_seconds':complete['prior_seconds']+complete['seconds'],
        'family_budget_seconds':650,'new_decryptions':[]}
    save('results/phase11_summary.json',summary)
    finish(summary,phase,done,prototype,now)


def finish(summary,phase,done,prototype,now):
    s=summary;exceed=s['null_exceedances']
    entries=[{'id':k,'fingerprint':e['fingerprint'],'output':e['output'],'sha256':e['output_sha256']} for k,e in phase.items()]
    status='eleventh_batch_complete_no_new_decryption' if exceed else 'eleventh_batch_candidate_requires_larger_null'
    queue=([{'id':'E037-larger-null','priority':0,'task':'Freeze E037 winner and preregister larger fresh full-grid matched-null calibration.'}] if not exceed else [])+[
        {'id':'H033','priority':1,'task':'Direct unknown repeating-key attack beyond the381literal keys: preregister bounded search for arbitrary rune keys of periods2..16, recover historical DIVINITY/CIRCUMFERENCE controls and source-excluded external synthetic controls before scanning unknown pages. Same optimizer and selection in matched nulls. Account for periodic symmetries; no claim of exhaustive29^period search.'},
        {'id':'H031','priority':2,'task':'Pause large substitution scans: E035 and E036 objectives rank incorrect short text above truth. Keep full evidence. Revisit only with independently justified additional context or calibration; do not tune to the single wrong rune.'},
        {'id':'H023','priority':3,'task':'Delay3 plaintext feedback remains deferred pending feasible control/null-calibrated reduction.'}]
    state=load('research_state.json');known={r['fingerprint'] for r in state['completed_experiments']}
    state['completed_experiments'] += [e for e in entries if e['fingerprint'] not in known]
    state.update(status=status,updated_at=now,latest_report='reports/attack_phase11_report.md',
        next_experiments=[r['id'] for r in queue],
        promising_candidates=[] if exceed else [{'page':s['selected_page'],'status':'screen_maximum_requires_larger_null'}],
        validation={'tests_passed':s['tests_passed'],'path':'results/validation_phase11.txt',
                    'phase11_candidate_records_recomputed':s['candidate_records_recomputed'],
                    'phase11_substitution_candidate_records_recomputed':s['substitution_candidate_records_recomputed']},
        session_budget={'phase':'eleventh bounded substitution-control and quadratic-stream queue',
                        'max_compute_wall_seconds':900,'max_experiment_wall_seconds':180,'workers':1,'background_jobs':False},
        scoring_gate='E036 boundary substitution2/3 exact and355/360 heldout wins: full gate failed because wrong short control outranks truth. No substitution unknown scan. Independent E037 quadratic-stream family3/3 exact.',
        notes=['No previously unknown plaintext confirmed.','Direct solving only; no community-claim audits.',
               'E036 recovers515/515,319/319,94/95 runes. Short error remains an objective limitation, not merely search failure.',
               'E037 exhausts the declared degree<=2 progressive-key family on all55unknown rune pages; no source normalization or raw-data changes.',
               'E036 plan conditionally earmarked E037 for substitution, but its failed gate prevented that experiment. E037 is instead a separately preregistered quadratic-stream family, with its own passed gate.',
               'No research process remains running.'])
    state['resources'].update(recorded_successful_experiment_runs=len(done),
        recorded_experiment_subprocess_wall_seconds=sum(e['wall_seconds'] for e in done),phase11_wall_seconds=s['seconds'])
    message=f'E037 polynomial degree<=2 progressive keys on55pages: {s["selected_page"]}, rawp={s["raw_p"]}, adjusted={s["bonferroni55"]}; no supported plaintext.'
    if exceed and message not in state['failed_approaches']:state['failed_approaches'].append(message)
    save('research_state.json',state)
    hypotheses=load('hypotheses.json')
    old=next(h for h in hypotheses['hypotheses'] if h['id']=='H031')
    old.update(experiments=['E035','E036'],status='control_gate_failed_under_both_objectives',
        boundary_result={'controls':s['substitution_controls'],'heldout_wins_character_word':s['heldout_wins_character_word'],
                         'heldout_comparisons':360},
        limits='E036 training excludes chaptersX/XI/XII for both objectives.355/360 mutation wins, but short LP control94/95 and wrong output outranks truth. No unknown substitution scan; no control-specific tuning.')
    hypotheses['hypotheses']=[h for h in hypotheses['hypotheses'] if h['id'] not in ('H032','H033')]+[
        {'id':'H032','claim':'A degree<=2 polynomial additive key modulo29 with nonzero affine rune multiplier can reveal unknown plaintext.',
         'experiments':['E037'],'status':'finite_screen_complete' if exceed else 'larger_null_required','result':s,
         'basis':'Low-complexity progressive-key family not exhausted by named numerical streams. No specific historical clue asserted.',
         'limits':'All682080declared rules per page; no broad exclusion of arbitrary periodic or nonpolynomial keys. Exploratory selection; nineteen nulls cannot resolve corrected significance.'},
        {'id':'H033','claim':'Unknown repeating rune keys outside the381literal-key catalogue may recover unknown pages.',
         'status':'queued','basis':'Historically reproduced DIVINITY and CIRCUMFERENCE solutions establish repeating-key mechanisms; earlier literal searches do not cover arbitrary key material.',
         'mechanism':'Repeating modular additive key with source-order runes; separately specify signs and interruption policies before execution.',
         'parameters':'Proposed periods2..16 and bounded coordinate/beam or restart optimization; freeze detailed seeds and controls before execution.',
         'cost':'Benchmark first; full55page and matched-null optimization must fit a separately declared family budget.',
         'success_criterion':'Exact known controls plus external source-excluded synthetic recovery; source-reversible unknown candidate survives full optimizer null comparison and selection correction.',
         'rejection_criterion':'Failed positive controls or infeasible matched-null runtime prevents broad escalation.',
         'limits':'Heuristic optimization is not exhaustive over29^period; short controls need calibrated treatment and no candidate-driven score tuning.'}]
    hypotheses.update(status=status,updated_at=now,next_queue=queue);save('hypotheses.json',hypotheses)
    report=f'''# Elfte Forschungsserie: Wortbewertung und fortschreitende Schlüssel

Stand (UTC): {now}. **Keine neue Entschlüsselung bestätigt.**

## Direkter Angriff E037

Geprüft wurde `P_i = a*C_i + b*i² + c*i + d mod29`, i=0 am Seitenanfang.
a durchläuft 1–28, b,c,d jeweils 0–28. b=c=0 bleibt ausgespart,
weil konstante affine Ersetzungen bereits untersucht wurden.
**682.080 Regeln je Seite, 37.514.400 Regeln auf allen 55 ungelösten
Runenseiten.** LP2-50 bleibt als Zahlenseite erhalten.

Die Rückverschlüsselung ist `C_i = a^-1*(P_i-b*i²-c*i-d) mod29`.
Keine Rune wird entfernt oder ausgelassen. Keine F-Unterbrechung, Umordnung
oder behauptete Ergänzung. Die Schlüsselfolge hat modulo29 eine Periode, die 29 teilt.
Verschobene Indexursprünge und die Umkehr der Indexrichtung sind bereits in
den Koeffizienten enthalten; sie benötigen keine zusätzliche Suche.
Das ist eine kleine, prüfbare progressive Schlüsselfamilie, kein behaupteter
historischer Hinweis. Beliebige Perioden-29-Schlüssel werden dadurch nicht abgedeckt.

Drei synthetisch verschlüsselte bekannte Texte werden im vollständigen Suchraum
exakt als bestes Ergebnis gefunden, darunter ein linearer Fall mit b=0 und
der kurze LP2-57-Text. Der externe Viergramm-Score von E016 bleibt unverändert.
Kein LP-Text ist Trainingsmaterial; die Kontrolltexte wurden allerdings schon
in früheren Versuchen betrachtet. Dies ist Funktionsvalidierung, keine neue
historische Entschlüsselung.

Stärkster Treffer: **{s['selected_page']}**, Score {s['top']['score']:.6f}.
Regel: `{json.dumps(s['top']['recipe'])}`.
Unveränderte Transliteration:

```text
{s['top']['transliteration']}
```

Dieser Suchtreffer ist kein bestätigter Klartext. Vor den Zufallsversuchen
wurden Auswahl und alle Quellergebnis-Prüfsummen eingefroren.
19 unabhängige Zufallstexte erhalten exakt die Runenhäufigkeiten und die Anzahl
gleicher Nachbarpaare. Jeder durchläuft dieselbe vollständige Suche.
**{exceed}/19** erreichen mindestens den beobachteten Score.
Plus-eins-p={s['raw_p']:.3f}; Bonferroni55={s['bonferroni55']:.3f}.
Die 19 Replikate können korrigierte Signifikanz nicht auflösen.
{'Eine größere frische Kalibrierung ist vorgemerkt; noch keine Signifikanzbehauptung.' if not exceed else 'Dieser Vergleich liefert keinen Anlass, den Treffer als Lösung weiterzuverfolgen.'}
Der Seitenfaktor ist keine projektweite Korrektur über alle bisherigen
explorativen Hypothesen. Ein negativer Befund widerlegt keine umfassendere
Verschlüsselungsfamilie.

[Plan](../experiments/quadratic_stream_plan.json),
[eingefrorene Auswahl](../experiments/quadratic_stream_selection.json).

## E036: Wortgrenzen beheben das Substitutionsproblem noch nicht

Vor E037 wurde der allgemeine Substitutionssolver mit dem unveränderten
E027-Wortmodell geprüft: `P(w|L)=(count(w)+20*Q(w))/(N_L+20)`.
Q ist das Zeichenmodell, jeweils am Wortanfang neu gestartet.
Training für Wörterbuch und Zeichenmodell ausschließlich auf Emerson I,
III–IX; X, XI, XII ausgeschlossen. Keine LP-Texte im Training.
Diese Kapitel sind gegenüber diesem Training zurückgehalten, wurden aber
schon in früheren Projektphasen verwendet; kein historisch frischer Blindtest.

Höchstens 24 Muster-/Häufigkeitsstarts, erst höchstens 40 vollständige
406-Tausch-Schritte nach Zeichenwertung, dann höchstens 40 nach Wortwertung.
Die endgültige Auswahl erfolgt nur nach Wortwertung.

| Kontrolle | Exakt richtige Runen | Vollständig |
|---|---:|---|
| LP1-03/04, DIVINITY-Text neu substituiert | 515/515 | ja |
| LP1-14/15, CIRCUMFERENCE-Text neu substituiert | 319/319 | ja |
| LP2-57, Direkttext neu substituiert | 94/95 | nein |

Bei LP2-57 wird Offset 25 von NG (Index 21) zu EA (Index 28) geändert.
Der korrekte Text erzielt {s['substitution_controls'][-1]['truth_score']:.6f},
der falsche {s['substitution_controls'][-1]['best_score']:.6f}.
Der Score bevorzugt den Fehler; zusätzliche Suchzeit allein kann diesen
Rankingfehler nicht beheben. Keine gezielte Modellanpassung an diese Rune.

18 externe Fenster aus X, XI, XII mit je 20 Wörtern und je 20 vorab gesäten
Ein-Runen-Mutationen: Wortscore **{s['heldout_wins_character_word'][1]}/360**
korrekte Rangfolgen, Zeichenmodell **{s['heldout_wins_character_word'][0]}/360**.
Das externe Teilkriterium besteht, die geforderte exakte Wiedergewinnung
aller drei LP-Kontrollen jedoch nicht. **Kein unbekannter Text wurde mit
diesem Substitutionssolver gesucht.**
Neun zusätzliche Optimierungsläufe auf Häufigkeits-permutierten Kontrolltexten
sind Fähigkeitsdiagnosen; sie konditionieren nicht auf gleiche Nachbarpaare
und tragen keinen Entdeckungs-p-Wert.

E036 hatte die Nummer E037 bedingt für eine nachfolgende Substitutionssuche
vorgesehen. Diese Bedingung trat nicht ein. E037 bezeichnet stattdessen
den separat festgelegten progressiven Schlüsselstrom mit eigenen Kontrollen.
Der historische E036-Plan wird unverändert erhalten.

[E036-Plan](../experiments/boundary_substitution_plan.json).

## Prüfung und nächster Angriff

**{s['tests_passed']} Tests bestanden.** Alle {s['candidate_records_recomputed']}
gespeicherten E037-Kandidaten wurden unabhängig mit der skalaren Gleichung
entschlüsselt, rückverschlüsselt und neu bewertet. Alle
{s['substitution_candidate_records_recomputed']} gespeicherten E036-Startläufe
beider Suchstufen wurden als Bijektionen und durch skalare Scores überprüft.
Alle Seeds der Kontrollverschlüsselungen, Mutationen und Zufallstexte wurden
reproduziert; die 18 Prüffenster auf originale Quellenpositionen zurückgeführt
und die Trennung ihrer Quellbereiche vom Training geprüft.
Ergebnis- und Abhängigkeitshashes stimmen.

{s['successful_tasks']} Aufgaben, {s['seconds']:.3f} Sekunden protokollierte
Experimentzeit; E037 einschließlich Wiederaufnahme und Reserve
{s['family_accounted_seconds']:.3f} Sekunden unter 650.
Phasenbudget 900, Einzelaufgabe 180 Sekunden, ein Prozess, begrenzte Arrays.
Keine laufenden Hintergrundjobs, keine neuen Fremdquellen oder Lösungsmeldungen.

Vor Beginn der Nullversuche wurde der Queue-Prozess einmal gestoppt, um einen
kopierten Seed-Vermerk für die Auswahldatei zu korrigieren. Der tatsächliche
Such-/Nullcode und sein vorab festgelegter Seed 3301037 blieben unverändert.
Der aktive LP2-52-Prozess scheiterte bei der Rückmeldung an die geschlossene
Pipe (`OSError(22)`); sein Fehlereintrag bleibt im Log. Dieser fehlgeschlagene
Versuch wurde wiederholt, alle erfolgreich abgeschlossenen Fingerprints
wurden übersprungen. Zusätzlich zu erfolgreichen Prozesszeiten und der neuen
Queuezeit sind 60 Sekunden Reserve für diesen fehlgeschlagenen Lauf
(5,875 Sekunden) und den alten Ablaufaufwand eingerechnet, keine als Messung
ausgegebene Zeit.
[Ablaufvermerk](../checkpoints/phase11_orchestration_interruption.json).

Als nächster direkter Ansatz sind beliebige wiederholte Runenschlüssel
außerhalb des bisherigen Katalogs von 381 Wörtern vorgesehen. Die bekannten
DIVINITY-/CIRCUMFERENCE-Lösungen liefern passende Kontrollen. Perioden 2–16,
Suchbudget und Zufallsvergleich werden vor Ausführung getrennt festgelegt;
heuristische Suche darf nicht als vollständige Prüfung von 29^Periode gelten.
Die allgemeine Substitution bleibt bis zu einer unabhängig begründeten
Verbesserung der Textbewertung zurückgestellt.

[Checkpoint](../checkpoints/phase11_complete.json),
[Messübersicht](../results/phase11_summary.json).
'''
    (ROOT/'reports/attack_phase11_report.md').write_text(report,encoding='utf-8')
    save('checkpoints/phase11_complete.json',{'created_at':now,'status':status,'summary':'results/phase11_summary.json',
        'summary_sha256':sha('results/phase11_summary.json'),'experiments':entries})
    print(json.dumps({k:v for k,v in s.items() if k!='top'},ensure_ascii=True))


if __name__=='__main__':main()
