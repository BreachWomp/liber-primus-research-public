"""Checkpoint completed, independently audited affine-constant research."""
from datetime import datetime,timezone
import json
import re
import subprocess
import sys
from verify_affine_feedback import ROOT,load,sha,to_indices
from phase26_provenance import verify_dependency
from liberprimus.alphabet import render_like


def save(path,data):
    (ROOT/path).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def main():
    assert not (ROOT/'checkpoints/phase26_complete.json').exists()
    controls=load('results/phase26_controls_validation.json')
    unknown=load('results/phase26_unknown_validation.json')
    algebra=load('results/E071-algebra-c88504248ab7.json')
    assert controls['full_gate_passed'] and algebra['gate_passed']
    assert len(controls['controls'])==16 and len(unknown['sections'])==56 and len(unknown['nulls'])==19
    events=[json.loads(line) for line in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    done=[e for e in events if e['status']=='completed']
    algebra_event=next(e for e in done if e['experiment']=='E071-algebra')
    entries=[{'id':algebra_event['experiment'],'fingerprint':algebra_event['fingerprint'],
        'output':algebra_event['output'],'sha256':algebra_event['output_sha256']}]+controls['entries']+unknown['entries']
    assert len(entries)==93 and len({e['fingerprint'] for e in entries})==93
    by_fp={e['fingerprint']:e for e in done}
    for e in entries:
        event=by_fp[e['fingerprint']]
        assert sha(e['output'])==e['sha256']==event['output_sha256']
        for path,digest in event['input_dependencies'].items():verify_dependency(path,digest)
    for path in ('experiments/affine_feedback_plan.json','tests/test_affine_feedback.py'):
        assert (ROOT/path).read_bytes()==subprocess.check_output(['git','show','HEAD:'+path],cwd=ROOT)
    assert (ROOT/'experiment_log.jsonl').read_bytes().startswith(subprocess.check_output(['git','show','HEAD:experiment_log.jsonl'],cwd=ROOT))
    tests=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,
        capture_output=True,text=True,encoding='utf-8',timeout=90)
    output=tests.stdout+tests.stderr
    (ROOT/'results/validation_phase26.txt').write_text(output,encoding='utf-8')
    assert tests.returncode==0,output
    count=int(re.search(r'Ran (\d+) tests',output)[1]);now=datetime.now(timezone.utc).isoformat()
    seconds=sum(by_fp[e['fingerprint']]['wall_seconds'] for e in entries)
    assert seconds<3600
    pending=unknown['pending_larger_calibration']
    status='twentysixth_batch_affine_constant_'+('larger_null_pending' if pending else 'no_supported_decryption')
    peak=max(controls['peak_sampled_bytes'],unknown['peak_sampled_bytes'])
    summary={'created_at':now,'status':status,'algebra':algebra,'controls':controls,'unknown':unknown,
        'successful_tasks':len(entries),'seconds':seconds,'peak_sampled_search_bytes':peak,
        'algebra_memory_note':'E071 bounded synthetic arrays and cooperative120-second deadline; no sampled OS peak recorded for that preliminary process.',
        'tests_passed':count,'source_path_migration':'checkpoints/phase26_path_migration.json',
        'new_decryptions':[]}
    save('results/phase26_summary.json',summary)
    queue=[]
    if pending:
        queue.append({'id':'H049','priority':1,'task':'Preregister fresh larger null calibration of frozen E073 selection; keep original19 descriptive and do not pool adaptively.'})
    queue.extend([{'id':'H023','priority':len(queue)+1,'task':'Derive and benchmark a bounded delay3 feedback attack using the new affine family reduction. E025 tested delay2 only, E072/E073 delays4..32. Validate fresh keys and constants, exact prefix enumeration where feasible, and matched nulls before unknown claims.'},
        {'id':'H031','priority':len(queue)+2,'task':'General substitution deferred pending independently justified scoring repair; previous short-control objective fails.'}])
    next_sentence=('Eine größere, separat registrierte Nullkalibrierung der festgeschriebenen E073-Auswahl.' if pending else
        'Die noch offene Verzögerung von drei Runen untersuchen. Die neue Reduktion könnte eine begrenzte Suche ermöglichen; zuerst sind Kontrollen und ein Laufzeitbenchmark erforderlich. Dies ist noch ungetestet.')
    state=load('research_state.json');known={e['fingerprint'] for e in state['completed_experiments']}
    assert not any(e['fingerprint'] in known for e in entries)
    state['completed_experiments']+=entries
    state.update(status=status,updated_at=now,latest_report='reports/attack_phase26_report.md',
        next_experiments=[q['id'] for q in queue],new_decryptions=[],promising_candidates=[],
        session_budget={'phase':'twentysixth delayed affine constant','max_compute_wall_seconds':3600,
            'max_experiment_wall_seconds':180,'memory_ceiling_mib':768,'workers':1,'background_jobs':False},
        scoring_gate='E07216/16 exact plaintext/key/a/b/c controls. E07356 unknown inputs and19 full-optimizer matched nulls. Independent retained-family/queue/score checks; complete screen replay distinguished from independent enumeration.',
        notes=['No previously unknown plaintext confirmed. Direct cryptanalysis only.',
            'All a,b1..28,c0..28,m4..32;659344 families,8 retained per period. Heuristic, no skips or unknown reset search.',
            '12 fresh-key/constant controls on previously inspected excluded texts plus4 E068 input regressions; not16 unseen texts.',
            'All55 unknown rune pages represented; numeric LP2-50 preserved as empty rune span, not deciphered.',
            'Historical filename collision restored byte-for-byte. Exact E072 input snapshots and migration mapping retained; no output/log rewritten.',
            'No research jobs left running.'])
    state['validation'].update(tests_passed=count,path='results/validation_phase26.txt',
        phase26={'controls':controls['validation'],'unknown':unknown['validation']})
    state['resources'].update(recorded_successful_experiment_runs=len(done),
        recorded_experiment_subprocess_wall_seconds=sum(e['wall_seconds'] for e in done),phase26_wall_seconds=seconds)
    state['failed_approaches'].append(f'E073 affine delayed feedback:56 inputs, {unknown["exceedances"]}/19 full matched nulls >= selected score, adjusted p={unknown["bonferroni56"]}. Heuristic screen; no supported decryption.')
    save('research_state.json',state)
    hypotheses=load('hypotheses.json');h=next(h for h in hypotheses['hypotheses'] if h['id']=='H049')
    h.update(status='controls_passed_'+('larger_null_pending' if pending else 'unknown_screen_negative'),
        experiments=['E071','E072','E073'],result={'controls_exact':16,'controls_total':16,
            'unknown_inputs':56,'exceedances':unknown['exceedances'],'nulls':19,'raw_p':unknown['raw_p'],
            'bonferroni56':unknown['bonferroni56'],'summary':'results/phase26_summary.json'},
        limits='Top8 of22736 families per period; finite heuristic, no exclusions of all keys or texts. No omissions or hidden boundaries. Coarse19-null screen cannot establish selection-corrected significance.')
    hypotheses.update(status=status,updated_at=now,next_queue=queue);save('hypotheses.json',hypotheses)
    winner=next(r for r in unknown['sections'] if r['section']==unknown['selected_section'])
    data=load(winner['output']);top=data['result']['top'][0];plain=to_indices(top['plaintext_runes'])
    catalog={p['id']:p for p in load('transcriptions/pages.json')}
    candidate=f'# Stärkster E073-Kandidat: {winner["section"]}\n\nKeine bestätigte Entschlüsselung. Nach Score aus 56 Eingaben ausgewählt; '
    candidate+=f'{unknown["exceedances"]}/19 passende Nulltexte erreichen mindestens denselben Score.\n\n'
    candidate+='Die Worttrenner und Zeilen entsprechen unverändert der kanonischen Transkription. Keine ergänzten Leerzeichen oder Schreibkorrekturen.\n\n'
    for span in data['page_spans']:
        candidate+=f'## {span["page_id"]}\n\n'
        if span['runes']:
            layout=render_like(catalog[span['page_id']]['text_with_layout'],plain[span['start']:span['end']],latin=True)
            candidate+=f'```text\n{layout}\n```\n\n'
        else:candidate+='Leere Runenspanne; numerischer Inhalt nicht entschlüsselt.\n\n'
    candidate+=f'Regel: `P_i=a*C_i+b*P_(i-m)+c mod29`; Rezept:\n\n```json\n{json.dumps(top["recipe"],indent=2)}\n```\n\n'
    candidate+=f'[Vollständiges Ergebnis](../{winner["output"]}), SHA-256 `{sha(winner["output"])}`.\n'
    (ROOT/'reports/phase26_selected_candidate.md').write_text(candidate,encoding='utf-8')
    table='\n'.join(f'| {r["index"]} | {r["runes"]} | {r["key_length"]} | {r["cipher_sign"]} | {r["feedback_sign"]} | {r["constant"]} | {r["family_rank"]} | exakt |' for r in controls['controls'])
    section_table='\n'.join(f'| {r["section"]} | {r["runes"]} | {r["key_length"]} | {r["cipher_sign"]} | {r["feedback_sign"]} | {r["constant"]} | {r["score"]:.6f} |' for r in unknown['sections'])
    report=f'''# Forschungsserie 26: Additive Konstante in verzögerter Rückkopplung

Stand UTC: {now}. **Keine neue Entschlüsselung bestätigt.**

## Mechanismus und E071

`P_i=a*C_i+b*P_(i-m)+c mod29`, a,b1..28,c0..28,m4..32.
Der Anfangsschlüssel ist `(P-a*C-c)/b`, die Rückverschlüsselung `(P-b*queue-c)/a`.
Für b ungleich 1 gilt mit d=c/(1-b): `P_i=a*(base1_i+b^q*t_r)+d`.
Für b=1 gilt `P_i=a*(base1_i+t_r)+q*c`, q=floor(i/m).
Damit bleiben alle Anfangswerte vertreten. Die Sprachbewertung muss d bzw. q*c
berücksichtigen; diese Fälle waren nicht bereits durch c=0 erledigt.
Die affine Umparametrisierung ist keine mathematische Neuentdeckung.

E071 prüft {algebra['direct_families_checked']} Familien unabhängig durch direkte
Warteschlangen; maximale Abweichung {algebra['max_absolute_error']:.3g}.
Die vollständige Vorauswahl auf 3.316 synthetischen Runen benötigt
{algebra['benchmark_seconds']:.3f} Sekunden. Pro Eingabe werden 659.344 Familien
bewertet und pro Verzögerung 8 von 22.736 behalten. Danach folgen 232 heuristische
Optimierungen und 12 Viergramm-Verfeinerungen mit festen Seeds.

## E072: Kontrollen

Alle 16 Klartexte, Schlüssel und a/b/c-Werte exakt. Zwölf neue Schlüssel und
Konstanten verwenden bereits betrachtete, vom Training ausgeschlossene
Emerson-Blöcke; vier E068-Eingaben prüfen die geänderte Suche bei c=0.
Vier frische Fälle decken b=1 ab. Es handelt sich nicht um 16 unbekannte Testtexte.
Der diagnostische Nulltext erreicht {controls['null_score']:.6f}; daraus folgt kein p-Wert.

| Kontrolle | Runen | m | a | b | c | Vorauswahlrang | Ergebnis |
|---|---:|---:|---:|---:|---:|---:|---|
{table}

## E073: Direkter Angriff

46 Einzel-Seiten und 10 bestehende Seitengruppen; alle 55 unbekannten Runenseiten
sind vertreten. Gruppen und Seitenstarts sind hypothetische Chiffrengrenzen.
Innerhalb einer Gruppe läuft der Zustand ohne Reset weiter. Die Zahlenseite
LP2-50 bleibt in der Quellenfolge als leere Runenspanne erhalten.

| Eingabe | Runen | m | a | b | c | Score |
|---|---:|---:|---:|---:|---:|---:|
{section_table}

Stärkste Eingabe **{unknown['selected_section']}**, Score {unknown['score']:.6f}.
Auswahl und alle 56 Ergebnishashes wurden vor den Nullversuchen fixiert.
Jeder Nulltext erhält seitenweise Häufigkeiten, Randrunen und die Zahl gleicher
Nachbarn und durchläuft den ganzen Optimierer. **{unknown['exceedances']}/19**
Nullscores mindestens so hoch; Plus-eins-p={unknown['raw_p']:.2f},
Bonferroni56={unknown['bonferroni56']:.2f}. Mit 19 Nulltexten beträgt der kleinste
korrigierte Wert bereits 1: ein grober Vergleich, kein Signifikanznachweis.
{'Eine gesonderte größere Kalibrierung der fixierten Auswahl steht aus.' if pending else 'Die Auswahl liefert keine belastbare sprachliche Evidenz über dieses Nullmodell hinaus.'}

## Prüfung und Grenzen

Quellbereiche, Schlüssel-Seeds, skalare Warteschlangen, Rückverschlüsselungen,
Kandidatenscores, Koordinatenmaxima und durchgehende Seitenzustände geprüft.
Alle 56 LP2-Forschungsseiten sind als wörtliche Layout-Abschnitte in den gespeicherten
Quellen verankert; die Prüfsummen aller 10 zugehörigen Quelldateien stimmen.
Die 732.540 Sprachmodell-Einträge sind separat durch skalare Wahrscheinlichkeiten
kontrolliert. Pro Angriff wurden sämtliche 232 behaltenen Familien sowie bei
Kontrollen die injizierte Familie direkt nachgerechnet. Die 659.344 vollständigen
Vorauswahlscores wurden mit dem Produktionsverfahren reproduziert; das ist
Replikation, keine zweite unabhängige Vollgitter-Implementierung. E071 liefert
die separate direkte Prüfung an 27.608 synthetischen Familien.

Die Suche behält nur 8 Familien je Verzögerung. Kontroll-Erfolge beweisen keine
Vollständigkeit. Ein größerer Parameterraum garantiert bei begrenzter Vorauswahl
keinen höheren Score als ältere Suchen. Keine ausgelassenen Runen oder unbekannten
Resets gesucht. Ein negatives heuristisches Ergebnis widerlegt die Chiffrenfamilie nicht.
Das Sprachmodell stammt aus englischer Emerson-Prosa; andere Sprachen, Zahlenfolgen
oder nichtsprachliche Klartexte werden durch diesen Angriff nicht zuverlässig erkannt.

{count} Tests bestanden; 93 registrierte Aufgaben; {seconds:.3f} Sekunden
erfolgreiche Experimentzeit bei 3.600 Sekunden Budget. E072/E073 höchster
abgetasteter Speicher {peak/1024**2:.1f} MiB, Grenze 768 MiB, ein Suchworker.
E071 hatte einen kooperativen 120-Sekunden-Deckel und begrenzte Arraygrößen;
für diesen Vorlauf wurde kein Betriebssystem-Speichermaximum aufgezeichnet.
Prüfzeiten sind gesondert in den Validierungsdateien enthalten. Keine laufenden Jobs.

Eine Dateinamenskollision mit dem historischen E019-Plan und dessen Testdatei
wurde entdeckt und bytegenau aus Git wiederhergestellt. Die tatsächlich von
E072 verwendeten Plan-/Runnerbytes sind separat archiviert. Kein früheres
Ergebnis und kein Experimentlog-Eintrag wurde umgeschrieben.
[Zuordnung und Reproduktionshinweis](../checkpoints/phase26_path_migration.json).

Nächste Priorität: {next_sentence}

[Kontrollplan](../experiments/delayed_affine_feedback_plan.json),
[Angriffsplan](../experiments/affine_feedback_unknown_plan.json),
[Messübersicht](../results/phase26_summary.json),
[Kandidat mit Originalgrenzen](phase26_selected_candidate.md).
'''
    (ROOT/'reports/attack_phase26_report.md').write_text(report,encoding='utf-8')
    p=ROOT/'README.md';text=p.read_text(encoding='utf-8');a,b=text.index('Reproduzierbare Kryptanalyse'),text.index('Start:')
    text=text[:a]+f'Reproduzierbare Kryptanalyse des Liber Primus. **Keine neue Entschlüsselung\nnachgewiesen.** Serie 26 ergänzt eine additive Konstante: 16 Kontrollen exakt,\n46 Seiten und 10 Seitengruppen geprüft; {unknown["exceedances"]}/19 Nullscores mindestens so hoch.\n\n'+text[b:]
    text=text.replace('reports/attack_phase25_report.md','reports/attack_phase26_report.md',1)
    text=text.replace('## Aktueller Stand\n\n','## Aktueller Stand\n\n- E071/E072: affine Konstante und Sonderfall b=1 geprüft;16/16 Kontrollen exakt.\n'+f'- E073:56 Eingaben, {unknown["exceedances"]}/19 Nullscores mindestens so hoch; keine neue Lösung.\n',1)
    groups=len({e['experiment'].split('-')[0] for e in done})
    text=re.sub(r'- \d+ Tests bestanden; \d+ Experimentgruppen',f'- {count} Tests bestanden; {groups} Experimentgruppen',text,count=1)
    a=text.index('Nächste Priorität:');b=text.index('Kein Hintergrundprozess',a)
    text=text[:a]+'Nächste Priorität: '+next_sentence+'\n'+text[b:]
    p.write_text(text,encoding='utf-8')
    save('checkpoints/phase26_complete.json',{'created_at':now,'status':status,'summary':'results/phase26_summary.json',
        'summary_sha256':sha('results/phase26_summary.json'),'experiments':entries})
    print({'status':status,'tests_passed':count,'seconds':seconds,'exceedances':unknown['exceedances']})


if __name__=='__main__':main()
