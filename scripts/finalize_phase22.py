"""Checkpoint verified long-seed autokey controls and direct LP2 search."""
from collections import Counter
from datetime import datetime,timezone
import difflib
import json
import re
import subprocess
import sys
from verify_autokey_extended import ROOT,load,sha
def save(path,data):(ROOT/path).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')


def main():
    assert not (ROOT/'checkpoints/phase22_complete.json').exists()
    controls=load('results/phase22_controls_validation.json');unknown=load('results/phase22_unknown_validation.json')
    assert controls['full_gate_passed'] and len(controls['controls'])==12 and len(unknown['pages'])==46
    entries=controls['entries']+unknown['entries'];assert len(entries)==79
    events=[json.loads(x) for x in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    done=[e for e in events if e['status']=='completed'];by_fp={e['fingerprint']:e for e in done}
    for entry in entries:
        event=by_fp[entry['fingerprint']];assert sha(entry['output'])==entry['sha256']==event['output_sha256']
        for path,digest in event['input_dependencies'].items():assert sha(path)==digest,path
    old_log=subprocess.check_output(['git','show','HEAD:experiment_log.jsonl'],cwd=ROOT)
    assert (ROOT/'experiment_log.jsonl').read_bytes().startswith(old_log)
    result=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=60)
    output=result.stdout+result.stderr;(ROOT/'results/validation_phase22.txt').write_text(output,encoding='utf-8')
    if result.returncode:raise RuntimeError(output)
    count=int(re.search(r'Ran (\d+) tests',output)[1]);now=datetime.now(timezone.utc).isoformat()
    validation=Counter(controls['validation']);validation.update(unknown['validation'])
    seconds=controls['seconds']+unknown['seconds'];assert seconds<2400
    comparisons=[]
    for control in controls['controls']:
        row=load(control['output']);truth=row['source']['truth_runes'];branch={}
        from liberprimus.autokey_chains import decode_prefix
        from attack_support import to_runes
        for origin in ('coordinate','beam'):
            candidates=[r for f in row['result']['families'] for r in f['candidates'] if r['origin']==origin]
            winner=max(candidates,key=lambda r:r['score'])
            plain,_=decode_prefix(row['source']['ciphertext_indices'],winner['prefix'],winner['cipher_sign'],winner['feedback_sign'])
            branch[origin]=to_runes(plain)==truth
        comparisons.append({'index':control['index'],'before_refinement_exact':branch,'after_union_refinement_exact':control['exact']})
    summary={'controls':controls['controls'],'branch_comparisons':comparisons,'control_null_score':controls['null_score'],
        'null_deviation':controls['null_deviation'],'original_noncompliant_null_score':controls['original_noncompliant_null_score'],
        'unknown':{k:v for k,v in unknown.items() if k not in ('entries','validation')},'validation':dict(validation),
        'tests_passed':count,'successful_tasks':len(entries),'seconds':seconds,
        'peak_sampled_bytes':max(controls['peak_sampled_bytes'],unknown['peak_sampled_bytes']),
        'new_decryptions':[]}
    save('results/phase22_summary.json',summary)
    pending=unknown['pending_larger_calibration'];status='twentysecond_batch_autokey_'+('larger_null_pending' if pending else 'no_supported_decryption')
    next_item=({'id':'H045','priority':1,'task':'Preregister larger full-optimizer null calibration for the frozen E063 selected page; no significance claim from19 nulls.'} if pending else
        {'id':'H046','priority':1,'task':'Test continuous plaintext-autokey across the existing LP2 section groups. First calibrate the unchanged4..32 seed solver on fresh-key long controls up to3316 runes, including retained empty numeric-page spans. Page grouping is a hypothesis; use full matched nulls and selection correction. No per-page resets, F omissions or invented plaintext cribs.'})
    queue=[next_item,{'id':'H031','priority':2,'task':'General substitution deferred pending independently justified scoring repair.'},
        {'id':'H023','priority':3,'task':'Delay3 feedback deferred pending feasible calibrated reduction.'}]
    state=load('research_state.json');old_fps={e['fingerprint'] for e in state['completed_experiments']}
    assert not any(e['fingerprint'] in old_fps for e in entries)
    state['completed_experiments']+=entries
    state.update(status=status,updated_at=now,latest_report='reports/attack_phase22_report.md',next_experiments=[q['id'] for q in queue],new_decryptions=[],promising_candidates=[],
        session_budget={'phase':'twentysecond long-seed plaintext-autokey','max_compute_wall_seconds':2400,'max_experiment_wall_seconds':180,'memory_ceiling_mib':768,'workers':1,'background_jobs':False},
        scoring_gate='E06212/12 fresh-key blind controls exact; source, queue inverse and conditional coordinate maxima independently checked. E06346 eligible unknown pages plus19 matched endpoint-preserving nulls verified.',
        notes=['No previously unknown plaintext confirmed. Direct cryptanalysis only.',
            '4..32-rune plaintext-autokey seeds, four sign pairs, no omitted symbols, reset at each original page.',
            'All12 controls exact for200/300/729 runes; synthetic validation is not evidence of the authentic cipher.',
            'Nine shorter unknown rune pages excluded by validated length bound; LP2-50 numeric page explicitly retained in exclusion ledger.',
            controls['null_deviation'],
            'Unchanged original sources, earlier outputs and append-only experiment history. No running research jobs.'])
    state['validation'].update(tests_passed=count,path='results/validation_phase22.txt',phase22=dict(validation))
    state['resources'].update(recorded_successful_experiment_runs=len(done),recorded_experiment_subprocess_wall_seconds=sum(e['wall_seconds'] for e in done),phase22_wall_seconds=seconds)
    state['failed_approaches'].append(f'E063 page-local plaintext-autokey4..32 without skips: {unknown["exceedances"]}/19 matched null scores >= selected page; adjusted p={unknown["bonferroni46"]}. No confirmed decryption; heuristic negative screen does not exclude cipher family.')
    save('research_state.json',state)
    hypotheses=load('hypotheses.json');by_id={h['id']:h for h in hypotheses['hypotheses']}
    by_id['H045'].update(status='controls_passed_'+('larger_null_pending' if pending else 'page_local_unknown_screen_negative'),experiments=['E062','E063'],
        result={'controls_exact':12,'controls_total':12,'unknown_pages':46,'exceedances':unknown['exceedances'],'raw_p':unknown['raw_p'],'bonferroni46':unknown['bonferroni46'],'summary':'results/phase22_summary.json'},
        limits='Finite heuristic search, only no-skip page-local rule and200..729 rune control lengths. Null-generator endpoint mismatch recorded and corrected in a separate preserved run. Original E017 recurrence is reused, not novel.')
    if not pending:
        assert 'H046' not in by_id
        hypotheses['hypotheses'].append({'id':'H046','status':'queued_untested','claim':'A plaintext-feedback stream might continue across original page boundaries rather than restarting on each page.',
            'basis':'E063 validates and screens page-local4..32 seeds; it does not test cross-page continuation. Existing section groupings are unverified cipher-boundary hypotheses.',
            'mechanism':'Apply unchanged autokey recurrence to concatenated existing section rune streams, preserve source page spans and empty LP2-50. No language or key reset between pages.',
            'success_criterion':'Prospective bounds, fresh-key long controls and shorter regressions, independent original-source and queue replay; exact controls before unknown scan, full optimizer nulls and correction across groups.',
            'limits':'Untested proposal, no E064 result and no evidence that any proposed grouping is authentic. Longer text can help residue estimation but may be invalid if actual pages restart.'})
    hypotheses.update(status=status,updated_at=now,next_queue=queue);save('hypotheses.json',hypotheses)
    table='\n'.join(f'| {r["index"]} | {r["runes"]} | {r["key_length"]} | exakt |' for r in controls['controls'])
    best=sorted(unknown['pages'],key=lambda r:r['score'],reverse=True)[:5]
    page_table='\n'.join(f'| {r["page"]} | {r["runes"]} | {r["key_length"]} | {r["score"]:.6f} |' for r in best)
    coordinate=sum(r['before_refinement_exact']['coordinate'] for r in comparisons);beam=sum(r['before_refinement_exact']['beam'] for r in comparisons)
    report=f'''# Forschungsserie 22: Längere Autokey-Startschlüssel direkt geprüft

Stand (UTC): {now}. **Keine neue Entschlüsselung bestätigt.**
Zwölf Blindkontrollen wurden exakt rekonstruiert. Danach lief dieselbe Suche
auf 46 unbekannten LP2-Seiten; der stärkste Kandidat wurde gegen 19 vollständig
optimierte Zufallstexte geprüft.

## E062: Suchverfahren und Kalibrierung

Untersucht wird `P_i = cs*C_i + ks*P_(i-m) (mod 29)` nach einem unbekannten
Startschlüssel der Länge m. Beide Vorzeichen sind jeweils +1 oder -1.
Alle Runen verbrauchen einen Schritt, einschließlich F. Die affine Darstellung
jeder Restklasse durch ihre erste Klartextrune stammt bereits aus E014/E017;
sie wird hier wiederverwendet und nicht als neue Entdeckung bezeichnet.

E017 erfasste Längen 4–12. Die neue Suche erfasst 4–32 mit vier Vorzeichenpaaren,
also 116 Familien pro Eingabe. Acht Häufigkeitsstarts je Familie werden durch
bis zu sechs vollständige Koordinatendurchläufe auf dem Trigrammziel
verbessert. Daneben läuft eine feste Beam-Suche mit Breite 128, zwei Schnitten
und zwei behaltenen Pfaden pro Schnitt. Beide Mengen werden nach Viergrammen
bewertet; die zwölf besten unterschiedlichen Startkombinationen werden jeweils
bis zu sechs vollständige Koordinatendurchläufe weiter verbessert.
Das ist eine begrenzte Heuristik, kein globaler Optimalitätsbeweis.

Trainiert wird unverändert auf Emerson I, III–IX. Kontrolltexte stammen aus
X/XI/XII, mit separat festgelegten Textbereichen und neuen Zufallsschlüsseln
aus allen 29 Symbolen. Die Kapitel sind historisch bekannt; die Fälle sind
keine unabhängige neue Textsammlung. Die kurzen Schlüssel 4/8/12 sind frische
Regressionstests, keine erneute Ausführung der historischen E017-Kontrollen.

| Kontrolle | Runen | Startschlüssellänge | Klartext |
|---|---:|---:|---|
{table}

Alle zwölf Fälle rekonstruieren den vollständigen Klartext; auch die injizierten
Rezepte wurden separat geprüft. Vor der abschließenden Verfeinerung liefert
der Häufigkeitszweig {coordinate}/12 und der Beam-Zweig {beam}/12 exakte
Spitzenkandidaten. Dies ist ein beschreibender Vergleich unterschiedlicher
fester Rechenbudgets, keine Aussage über gleiche Laufzeit oder allgemeine Güte.

### Dokumentierte Abweichung beim diagnostischen Nullversuch

E062-null-2 verwendete versehentlich den bereits vorhandenen Generator für
vollständige Permutationen. Er erhält Häufigkeiten und die Zahl gleicher
Nachbarn, aber nicht die im Plan vorgeschriebenen Randrunen. Die unabhängige
Prüfung hat diese Abweichung erkannt. Ausgabe und Protokoll bleiben unverändert;
der Score {controls['original_noncompliant_null_score']:.6f} wird nicht als
plankonformer Vergleich verwendet. Der separat registrierte Lauf
E062-null-endpoints erhält zusätzlich beide Randrunen und erreicht
{controls['null_score']:.6f}. Er verwendet denselben Solver und denselben Seed.
Erst nach seiner unabhängigen Prüfung wurde E063 gestartet. Aus einzelnen
diagnostischen Nullversuchen wird kein p-Wert abgeleitet.

## E063: Unbekannte Seiten und Zufallsvergleich

46 unbekannte LP2-Seiten mit mindestens 200 Runen wurden einzeln untersucht.
Neun kürzere Runenseiten sind außerhalb des getesteten Längenbereichs und
wurden in dieser Serie nicht angegriffen. LP2-50 bleibt als Zahlenseite ohne
Runen ausdrücklich erfasst. Vollständige Seiten- und Ausschlusslisten samt
Quellreferenzen stehen im Plan und der Messübersicht. Keine Quellnormalisierung
und keine nachträgliche Anpassung der Suchparameter.

Die fünf höchsten Scores sind:

| Seite | Runen | gefundene Startschlüssellänge | Score |
|---|---:|---:|---:|
{page_table}

Nach allen 46 Seiten wurde **{unknown['selected_page']}** ausgewählt und die
Auswahl samt Ausgabehashes vor den Nullversuchen festgeschrieben. Jede der
19 unabhängigen Permutationen erhält Häufigkeiten, Randrunen und die Zahl
benachbarter gleicher Runen; jede durchläuft alle 116 Familien und dieselbe
abschließende Auswahl und Verfeinerung. **{unknown['exceedances']}/19** erreichen
mindestens den beobachteten Score. Plus-eins-p={unknown['raw_p']:.2f};
Bonferroni-Korrektur für 46 Seiten={unknown['bonferroni46']:.2f}.
Mit nur 19 Nullversuchen kann diese Korrektur keinen signifikanten Wert liefern.
Ein solcher Grobvergleich ist ein Filter gegen zufällige Sprachähnlichkeit;
er bestätigt keinen Klartext und schließt die Chiffrenfamilie nicht aus.

## Prüfung, Ressourcen und nächster Schritt

{count} Unit-Tests bestanden. Separater Verifikationscode rekonstruiert die
Klartexte durch eine skalare Schlüsselwarteschlange, prüft Rückverschlüsselung,
Quellbereiche, feste Seeds, gespeicherte Scores, bedingte Koordinatenmaxima und
die Auswahlkorrektur. Einzelne ungeänderte historische Ergebnisse wurden nicht
erneut berechnet. Die genaue Zahl aller Prüfungen steht in der Messübersicht.

{len(entries)} registrierte Aufgaben, {seconds:.3f} Sekunden gemessene erfolgreiche
Experimentzeit. Budget 2400 Sekunden pro Serie, höchstens 180 pro Aufgabe;
ein Worker, höchster abgetasteter Speicherwert {summary['peak_sampled_bytes']/1024**2:.1f} MiB
bei 768 MiB Grenze. Keine weiterlaufenden Forschungsprozesse.

Nächster Vorschlag, noch ungetestet: {'größere Nullkalibrierung der festgeschriebenen Auswahl.' if pending else 'Autokey ohne Neustart über vorhandene Seitengruppen hinweg. Zuerst sind längere Kontrollen erforderlich; die Gruppierung selbst bleibt eine Hypothese.'}

[Kontrollplan](../experiments/autokey_extended_plan.json),
[Nullkorrektur](../experiments/autokey_endpoint_null_plan.json),
[Angriffsplan](../experiments/autokey_extended_unknown_plan.json),
[Messübersicht](../results/phase22_summary.json),
[Checkpoint](../checkpoints/phase22_complete.json).
'''
    (ROOT/'reports/attack_phase22_report.md').write_text(report,encoding='utf-8')
    path=ROOT/'README.md';original=path.read_bytes().decode('utf-8');text=original.replace('\r\n','\n')
    a,b=text.index('Reproduzierbare Kryptanalyse'),text.index('Start:')
    text=text[:a]+('Reproduzierbare Kryptanalyse des Liber Primus. **Keine neue Entschlüsselung\n'
        'nachgewiesen.** Serie 22 erweitert die Autokey-Suche auf Startschlüssel\n'
        'mit 4–32 Runen: zwölf Blindkontrollen exakt, 46 unbekannte Seiten geprüft.\n'
        f'19 passende Zufallstexte ergeben ein korrigiertes p={unknown["bonferroni46"]:.2f}.\n\n')+text[b:]
    text=text.replace('Start: [Aktueller Forschungsbericht](reports/attack_phase21_report.md)','Start: [Aktueller Forschungsbericht](reports/attack_phase22_report.md)')
    text=text.replace('- 124 Tests bestanden; 60 Experimentgruppen',f'- {count} Tests bestanden; 62 Experimentgruppen')
    text=text.replace('## Aktueller Stand\n\n','## Aktueller Stand\n\n'
        '- E062: 12/12 Autokey-Kontrollen exakt; Abweichung beim Nullgenerator erkannt,\n'
        '  historisch erhalten und durch separaten plankonformen Lauf ergänzt.\n'
        f'- E063: 46 unbekannte Seiten geprüft, {unknown["exceedances"]}/19 Nullscores mindestens so hoch.\n',1)
    before,after=original.splitlines(keepends=True),text.splitlines(keepends=True);out=[]
    matcher=difflib.SequenceMatcher(a=[x.rstrip('\r\n') for x in before],b=[x.rstrip('\r\n') for x in after],autojunk=False)
    for tag,a,b,c,d in matcher.get_opcodes():out.extend(before[a:b] if tag=='equal' else after[c:d])
    path.write_bytes(''.join(out).encode('utf-8'))
    save('checkpoints/phase22_complete.json',{'created_at':now,'status':status,'summary':'results/phase22_summary.json',
        'summary_sha256':sha('results/phase22_summary.json'),'experiments':entries})
    print({'status':status,'tests_passed':count,'seconds':seconds,'controls_exact':12,'unknown_pages':46,
        'exceedances':unknown['exceedances'],'bonferroni46':unknown['bonferroni46']})


if __name__=='__main__':main()
