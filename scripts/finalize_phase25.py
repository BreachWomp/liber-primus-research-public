"""Checkpoint independently verified all-unit delayed-feedback experiments."""
from collections import Counter
from datetime import datetime,timezone
import difflib
import json
import re
import subprocess
import sys
from verify_bilinear_feedback import ROOT,load,sha,to_indices
from liberprimus.alphabet import render_like


def save(path,data):
    (ROOT/path).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def main():
    assert not (ROOT/'checkpoints/phase25_complete.json').exists()
    controls=load('results/phase25_controls_validation.json');initial_unknown=load('results/phase25_unknown_validation.json')
    more=load('results/phase25_more_nulls_validation.json')
    assert initial_unknown['exceedances']==0 and more['fresh_null_count']==99
    unknown=dict(initial_unknown)
    unknown.update({k:more[k] for k in ('exceedances','raw_p','bonferroni56','pending_larger_calibration','nulls')})
    unknown['initial_screen']={'null_count':19,'exceedances':0,'raw_p':initial_unknown['raw_p'],'bonferroni56':initial_unknown['bonferroni56'],'nulls':initial_unknown['nulls']}
    unknown['fresh_null_count']=99
    unknown['inference']='Fresh99 only; original19 retained descriptively, no pooled adaptive pvalue.'
    unknown['entries']=initial_unknown['entries']+more['entries']
    unknown['validation']=dict(Counter(initial_unknown['validation'])+Counter(more['validation']))
    unknown['seconds']=initial_unknown['seconds']+more['seconds']
    unknown['peak_sampled_bytes']=max(initial_unknown['peak_sampled_bytes'],more['peak_sampled_bytes'])
    assert controls['full_gate_passed'] and len(controls['controls'])==16
    assert unknown['unique_unknown_rune_pages']==55 and unknown['empty_pages_preserved']==['LP2-50']
    entries=controls['entries']+unknown['entries'];assert len(entries)==191
    seed_audit=load('results/phase25_seed_audit.json')
    assert seed_audit['families_checked']==191*232 and seed_audit['seeded_initializers_checked']==191*232*8
    assert seed_audit['outputs']=={e['output']:e['sha256'] for e in entries}
    events=[json.loads(x) for x in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    done=[e for e in events if e['status']=='completed'];by_fp={e['fingerprint']:e for e in done}
    for entry in entries:
        event=by_fp[entry['fingerprint']];assert sha(entry['output'])==entry['sha256']==event['output_sha256']
        for path,digest in event['input_dependencies'].items():assert sha(path)==digest,path
    assert (ROOT/'experiment_log.jsonl').read_bytes().startswith(subprocess.check_output(['git','show','HEAD:experiment_log.jsonl'],cwd=ROOT))
    tests=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=60)
    output=tests.stdout+tests.stderr;(ROOT/'results/validation_phase25.txt').write_text(output,encoding='utf-8')
    if tests.returncode:raise RuntimeError(output)
    count=int(re.search(r'Ran (\d+) tests',output)[1]);now=datetime.now(timezone.utc).isoformat()
    validation=Counter(controls['validation']);validation.update(unknown['validation'])
    seconds=controls['seconds']+unknown['seconds'];assert seconds<3600
    summary={'controls':controls['controls'],'control_null_score':controls['null_score'],
        'unknown':{k:v for k,v in unknown.items() if k not in ('entries','validation')},
        'validation':dict(validation),'tests_passed':count,'successful_tasks':len(entries),'seconds':seconds,
        'peak_sampled_bytes':max(controls['peak_sampled_bytes'],unknown['peak_sampled_bytes']),
        'control_validation_sha256':sha('results/phase25_controls_validation.json'),
        'unknown_validation_sha256':sha('results/phase25_unknown_validation.json'),
        'more_nulls_validation_sha256':sha('results/phase25_more_nulls_validation.json'),
        'seed_audit_sha256':sha('results/phase25_seed_audit.json'),'new_decryptions':[]}
    save('results/phase25_summary.json',summary)
    pending=unknown['pending_larger_calibration'];status='twentyfifth_batch_all_unit_feedback_'+('larger_null_pending' if pending else 'no_supported_decryption')
    next_item=({'id':'H048','priority':1,'task':'Preregister a further fixed fresh-null calibration for immutable E069 selection. No significance claim from E07099 nulls; keep prior stages separate.'} if pending else
        {'id':'H049','priority':1,'task':'Derive a bounded extension with affine constant c0..28 in delayed plaintext feedback. Benchmark reduction for b!=1 by a plaintext shift and separately handle b=1. Freeze parameters before fresh-key/constant controls and regressions; no unknown search before independent validation.'})
    queue=[next_item,{'id':'H031','priority':2,'task':'General substitution deferred pending independently justified scoring repair.'},
        {'id':'H023','priority':3,'task':'Delay3 feedback deferred pending feasible calibrated reduction.'}]
    state=load('research_state.json');old={e['fingerprint'] for e in state['completed_experiments']}
    assert not any(e['fingerprint'] in old for e in entries);state['completed_experiments']+=entries
    state.update(status=status,updated_at=now,latest_report='reports/attack_phase25_report.md',next_experiments=[q['id'] for q in queue],
        new_decryptions=[],promising_candidates=[],session_budget={'phase':'twentyfifth all-unit delayed feedback','max_compute_wall_seconds':3600,
            'max_experiment_wall_seconds':180,'memory_ceiling_mib':768,'workers':1,'background_jobs':False},
        scoring_gate='E06816/16 exact plaintext/key/a/b controls; independent22736-family literal screening and candidate checks. E06946 pages+10groups and19 initial plus99 fresh selected-input full null optimizations.',
        notes=['No previously unknown plaintext confirmed. Direct cryptanalysis only.',
            'All units a,b1..28, delays4..32, no omissions or affine constant. Histogram screen retains8 families per period,232 full families.',
            '12 fresh-key controls on previously inspected excluded texts plus4 E066 inputs under changed search; not16 unseen texts.',
            'All55 unknown rune pages represented in10 overlapping group hypotheses;46 also separately searched. Numeric LP2-50 preserved as empty rune span, not decrypted.',
            'Original sources and historical outcomes unchanged; no running research jobs.'])
    state.pop('active_phase25',None)
    state['validation'].update(tests_passed=count,path='results/validation_phase25.txt',phase25=dict(validation))
    state['resources'].update(recorded_successful_experiment_runs=len(done),recorded_experiment_subprocess_wall_seconds=sum(e['wall_seconds'] for e in done),phase25_wall_seconds=seconds)
    state['failed_approaches'].append(f'E069 a,b1..28 delayed feedback4..32:56 inputs; {unknown["exceedances"]}/99 fresh matched nulls >= selected score, adjusted p={unknown["bonferroni56"]}. No supported decryption; family selection remains heuristic.')
    save('research_state.json',state)
    hypotheses=load('hypotheses.json');by_id={h['id']:h for h in hypotheses['hypotheses']}
    by_id['H048'].update(status='controls_passed_'+('larger_null_pending' if pending else 'unknown_screen_negative'),experiments=['E068','E069','E070'],
        result={'controls_exact':16,'controls_total':16,'fresh_general_keys':12,'old_inputs_changed_search':4,
            'unknown_page_hypotheses':46,'unknown_group_hypotheses':10,'unknown_rune_pages':55,
            'initial_exceedances':0,'initial_nulls':19,'fresh_exceedances':unknown['exceedances'],'fresh_nulls':99,'raw_p':unknown['raw_p'],'bonferroni56':unknown['bonferroni56'],'summary':'results/phase25_summary.json'},
        limits='Top8 of784 coefficient pairs per period; no guarantee for every key/text. No affine constant, omitted symbols or unknown boundary search. Coarse19-null screen followed by99 fresh nulls, separately evaluated.')
    if not pending:
        assert 'H049' not in by_id
        hypotheses['hypotheses'].append({'id':'H049','status':'queued_untested',
            'claim':'A nonzero additive constant may occur in delayed affine plaintext feedback.',
            'basis':'E068/E069 have a,b arbitrary units but c=0; H030 tested a constant only at delay1. Affine shift algebra is not a new discovery.',
            'mechanism':'P_i=a*C_i+b*P_(i-m)+c mod29, a,b1..28,c0..28,m4..32. For b!=1 a uniform plaintext shift can remove c; b=1 requires separate handling.',
            'success_criterion':'Prove and independently test reduction, bound runtime/memory and freeze screening before fresh-key/constant controls, b=1 edge cases, old-pair regressions and full nulls.',
            'limits':'Untested proposal; no E071 result. Expansion may defeat family retention or runtime bounds. No omissions or hidden boundaries.'})
    hypotheses.update(status=status,updated_at=now,next_queue=queue);save('hypotheses.json',hypotheses)
    winner=next(r for r in unknown['sections'] if r['section']==unknown['selected_section']);data=load(winner['output']);top=data['result']['top'][0]
    pages={p['id']:p for p in load('transcriptions/pages.json')};plain=to_indices(top['plaintext_runes'])
    candidate=f"# Stärkster E069-Kandidat: {winner['section']}\n\nKeine bestätigte Entschlüsselung. Score {top['score']}; nach Score aus 56 Eingaben ausgewählt.\nWorttrenner und Zeilen bleiben wie in der kanonischen Quelltranskription.\n\n"
    for span in data['page_spans']:
        if span['runes']:
            layout=render_like(pages[span['page_id']]['text_with_layout'],plain[span['start']:span['end']],latin=True)
            candidate+=f"## {span['page_id']}\n\n```text\n{layout}\n```\n\n"
        else:candidate+=f"## {span['page_id']}\n\nLeere Runenspanne; numerischer Inhalt nicht entschlüsselt.\n\n"
    candidate+=f"[Vollständiges Ergebnis mit Schlüssel](../{winner['output']}); SHA-256 `{sha(winner['output'])}`.\n"
    (ROOT/'reports/phase25_selected_candidate.md').write_text(candidate,encoding='utf-8')
    control_table='\n'.join(f'| {r["index"]} | {r["runes"]} | {r["key_length"]} | {r["cipher_sign"]} | {r["feedback_sign"]} | {r["family_rank"]} | exakt |' for r in controls['controls'])
    unknown_table='\n'.join(f'| {r["section"]} | {r["runes"]} | {r["key_length"]} | {r["cipher_sign"]} | {r["feedback_sign"]} | {r["score"]:.6f} |' for r in unknown['sections'])
    report=f'''# Forschungsserie 25: Beide Koeffizienten erweitert

Stand (UTC): {now}. **Keine neue Entschlüsselung bestätigt.**
16 Kontrollen exakt; anschließend46 Einzel-Seiten und 10 Seitengruppen direkt
angegriffen. Keine Community-Lösungsbehauptungen untersucht.

## E068: Umfang und Kalibrierung

Die Regel lautet `P_i=a*C_i+b*P_(i-m) mod29`, jetzt mit beiden Koeffizienten
`a,b=1..28` und `m=4..32`. Die Rückverschlüsselung braucht das Inverse von a,
der Anfangsschlüssel das Inverse von b. Der negative Faktor -1 wird als 28 gespeichert.
Die affine Algebra und frühere Tests kurzer Verzögerungen sind keine neue Entdeckung.

22.736 Familien werden pro Eingabe bewertet. Pro Schlüssellänge bleiben8 von784
Koeffizientenpaaren erhalten; für232 Familien folgen die festgelegten Suchbudgets
aus E066. Die Vorauswahl verwendet Häufigkeitstabellen: Multiplizieren mit a
permutiert die 29 möglichen Präfixwerte. Dadurch kann dieselbe Unigramm-Bewertung
schneller berechnet werden. Die unabhängige Prüfung zählt keine solchen Tabellen,
sondern setzt die Symbole direkt in die Formel ein. Bewertungsdifferenzen müssen
unter 1e-7 liegen. Die Rangfolge verwendet auf 9 Nachkommastellen gerundete Scores,
danach die vorab festgelegte Reihenfolge. Es bleibt eine heuristische Suche.
Die größere Parameterliste garantiert keinen höheren Score auf jeder Eingabe:
Die begrenzte Vorauswahl kann frühere Familien verwerfen, und neue feste Seeds
können andere lokale Maxima liefern. Frühere Ergebnisse bleiben separat erhalten.

Zwölf neue Schlüssel verschlüsseln bereits betrachtete, vom Training ausgeschlossene
Emerson-Abschnitte mit 200/300/729/3.316 Runen. Vier E066-Eingaben sind Regressionen
für den geänderten Algorithmus. Alle 16 liefern den vollständigen Klartext sowie
Schlüssel und Koeffizienten exakt. Ein vollständiger diagnostischer Nulllauf erreicht
{controls['null_score']:.6f}; daraus wird kein p-Wert berechnet.

| Kontrolle | Runen | m | a | b | Vorauswahlrang | Ergebnis |
|---|---:|---:|---:|---:|---:|---|
{control_table}

## E069: Originaltexte und passende Nulltexte

46 einzelne LP2-Seiten ab 200 Runen und 10 bestehende Seitengruppen bilden 56
Eingabehypothesen. Die Gruppen vertreten alle 55 unbekannten Runenseiten; sie
sind keine bestätigten Chiffrengrenzen. In Gruppen läuft der Schlüsselstrom
über Seitenwechsel fort. LP2-50 bleibt mit Quellreferenzen als leere Runenspanne
erhalten; ihre Zahlen werden nicht entschlüsselt.

| Eingabe | Runen | m | a | b | Score |
|---|---:|---:|---:|---:|---:|
{unknown_table}

Stärkste Eingabe: **{unknown['selected_section']}**, Score {unknown['score']:.6f}.
Auswahl und alle 56 Ergebnishashes wurden vor den ersten 19 Nullversuchen fixiert.
Keiner dieser 19 Nullscores übertraf die Auswahl; die separat registrierte
Nachprüfung E070 ergänzt daher 99 frische Nulltexte. Die ursprünglichen
Ergebnisse bleiben unverändert erhalten.
Jeder Nulltext erhält pro Seite Häufigkeiten, Randrunen und die Zahl gleicher
Nachbarn und durchläuft die vollständige Vorauswahl und Optimierung.
**{unknown['exceedances']}/99 frische** Nullscores erreichen mindestens den beobachteten Wert.
Plus-eins-p={unknown['raw_p']:.2f}; Bonferroni56={unknown['bonferroni56']:.2f}.
Die p-Werte verwenden ausschließlich die 99 frischen Vergleiche. Die ersten 19
werden nicht zu einem adaptiv gestoppten p-Wert zusammengelegt. Der kleinste
mögliche korrigierte Wert dieser Nachprüfung beträgt 0,56.
Dies ist ein grober Vergleich, kein Signifikanznachweis mit ausreichender Auflösung.
Eine Nulltrefferzahl von null verlangt eine gesondert registrierte größere Kalibrierung.

## Validierung und Grenzen

Unabhängige Quellenrekonstruktion, modulare Warteschlangen, Rückverschlüsselung,
direkte Familienbewertung, Kandidatenscores, Koordinatenmaxima und Seitenübergänge
sind geprüft. Alle 732.540 Sprachmodell-Tabelleneinträge wurden durch separate
skalare Wahrscheinlichkeitsrechnung kontrolliert; Sequenzscores wurden zusätzlich
an sechs Längen mit zwei Modellordnungen gegengeprüft. Alle {seed_audit['seeded_initializers_checked']} Startpräfixe wurden aus den Seeds
reproduziert. {count} Tests bestanden; insbesondere alle 784 Koeffizientenpaare
an zwei Verzögerungen und Histogramm-Bewertungen gegen direkte Enumeration.

191 registrierte Aufgaben, {seconds:.3f} Sekunden erfolgreiche Experimentzeit;
höchster abgetasteter Prozessspeicher {summary['peak_sampled_bytes']/1024**2:.1f} MiB.
Budget 3.600 Sekunden Experimentzeit, 180 pro Aufgabe, 768 MiB, ein Worker.
Validierungszeiten stehen zusätzlich in den Prüfdateien. Keine laufenden Jobs.
Quellbytes, alte Programme und historische Ergebnisse bleiben unverändert.
Die Kontrollen beweisen keine vollständige Suche über alle Schlüssel, Texte oder Grenzen.

Nächster ungetesteter Schritt: {'größere Nullkalibrierung der fixierten Auswahl.' if pending else 'eine begrenzte Erweiterung um eine additive Konstante, einschließlich Sonderfall b=1, zuerst an Kontrollen.'}

[Kontrollplan](../experiments/bilinear_feedback_plan.json),
[Angriffsplan](../experiments/bilinear_feedback_unknown_plan.json),
[Plan der frischen Nullversuche](../experiments/bilinear_feedback_more_null_plan.json),
[Messübersicht](../results/phase25_summary.json),
[Kandidat mit Originalgrenzen](phase25_selected_candidate.md),
[Checkpoint](../checkpoints/phase25_complete.json).
'''
    (ROOT/'reports/attack_phase25_report.md').write_text(report,encoding='utf-8')
    path=ROOT/'README.md';original=path.read_bytes().decode('utf-8');text=original.replace('\r\n','\n')
    a,b=text.index('Reproduzierbare Kryptanalyse'),text.index('Start:')
    text=text[:a]+('Reproduzierbare Kryptanalyse des Liber Primus. **Keine neue Entschlüsselung\n'
        'nachgewiesen.** Serie 25 prüft beide Koeffizienten über alle Nichtnullwerte:\n'
        '16 Kontrollen exakt, 46 Einzel-Seiten und 10 Seitengruppen direkt angegriffen.\n'
        f'{unknown["exceedances"]}/99 frische Nullscores mindestens so hoch wie der stärkste Kandidat.\n\n')+text[b:]
    text=text.replace('reports/attack_phase24_report.md','reports/attack_phase25_report.md',1)
    text=text.replace('reports/phase25_interim_report.md','reports/attack_phase25_report.md',1)
    text=re.sub(r'\n\*\*Serie 25 in Arbeit:\*\*[^\n]*\n','\n',text)
    text=re.sub(r'- \d+ Tests bestanden; \d+ Experimentgruppen',f'- {count} Tests bestanden; 69 Experimentgruppen',text,count=1)
    text=text.replace('## Aktueller Stand\n\n','## Aktueller Stand\n\n'
        '- E068: alle 16 Kontrollen exakt; 22.736 Familien pro Eingabe, direkte Gegenprüfung der Vorauswahl.\n'
        f'- E069/E070: 56 Eingabehypothesen, {unknown["exceedances"]}/99 frische Nullscores mindestens so hoch; keine neue Lösung.\n',1)
    before,after=original.splitlines(keepends=True),text.splitlines(keepends=True);out=[]
    matcher=difflib.SequenceMatcher(a=[x.rstrip('\r\n') for x in before],b=[x.rstrip('\r\n') for x in after],autojunk=False)
    for tag,a,b,c,d in matcher.get_opcodes():out.extend(before[a:b] if tag=='equal' else after[c:d])
    path.write_bytes(''.join(out).encode('utf-8'))
    save('checkpoints/phase25_complete.json',{'created_at':now,'status':status,'summary':'results/phase25_summary.json',
        'summary_sha256':sha('results/phase25_summary.json'),'experiments':entries})
    print({'status':status,'tests_passed':count,'seconds':seconds,'exact_controls':16,'unknown_inputs':56,
        'exceedances':unknown['exceedances'],'bonferroni56':unknown['bonferroni56']})


if __name__=='__main__':main()
