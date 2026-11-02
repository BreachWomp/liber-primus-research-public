"""Checkpoint the independently validated general-feedback search."""
from collections import Counter
from datetime import datetime,timezone
import difflib
import json
import re
import subprocess
import sys
from verify_general_feedback import ROOT,load,sha


def save(path,data):
    (ROOT/path).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def main():
    assert not (ROOT/'checkpoints/phase24_complete.json').exists()
    controls=load('results/phase24_controls_validation.json');unknown=load('results/phase24_unknown_validation.json')
    assert controls['full_gate_passed'] and len(controls['controls'])==16
    assert unknown['unique_unknown_rune_pages']==55 and unknown['empty_pages_preserved']==['LP2-50']
    entries=controls['entries']+unknown['entries'];assert len(entries)==92
    seed_audit=load('results/phase24_seed_audit.json')
    assert seed_audit['families_checked']==92*116 and seed_audit['seeded_initializers_checked']==92*116*8
    assert seed_audit['outputs']=={e['output']:e['sha256'] for e in entries}
    fragments=load('results/phase24_language_fragments.json')
    for page in fragments['pages']:
        assert sha(page['output'])==page['output_sha256']
    events=[json.loads(x) for x in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    done=[e for e in events if e['status']=='completed'];by_fp={e['fingerprint']:e for e in done}
    for entry in entries:
        event=by_fp[entry['fingerprint']];assert sha(entry['output'])==entry['sha256']==event['output_sha256']
        for path,digest in event['input_dependencies'].items():assert sha(path)==digest,path
    assert (ROOT/'experiment_log.jsonl').read_bytes().startswith(subprocess.check_output(['git','show','HEAD:experiment_log.jsonl'],cwd=ROOT))
    tests=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=60)
    output=tests.stdout+tests.stderr;(ROOT/'results/validation_phase24.txt').write_text(output,encoding='utf-8')
    if tests.returncode:raise RuntimeError(output)
    count=int(re.search(r'Ran (\d+) tests',output)[1]);now=datetime.now(timezone.utc).isoformat()
    validation=Counter(controls['validation']);validation.update(unknown['validation'])
    seconds=controls['seconds']+unknown['seconds'];assert seconds<3000
    summary={'controls':controls['controls'],'control_null_score':controls['null_score'],
        'unknown':{k:v for k,v in unknown.items() if k not in ('entries','validation')},
        'validation':dict(validation),'tests_passed':count,'successful_tasks':len(entries),'seconds':seconds,
        'peak_sampled_bytes':max(controls['peak_sampled_bytes'],unknown['peak_sampled_bytes']),
        'control_validation_sha256':sha('results/phase24_controls_validation.json'),
        'unknown_validation_sha256':sha('results/phase24_unknown_validation.json'),'new_decryptions':[]}
    summary['seed_audit_sha256']=sha('results/phase24_seed_audit.json')
    summary['language_fragments_sha256']=sha('results/phase24_language_fragments.json')
    save('results/phase24_summary.json',summary)
    pending=unknown['pending_larger_calibration'];status='twentyfourth_batch_general_feedback_'+('larger_null_pending' if pending else 'no_supported_decryption')
    next_item=({'id':'H047','priority':1,'task':'Preregister larger null calibration for immutable E067 selection; no significance claim from19 nulls.'} if pending else
        {'id':'H048','priority':1,'task':'Bound and calibrate a joint search with cipher coefficient a=1..28 as well as feedback b=1..28 at delays4..32. Freeze family screening before fresh-key controls with a outside1/28 and coefficient-pair regressions. Benchmark enlarged screening before unknown data; preserve E066/E067 outcomes.'})
    queue=[next_item,{'id':'H031','priority':2,'task':'General substitution deferred pending independently justified scoring repair.'},
        {'id':'H023','priority':3,'task':'Delay3 feedback deferred pending feasible calibrated reduction.'}]
    state=load('research_state.json');old={e['fingerprint'] for e in state['completed_experiments']}
    assert not any(e['fingerprint'] in old for e in entries);state['completed_experiments']+=entries
    state.update(status=status,updated_at=now,latest_report='reports/attack_phase24_report.md',next_experiments=[q['id'] for q in queue],
        new_decryptions=[],promising_candidates=[],session_budget={'phase':'twentyfourth general plaintext feedback','max_compute_wall_seconds':3000,
            'max_experiment_wall_seconds':180,'memory_ceiling_mib':768,'workers':1,'background_jobs':False},
        scoring_gate='E06616/16 full plaintext/key/coefficient controls exact; independently verified1624-family screening and candidates. E06746 page-local plus10 continuous-group hypotheses,19 selected-input full null optimizations.',
        notes=['No previously unknown plaintext confirmed. Direct cryptanalysis only.',
            'General feedback b1..28; cipher multiplier restricted to+1/-1; delays4..32; no skipped runes. Top4 families per period retained after unigram screening.',
            '12 fresh-key controls on previously inspected excluded texts plus4 old control inputs under changed search. No claim of16 unseen texts or unchanged-search reuse.',
            'All55 unknown rune pages represented within10 overlapping group hypotheses;46 separately searched. Numeric LP2-50 preserved as empty rune span, not decrypted.',
            'Original sources and historical results unchanged; no running research jobs.'])
    state['validation'].update(tests_passed=count,path='results/validation_phase24.txt',phase24=dict(validation))
    state['resources'].update(recorded_successful_experiment_runs=len(done),recorded_experiment_subprocess_wall_seconds=sum(e['wall_seconds'] for e in done),phase24_wall_seconds=seconds)
    state['failed_approaches'].append(f'E067 general b1..28, a+/-1 feedback4..32:56 hypotheses; {unknown["exceedances"]}/19 matched nulls >= strongest score, adjusted p={unknown["bonferroni56"]}. No supported decryption; heuristic family selection limits remain.')
    save('research_state.json',state)
    hypotheses=load('hypotheses.json');by_id={h['id']:h for h in hypotheses['hypotheses']}
    by_id['H047'].update(status='controls_passed_'+('larger_null_pending' if pending else 'unknown_screen_negative'),experiments=['E066','E067'],
        result={'controls_exact':16,'controls_total':16,'fresh_keys_general_coefficients':12,'old_control_inputs_rerun_changed_search':4,
            'unknown_page_hypotheses':46,'unknown_group_hypotheses':10,'unknown_rune_pages':55,
            'exceedances':unknown['exceedances'],'raw_p':unknown['raw_p'],'bonferroni56':unknown['bonferroni56'],'summary':'results/phase24_summary.json'},
        limits='Heuristic top4 of56 coefficient pairs per period. Controls cover b2/7/14/27 and1/28, not all possible keys or texts. Cipher multiplier remains+1/-1; no skips or unknown boundary search.')
    if not pending:
        assert 'H048' not in by_id
        hypotheses['hypotheses'].append({'id':'H048','status':'queued_untested',
            'claim':'The ciphertext coefficient may also differ from+1/-1 in a delayed plaintext-feedback recurrence.',
            'basis':'E066/E067 generalize only feedback b; E020 short-delay general multipliers remain prior work.',
            'mechanism':'P_i=a*C_i+b*P_(i-m) mod29, a,b1..28, delays4..32. Each delay has784 coefficient pairs; bounded screened search needs new calibration.',
            'success_criterion':'Preregister finite runtime, memory, seeds and family retention; fresh-key controls with a outside1/28 and old-pair regression; independent modular queue and full-null verification before unknown claims.',
            'limits':'Untested proposal; no E068 result. Larger search can undermine family retention and increase null overfitting. No affine constant, omissions or unknown resets.'})
    hypotheses.update(status=status,updated_at=now,next_queue=queue);save('hypotheses.json',hypotheses)
    control_table='\n'.join(f'| {r["index"]} | {r["runes"]} | {r["key_length"]} | {r["cipher_sign"]} | {r["feedback_sign"]} | {r["family_rank"]} | exakt |' for r in controls['controls'])
    unknown_table='\n'.join(f'| {r["section"]} | {r["runes"]} | {r["key_length"]} | {r["cipher_sign"]} | {r["feedback_sign"]} | {r["score"]:.6f} |' for r in unknown['sections'])
    report=f'''# Forschungsserie 24: Allgemeine Klartextrückkopplung

Stand (UTC): {now}. **Keine neue Entschlüsselung bestätigt.**
16 Kontrollen exakt; anschließend 46 einzelne unbekannte LP2-Seiten und zehn
bestehende Seitengruppen direkt angegriffen. Originalquellen und alte Ergebnisse
bleiben unverändert. Es wurden keine unbelegten Community-Lösungen untersucht.

## Mechanismus und festgelegte Begrenzung

E066/E067 prüfen `P_i = a*C_i + b*P_(i-m) mod 29` mit `a=+1/-1`,
`b=1..28`, `m=4..32`. Der Anfangsschlüssel ergibt sich aus den ersten m
Klartextsymbolen durch Multiplikation mit dem modularen Inversen von b.
Alle Kettenkoeffizienten werden modulo 29 reduziert, damit lange Ketten nicht
überlaufen. Das verallgemeinert die frühere Suche; die affine Algebra und
frühere Tests kurzer Verzögerungen sind keine neue Entdeckung.

Pro Eingabe werden 1.624 Familien nach maximaler Unigramm-Bewertung geprüft.
Innerhalb jeder Schlüssellänge bleiben genau vier der 56 Koeffizientenpaare
erhalten. Für diese 116 Familien folgen die festen E062-Budgets für zwei
Initialisierungen, Trigramm- und Viergramm-Verfeinerung. Die Suche ist heuristisch;
eine erfolgreiche Kontrolle garantiert nicht, dass jede echte Familie erhalten bleibt.

## E066: Blindkontrollen und diagnostischer Nulltext

Zwölf neue Zufallsschlüssel verschlüsseln 200/300/729/3.316 Runen aus den
vom Training ausgeschlossenen Emerson-Kapiteln X/XI/XII. Die Textbereiche
wurden bereits zuvor betrachtet. Vier alte E062-Kontrolleingaben werden mit
dem geänderten Algorithmus neu bearbeitet; sie sind weder neue Texte noch
unverändert übernommene Suchläufe. Bei allen 16 Kontrollen stimmen Klartext,
Schlüssel und beide Koeffizienten exakt; die richtige Familie steht jedes Mal
auf Rang eins. Die alten Vorzeichen -1 werden als Restklasse 28 dargestellt.

| Kontrolle | Runen | m | a | b | Rang | Ergebnis |
|---|---:|---:|---:|---:|---:|---|
{control_table}

Ein vollständiger diagnostischer Nulllauf erhält Randrunen, Häufigkeiten
und die Zahl gleicher Nachbarn. Score: {controls['null_score']:.6f}.
Aus diesem einzelnen Vergleich wird kein p-Wert abgeleitet.

## E067: Unbekannte Seiten und Fortsetzungen

46 Seiten mit mindestens 200 Runen werden einzeln untersucht; die zehn
bestehenden Gruppen ergänzen die Hypothese eines über Seitengrenzen
fortlaufenden Stroms. Zusammen vertreten sie alle 55 unbekannten Runenseiten.
Die Gruppengrenzen bleiben unbestätigt. LP2-50 bleibt mit Quellreferenzen als
leere Runenspanne erhalten; ihre Zahlen sind damit nicht entschlüsselt.

| Eingabe | Runen | m | a | b | Score |
|---|---:|---:|---:|---:|---:|
{unknown_table}

Die stärkste Eingabe ist **{unknown['selected_section']}** mit Score
{unknown['score']:.6f}. Ihre Auswahl und sämtliche 56 Ergebnishashes wurden
vor den Nullversuchen fixiert. 19 Nulltexte bewahren pro Originalseite
Häufigkeiten, Randrunen und gleiche Nachbarn. Jeder durchläuft die gesamte
Vorauswahl und Optimierung erneut; interne Auswahl wird dadurch berücksichtigt.

**{unknown['exceedances']}/19** Nullscores erreichen mindestens den beobachteten
Wert. Plus-eins-p={unknown['raw_p']:.2f}, Bonferroni für 56 ausgewählte
Eingabehypothesen={unknown['bonferroni56']:.2f}. Bei nur 19 Nullversuchen kann
der korrigierte Wert hier niemals unter 1 fallen. Dies ist eine grobe
Aussortierung, kein Signifikanztest mit ausreichender Auflösung. Nulltrefferzahl
null würde eine separat registrierte größere Kalibrierung verlangen.

## Unabhängige Prüfung und Ressourcen

Eine separate Schlüsselwarteschlange rekonstruiert Quellenkontrollen,
Kandidaten und Rückverschlüsselungen. Die Vorauswahl wird aus unabhängigen
Queue-Dekodierungen nachgerechnet; gespeicherte Sprachscores, Auswahl,
bedingte Koordinatenmaxima, Seitenübergänge und Nullgenerator werden geprüft.
Zusätzlich sind alle {seed_audit['seeded_initializers_checked']} Startpräfixe
aus den festgelegten Seeds unabhängig rekonstruiert.
{count} Unit-Tests bestanden, einschließlich aller 28 Rückkopplungsfaktoren
auf langen Ketten und unabhängiger Prüfung der Trigrammfaktoren.

{len(entries)} registrierte Aufgaben, {seconds:.3f} Sekunden erfolgreiche
Experimentzeit; höchster abgetasteter Prozessspeicher
{summary['peak_sampled_bytes']/1024**2:.1f} MiB. Festgelegtes Budget: 3.000
Sekunden Experimentzeit, 180 pro Aufgabe, 768 MiB, ein Worker. Keine laufenden Jobs.
Die unabhängigen Prüfzeiten stehen zusätzlich in den Validierungsdateien.

Nächster ungetesteter Schritt: {'größere Nullkalibrierung der unveränderten Auswahl.' if pending else 'auch den Chiffrekoeffizienten a über alle Nichtnullwerte erweitern, zunächst begrenzt und an Kontrollen kalibriert.'}

[Kontrollplan](../experiments/general_feedback_plan.json),
[Angriffsplan](../experiments/general_feedback_unknown_plan.json),
[Messübersicht](../results/phase24_summary.json),
[Sprachähnliche Stücke mit Originalgrenzen](phase24_language_fragments.md),
[Checkpoint](../checkpoints/phase24_complete.json).
'''
    (ROOT/'reports/attack_phase24_report.md').write_text(report,encoding='utf-8')
    path=ROOT/'README.md';original=path.read_bytes().decode('utf-8');text=original.replace('\r\n','\n')
    a,b=text.index('Reproduzierbare Kryptanalyse'),text.index('Start:')
    text=text[:a]+('Reproduzierbare Kryptanalyse des Liber Primus. **Keine neue Entschlüsselung\n'
        'nachgewiesen.** Serie 24 erweitert Klartextrückkopplung auf alle 28 Faktoren:\n'
        '16 Kontrollen exakt, 46 einzelne LP2-Seiten und zehn Seitengruppen geprüft.\n'
        f'{unknown["exceedances"]}/19 passende Nullscores mindestens so hoch wie der stärkste Kandidat.\n\n')+text[b:]
    text=text.replace('reports/attack_phase23_report.md','reports/attack_phase24_report.md',1)
    text=text.replace('- 126 Tests bestanden; 64 Experimentgruppen',f'- {count} Tests bestanden; 66 Experimentgruppen')
    text=text.replace('## Aktueller Stand\n\n','## Aktueller Stand\n\n'
        '- E066: alle 16 Kontrollen exakt; unabhängige Prüfung der Vorauswahl und Rückverschlüsselung.\n'
        f'- E067: 56 Eingabehypothesen, {unknown["exceedances"]}/19 Nullscores mindestens so hoch; keine neue Lösung.\n',1)
    before,after=original.splitlines(keepends=True),text.splitlines(keepends=True);out=[]
    matcher=difflib.SequenceMatcher(a=[x.rstrip('\r\n') for x in before],b=[x.rstrip('\r\n') for x in after],autojunk=False)
    for tag,a,b,c,d in matcher.get_opcodes():out.extend(before[a:b] if tag=='equal' else after[c:d])
    path.write_bytes(''.join(out).encode('utf-8'))
    save('checkpoints/phase24_complete.json',{'created_at':now,'status':status,'summary':'results/phase24_summary.json',
        'summary_sha256':sha('results/phase24_summary.json'),'experiments':entries})
    print({'status':status,'tests_passed':count,'seconds':seconds,'exact_controls':16,'unknown_inputs':56,
        'exceedances':unknown['exceedances'],'bonferroni56':unknown['bonferroni56']})


if __name__=='__main__':main()
