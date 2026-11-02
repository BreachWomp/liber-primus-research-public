"""Checkpoint the validated delay-three screen without rewriting older findings."""
from datetime import datetime,timezone
import difflib
import json
import re
import subprocess
import sys
from verify_delay_three import ROOT,load,sha,to_indices
from liberprimus.alphabet import RUNES,RUNE_ALIASES,LATIN


def save(path,data):(ROOT/path).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def main():
    assert not (ROOT/'checkpoints/phase27_complete.json').exists()
    controls=load('results/phase27_controls_validation.json');unknown=load('results/phase27_unknown_validation.json')
    assert controls['full_gate_passed'] and len(controls['controls'])==16 and len(unknown['pages'])==55
    entries=controls['entries']+unknown['entries'];assert len(entries)==92
    assert controls['validation']['independent_full_prefix_scores']==18*390224
    assert unknown['validation']['independent_full_prefix_scores']==74*390224
    events=[json.loads(x) for x in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    done=[e for e in events if e['status']=='completed'];by_fp={e['fingerprint']:e for e in done}
    for r in entries:
        e=by_fp[r['fingerprint']];assert sha(r['output'])==r['sha256']==e['output_sha256']
        for path,digest in e['input_dependencies'].items():assert sha(path)==digest,path
    assert (ROOT/'experiment_log.jsonl').read_bytes().startswith(subprocess.check_output(['git','show','HEAD:experiment_log.jsonl'],cwd=ROOT))
    processes=load('results/phase27_processes.json')
    assert len(processes)==92 and all(p['exit_code']==0 and p['reason'] is None and p['seconds']<185 and p['peak_sampled_bytes']<=768*1024**2 for p in processes)
    tests=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=90)
    output=tests.stdout+tests.stderr;(ROOT/'results/validation_phase27.txt').write_text(output,encoding='utf-8')
    assert tests.returncode==0,output
    count=int(re.search(r'Ran (\d+) tests',output)[1]);now=datetime.now(timezone.utc).isoformat()
    seconds=sum(by_fp[e['fingerprint']]['wall_seconds'] for e in entries);assert seconds<1800
    pending=unknown['pending_larger_calibration'];status='twentyseventh_batch_delay_three_'+('larger_null_pending' if pending else 'no_supported_decryption')
    peak=max(p['peak_sampled_bytes'] for p in processes)
    summary={'created_at':now,'status':status,'controls':controls,'unknown':unknown,'tests_passed':count,
        'successful_tasks':92,'seconds':seconds,'peak_sampled_bytes':peak,'new_decryptions':[]}
    save('results/phase27_summary.json',summary)
    next_task=('Preregister a fresh larger calibration of frozen E076 selection; do not pool the original19 adaptively.' if pending else
        'Benchmark the remaining delay2 nonzero-constant family using bounded family screening and exact841-prefix evaluation. E025 tested delay2 only at c0. Fresh controls and matched nulls required before unknown conclusions.')
    queue=[{'id':'H023' if pending else 'H050','priority':1,'task':next_task},
        {'id':'H031','priority':2,'task':'General substitution remains deferred pending source-excluded scoring repair; preserve prior short-control failures.'}]
    state=load('research_state.json');old={e['fingerprint'] for e in state['completed_experiments']}
    assert not any(e['fingerprint'] in old for e in entries);state['completed_experiments']+=entries
    state.update(status=status,updated_at=now,latest_report='reports/attack_phase27_report.md',next_experiments=[q['id'] for q in queue],
        new_decryptions=[],promising_candidates=[],session_budget={'phase':'twentyseventh delay-three exact prefixes',
            'max_compute_wall_seconds':1800,'max_experiment_wall_seconds':180,'memory_ceiling_mib':768,'workers':1,'background_jobs':False},
        scoring_gate='E07516/16 exact plaintext/key/a/b/c; E074 scalar73167-prefix audit; separate queue vectors verify all390224 retained-family prefix scores per input. E07655pages plus19 matched full nulls.',
        notes=['No previously unknown plaintext confirmed. Direct cryptanalysis only.',
            'Delay3,a,b1..28,c0..28; top16 of22736 families remain heuristic. Every24389 prefix exact only within retained families.',
            'Fresh keys on previously inspected excluded Emerson blocks; short66/95/200/300 and200/300/729/3316-rune regressions. Not16 unseen texts.',
            'All55 unknown rune pages individually searched; numericLP2-50 remains source-anchored and not deciphered.',
            'No historical source/output modified; no running research jobs.'])
    state['validation'].update(tests_passed=count,path='results/validation_phase27.txt',phase27={'controls':controls['validation'],'unknown':unknown['validation']})
    state['resources'].update(recorded_successful_experiment_runs=len(done),recorded_experiment_subprocess_wall_seconds=sum(e['wall_seconds'] for e in done),phase27_wall_seconds=seconds)
    state['failed_approaches'].append(f'E076 delay3 affine feedback,55 individual pages: {unknown["exceedances"]}/19 full null scores >= selection; corrected p={unknown["bonferroni55"]}. No supported decryption; coefficient screening remains heuristic.')
    save('research_state.json',state)
    hypotheses=load('hypotheses.json');h=next(h for h in hypotheses['hypotheses'] if h['id']=='H023')
    h['experiments']+=['E074','E075','E076'];h['status']='delay3_controls_passed_'+('larger_null_pending' if pending else 'unknown_screen_negative')
    h['prior_period2_limits']=h['limits']
    h['limits']='E025 exhaustive delay2 at c0 remains historical. E076 delay3,c0..28 retains16 coefficient families and enumerates their prefix space exactly; no all-family/key exclusion or skipped-rune test.'
    h['delay3_result']={'controls_exact':16,'unknown_pages':55,'exceedances':unknown['exceedances'],'nulls':19,
        'raw_p':unknown['raw_p'],'bonferroni55':unknown['bonferroni55'],'summary':'results/phase27_summary.json'}
    if not pending:
        assert not any(x['id']=='H050' for x in hypotheses['hypotheses'])
        hypotheses['hypotheses'].append({'id':'H050','status':'queued_untested','claim':'Delay2 plaintext feedback may include a nonzero additive constant.',
            'basis':'E025 covers delay2,c0; E034 covers delay1; E072/E073 and E075/E076 cover delays4..32 and3 with constants. This is an untested gap, not positive cipher evidence.',
            'mechanism':'P_i=a*C_i+b*P_(i-2)+c mod29,a,b1..28,c1..28. Benchmark bounded coefficient screening plus exact841 plaintext prefixes.',
            'success_criterion':'Prospective bounds/seeds, fresh short/long controls and c0 regressions; independent full-prefix and source verification, then matched full-search nulls.',
            'limits':'Untested; no E077 result. No omitted symbols or hidden boundaries.'})
    hypotheses.update(status=status,updated_at=now,next_queue=queue);save('hypotheses.json',hypotheses)
    winner=next(p for p in unknown['pages'] if p['page']==unknown['selected_page']);data=load(winner['output']);top=data['result']['top'][0]
    page=next(p for p in load('transcriptions/pages.json') if p['id']==winner['page']);plain=to_indices(top['plaintext_runes'])
    assert sum(RUNE_ALIASES.get(x,x) in RUNES for x in page['text_with_layout'])==len(plain)
    it=iter(plain);layout=''.join(LATIN[next(it)] if RUNE_ALIASES.get(x,x) in RUNES else x for x in page['text_with_layout'])
    candidate=f'''# Stärkster E076-Kandidat: {winner['page']}

Keine bestätigte Entschlüsselung. Aus 55 Seiten nach Score ausgewählt;
{unknown['exceedances']}/19 passende Zufallstexte erreichen mindestens denselben Score.
Worttrenner, Zeilen und etwaige Zahlen bleiben aus der Quelle erhalten.
Zahlen wurden nicht entschlüsselt. Keine ergänzten Leerzeichen oder Schreibkorrekturen.

```text
{layout}
```

Regel: `P_i=a*C_i+b*P_(i-3)+c mod29`.

```json
{json.dumps(top['recipe'],indent=2)}
```

[Vollständiges Ergebnis](../{winner['output']}), SHA-256 `{sha(winner['output'])}`.
'''
    (ROOT/'reports/phase27_selected_candidate.md').write_text(candidate,encoding='utf-8')
    rows='\n'.join(f'| {r["index"]} | {r["runes"]} | {r["a"]} | {r["b"]} | {r["c"]} | {r["family_rank"]} | exakt |' for r in controls['controls'])
    pages='\n'.join(f'| {r["page"]} | {r["runes"]} | {r["a"]} | {r["b"]} | {r["c"]} | {r["score"]:.6f} |' for r in unknown['pages'])
    next_sentence=('Die festgeschriebene Auswahl benötigt eine separat registrierte größere Nullkalibrierung.' if pending else
        'Als nächste ungetestete Lücke folgt Verzögerung zwei mit einer von null verschiedenen Konstante, zunächst mit Laufzeitbenchmark und Kontrollen.')
    report=f'''# Forschungsserie 27: Rückkopplung mit drei Runen Verzögerung

Stand UTC: {now}. **Keine neue Entschlüsselung bestätigt.**

## E074/E075: Verfahren und Kontrollen

`P_i=a*C_i+b*P_(i-3)+c mod29`, a,b=1..28,c=0..28.
Die bekannte affine Reduktion bewertet 22.736 Parameterfamilien nach Unigrammen.
16 bleiben erhalten. Für jede davon werden sämtliche 29³ = 24.389
Anfangspräfixe gegen das unveränderte externe Viergramm-Modell bewertet.
Diese Präfixsuche ist exakt; die Auswahl der Parameterfamilien ist es nicht.
Es gibt keine ausgelassenen Runen oder versteckten Resets.

E074 vergleicht 73.167 Präfixscores mit einer getrennten skalaren Rekursion;
der längste Durchsatztest mit 3.316 Zufallsrunen dauert rund 36 Sekunden.
Die zwölf neuen kurzen Kontrollen verwenden 66/95/200/300 Runen aus bereits
betrachteten, vom Training ausgeschlossenen Emerson-Blöcken. Vier neue
Verschlüsselungen bei c=0 prüfen 200/300/729/3.316 Runen und die alten Vorzeichenpaare.
Die Schlüssel sind neu; die Textausschnitte sind teilweise verschachtelt und
keine 16 unabhängigen unbekannten Texte. Alle Klartexte, Schlüssel und a/b/c-Werte exakt.
Diagnostischer Kontroll-Nullscore {controls['null_score']:.6f}, ohne p-Wert.

| Kontrolle | Runen | a | b | c | Vorauswahlrang | Ergebnis |
|---|---:|---:|---:|---:|---:|---|
{rows}

## E076: Alle unbekannten Runenseiten einzeln

55 Seiten einschließlich der kurzen Abschnitte direkt geprüft. LP2-50 bleibt
mit Originalinhalt und Quellenreferenzen im Plan erhalten, ohne Runenangriff.
Das Seitenlayout aller 56 Forschungsseiten ist wörtlich in den gepinnten
Quelldateien verankert; alle zehn zugehörigen Dateihashes stimmen.

| Seite | Runen | a | b | c | Score |
|---|---:|---:|---:|---:|---:|
{pages}

Stärkste Seite **{unknown['selected_page']}**, Score {unknown['score']:.6f}.
Auswahl und alle 55 Ergebnishashes wurden vor den Nullversuchen fixiert.
19 unabhängig erzeugte Nulltexte erhalten Häufigkeiten, Randrunen und gleiche
Nachbarpaare. Sie durchlaufen dieselbe vollständige Vorauswahl und Präfixsuche.
**{unknown['exceedances']}/19** erzielen mindestens denselben Score:
Plus-eins-p={unknown['raw_p']:.2f}, Bonferroni55={unknown['bonferroni55']:.2f}.
Der kleinste korrigierte p-Wert mit 19 Nulltexten beträgt bereits 1.
Das ist ein grober Vergleich, kein Signifikanznachweis.

## Validierung und Grenzen

Eine zweite Implementierung berechnet die Klartexte als explizite Warteschlangen,
ohne die affine Formel des Suchprogramms. Alle 35.900.608 Präfixscores der
92 Suchläufe stimmen einschließlich ihrer vollständigen Vektor-Prüfsummen.
Sämtliche behaltenen Familienoptima, Quellbereiche, Schlüssel-Seeds, Kandidaten,
Rückverschlüsselungen, Nullziehungen und die Auswahl wurden geprüft.
Die Sprachmodelltabellen sind separat gegen skalare Wahrscheinlichkeiten kontrolliert.
Die vollständige Unigramm-Vorauswahl wurde reproduziert; direkt nachgerechnet
wurden die behaltenen Familien und die Kontrollfamilien. Vollständige
Scorevektor-Prüfung bedeutet keine unabhängige Vollgitter-Prüfung der Vorauswahl.

Die verworfenen 22.720 Familien bleiben außerhalb der exakten Präfixsuche.
Das negative Ergebnis schließt die Chiffrenklasse nicht aus. Der englische
Prosa-Score kann andere Sprachen oder nichtsprachliche Klartexte übersehen.
Die affine Algebra ist keine Neuentdeckung; E025 und die früheren Verzögerungen
bleiben historische Ergebnisse und werden nicht als neue Entschlüsselungen gezählt.

{count} Tests bestanden; 92 registrierte Aufgaben; {seconds:.3f} Sekunden
Experimentzeit bei 1.800 Sekunden Budget; höchster abgetasteter Speicher
{peak/1024**2:.1f} MiB bei 768 MiB Grenze, ein Suchworker.
Prüfzeiten stehen gesondert in den Validierungsdateien. Keine laufenden Jobs.

{next_sentence}

[Plan](../experiments/delay_three_plan.json),
[Angriffsplan](../experiments/delay_three_unknown_plan.json),
[Ergebnisse](../results/phase27_summary.json),
[Ausgabe mit Originalgrenzen](phase27_selected_candidate.md).
'''
    (ROOT/'reports/attack_phase27_report.md').write_text(report,encoding='utf-8')
    p=ROOT/'README.md';original=p.read_bytes().decode('utf-8');text=original.replace('\r\n','\n')
    a,b=text.index('Reproduzierbare Kryptanalyse'),text.index('Start:')
    text=text[:a]+f'Reproduzierbare Kryptanalyse des Liber Primus. **Keine neue Entschlüsselung\nnachgewiesen.** Serie 27 prüft drei Runen Verzögerung: 16 Kontrollen exakt,\n55 unbekannte Runenseiten einzeln angegriffen; {unknown["exceedances"]}/19 Nullscores mindestens so hoch.\n\n'+text[b:]
    text=text.replace('reports/attack_phase26_report.md','reports/attack_phase27_report.md',1)
    text=text.replace('## Aktueller Stand\n\n','## Aktueller Stand\n\n- E074/E075: exakte Präfixsuche innerhalb 16 vorausgewählter Familien;16/16 Kontrollen exakt.\n'+f'- E076:55 einzelne Seiten, {unknown["exceedances"]}/19 Nullscores mindestens so hoch; keine neue Lösung.\n',1)
    groups=len({e['experiment'].split('-')[0] for e in done})
    text=re.sub(r'- \d+ Tests bestanden; \d+ Experimentgruppen',f'- {count} Tests bestanden; {groups} Experimentgruppen',text,count=1)
    a=text.index('Nächste Priorität:');b=text.index('Kein Hintergrundprozess',a)
    text=text[:a]+'Nächste Priorität: '+next_sentence+'\n'+text[b:]
    before,after=original.splitlines(keepends=True),text.splitlines(keepends=True);out=[]
    matcher=difflib.SequenceMatcher(a=[x.rstrip('\r\n') for x in before],b=[x.rstrip('\r\n') for x in after],autojunk=False)
    for tag,a,b,c,d in matcher.get_opcodes():out.extend(before[a:b] if tag=='equal' else after[c:d])
    p.write_bytes(''.join(out).encode('utf-8'))
    save('checkpoints/phase27_complete.json',{'created_at':now,'status':status,'summary':'results/phase27_summary.json',
        'summary_sha256':sha('results/phase27_summary.json'),'experiments':entries})
    print({'status':status,'tests_passed':count,'seconds':seconds,'exceedances':unknown['exceedances']})


if __name__=='__main__':main()
