"""Checkpoint independently verified continuous-section autokey experiment."""
from collections import Counter
from datetime import datetime,timezone
import difflib
import json
import re
import subprocess
import sys
from verify_autokey_sections import ROOT,load,sha
def save(path,data):(ROOT/path).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def main():
    assert not (ROOT/'checkpoints/phase23_complete.json').exists()
    controls=load('results/phase23_controls_validation.json');unknown=load('results/phase23_unknown_validation.json')
    assert controls['full_gate_passed'] and len(controls['controls'])==4 and len(controls['reused_control_entries'])==12
    assert unknown['unique_unknown_rune_pages']==55 and unknown['empty_pages_preserved']==['LP2-50']
    entries=controls['entries']+unknown['entries'];assert len(entries)==34
    events=[json.loads(x) for x in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    done=[e for e in events if e['status']=='completed'];by_fp={e['fingerprint']:e for e in done}
    for entry in entries+controls['reused_control_entries']:
        event=by_fp[entry['fingerprint']];assert sha(entry['output'])==entry['sha256']==event['output_sha256']
        for path,digest in event['input_dependencies'].items():assert sha(path)==digest,path
    assert (ROOT/'experiment_log.jsonl').read_bytes().startswith(subprocess.check_output(['git','show','HEAD:experiment_log.jsonl'],cwd=ROOT))
    tests=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=60)
    output=tests.stdout+tests.stderr;(ROOT/'results/validation_phase23.txt').write_text(output,encoding='utf-8')
    if tests.returncode:raise RuntimeError(output)
    count=int(re.search(r'Ran (\d+) tests',output)[1]);now=datetime.now(timezone.utc).isoformat()
    validation=Counter(controls['validation']);validation.update(unknown['validation'])
    seconds=controls['seconds']+unknown['seconds'];assert seconds<3000
    summary={'new_controls':controls['controls'],'reused_control_entries':controls['reused_control_entries'],
        'control_null_score':controls['null_score'],'unknown':{k:v for k,v in unknown.items() if k not in ('entries','validation')},
        'validation':dict(validation),'tests_passed':count,'successful_tasks':len(entries),'seconds':seconds,
        'peak_sampled_bytes':max(controls['peak_sampled_bytes'],unknown['peak_sampled_bytes']),
        'control_validation_sha256':sha('results/phase23_controls_validation.json'),
        'unknown_validation_sha256':sha('results/phase23_unknown_validation.json'),'new_decryptions':[]}
    save('results/phase23_summary.json',summary)
    pending=unknown['pending_larger_calibration'];status='twentythird_batch_continuous_autokey_'+('larger_null_pending' if pending else 'no_supported_decryption')
    next_item=({'id':'H046','priority':1,'task':'Preregister larger selected-group null calibration with frozen E065 solver and immutable selection. No significance claim from19 nulls.'} if pending else
        {'id':'H047','priority':1,'task':'Calibrate a bounded search for plaintext-feedback coefficients b=1..28 at delays4..32, with cipher coefficient restricted to+1/-1. Derive residue chains modulo29 without integer overflow; freeze cheap family screening and retained full searches before fresh-key controls and matched nulls. Existing E020/E023 short-delay results are prior work, not new discoveries.'})
    queue=[next_item,{'id':'H031','priority':2,'task':'General substitution deferred pending independently justified scoring repair.'},
        {'id':'H023','priority':3,'task':'Delay3 feedback deferred pending feasible calibrated reduction.'}]
    state=load('research_state.json');old={e['fingerprint'] for e in state['completed_experiments']}
    assert not any(e['fingerprint'] in old for e in entries)
    state['completed_experiments']+=entries
    state.update(status=status,updated_at=now,latest_report='reports/attack_phase23_report.md',next_experiments=[q['id'] for q in queue],
        new_decryptions=[],promising_candidates=[],session_budget={'phase':'twentythird continuous-section plaintext-autokey','max_compute_wall_seconds':3000,
            'max_experiment_wall_seconds':180,'memory_ceiling_mib':768,'workers':1,'background_jobs':False},
        scoring_gate='E064 four fresh-key3316-rune controls exact;12 shorter validated E062 runs reused by hash. E06510 original section hypotheses and19 full per-page matched nulls independently verified.',
        notes=['No previously unknown plaintext confirmed. Direct cryptanalysis only.',
            'Frozen E0624..32-seed no-skip autokey engine; key, feedback and language context continue across section page boundaries.',
            'Four new long controls,12 prior short controls reused; synthetic calibration does not authenticate a cipher or grouping.',
            'All55 unknown rune pages represented in10 overlapping section hypotheses. Numeric LP2-50 remains an empty rune span with source refs.',
            'No original source, historical result or frozen solver modified; no running research jobs.'])
    state['validation'].update(tests_passed=count,path='results/validation_phase23.txt',phase23=dict(validation))
    state['resources'].update(recorded_successful_experiment_runs=len(done),recorded_experiment_subprocess_wall_seconds=sum(e['wall_seconds'] for e in done),phase23_wall_seconds=seconds)
    state['failed_approaches'].append(f'E065 continuous no-skip plaintext-autokey4..32 across10 sections: {unknown["exceedances"]}/19 matched null scores >= selected group; adjusted p={unknown["bonferroni10"]}. No supported plaintext; hypothetical group boundaries and heuristic limits remain.')
    save('research_state.json',state)
    hypotheses=load('hypotheses.json');by_id={h['id']:h for h in hypotheses['hypotheses']}
    by_id['H046'].update(status='long_controls_passed_'+('larger_null_pending' if pending else 'continuous_unknown_screen_negative'),experiments=['E064','E065'],
        result={'new_controls_exact':4,'new_controls_total':4,'prior_exact_controls_reused':12,'unknown_sections':10,'unknown_rune_pages':55,
            'exceedances':unknown['exceedances'],'raw_p':unknown['raw_p'],'bonferroni10':unknown['bonferroni10'],'summary':'results/phase23_summary.json'},
        limits='Continuous no-skip stream,4..32 seed, four sign pairs,10 unauthenticated overlapping groupings. Heuristic screen only; numeric LP2-50 is preserved, not decrypted.')
    if not pending:
        assert 'H047' not in by_id
        hypotheses['hypotheses'].append({'id':'H047','status':'queued_untested',
            'claim':'Plaintext feedback at delays4..32 might use a nonzero coefficient other than+1/-1.',
            'basis':'E062/E065 use feedback coefficient+1/-1. E020 covers general multipliers at delay1; E023 addresses shorter delays. Those prior results and affine-chain algebra are not new discoveries.',
            'mechanism':'P_i=a*C_i+b*P_(i-m) modulo29 with a in{+1,-1}, b in1..28, m4..32; no skipped runes. Compute modular residue coefficients and test a fixed bounded family-ranking stage before expensive refinement.',
            'success_criterion':'Prospective parameters/seeds/budget; source-excluded fresh-key controls with b outside{1,28}, old-sign regressions reused where identical, independent queue/re-encryption checks and full optimizer nulls before unknown claims.',
            'limits':'Untested proposal, no E066 result. Family screening may discard the true family; calibration must test it. Does not cover arbitrary cipher multiplier, constant term, omissions or unknown resets.'})
    hypotheses.update(status=status,updated_at=now,next_queue=queue);save('hypotheses.json',hypotheses)
    control_table='\n'.join(f'| {r["index"]} | {r["runes"]} | {r["key_length"]} | exakt |' for r in controls['controls'])
    section_table='\n'.join(f'| {r["section"]} | {r["runes"]} | {r["key_length"]} | {r["score"]:.6f} |' for r in unknown['sections'])
    report=f'''# Forschungsserie 23: Autokey über Seitengrenzen

Stand (UTC): {now}. **Keine neue Entschlüsselung bestätigt.**
Vier neue lange Kontrollfälle wurden exakt rekonstruiert. Die unveränderte
Suche lief danach auf zehn bestehenden LP2-Gruppen, die sämtliche 55 unbekannten
Runenseiten abdecken. Die Seitengruppen sind Hypothesen, keine bestätigten
Grenzen einer Chiffre.

## E064: Fortlaufenden Schlüsselstrom auf längeren Texten kalibriert

Der E062-Solver bleibt bytegleich: Startschlüssel mit 4–32 Runen, vier
Vorzeichenpaare, keine ausgelassenen Runen, beide Initialisierungen und alle
nachfolgenden Auswahl- und Verfeinerungsschritte. Neu ist ausschließlich die
Anwendung auf längere, fortlaufende Texte über Seitenwechsel hinweg.
Weder Schlüssel noch Klartextrückkopplung oder Sprachkontext werden zurückgesetzt.

Vier Kontrollen mit jeweils 3.316 Runen verwenden neue Zufallsschlüssel
der Längen 13/23/31/32 und alle vier Vorzeichenpaare. Die Texte stammen aus
bereits betrachteten Bereichen der vom Training ausgeschlossenen Emerson-Kapitel
X/XI/XII. Es sind neue Schlüssel, keine neue unabhängige Textsammlung.
Die künstlichen Seitenlängen entsprechen LP2-40_55 und enthalten eine leere
Spanne nach dem Vorbild LP2-50. Diese verbraucht keine Runen oder Schlüsselwerte.

| Neue Kontrolle | Runen | Startschlüssellänge | Klartext/Schlüssel/Vorzeichen |
|---|---:|---:|---|
{control_table}

Die zwölf exakten kürzeren E062-Kontrollen wurden über unveränderte Quell-,
Code-, Ausgabe- und Validierungshashes übernommen; ihre Suche wurde nicht
wiederholt. Damit sind vier neue Erfolge und zwölf wiederverwendete Erfolge
dokumentiert. Der komplette Optimierer auf einem pro Seite passenden
diagnostischen Zufallstext erreicht Score {controls['null_score']:.6f}.
Aus diesem einzelnen Vergleich wird kein p-Wert abgeleitet.

## E065: Unbekannte Seitengruppen direkt angegriffen

Alle zehn bereits festgelegten E012-Gruppen wurden geprüft, einschließlich
der überlappenden Alternativen LP2-40_53, LP2-54_55 und LP2-40_55.
Die kleinste Gruppe hat 308 Runen und liegt im bereits kalibrierten Bereich;
die größte hat 3.316. Dadurch sind auch die in Serie 22 wegen ihrer Kürze
ausgelassenen einzelnen Runenseiten hier innerhalb von Gruppen vertreten.
Originalreihenfolge, Seitenkennungen und Quellreferenzen bleiben erhalten.
Die Zahlen von LP2-50 werden durch die leere Runenspanne nicht entschlüsselt.

| Gruppe | Runen | gefundene Startschlüssellänge | Score |
|---|---:|---:|---:|
{section_table}

Die höchste Bewertung erhielt **{unknown['selected_section']}**. Diese Auswahl
wurde mit den Hashes aller zehn Ergebnisse vor dem Zufallsvergleich fixiert.
19 unabhängige Nulltexte erhalten pro Seite Häufigkeiten, Randrunen und die
Zahl gleicher Nachbarn; leere Spannen bleiben erhalten. Jeder Nulltext durchläuft
denselben vollständigen Optimierer einschließlich aller internen Entscheidungen.

**{unknown['exceedances']}/19** Nullscores erreichen mindestens den beobachteten
Wert. Plus-eins-p={unknown['raw_p']:.2f}, Bonferroni-Korrektur für die Auswahl
unter zehn Gruppen={unknown['bonferroni10']:.2f}. Mit 19 Vergleichen ist der
kleinste mögliche korrigierte Wert 0,50; das ist ein grober Vergleich und kein
Signifikanznachweis. Die Suche bleibt heuristisch und die Gruppierung ungesichert.
Ein negativer Befund schließt andere Chiffren oder Fortsetzungsregeln nicht aus.

## Unabhängige Prüfung und Ressourcen

{count} Unit-Tests bestanden. Die unabhängige Prüfung rekonstruiert Quellbereiche
aus den erhaltenen Textbytes, berechnet gespeicherte Scores und bedingte
Koordinatenmaxima nach und prüft Rückverschlüsselungen. Zusätzlich wird eine
rollende Schlüsselwarteschlange ausdrücklich über jede Seitengrenze geführt;
an leeren Seiten muss ihr Zustand unverändert bleiben. Alle Nulltexte, Seeds,
Auswahlregeln und Prüfsummen wurden separat nachvollzogen.

{len(entries)} neue registrierte Aufgaben, {seconds:.3f} Sekunden gemessene
erfolgreiche Experimentzeit. Budget 3000 Sekunden pro Serie, höchstens 180 pro
Aufgabe, ein Worker. Höchster abgetasteter Speicherwert
{summary['peak_sampled_bytes']/1024**2:.1f} MiB bei 768 MiB Grenze.
Originalquellen, frühere Ergebnisse und der E062-Solver bleiben unverändert.
Es läuft kein Forschungsprozess weiter.

Nächster ungetesteter Schritt: {'größere Nullkalibrierung der fixierten Auswahl.' if pending else 'ein begrenzter Test von Rückkopplungsfaktoren außer +1 und −1, modulo 29, bei Verzögerungen 4–32. Zuerst muss eine feste Auswahl der zu untersuchenden Familien an Kontrollen bestehen; die Arbeiten für kürzere Verzögerungen bleiben ausdrücklich Vorwissen.'}

[Kontrollplan](../experiments/autokey_section_plan.json),
[Angriffsplan](../experiments/autokey_section_unknown_plan.json),
[Messübersicht](../results/phase23_summary.json),
[Checkpoint](../checkpoints/phase23_complete.json).
'''
    (ROOT/'reports/attack_phase23_report.md').write_text(report,encoding='utf-8')
    path=ROOT/'README.md';original=path.read_bytes().decode('utf-8');text=original.replace('\r\n','\n')
    a,b=text.index('Reproduzierbare Kryptanalyse'),text.index('Start:')
    text=text[:a]+('Reproduzierbare Kryptanalyse des Liber Primus. **Keine neue Entschlüsselung\n'
        'nachgewiesen.** Serie 23 prüft Autokey über Seitengrenzen: vier neue lange\n'
        'Kontrollen exakt, zwölf kürzere übernommen, zehn unbekannte Gruppen geprüft.\n'
        f'19 passende Zufallstexte ergeben ein korrigiertes p={unknown["bonferroni10"]:.2f}.\n\n')+text[b:]
    text=text.replace('Start: [Aktueller Forschungsbericht](reports/attack_phase22_report.md)','Start: [Aktueller Forschungsbericht](reports/attack_phase23_report.md)')
    text=text.replace('- 126 Tests bestanden; 62 Experimentgruppen',f'- {count} Tests bestanden; 64 Experimentgruppen')
    text=text.replace('## Aktueller Stand\n\n','## Aktueller Stand\n\n'
        '- E064: vier neue 3316-Runen-Kontrollen exakt; zwölf E062-Kontrollen unverändert übernommen.\n'
        f'- E065: zehn Gruppen mit allen 55 unbekannten Runenseiten; {unknown["exceedances"]}/19 Nullscores\n'
        '  mindestens so hoch wie die stärkste Gruppe. Keine bestätigte Entschlüsselung.\n',1)
    before,after=original.splitlines(keepends=True),text.splitlines(keepends=True);out=[]
    matcher=difflib.SequenceMatcher(a=[x.rstrip('\r\n') for x in before],b=[x.rstrip('\r\n') for x in after],autojunk=False)
    for tag,a,b,c,d in matcher.get_opcodes():out.extend(before[a:b] if tag=='equal' else after[c:d])
    path.write_bytes(''.join(out).encode('utf-8'))
    save('checkpoints/phase23_complete.json',{'created_at':now,'status':status,'summary':'results/phase23_summary.json',
        'summary_sha256':sha('results/phase23_summary.json'),'experiments':entries})
    print({'status':status,'tests_passed':count,'seconds':seconds,'new_controls_exact':4,'reused_controls':12,
        'unknown_sections':10,'exceedances':unknown['exceedances'],'bonferroni10':unknown['bonferroni10']})


if __name__=='__main__':main()
