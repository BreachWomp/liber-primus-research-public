"""Preserve the partial scoring repair and failed full control gate."""
from datetime import datetime,timezone
import difflib
import json
import re
import subprocess
import sys
from verify_terminated_benchmark import ROOT,load,sha,to_indices
from liberprimus.alphabet import transliterate
from liberprimus.boundaries import segments

def save(p,data):(ROOT/p).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def main():
    assert not (ROOT/'checkpoints/phase29_complete.json').exists()
    benchmark=load('results/phase29_benchmark_validation.json');controls=load('results/phase29_controls_validation.json')
    assert benchmark['gate_passed'] and not controls['full_gate_passed']
    assert len(controls['controls'])==9 and sum(r['exact'] for r in controls['controls'])==8
    assert controls['unknown_pages_searched']==0
    entries=[{'id':'E080-terminated-benchmark',**{k:benchmark[k] for k in ('output','sha256','fingerprint')}}]+controls['entries']
    events=[json.loads(s) for s in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    done=[e for e in events if e['status']=='completed'];by_fp={e['fingerprint']:e for e in done}
    for r in entries:
        e=by_fp[r['fingerprint']];assert sha(r['output'])==r['sha256']==e['output_sha256']
        for path,digest in e['input_dependencies'].items():assert sha(path)==digest,path
    assert (ROOT/'experiment_log.jsonl').read_bytes().startswith(subprocess.check_output(['git','show','HEAD:experiment_log.jsonl'],cwd=ROOT))
    assert len(entries)==13 and not any(e['experiment'].startswith('E082') for e in events)
    processes=load('results/phase29_processes.json')
    assert len(processes)==13 and all(p['exit_code']==0 and p['reason'] is None and p['seconds']<185 and p['peak_sampled_bytes']<=768*1024**2 for p in processes)
    test=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=90)
    output=test.stdout+test.stderr;(ROOT/'results/validation_phase29.txt').write_text(output,encoding='utf-8')
    assert test.returncode==0,output
    count=int(re.search(r'Ran (\d+) tests',output)[1]);now=datetime.now(timezone.utc).isoformat()
    seconds=sum(by_fp[e['fingerprint']]['wall_seconds'] for e in entries);assert seconds<1800
    peak=max(p['peak_sampled_bytes'] for p in processes)
    status='twentyninth_batch_terminated_words_partial_repair_full_gate_failed'
    summary={'created_at':now,'status':status,'benchmark':benchmark,'controls':controls,
        'tests_passed':count,'successful_tasks':13,'seconds':seconds,'peak_sampled_bytes':peak,
        'unknown_pages_searched':0,'new_decryptions':[]}
    save('results/phase29_summary.json',summary)
    next_task='Prospectively test a separate >=200-rune general-substitution scope with the frozen BOS/EOS model:12 fresh-key/source-window controls at200/300/500/729 runes, all exact before an unknown long-page scan. This does not waive or relabel the failed E081 all-length gate. Preserve short failures; no parameter tuning on unknowns.'
    queue=[{'id':'H051','priority':1,'task':next_task},{'id':'H031','priority':2,
        'task':'Short substitution remains unvalidated: preserve E081 TRAYS/PANS versus TRAPS/YANS counterexample; defer broader language-score changes pending independent external validation.'}]
    state=load('research_state.json');old={e['fingerprint'] for e in state['completed_experiments']}
    assert not any(e['fingerprint'] in old for e in entries);state['completed_experiments']+=entries
    state.update(status=status,updated_at=now,latest_report='reports/attack_phase29_report.md',next_experiments=[q['id'] for q in queue],
        new_decryptions=[],promising_candidates=[],session_budget={'phase':'twentyninth terminated-word substitution controls',
            'max_compute_wall_seconds':1800,'max_experiment_wall_seconds':180,'memory_ceiling_mib':768,'workers':1,'background_jobs':False},
        scoring_gate='E080 local/mutation gate passed; E0818/9 blind-key controls exact. New67-rune control65/67 and wrong output outscores truth. E082 unknown scan NOT registered or run.',
        notes=['No previously unknown plaintext confirmed; only source-anchored synthetic controls in this batch.',
            'BOS/EOS word model restores old LP2-57 regression95/95; known text was not added to training.',
            'E081 independent rare-word counterexample exposes remaining word-frequency bias; no same-batch retuning.',
            'Five controls>=200runes passed, but this does not establish a long-page gate; a new prospective scope requires fresh controls.',
            'Historical outcomes preserved, no running research jobs.'])
    state['validation'].update(tests_passed=count,path='results/validation_phase29.txt',phase29={'benchmark':benchmark,'controls':controls['validation']})
    state['resources'].update(recorded_successful_experiment_runs=len(done),recorded_experiment_subprocess_wall_seconds=sum(e['wall_seconds'] for e in done),phase29_wall_seconds=seconds)
    state['failed_approaches'].append('E081 explicit-word-end substitution:8/9 controls exact; new67-rune control65/67, wrong TRAPS/YANS outranks true TRAYS/PANS. E080 diagnostic passed but full optimizer gate failed; no E082 unknown scan.')
    save('research_state.json',state)
    hypotheses=load('hypotheses.json');h=next(h for h in hypotheses['hypotheses'] if h['id']=='H031')
    assert 'terminated_word_result' not in h
    h['experiments']+=['E080','E081'];h['status']='word_end_regression_repaired_new_short_control_gate_failed'
    h['prior_E036_limits']=h['limits']
    h['limits']='E035/E036 historical results unchanged. E080 fixed BOS/EOS model passes local/mutation diagnostics; E0818/9 exact, new67-rune wrong output outscores truth. No unknown general-substitution scan. Word-frequency bias and short ambiguity remain.'
    h['terminated_word_result']={'controls_exact':8,'controls_total':9,'old_LP2_57_regression_exact':True,
        'failed_control':5,'failed_correct_positions':65,'failed_runes':67,'unknown_pages_searched':0,'summary':'results/phase29_summary.json'}
    assert not any(h['id']=='H051' for h in hypotheses['hypotheses'])
    hypotheses['hypotheses'].append({'id':'H051','status':'queued_untested_scope',
        'claim':'The fixed terminated-word substitution objective may permit direct solving on inputs of at least200runes.',
        'basis':'E081 all5 controls>=200runes exact; one67-rune rare-word error remains. This post-result observation motivates a separate prospective test, not a passed gate or cipher evidence.',
        'mechanism':'Same general29-symbol bijection and E081 frozen search/model; original lexical boundaries, restricted minimum length200.',
        'success_criterion':'Preregister12 fresh-key/source-window controls across200/300/500/729runes; require every plaintext exact before separately registering unknown long-page search with matched optimizer nulls and correction.',
        'limits':'Untested new scope; no retrospective exemption to E081. No evidence yet that an unknown LP page uses monoalphabetic substitution.'})
    hypotheses.update(status=status,updated_at=now,next_queue=queue);save('hypotheses.json',hypotheses)
    failed=next(r for r in controls['controls'] if not r['exact']);r=load(failed['output']);s=r['source'];ends=s['segment_ends']
    truth=' / '.join(transliterate(w) for w in segments(s['plaintext_indices'],ends))
    found=' / '.join(transliterate(w) for w in segments(to_indices(r['result']['top']['plaintext_runes']),ends))
    comparison=f'''# Sprachähnliche Ausgabe einer bekannten Kontrolle, Serie 29

**Kein Text einer neu entschlüsselten LP-Seite.** Dies ist ein absichtlich
verschlüsselter Emerson-Kontrolltext, dessen Lösung vorab bekannt ist.
Die Schlüsselsuche erhält nur Chiffre und Wortgrenzen. Trenner entsprechen
den festgelegten Quellwortgrenzen; GP-Schreibungen bleiben unverändert.

Quelle: Kapitel {s['chapter']}, Absatz {s['paragraph']}, Zeichenbereich
{s['source_character_range']} der unveränderten UTF-8-dekodierten Quelldatei.

Richtiger Text:
```text
{truth}
```

Bestbewertete, falsche Ausgabe:
```text
{found}
```

65/67 Runen stimmen. Score richtig {failed['truth_score']:.9f}, falsch
{failed['found_score']:.9f}; höher gilt im Modell als besser.
Der Tausch P/Y erzeugt TRAPS statt TRAYS und YANS statt PANS.
TRAPS kommt einmal im Training vor, die drei anderen Wörter keinmal.
Die Belohnung für TRAPS überwiegt die Verschlechterung PANS→YANS.
Das ist ein konkret nachgewiesener Bewertungsfehler, keine neue Lösung.

[Vollständiger Lauf](../{failed['output']}), SHA-256 `{sha(failed['output'])}`.
Die genaue reversible 29-Runen-Abbildung steht in `result.top.mapping_cipher_to_plain`.
'''
    (ROOT/'reports/phase29_control_comparison.md').write_text(comparison,encoding='utf-8')
    rows='\n'.join(f'| {r["index"]} | {r["runes"]} | {r["correct_positions"]}/{r["runes"]} | {r["truth_score"]:.6f} | {r["found_score"]:.6f} |' for r in controls['controls'])
    report=f'''# Forschungsserie 29: Wortenden und allgemeine Substitution

Stand UTC: {now}. **Keine neue Entschlüsselung. Keine unbekannten Seiten mit
diesem Verfahren durchsucht: Die festgeschriebene Kontrollbedingung scheitert.**

## E080: Ein vorab festgelegter Modellversuch

E036 bevorzugte im bekannten LP2-57-Kontrolltext TUNNELEA statt TUNNELNG.
Das neue Modell zählt Wortanfang und Wortende ausdrücklich: drei BOS-Marker,
29 Runen und ein EOS-Ereignis, Viergramm-Backoff mit alpha0,5 und Stärke 5.
Wortwahrscheinlichkeit `(count(w)+20*Q(w))/(N+20)`, Q einschließlich EOS.
Q lässt auch eine leere Emission zu; beobachtete Segmente bleiben nichtleer.
Keine zusätzlichen LP-Wörter, Rechtschreibregeln oder fallspezifischen Boni.
Das ist eine bekannte Sprachmodell-Technik, keine neue kryptographische Entdeckung.

Nur die gepinnten Emerson-Kapitel I,III,IV,V,VI,VII,VIII,IX trainieren das Modell.
II ausgeschlossen; X/XI/XII nicht zum Fit verwendet. Diese Texte wurden früher
bereits betrachtet: keine Behauptung eines historisch ungesehenen Testkorpus.
Wortgrenzen und GP-Tokenisierung bleiben wie zuvor; keine Apostroph-Zusammenführung,
keine erfundenen Seitenrandkorrekturen. Der Versuch wurde nach Kenntnis des
alten Fehlers entworfen, nicht blind gegenüber E036.

Bei allen 3 bekannten Kontrollen übertrifft die Wahrheit jede tatsächlich
verändernde einzelne Symbolvertauschung. 358/360 frische Ein-Runen-Mutationen
werden schlechter bewertet, beim alten Wortmodell 355/360. Beide Modelle
bewerten alle 342 Häufigkeits-Shuffles schlechter als ihre Ausgangstexte.
Keine p-Werte daraus: abhängige Sprachdiagnostik, kein optimierter Chiffrenangriff.
Eine getrennte Berechnung prüft {benchmark['independent_scores']} Scores gegen neu
aus den Quellbereichen gezählte Ereignisse; max. Abweichung
{benchmark['max_absolute_error']:.3g}. Tokenisierung ist bewusst gemeinsam,
Ereigniszählung und Wahrscheinlichkeitsrechnung sind getrennt implementiert.

## E081: Blind gegenüber frischen Schlüsseln

Neun neue zufällige 29-Runen-Substitutionen: drei LP-Regressionen sowie sechs
Quellfenster aus X/XI/XII. Neue Schlüssel und festgeschriebene Such-Seeds.
Die zuvor bekannte Wahrheit wird nicht an die Suche übergeben. Höchstens 24
unveränderte Wortmuster-/Häufigkeits-/Zufallsstarts, je 40 vollständige
406-Tausch-Schritte für Zeichen-Warmup und neue Wortbewertung. Keine zusätzlichen
Neustarts nach Sichtung von Fehlern. Drei identisch optimierte Kontrollnulls.

| Kontrolle | Runen | Richtige Positionen | Wahrheits-Score | Gefundener Score |
|---|---:|---:|---:|---:|
{rows}

Der alte LP2-57-Fehler ist behoben:95/95. Insgesamt jedoch nur **8/9 exakt**.
Kontrolle 5 aus Kapitel XII scheitert mit 65/67: **TRAYS/PANS → TRAPS/YANS**.
TRAPS steht einmal im Training, TRAYS/PANS/YANS fehlen. Die Logbewertung
steigt durch TRAYS→TRAPS um 7,636 und sinkt durch PANS→YANS nur um 0,934.
Die falsche Abbildung hat daher einen höheren Gesamt-Score. Das ist ein
Bewertungsproblem; längere Suche kann den richtigen Text unter diesem Score
nicht zum global besten Kandidaten machen. E080s lokale Diagnose war kein
Ersatz für den unabhängigen Kontrolllauf auf weiteren Quellfenstern.

Die 3 vollständig optimierten Nullscores der 95-Runen-Kontrolle lauten
{', '.join(f'{r["score"]:.6f}' for r in controls['nulls'])}.
Nur Fähigkeitsdiagnostik, keine Signifikanz- oder Entschlüsselungsaussage.
Die neun Texte sind keine neun unabhängigen Sprachkorpora.

## Nachprüfung und Entscheidung

{controls['validation']['independent_candidate_scores']} Kandidaten-/Wahrheitsscores,
{controls['validation']['independent_final_neighbor_scores']} abschließende Nachbarscores
und {controls['validation']['reencryptions']} Rückverschlüsselungen getrennt geprüft.
Alle ausgegebenen Abbildungen sind bijektiv. Quellfenster, Schlüssel-Seeds,
Nullziehungen, Auswahl unter Neustarts und letzte lokale Optima bestätigt.
Zwischenschritte und Initialisierungslogik wurden nicht unabhängig neu implementiert.
Nicht vorkommende Runen lassen sich aus einer Kontrolle nicht identifizieren;
Exaktheit gilt für Klartext und Abbildung der tatsächlich beobachteten Symbole.

Die vorab verlangten 9/9 werden nicht nachträglich abgeschwächt: **E082 wurde
nicht registriert oder ausgeführt.** Keine Anpassung des Modells an diesen
neuen Fehler innerhalb dieser Serie. Alle historischen E035/E036-Ergebnisse
bleiben erhalten; neue Kontrollen sind keine historischen Entschlüsselungen.

Fünf Kontrollen mit mindestens 200 Runen waren exakt. Das motiviert H051 als
separate, noch ungeprüfte Längeneinschränkung. Zunächst 12 neue, vorher festgelegte
Kontrollen mit 200/300/500/729 Runen. Erst bei vollständigem Erfolg wäre ein
direkter Angriff auf längere unbekannte Seiten zulässig. Der kurze Gegenbeleg
bleibt bestehen; seine Auslassung wird nicht als bestandener E081-Test gewertet.

{count} Tests bestanden, 13 registrierte Aufgaben,{seconds:.3f} Sekunden
Experimentzeit; maximale abgetastete Speichernutzung {peak/1024**2:.1f} MiB.
Budget 1.800 Sekunden, 180 je Aufgabe, 768 MiB, ein Worker. Nach dem fehlgeschlagenen
Gate beendet, kein weiterer Rechenaufwand für ungültige unbekannte Kandidaten.
Keine laufenden Forschungsprozesse.

[Modellplan](../experiments/terminated_substitution_plan.json),
[Kontrollplan](../experiments/terminated_controls_plan.json),
[Validierte Ergebnisse](../results/phase29_summary.json),
[Textvergleich mit Original-Wortgrenzen](phase29_control_comparison.md).
'''
    (ROOT/'reports/attack_phase29_report.md').write_text(report,encoding='utf-8')
    p=ROOT/'README.md';original=p.read_bytes().decode('utf-8');text=original.replace('\r\n','\n')
    a,b=text.index('Reproduzierbare Kryptanalyse'),text.index('Start:')
    text=text[:a]+'Reproduzierbare Kryptanalyse des Liber Primus. **Keine neue Entschlüsselung\nnachgewiesen.** Serie 29 verbessert die Substitutionsbewertung durch Wortenden:\nalte LP2-57-Kontrolle exakt, insgesamt 8/9 Kontrollen. Ein neuer kurzer\nGegenbeleg verhindert die Freigabe unbekannter Seiten.\n\n'+text[b:]
    text=text.replace('reports/attack_phase28_report.md','reports/attack_phase29_report.md',1)
    text=text.replace('## Aktueller Stand\n\n','## Aktueller Stand\n\n- E080: explizite Wortenden, 358/360 Mutationen richtig bewertet; getrennte Nachrechnung.\n- E081: 8/9 Substitutionskontrollen exakt; neuer 67-Runen-Gegenbeleg, keine unbekannten Seiten angegriffen.\n',1)
    groups=len({e['experiment'].split('-')[0] for e in done})
    text=re.sub(r'- \d+ Tests bestanden; \d+ Experimentgruppen',f'- {count} Tests bestanden; {groups} Experimentgruppen',text,count=1)
    a=text.index('Nächste Priorität:');b=text.index('Kein Hintergrundprozess',a)
    text=text[:a]+'Nächste Priorität: H051 separat für mindestens 200 Runen prüfen: 12 neue Kontrollen vor einem direkten Angriff auf längere Seiten. Das fehlgeschlagene E081-Gate bleibt unverändert.\n'+text[b:]
    before,after=original.splitlines(keepends=True),text.splitlines(keepends=True);out=[]
    matcher=difflib.SequenceMatcher(a=[x.rstrip('\r\n') for x in before],b=[x.rstrip('\r\n') for x in after],autojunk=False)
    for tag,a,b,c,d in matcher.get_opcodes():out.extend(before[a:b] if tag=='equal' else after[c:d])
    p.write_bytes(''.join(out).encode('utf-8'))
    save('checkpoints/phase29_complete.json',{'created_at':now,'status':status,'summary':'results/phase29_summary.json',
        'summary_sha256':sha('results/phase29_summary.json'),'experiments':entries})
    print({'status':status,'tests_passed':count,'seconds':seconds,'unknown_pages_searched':0})


if __name__=='__main__':main()
