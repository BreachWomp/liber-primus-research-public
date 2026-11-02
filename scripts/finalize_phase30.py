"""Checkpoint the prospective long-text substitution test and unknown screen."""
from datetime import datetime,timezone
import difflib
import json
import re
import subprocess
import sys
from verify_terminated_benchmark import ROOT,load,sha,to_indices
from liberprimus.alphabet import RUNES,RUNE_ALIASES,LATIN

def save(p,data):(ROOT/p).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def main():
    assert not (ROOT/'checkpoints/phase30_complete.json').exists()
    controls=load('results/phase30_controls_validation.json');unknown=load('results/phase30_unknown_validation.json')
    assert controls['full_gate_passed'] and len(controls['controls'])==12 and len(unknown['pages'])==46
    entries=controls['entries']+unknown['entries'];assert len(entries)==80
    events=[json.loads(s) for s in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    done=[e for e in events if e['status']=='completed'];by_fp={e['fingerprint']:e for e in done}
    for r in entries:
        e=by_fp[r['fingerprint']];assert sha(r['output'])==r['sha256']==e['output_sha256']
        for path,digest in e['input_dependencies'].items():assert sha(path)==digest,path
    assert (ROOT/'experiment_log.jsonl').read_bytes().startswith(subprocess.check_output(['git','show','HEAD:experiment_log.jsonl'],cwd=ROOT))
    processes=load('results/phase30_processes.json');assert len(processes)==81
    failures=[p for p in processes if p['exit_code']!=0]
    assert len(failures)==1 and failures[0]['experiment']=='E083-control-0' and failures[0]['reason'] is None
    log=(ROOT/failures[0]['log']).read_text(encoding='utf-8')
    assert 'FileNotFoundError' in log and 'phase30_benchmark_validation.json' in log
    assert not any(e['experiment'].startswith(('E083-','E084-')) and e['status']=='failed' for e in events)
    assert all(p['reason'] is None and p['seconds']<185 and p['peak_sampled_bytes']<=768*1024**2 for p in processes)
    tests=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=90)
    output=tests.stdout+tests.stderr;(ROOT/'results/validation_phase30.txt').write_text(output,encoding='utf-8')
    assert tests.returncode==0,output
    count=int(re.search(r'Ran (\d+) tests',output)[1]);now=datetime.now(timezone.utc).isoformat()
    seconds=sum(by_fp[e['fingerprint']]['wall_seconds'] for e in entries)
    supervised=sum(p['seconds'] for p in processes);assert supervised<1800
    peak=max(p['peak_sampled_bytes'] for p in processes);pending=unknown['pending_larger_calibration']
    status='thirtieth_batch_long_substitution_'+('larger_null_pending' if pending else 'no_supported_decryption')
    summary={'created_at':now,'status':status,'controls':controls,'unknown':unknown,'tests_passed':count,
        'successful_tasks':80,'seconds':seconds,'supervised_seconds_including_preflight_failure':supervised,
        'preflight_failures':failures,'peak_sampled_bytes':peak,'new_decryptions':[]}
    save('results/phase30_summary.json',summary)
    next_task=('Preregister larger fresh calibration of frozen E084 selection; do not pool the initial19 adaptively.' if pending else
        'Test a general substitution of first modular ciphertext differences, beyond E015 affine-only maps. Preregister explicit initial-value/page-edge treatment, reversible integration, bounded fresh controls and matched full-search nulls before unknown conclusions. No silently discarded first rune.')
    queue=[{'id':'H051' if pending else 'H052','priority':1,'task':next_task},
        {'id':'H031','priority':2,'task':'Short-page word-frequency failure remains unresolved; no retrospective waiver or unknown short-page attack.'}]
    state=load('research_state.json');old={e['fingerprint'] for e in state['completed_experiments']}
    assert not any(e['fingerprint'] in old for e in entries);state['completed_experiments']+=entries
    state.update(status=status,updated_at=now,latest_report='reports/attack_phase30_report.md',next_experiments=[q['id'] for q in queue],
        new_decryptions=[],promising_candidates=[],session_budget={'phase':'thirtieth prospective long-text substitution',
            'max_compute_wall_seconds':1800,'max_experiment_wall_seconds':180,'memory_ceiling_mib':768,'workers':1,'background_jobs':False},
        scoring_gate='E08312/12 fresh-window/key controls exact, independent source/map/score/local-neighborhood checks. E08446 unknown pages>=200runes plus19 full-search matched nulls. E081 failed short gate remains unchanged.',
        notes=['No previously unknown plaintext confirmed. Direct unknown-page cryptanalysis performed after the new prospective gate.',
            'Model/search unchanged from E081; controls are excluded-source, not historically unseen prose.',
            'Nine short rune pages and numericLP2-50 preserved with explicit reasons; no inference to them.',
            'One dependency-path preflight failure before registry/search, retained with retry log and charged supervised runtime.',
            'Historical results preserved; no running research jobs.'])
    state['validation'].update(tests_passed=count,path='results/validation_phase30.txt',phase30={'controls':controls['validation'],'unknown':unknown['validation']})
    state['resources'].update(recorded_successful_experiment_runs=len(done),recorded_experiment_subprocess_wall_seconds=sum(e['wall_seconds'] for e in done),
        phase30_wall_seconds=seconds,phase30_supervised_seconds_including_preflight_failure=supervised)
    state['failed_approaches'].append(f'E084 general substitution/BOS-EOS score on46pages>=200runes: {unknown["exceedances"]}/19 full-search matched nulls >= winner, corrected p={unknown["bonferroni46"]}. No supported decryption; finite search not an exclusion of all bijections.')
    save('research_state.json',state)
    hypotheses=load('hypotheses.json');h=next(h for h in hypotheses['hypotheses'] if h['id']=='H051')
    h.update(status='controls_passed_'+('larger_null_pending' if pending else 'unknown_screen_negative'),experiments=['E083','E084'],
        limits='All12 fresh-window controls exact;46pages>=200runes searched under fixed heuristic,19 full-search nulls. No exhaustive29! exclusion, no short-page inference; E081 failure not relabeled.',
        result={'controls_exact':12,'unknown_pages':46,'exceedances':unknown['exceedances'],'nulls':19,
            'raw_p':unknown['raw_p'],'bonferroni46':unknown['bonferroni46'],'summary':'results/phase30_summary.json'})
    if not pending:
        assert not any(h['id']=='H052' for h in hypotheses['hypotheses'])
        hypotheses['hypotheses'].append({'id':'H052','status':'queued_untested',
            'claim':'A general rune substitution of modular ciphertext differences may expose plaintext.',
            'basis':'E015 tested affine substitutions of first differences only and explicitly excluded arbitrary substitutions. E083 supplies a prospective long-text capability check for a general substitution solver. Neither observation is evidence of an actual LP cipher.',
            'mechanism':'P_i=S((C_i-C_(i-1)) mod29), S a29-symbol bijection. Initial-value/page-edge policy must be fixed before experiment. Inverse is modular cumulative addition after S inverse.',
            'success_criterion':'Source-preserving initial-value policy, reversible positive controls, independent score/map/integration audit, bounded search and full matched nulls corrected for page/model selection.',
            'limits':'Untested, no omitted first rune, no historical novelty claim for differencing or substitution. E015 remains a negative affine-only result.'})
    hypotheses.update(status=status,updated_at=now,next_queue=queue);save('hypotheses.json',hypotheses)
    winner=next(p for p in unknown['pages'] if p['page']==unknown['selected_page']);r=load(winner['output'])
    page=next(p for p in load('transcriptions/pages.json') if p['id']==winner['page'])
    ranked=[];seen=set()
    for candidate in sorted(r['result']['restarts'],key=lambda x:x['score'],reverse=True):
        if candidate['plaintext_runes'] not in seen:ranked.append(candidate);seen.add(candidate['plaintext_runes'])
    text=f'''# E084-Ausgaben: {winner['page']}

**Keine bestätigte Entschlüsselung.** Höchster Score unter 46 untersuchten Seiten;
{unknown['exceedances']}/19 passende, vollständig optimierte Zufallstexte erreichen
mindestens denselben Score. Worttrenner, Zeilen und Nicht-Runen stammen unverändert
aus der Quelle. Keine ergänzten Leerzeichen oder Schreibkorrekturen.

Regel: `P_i = mapping_cipher_to_plain[C_i]`, GP-Indizes 0..28.
Die Abbildung ist bijektiv; Rückverschlüsselung über ihre inverse Permutation.
Die Alternativen sind verschiedene Ergebnisse derselben Suche, keine unabhängige Evidenz.
'''
    for k,candidate in enumerate(ranked[:3],1):
        plain=to_indices(candidate['plaintext_runes']);assert len(plain)==page['rune_count']
        it=iter(plain);layout=''.join(LATIN[next(it)] if RUNE_ALIASES.get(x,x) in RUNES else x for x in page['text_with_layout'])
        text+=f'\n## Rang {k}, Score {candidate["score"]:.6f}\n\n```text\n{layout}\n```\n\n```json\n'+json.dumps({'mapping_cipher_to_plain':candidate['mapping_cipher_to_plain']},indent=2)+'\n```\n'
    text+=f'\n[Ergebnis](../{winner["output"]}), SHA-256 `{sha(winner["output"])}`.\n'
    (ROOT/'reports/phase30_selected_candidates.md').write_text(text,encoding='utf-8')
    control_rows='\n'.join(f'| {r["index"]} | {r["runes"]} | exakt |' for r in controls['controls'])
    page_rows='\n'.join(f'| {r["page"]} | {r["runes"]} | {r["score"]:.6f} |' for r in unknown['pages'])
    next_sentence=('Die eingefrorene Auswahl braucht eine separat registrierte größere Nullkalibrierung.' if pending else
        'Nächster Ansatz H052: allgemeine Substitution auf modularen Differenzen. E015 deckte nur affine Abbildungen ab. Vor dem Angriff müssen Anfangswert, Seitenrand und Rückverschlüsselung ausdrücklich festgelegt und kontrolliert werden.')
    report=f'''# Forschungsserie 30: Allgemeine Substitution auf längeren Seiten

Stand UTC: {now}. **Keine neue Entschlüsselung bestätigt.**

## E083: Neue prospektive Kontrollen

E081s kurzer Gegenbeleg bleibt unverändert. Diese Serie prüft einen getrennten
Bereich ab 200 Runen. Modell, Wortendmarkierung und Suchverfahren sind unverändert:
höchstens 24 Starts, 40 vollständige 406-Tausch-Sweeps im Zeichenmodell und 40 im
BOS/EOS-Wortmodell. Kein Training auf LP-Texten oder den Kontrollkapiteln X/XI/XII.

Zwölf andere Quellfenster, vier unterschiedliche Absätze je ausgeschlossenem
Kapitel. Zielpräfixe 200/300/500/729 Runen; das letzte Wort bleibt vollständig.
Neue Schlüssel, vorher festgelegte Such-Seeds. Die Texte sind vom Fit getrennt,
aber das Korpus wurde historisch bereits betrachtet. Alle 12 Klartexte sowie
die Abbildung der beobachteten Symbole exakt. Fehlende Symbole sind nicht identifizierbar.
Die drei Kontrollnulls werden mit der gleichen vollständigen Suche bearbeitet;
sie sind Fähigkeitsdiagnostik ohne Signifikanzbehauptung.

| Kontrolle | Tatsächliche Runen | Ergebnis |
|---|---:|---|
{control_rows}

## E084: Direkter Angriff und Vergleich

Nach unabhängiger Kontrollprüfung separat registriert: 46 unbekannte LP2-Seiten
mit mindestens 200 Runen. LP2-06/14/15/22/32/49/51/53/55 sind unterhalb der
Längenschwelle; LP2-50 hat keine Runen. Alle zehn ausgeschlossenen Seiten sind
mit Originalinhalt und Grund im Plan erhalten, nicht als entschlüsselt gezählt.
Die originalen lexikalischen Endpunkte stimmen mit dem bestehenden E026-Audit.
Die Quellanker aller 56 Forschungsseiten und zehn gepinnten Quelldateien geprüft.

| Seite | Runen | Höchster Score |
|---|---:|---:|
{page_rows}

Stärkste Ausgabe **{unknown['selected_page']}**, Score {unknown['score']:.6f}.
Seitenwahl und 46 Ergebnishashes vor Nullziehungen eingefroren. Jeder der 19
unabhängigen Nulltexte erhält Randrunen, Häufigkeiten, Wortgrenzen und die Anzahl
gleicher Nachbarpaare; maximal 100.000 Rejection-Vorschläge. Dieselbe vollständige
Schlüsselsuche einschließlich Initialisierung mit demselben seitenbezogenen Seed.
**{unknown['exceedances']}/19** erreichen mindestens den beobachteten Score.
Plus-eins-p={unknown['raw_p']:.2f}, Bonferroni46={unknown['bonferroni46']:.2f}.
Mit 19 Nulltexten beträgt bereits der kleinste erreichbare korrigierte Wert 1:
grobes Screening, kein Signifikanznachweis und keine Entschlüsselung.

## Prüfung, Grenzen und Ressourcen

Kontrollen: {controls['validation']['independent_candidate_scores']} unabhängige Scores,
{controls['validation']['independent_final_neighbor_scores']} letzte Nachbarscores,
{controls['validation']['reencryptions']} Rückverschlüsselungen.
Unbekannte Seiten und Nulltexte: {unknown['validation']['independent_candidate_scores']} Scores,
{unknown['validation']['independent_final_neighbor_scores']} letzte Nachbarscores,
{unknown['validation']['reencryptions']} Rückverschlüsselungen.
Quellbereiche, Auswahl, Seeds und Nullziehungen geprüft. Der separate Prüfer zählt
Sprachereignisse neu aus den Quellbereichen; GP-Tokenisierung gemeinsam verwendet.
Die gesamte interne Optimierungstrajektorie wurde nicht unabhängig implementiert.
Endliche Heuristik, keine Ausschließung aller 29! Abbildungen. Englisches Prosa-
Modell und Wortgrenzenannahme können andere Klartexte übersehen. E081s kurze
Fehlbewertung bleibt ein dokumentiertes Risiko; keine Übertragung auf kurze Seiten.

Ein erster Start scheiterte **vor Registry und Suche** an einem falsch benannten
Benchmark-Verweis. Auf die vorhandene Phase-29-Validierung korrigiert; ursprüngliches
Fehlerprotokoll erhalten, Wiederholung mit eigenem Log. Keine Chiffrenparameter geändert.

{count} Tests bestanden, 80 registrierte abgeschlossene Aufgaben. Experimentzeit
{seconds:.3f} Sekunden; überwachte Prozesszeit einschließlich Startfehler
{supervised:.3f} Sekunden bei 1.800 Sekunden Budget. Spitzenwert {peak/1024**2:.1f} MiB
bei 768 MiB Grenze, ein Worker. Keine laufenden Jobs.

{next_sentence}

[Kontrollplan](../experiments/long_substitution_controls_plan.json),
[Angriffsplan](../experiments/long_substitution_unknown_plan.json),
[Ergebnisse](../results/phase30_summary.json),
[Ausgaben mit Originalgrenzen](phase30_selected_candidates.md).
'''
    (ROOT/'reports/attack_phase30_report.md').write_text(report,encoding='utf-8')
    p=ROOT/'README.md';original=p.read_bytes().decode('utf-8');text=original.replace('\r\n','\n')
    a,b=text.index('Reproduzierbare Kryptanalyse'),text.index('Start:')
    text=text[:a]+f'Reproduzierbare Kryptanalyse des Liber Primus. **Keine neue Entschlüsselung\nnachgewiesen.** Serie 30: 12 neue Substitutionskontrollen exakt; 46 unbekannte\nSeiten ab 200 Runen direkt angegriffen. {unknown["exceedances"]}/19 Nullscores mindestens so hoch.\n\n'+text[b:]
    text=text.replace('reports/attack_phase29_report.md','reports/attack_phase30_report.md',1)
    text=text.replace('## Aktueller Stand\n\n','## Aktueller Stand\n\n- E083: 12/12 neue Kontrollen für längere allgemeine Substitution exakt.\n'+f'- E084: 46 Seiten direkt geprüft, {unknown["exceedances"]}/19 passende Nullscores mindestens so hoch.\n',1)
    groups=len({e['experiment'].split('-')[0] for e in done})
    text=re.sub(r'- \d+ Tests bestanden; \d+ Experimentgruppen',f'- {count} Tests bestanden; {groups} Experimentgruppen',text,count=1)
    a=text.index('Nächste Priorität:');b=text.index('Kein Hintergrundprozess',a)
    text=text[:a]+'Nächste Priorität: '+next_sentence+'\n'+text[b:]
    before,after=original.splitlines(keepends=True),text.splitlines(keepends=True);out=[]
    matcher=difflib.SequenceMatcher(a=[x.rstrip('\r\n') for x in before],b=[x.rstrip('\r\n') for x in after],autojunk=False)
    for tag,a,b,c,d in matcher.get_opcodes():out.extend(before[a:b] if tag=='equal' else after[c:d])
    p.write_bytes(''.join(out).encode('utf-8'))
    save('checkpoints/phase30_complete.json',{'created_at':now,'status':status,'summary':'results/phase30_summary.json',
        'summary_sha256':sha('results/phase30_summary.json'),'experiments':entries})
    print({'status':status,'tests_passed':count,'seconds':seconds,'exceedances':unknown['exceedances']})


if __name__=='__main__':main()
