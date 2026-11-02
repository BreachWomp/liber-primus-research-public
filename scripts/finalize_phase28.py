"""Append the independently validated delay-two findings and checkpoint."""
from datetime import datetime,timezone
import difflib
import json
import re
import subprocess
import sys
from verify_delay_two import ROOT,load,sha,to_indices
from liberprimus.alphabet import RUNES,RUNE_ALIASES,LATIN


def save(path,data):
    (ROOT/path).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def main():
    assert not (ROOT/'checkpoints/phase28_complete.json').exists()
    controls=load('results/phase28_controls_validation.json')
    unknown=load('results/phase28_unknown_validation.json')
    benchmark=load(load('checkpoints/phase28_benchmark_complete.json')['output'])
    assert controls['full_gate_passed'] and len(controls['controls'])==16 and len(unknown['pages'])==55
    entries=controls['entries']+unknown['entries'];assert len(entries)==92
    assert controls['validation']['independent_full_prefix_scores']==18*107648
    assert unknown['validation']['independent_full_prefix_scores']==74*107648
    events=[json.loads(x) for x in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    done=[e for e in events if e['status']=='completed'];by_fp={e['fingerprint']:e for e in done}
    for r in entries:
        e=by_fp[r['fingerprint']];assert sha(r['output'])==r['sha256']==e['output_sha256']
        for path,digest in e['input_dependencies'].items():assert sha(path)==digest,path
    assert (ROOT/'experiment_log.jsonl').read_bytes().startswith(subprocess.check_output(['git','show','HEAD:experiment_log.jsonl'],cwd=ROOT))
    processes=load('results/phase28_processes.json')
    assert len(processes)==92 and all(p['exit_code']==0 and p['reason'] is None and p['seconds']<185 and p['peak_sampled_bytes']<=768*1024**2 for p in processes)
    tests=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=90)
    output=tests.stdout+tests.stderr;(ROOT/'results/validation_phase28.txt').write_text(output,encoding='utf-8')
    assert tests.returncode==0,output
    count=int(re.search(r'Ran (\d+) tests',output)[1]);now=datetime.now(timezone.utc).isoformat()
    seconds=sum(by_fp[e['fingerprint']]['wall_seconds'] for e in entries);assert seconds<1800
    pending=unknown['pending_larger_calibration'];peak=max(p['peak_sampled_bytes'] for p in processes)
    status='twentyeighth_batch_delay_two_'+('larger_null_pending' if pending else 'no_supported_decryption')
    summary={'created_at':now,'status':status,'controls':controls,'unknown':unknown,'tests_passed':count,
        'successful_tasks':92,'seconds':seconds,'peak_sampled_bytes':peak,'new_decryptions':[]}
    save('results/phase28_summary.json',summary)
    next_task=('Preregister fresh larger calibration of frozen E079 winner; do not adaptively pool the original19 nulls.' if pending else
        'Repair H031 substitution scoring using source-excluded short controls and original word boundaries; require exact blind control recovery before a direct unknown-page attack. Preserve previous scoring failures.')
    queue=[{'id':'H050' if pending else 'H031','priority':1,'task':next_task}]
    state=load('research_state.json');old={e['fingerprint'] for e in state['completed_experiments']}
    assert not any(e['fingerprint'] in old for e in entries);state['completed_experiments']+=entries
    state.update(status=status,updated_at=now,latest_report='reports/attack_phase28_report.md',next_experiments=[q['id'] for q in queue],
        new_decryptions=[],promising_candidates=[],session_budget={'phase':'twentyeighth delay-two affine constants',
            'max_compute_wall_seconds':1800,'max_experiment_wall_seconds':180,'memory_ceiling_mib':768,'workers':1,'background_jobs':False},
        scoring_gate='E07816/16 exact plaintext/key/a/b/c; E0772523 scalar prefix checks; independent queue verifies all107648 retained-family prefix scores per input. E07955pages plus19 full-search matched nulls.',
        notes=['No previously unknown plaintext confirmed. Direct cryptanalysis only.',
            'Delay2,a,b1..28,c0..28;128 of22736 families retained heuristically, all841 prefixes exact within each.',
            'Fresh keys on previously inspected excluded and partly overlapping Emerson blocks; not16 independent unseen texts.',
            'All55 unknown rune pages searched; numericLP2-50 preserved and source-anchored, not deciphered.',
            'Full-grid runtime is a pilot extrapolation, not an exhaustive search. Historical source/output preserved; no running research jobs.'])
    state['validation'].update(tests_passed=count,path='results/validation_phase28.txt',phase28={'controls':controls['validation'],'unknown':unknown['validation']})
    state['resources'].update(recorded_successful_experiment_runs=len(done),recorded_experiment_subprocess_wall_seconds=sum(e['wall_seconds'] for e in done),phase28_wall_seconds=seconds)
    state['failed_approaches'].append(f'E079 delay2 affine feedback with constants,55 pages: {unknown["exceedances"]}/19 full-search nulls >= selection; Bonferroni55={unknown["bonferroni55"]}. No supported decryption; discarded families not excluded.')
    save('research_state.json',state)
    hypotheses=load('hypotheses.json');h=next(h for h in hypotheses['hypotheses'] if h['id']=='H050')
    h.update(status='controls_passed_'+('larger_null_pending' if pending else 'unknown_screen_negative'),experiments=['E077','E078','E079'],
        limits='Top128 of22736 families, exact841 prefixes only within retained families. c0 included for matched regressions; c1..28 is new target. No omitted symbols/hidden boundaries. Negative result does not exclude full cipher class.',
        result={'controls_exact':16,'unknown_pages':55,'exceedances':unknown['exceedances'],'nulls':19,
            'raw_p':unknown['raw_p'],'bonferroni55':unknown['bonferroni55'],'summary':'results/phase28_summary.json'})
    hypotheses.update(status=status,updated_at=now,next_queue=queue);save('hypotheses.json',hypotheses)
    winner=next(p for p in unknown['pages'] if p['page']==unknown['selected_page'])
    candidates=load(winner['output'])['result']['top'];top=candidates[0]
    page=next(p for p in load('transcriptions/pages.json') if p['id']==winner['page']);plain=to_indices(top['plaintext_runes'])
    assert sum(RUNE_ALIASES.get(x,x) in RUNES for x in page['text_with_layout'])==len(plain)
    it=iter(plain);layout=''.join(LATIN[next(it)] if RUNE_ALIASES.get(x,x) in RUNES else x for x in page['text_with_layout'])
    candidate=f'''# Stärkster E079-Kandidat: {winner['page']}

Keine bestätigte Entschlüsselung. Nach Score aus 55 Seiten ausgewählt.
{unknown['exceedances']}/19 passende Zufallstexte erreichen mindestens denselben Score.
Originale Worttrenner, Zeilen und etwaige Zahlen bleiben erhalten.
Zahlen wurden nicht entschlüsselt; keine ergänzten Leerzeichen oder Schreibkorrekturen.

```text
{layout}
```

Regel: `P_i=a*C_i+b*P_(i-2)+c mod29`, Startwarteschlange `key_indices`.

```json
{json.dumps(top['recipe'],indent=2)}
```

[Ergebnis](../{winner['output']}), SHA-256 `{sha(winner['output'])}`.
'''
    for rank,alternative in enumerate(candidates[1:],2):
        it=iter(to_indices(alternative['plaintext_runes']))
        alternative_layout=''.join(LATIN[next(it)] if RUNE_ALIASES.get(x,x) in RUNES else x for x in page['text_with_layout'])
        candidate+=f'''\n## Weitere Ausgabe derselben Seite: Rang {rank}

Score {alternative['score']:.6f}. Keine zusätzliche unabhängige Evidenz;
der Nullvergleich oben bezieht sich auf das Maximum der Suche.

```text
{alternative_layout}
```

```json
{json.dumps(alternative['recipe'],indent=2)}
```
'''
    (ROOT/'reports/phase28_selected_candidate.md').write_text(candidate,encoding='utf-8')
    rows='\n'.join(f'| {r["index"]} | {r["runes"]} | {r["a"]} | {r["b"]} | {r["c"]} | {r["family_rank"]} | exakt |' for r in controls['controls'])
    pages='\n'.join(f'| {r["page"]} | {r["runes"]} | {r["a"]} | {r["b"]} | {r["c"]} | {r["score"]:.6f} |' for r in unknown['pages'])
    next_sentence=('Die fixierte Auswahl braucht eine separat registrierte größere Nullkalibrierung.' if pending else
        'Als Nächstes folgt die offene Substitutionssuche H031: zuerst die dokumentierte Fehlbewertung kurzer Kontrolltexte beheben, dann bei bestandenen Kontrollen direkt auf unbekannte Seiten anwenden.')
    report=f'''# Forschungsserie 28: Zwei Runen Rückkopplung mit affiner Konstante

Stand UTC: {now}. **Keine neue Entschlüsselung bestätigt.**

## Verfahren und Rechenbudget

`P_i=a*C_i+b*P_(i-2)+c mod29`, a,b=1..28,c=0..28.
E025 untersuchte c=0 mit anderem Modell und Parameterumfang. Hier ist c=1..28
das neue Ziel; c=0 bleibt für Kontrollen und identische Suchbedingungen enthalten.
Die bekannte affine Algebra ist keine Neuentdeckung.

22.736 Familien werden nach maximalem Unigramm-Score sortiert, mit Rundung auf
neun Nachkommastellen und stabilen lexikographischen Gleichständen. Die besten
128 bleiben erhalten. Je Familie werden alle 29²=841 Anfangspaare gegen das
unveränderte externe Viergramm-Modell bewertet: 107.648 Präfixe pro Eingabe.
Die Präfixsuche ist exakt, die Familienauswahl heuristisch.
Keine ausgelassenen Runen, keine versteckten Resets.

E077 prüft 2.523 Scores durch unabhängige skalare Rekursion; maximale Abweichung
{benchmark['max_absolute_error']:.3g}. Der Pilot mit 256 Familien und 277 Runen
dauert {benchmark['pilot']['seconds']:.3f} Sekunden. Die lineare Hochrechnung
ergibt {benchmark['pilot']['estimated_full_grid_seconds_per_277_rune_input']:.1f}
Sekunden pro vollständigem Gitter bzw. {benchmark['pilot']['estimated_55_equal_length_inputs_seconds']/3600:.2f}
Stunden für 55 gleich lange Eingaben, ohne Nullkalibrierung. **Nur Schätzung,
kein durchgeführter Vollgitterlauf.** Die eingefrorene 128-Familien-Suche
benötigt bei 3.316 Zufallsrunen {benchmark['benchmark_seconds']:.3f} Sekunden.

## E078: Kontrollen

16/16 Klartexte, Schlüssel und a/b/c exakt. Neue Zwei-Runen-Schlüssel auf bereits
betrachteten, vom Training ausgeschlossenen Emerson-Blöcken. Zwölf kurze Texte
bei c!=0 und vier Regressionen bei c=0. Teilweise verschachtelte Ausschnitte,
keine 16 unabhängigen ungesehenen Texte. Diagnostischer Kontroll-Nullscore
{controls['null_score']:.6f}, ohne p-Wert.

| Kontrolle | Runen | a | b | c | Vorauswahlrang | Ergebnis |
|---|---:|---:|---:|---:|---:|---|
{rows}

## E079: Direkter Angriff auf die unbekannten Seiten

Alle 55 unbekannten Runenseiten einzeln angegriffen, einschließlich kurzer
Seiten. LP2-50 bleibt mit Originalinhalt im Plan erhalten und wurde nicht
entschlüsselt. Layout und Runen aller 56 Forschungsseiten sind in den gepinnten
Quellen verankert; Quellprüfsummen und die deklarierte Runenvariante geprüft.

| Seite | Runen | a | b | c | Score |
|---|---:|---:|---:|---:|---:|
{pages}

Stärkste Ausgabe: **{unknown['selected_page']}**, Score {unknown['score']:.6f}.
Auswahl und alle 55 Ergebnishashes wurden vor den Nullversuchen fixiert.
19 unabhängig erzeugte Nulltexte erhalten Häufigkeiten, Randrunen und die
Anzahl gleicher Nachbarpaare. Jeder durchläuft die vollständige gleiche Suche.
**{unknown['exceedances']}/19** sind mindestens so hoch bewertet:
Plus-eins-p={unknown['raw_p']:.2f}, Bonferroni55={unknown['bonferroni55']:.2f}.
Schon der kleinste mit 19 Nulltexten erreichbare korrigierte Wert beträgt 1.
Dieser grobe Vergleich erlaubt keinen Signifikanznachweis.

## Unabhängige Prüfung und Grenzen

Eine getrennte Implementierung rekonstruiert den Klartext durch Warteschlangen,
ohne die affine Formel des Suchprogramms. Alle {92*107648:,} Präfixscores der
128-Familien-Suche in 92 Aufgaben stimmen einschließlich kompletter Vektor-Prüfsummen. Quellen,
Seeds, beibehaltene Familienoptima, Kandidaten, Rückverschlüsselungen,
Nullziehungen und Auswahl geprüft. Die Sprachmodelltabellen wurden separat
gegen skalare Wahrscheinlichkeiten kontrolliert. Die vollständige Unigramm-
Vorauswahl wurde reproduziert; unabhängig direkt nachgerechnet wurden die
beibehaltenen Familien und Kontrollfamilien, nicht das gesamte Vorauswahlgitter.

Die verworfenen 22.608 Familien bleiben offen. Die Chiffrenklasse ist nicht
ausgeschlossen; der englische Prosa-Score kann andere Klartextarten übersehen.
Sprachähnliche Fragmente sind ohne weiteren Nachweis keine Entschlüsselung.

{count} Tests bestanden; 92 registrierte Aufgaben; {seconds:.3f} Sekunden
Experimentzeit bei 1.800 Sekunden Budget, höchster abgetasteter Speicher
{peak/1024**2:.1f} MiB bei 768 MiB Grenze, ein Suchworker. Prüfzeiten gesondert
in den Validierungsdateien. Historische Ergebnisse erhalten, keine laufenden Jobs.

{next_sentence}

[Plan](../experiments/delay_two_plan.json),
[Angriffsplan](../experiments/delay_two_unknown_plan.json),
[Ergebnisse](../results/phase28_summary.json),
[Ausgabe mit Originalgrenzen](phase28_selected_candidate.md).
'''
    (ROOT/'reports/attack_phase28_report.md').write_text(report,encoding='utf-8')
    p=ROOT/'README.md';original=p.read_bytes().decode('utf-8');text=original.replace('\r\n','\n')
    a,b=text.index('Reproduzierbare Kryptanalyse'),text.index('Start:')
    text=text[:a]+f'Reproduzierbare Kryptanalyse des Liber Primus. **Keine neue Entschlüsselung\nnachgewiesen.** Serie 28 prüft zwei Runen Rückkopplung mit affiner Konstante:\n16 Kontrollen exakt, 55 unbekannte Runenseiten direkt angegriffen;\n{unknown["exceedances"]}/19 Nullscores mindestens so hoch.\n\n'+text[b:]
    text=text.replace('reports/attack_phase27_report.md','reports/attack_phase28_report.md',1)
    text=text.replace('## Aktueller Stand\n\n','## Aktueller Stand\n\n- E077/E078:128 vorausgewählte Familien, je841 Präfixe exakt;16/16 Kontrollen bestanden.\n'+f'- E079:55 Seiten, {unknown["exceedances"]}/19 Nullscores mindestens so hoch; keine neue Lösung.\n',1)
    groups=len({e['experiment'].split('-')[0] for e in done})
    text=re.sub(r'- \d+ Tests bestanden; \d+ Experimentgruppen',f'- {count} Tests bestanden; {groups} Experimentgruppen',text,count=1)
    a=text.index('Nächste Priorität:');b=text.index('Kein Hintergrundprozess',a)
    text=text[:a]+'Nächste Priorität: '+next_sentence+'\n'+text[b:]
    before,after=original.splitlines(keepends=True),text.splitlines(keepends=True);out=[]
    matcher=difflib.SequenceMatcher(a=[x.rstrip('\r\n') for x in before],b=[x.rstrip('\r\n') for x in after],autojunk=False)
    for tag,a,b,c,d in matcher.get_opcodes():out.extend(before[a:b] if tag=='equal' else after[c:d])
    p.write_bytes(''.join(out).encode('utf-8'))
    save('checkpoints/phase28_complete.json',{'created_at':now,'status':status,'summary':'results/phase28_summary.json',
        'summary_sha256':sha('results/phase28_summary.json'),'experiments':entries})
    print({'status':status,'tests_passed':count,'seconds':seconds,'exceedances':unknown['exceedances']})


if __name__=='__main__':main()
