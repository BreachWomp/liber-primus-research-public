"""Checkpoint validated E052/E053 evidence without altering prior outcomes."""
from collections import Counter
from datetime import datetime,timezone
import difflib
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
def load(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))
def save(path,value):(ROOT/path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def main():
    if (ROOT/'checkpoints/phase19_complete.json').exists():raise RuntimeError('Newer checkpoint exists')
    controls=load('results/phase18_control_validation.json');unknown=load('results/phase18_unknown_validation.json')
    assert controls['gate_passed'] and controls['successful_tasks']==7 and unknown['successful_tasks']==28
    assert unknown['unique_unknown_rune_pages']==55 and unknown['empty_pages_preserved']==['LP2-50']
    tests=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=60)
    output=tests.stdout+tests.stderr;(ROOT/'results/validation_phase18.txt').write_text(output,encoding='utf-8')
    if tests.returncode:raise RuntimeError(output)
    count=int(re.search(r'Ran (\d+) tests',output)[1]);now=datetime.now(timezone.utc).isoformat()
    entries=controls['entries']+unknown['entries']
    events=[json.loads(x) for x in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    done=[e for e in events if e['status']=='completed'];latest={e['experiment']:e for e in done}
    for entry in entries:
        event=latest[entry['id']]
        assert sha(entry['output'])==entry['sha256']==event['output_sha256']
        for path,digest in event['input_dependencies'].items():assert sha(path)==digest,path
    validation=Counter(controls['validation']);validation.update(unknown['validation'])
    stage_audit=[]
    canonical=lambda key:min(tuple(key[i:]+key[:i]) for i in range(len(key)))
    for entry in controls['entries']:
        row=load(entry['output'])
        if row['kind']=='null':continue
        source=row['source'];result=row['result'];key=canonical(source['injected_key'])
        match=lambda state:state['sign']==source['injected_sign'] and canonical(state['key'])==key
        stage_audit.append({'kind':row['kind'],'chapter':source['chapter'],
            'exact_unigram_start_indices':[s['start'] for s in result['unigram_starts'] if match(s)],
            'exact_bigram_pool_states':sum(match(s) for f in result['families'] for c in f['candidates'] for s in c['pool_trace'] if s['order']==2),
            'exact_fourgram_pool_states':sum(match(s) for f in result['families'] for c in f['candidates'] for s in c['pool_trace'] if s['order']==4),
            'exact_final_key_count':sum(match(r['final']) for r in result['restarts'])})
    summary={'controls':controls['controls'],'control_gate_passed':True,
             'control_key_stage_audit':stage_audit,
             'control_diagnostic_null_score':controls['null_score'],
             'unknown':{k:v for k,v in unknown.items() if k not in ('entries','validation','new_decryptions')},
             'validation':dict(validation),'tests_passed':count,'successful_tasks':35,
             'seconds':controls['seconds']+unknown['seconds'],
             'peak_sampled_bytes':max(controls['peak_sampled_bytes'],unknown['peak_sampled_bytes']),
             'control_validation_sha256':sha('results/phase18_control_validation.json'),
             'unknown_validation_sha256':sha('results/phase18_unknown_validation.json'),'new_decryptions':[]}
    save('results/phase18_summary.json',summary)
    pending=unknown['pending_larger_calibration']
    status='eighteenth_batch_long_key_controls_passed_'+('null_extension_pending' if pending else 'no_unknown_evidence')
    next_item=({'id':'H039','priority':1,'task':'Preregister a larger selected-group null calibration before interpreting E053 zero-exceedance screen; retain frozen solver and observed selection.'} if pending else
        {'id':'H040','priority':1,'task':'Test long shared keys with page-local phases using the validated pooled initialization. Preregister fresh source-excluded controls at short and long target lengths, with independent phase vectors and varied F schedules; retain E052 regressions. Only after gate pass test unknown groups with full matched null optimization.'})
    queue=[next_item,{'id':'H031','priority':2,'task':'General substitution remains deferred pending independently justified scoring repair.'},
           {'id':'H023','priority':3,'task':'Delay3 feedback remains deferred pending feasible calibrated reduction.'}]
    state=load('research_state.json');existing={e['fingerprint'] for e in state['completed_experiments']}
    state['completed_experiments'] += [e for e in entries if e['fingerprint'] not in existing]
    state.update(status=status,updated_at=now,latest_report='reports/attack_phase18_report.md',
                 next_experiments=[r['id'] for r in queue],new_decryptions=[],promising_candidates=[],
                 scoring_gate='E052 all six fresh/regression controls recover exact plaintext,key,sign and Fmask, including both31-key cases; independent replay and schedule checks pass.',
                 session_budget={'phase':'eighteenth pooled initialization and direct long-key unknown search',
                     'max_compute_wall_seconds':2460,'calibration_seconds':1260,'unknown_family_seconds':1200,
                     'max_experiment_wall_seconds':180,'memory_ceiling_mib':768,'workers':1,'background_jobs':False},
                 notes=['No previously unknown plaintext confirmed.',
                        'E052 repairs all three E049 regressions and solves three fresh source-excluded ranges exactly.',
                        'E053 applies unchanged solver to nine source groups covering55 unknown rune pages; numeric LP2-50 retained.',
                        'Nineteen fully reoptimized selected-group nulls; Bonferroni9 accounts for observed group selection.',
                        'Controls use alternating copied plaintextF; success does not establish sensitivity to every possible mask or key.',
                        'All source bytes and historical results retained; no unsupported solution-claim audits or running background research.'])
    state['validation'].update(tests_passed=count,path='results/validation_phase18.txt',phase18=summary['validation'])
    state['resources'].update(recorded_successful_experiment_runs=len(done),
        recorded_experiment_subprocess_wall_seconds=sum(e['wall_seconds'] for e in done),phase18_wall_seconds=summary['seconds'])
    message=f'E053 continuous long keys17..32 on9 unknown groups: selected {unknown["selected_section"]}, {unknown["exceedances"]}/19 null exceedances, raw p={unknown["raw_p"]}, Bonferroni9={unknown["bonferroni9"]}. No new decryption; E052 control-search failure repaired.'
    if message not in state['failed_approaches']:state['failed_approaches'].append(message)
    save('research_state.json',state)
    hypotheses=load('hypotheses.json');h=next(h for h in hypotheses['hypotheses'] if h['id']=='H039')
    h.update(status='initialization_validated_unknown_scan_no_decryption',experiments=['E052','E053'],result=summary,
        limits='All six controlled long-key cases recovered; this validates those cases, not every key/mask. Unknown scan has a coarse, selection-corrected null comparison, not a decryption.')
    if not pending:
        assert not any(r['id']=='H040' for r in hypotheses['hypotheses'])
        hypotheses['hypotheses'].append({'id':'H040','status':'queued',
            'claim':'A long shared key with page-local initial phases may be testable using the repaired pooled initialization.',
            'basis':'E052 resolves the31-key initialization failure; E053 tests continuous stream alignment only. E047 previously calibrated page-local phases only for nominal periods1..16.',
            'mechanism':'Pool F-free fragments for key initialization, then joint shared-key coordinates and exact perpage phase/F-schedule optimization for periods17..32.',
            'success_criterion':'Preregister fresh source-excluded controls at short and long target lengths, synthetic phase vectors and several copied-F distributions plus E052 regressions. Exact independent reproduction before unknown scan; full optimizer nulls and group selection correction.',
            'rejection_criterion':'Failed controls or bounded-cost failure blocks unknown escalation; no unbounded key brute force.',
            'limits':'A new search family, not evidence that actual LP pages use this rule. No score tuning to unknown output.'})
    hypotheses.update(status=status,updated_at=now,next_queue=queue);save('hypotheses.json',hypotheses)
    rows='\n'.join(f'| {"Frisch" if r["kind"]=="fresh" else "Regression"} | {r["chapter"]} | {r["key_length"]} | {r["runes"]} | exakt |' for r in controls['controls'])
    observed='\n'.join(f'| {r["section"]} | {r["runes"]} | {r["key_length"]} | {r["score"]:.6f} |' for r in unknown['sections'])
    next_report=('Größere Nullkalibrierung separat registrieren und die eingefrorene Auswahl sowie den Solver beibehalten.' if pending else
                 'Lange gemeinsame Schlüssel mit eigener Startphase pro Seite prüfen: zuerst frische kurze und lange Kontrolltexte, neue Kontrollphasen und verschiedene F-Ausnahmeverteilungen, danach bei bestandenen Tests direkt die unbekannten Abschnitte.')
    report=f'''# Achtzehnte Forschungsserie: Initialisierung repariert und unbekannte Abschnitte geprüft

Stand (UTC): {now}. **Keine neue Liber-Primus-Entschlüsselung bestätigt.**
Die neue Initialisierung löst alle sechs Kontrollen exakt, darunter den zuvor
gescheiterten 31-Runen-Schlüssel. Der unveränderte Solver wurde anschließend
direkt auf neun unbekannte Abschnittsgruppen angewandt.

## E052: Gemeinsame Schlüsselinitialisierung aus Fragmenten

Regel: `P_i = s*C_i + K_j mod29`, Vorzeichen ±1. Eine ausgewählte Chiffren-F
kann unverändert ausgegeben werden, ohne eine Schlüsselstelle zu verbrauchen.
Schlüssel und Sprachkontext laufen durch den gesamten Abschnitt. Nominale
Schlüssellängen 17–32; kürzere primitive Teiler können entstehen.

Zwölf längste F-freie Fragmente ab 16 Runen, jeweils höchstens 256 Runen,
werden gemeinsam ausgewertet. Ihre Schlüsselphasen sind zunächst unabhängig.
Pro Periode und Vorzeichen gibt es 16 feste Starts: alle Phasen null,
Positionen modulo Periode, Positionen abzüglich der halben Zahl vorausgehender
Chiffren-F sowie 13 zufällige Phasenvektoren aus festem Seed. Keine wahren
Schlüssel, Masken oder Längen werden an den Solver übergeben.

Zunächst bis zu 20 Wechsel zwischen exakten Unigramm-Schlüsselkoordinaten
und Phasen. Die zwei besten zyklisch unterschiedlichen Starts pro Familie
erhalten je drei Bigramm- und drei Viergrammrunden mit höchstens sechs
Koordinatendurchläufen. Für jede nominale Länge bleibt der beste Vorzeichen-
Kandidat erhalten; vier weitere Gegenzeichen-Kandidaten ergänzen die Auswahl.
Diese 20 Starts werden auf dem vollständigen Text mit exakter bedingter
F-Zeitplansuche und bis zu drei weiteren Schlüssel-/Zeitplanrunden verfeinert.

Der Volltextscore bleibt `mean(logp4) - (m*ln29 + F_count*ln2)/N`.
Der Poolscore berücksichtigt zusätzlich die freien Fragmentphasen. Seine
Sprachkontexte beginnen an jedem Fragment neu. Nur der Volltextscore bestimmt
die finale Kandidatenrangfolge.

| Prüfung | Kapitel | Schlüssellänge | Runen | Text, Schlüssel, Vorzeichen, F-Maske |
|---|---|---:|---:|---|
{rows}

Die frischen Bereiche sind die Kapitelrunen 4000:5200 aus Emerson X, XI, XII.
Die drei Regressionen übernehmen die E049-Eingaben unverändert. Training bleibt
I und III–IX mit 207.030 Runen; Quellbereiche sind disjunkt. Die Kapitel waren
bereits bekannt; dies ist keine historisch blinde Corpusprüfung. Sämtliche
Kontrollen kopieren jede zweite Klartext-F. Die Ergebnisse belegen deshalb
noch keine gleich gute Suche unter jeder beliebigen F-Verteilung.
Die Positivkontrollen umfassen 1200 und 3316 Runen; die Empfindlichkeit für
kürzere Eingaben im erlaubten Bereich ab 512 Runen ist damit nicht separat
kalibriert. Ein negativer Befund auf kurzen Abschnitten ist besonders schwach.

Besonders relevant: Die alte XII-Kontrolle verbessert sich von 59/1200
richtigen Runen in E049 beziehungsweise 78/1200 im adaptiven E051-Versuch
auf **1200/1200**, mit exakt richtigem Schlüssel und Zeitplan. Auch der
unabhängig neu verschlüsselte 31-Runen-Fall wird vollständig rekonstruiert.
Bei der alten XII-Kontrolle enthält noch keiner der gespeicherten Unigramm-,
Bigramm- oder Viergramm-Poolzustände den exakten Schlüssel. Er entsteht erst
bei der anschließenden Volltextoptimierung. Die neue Initialisierung liefert
hier einen ausreichend guten Ausgangspunkt; sie löst den Fall nicht allein.
Ein passender, vollständig neu optimierter diagnostischer Zufallstext hat
Score {controls['null_score']:.6f}; aus diesem einzelnen Vergleich wird kein
p-Wert abgeleitet. Alle früheren Fehlschläge bleiben unverändert gespeichert.

## E053: Direkter Angriff auf unbekannte Seiten

Nach bestandener unabhängiger Kontrollprüfung wurde ein eigener Plan
registriert: neun E012-Gruppen mit mindestens 512 Runen, unveränderter Solver,
unverändertes Training. LP2-54_55 allein liegt mit 308 Runen außerhalb der
Solvergrenze; beide Seiten sind in LP2-40_55 enthalten. Insgesamt werden alle
55 unbekannten Runenseiten erfasst. Die numerische Seite LP2-50 bleibt als
leerer Runenspanneneintrag erhalten. Die Gruppengrenzen sind Hypothesen und
keine authentifizierten Chiffrengrenzen.

| Abschnitt | Runen | bester primitiver Schlüssel | Score |
|---|---:|---:|---:|
{observed}

Ausgewählt wurde **{unknown['selected_section']}** mit Score
**{unknown['observed_score']:.6f}**. Die Auswahl wurde vor dem ersten Nulltext
mit den Hashes aller neun beobachteten Ergebnisse eingefroren.

Jeder von 19 Nulltexten erhält seitenweise dieselben Runenhäufigkeiten,
Randrunen und die Anzahl gleicher Nachbarpaare. Der komplette Solver wird
einschließlich sämtlicher Starts, Längen und Vorzeichen neu ausgeführt.
**{unknown['exceedances']} von 19** Nulltexten erreichen mindestens den
beobachteten Score. Roh-p = **{unknown['raw_p']:.2f}**, nach Bonferroni über
neun Abschnittsgruppen **{unknown['bonferroni9']:.2f}**.

Dieser Vergleich ist ein grobes Screening: Mit 19 Nulltexten kann der
korrigierte Wert niemals unter 0,45 fallen. Bei null Überschreitungen wäre
eine separat registrierte größere Kalibrierung nötig. Keine sprachähnliche
Ausgabe dieses Laufs wird als Entschlüsselung bezeichnet. Das Ergebnis
schließt die Chiffrenfamilie oder beliebige lange Schlüssel nicht aus.

## Unabhängige Prüfung und Ressourcen

{count} Tests bestanden. Zusätzlich {validation['pool_records_recomputed']}
skalare Prüfungen gespeicherter Poolzustände und {validation['stream_records_recomputed']}
Volltextzustandsprüfungen einschließlich Rückverschlüsselung;
{validation['independent_pool_phase_optima']}
Fragmentphasen-Maxima separat enumeriert und {validation['independent_stream_optima']}
Volltext-Zeitplanmaxima mit separatem Score-Viterbi bestätigt. Die Top-Auswahl
auf jeder Stufe, Quellbereiche, Zufallsschlüssel, Nulltexte und alle Ergebnis-
und Abhängigkeitshashes wurden nachgerechnet.

35 registrierte Aufgaben, {summary['seconds']:.3f} Sekunden erfolgreiche
Experimentzeit. Maximal 180 Sekunden je Aufgabe; E052-Budget 1260 Sekunden,
E053-Budget 1200 Sekunden; ein Experimentprozess. Gemessener höchster
abgetasteter Resident-/Private-Speicherwert {summary['peak_sampled_bytes']/1024**2:.1f} MiB,
Abbruchgrenze 768 MiB. Die Messung erfolgt alle 250 ms und ist kein Beweis
einer exakten kurzfristigen Spitzenbelegung. Originalquellen und historische
Ergebnisse bleiben unverändert; keine weiterlaufenden Forschungsprozesse.

Nächste priorisierte Prüfung: {next_report}

[Kontrollplan](../experiments/fragment_initialization_plan.json),
[Angriffsplan](../experiments/fragment_initialization_unknown_plan.json),
[Messübersicht](../results/phase18_summary.json),
[Checkpoint](../checkpoints/phase18_complete.json).
'''
    (ROOT/'reports/attack_phase18_report.md').write_text(report,encoding='utf-8')
    readme=ROOT/'README.md';original=readme.read_bytes().decode('utf-8');normalized=original.replace('\r\n','\n')
    start=normalized.index('Reproduzierbare Kryptanalyse');end=normalized.index('Start:',start)
    revised=normalized[:start]+('Reproduzierbare Kryptanalyse des Liber Primus. **Keine neue Entschlüsselung\n'
        'nachgewiesen.** Die achtzehnte Forschungsserie behebt den Suchfehler bei\n'
        'langen Schlüsseln: sechs Kontrollen mit 17, 23 und 31 Runen exakt.\n'
        f'Neun unbekannte Abschnittsgruppen geprüft; stärkster Kandidat im\nZufallsvergleich p={unknown["raw_p"]:.2f}, korrigiert {unknown["bonferroni9"]:.2f}.\n\n')+normalized[end:]
    revised=revised.replace('Start: [Aktueller Forschungsbericht](reports/attack_phase17_report.md)',
                            'Start: [Aktueller Forschungsbericht](reports/attack_phase18_report.md)')
    revised=revised.replace('- 108 Tests bestanden; 51 Experimentgruppen',f'- {count} Tests bestanden; 53 Experimentgruppen')
    marker='## Aktueller Stand\n\n'
    addition=('- E052 repariert die gemeinsame Initialisierung langer Schlüssel: alle sechs\n'
              '  frischen Kontrollen und Regressionen exakt; früherer 31-Runen-Fehler behoben.\n'
              f'- E053 prüft neun unbekannte Gruppen mit 19 vollständigen Nullsuchen: {unknown["exceedances"]}/19\n'
              f'  Nullscores mindestens so hoch; korrigiertes p={unknown["bonferroni9"]:.2f}, keine neue Lösung.\n')
    revised=revised.replace(marker,marker+addition,1)
    # Keep unchanged README lines byte-for-byte, including its historical mixed EOLs.
    before=original.splitlines(keepends=True);after=revised.splitlines(keepends=True)
    matcher=difflib.SequenceMatcher(a=[x.rstrip('\r\n') for x in before],b=[x.rstrip('\r\n') for x in after],autojunk=False)
    out=[]
    for tag,a,b,c,d in matcher.get_opcodes():out.extend(before[a:b] if tag=='equal' else after[c:d])
    readme.write_bytes(''.join(out).encode('utf-8'))
    save('checkpoints/phase18_complete.json',{'created_at':now,'status':status,'summary':'results/phase18_summary.json',
         'summary_sha256':sha('results/phase18_summary.json'),'experiments':entries})
    print(json.dumps({'status':status,'tests':count,'seconds':summary['seconds'],'validation':summary['validation'],
                      'selected_section':unknown['selected_section'],'raw_p':unknown['raw_p'],'bonferroni9':unknown['bonferroni9']}))


if __name__=='__main__':main()
