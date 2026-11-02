"""Append the fixed-zero-IV difference/substitution findings, retaining all history."""
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
    assert not (ROOT/'checkpoints/phase31_complete.json').exists()
    bridge=load('results/phase31_bridge_validation.json');unknown=load('results/phase31_unknown_validation.json')
    assert bridge['full_gate_passed'] and len(bridge['controls'])==12 and len(unknown['pages'])==46
    entries=bridge['entries']+unknown['entries'];assert len(entries)==66
    events=[json.loads(s) for s in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    done=[e for e in events if e['status']=='completed'];by_fp={e['fingerprint']:e for e in done}
    for r in entries:
        e=by_fp[r['fingerprint']];assert sha(r['output'])==r['sha256']==e['output_sha256']
        for path,digest in e['input_dependencies'].items():assert sha(path)==digest,path
    assert (ROOT/'experiment_log.jsonl').read_bytes().startswith(subprocess.check_output(['git','show','HEAD:experiment_log.jsonl'],cwd=ROOT))
    processes=load('results/phase31_processes.json')
    assert len(processes)==66 and all(p['exit_code']==0 and p['reason'] is None and p['seconds']<185 and p['peak_sampled_bytes']<=768*1024**2 for p in processes)
    tests=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=90)
    output=tests.stdout+tests.stderr;(ROOT/'results/validation_phase31.txt').write_text(output,encoding='utf-8');assert tests.returncode==0,output
    count=int(re.search(r'Ran (\d+) tests',output)[1]);now=datetime.now(timezone.utc).isoformat()
    seconds=sum(by_fp[e['fingerprint']]['wall_seconds'] for e in entries);supervised=sum(p['seconds'] for p in processes);assert supervised<1800
    peak=max(p['peak_sampled_bytes'] for p in processes);pending=unknown['pending_larger_calibration']
    status='thirtyfirst_batch_difference_substitution_'+('larger_null_pending' if pending else 'no_supported_decryption')
    summary={'created_at':now,'status':status,'bridge':bridge,'unknown':unknown,'tests_passed':count,
        'successful_tasks':66,'seconds':seconds,'supervised_seconds':supervised,'peak_sampled_bytes':peak,'new_decryptions':[]}
    save('results/phase31_summary.json',summary)
    next_task=('Preregister larger fresh calibration of the frozen E086 winner; do not pool original19 adaptively.' if pending else
        'Benchmark exact profiling of all29 unknown initial values per candidate permutation: only first plaintext rune changes. Freeze model/initializer and fresh control criteria before testing unknown pages; explicitly retain first-rune ambiguity and no omitted source rune. Do not claim E086 covered nonzero IVs.')
    queue=[{'id':'H052' if pending else 'H053','priority':1,'task':next_task},
        {'id':'H031','priority':2,'task':'Short-page word-frequency counterexample remains unresolved; do not extrapolate long-page capability.'}]
    state=load('research_state.json');old={e['fingerprint'] for e in state['completed_experiments']}
    assert not any(e['fingerprint'] in old for e in entries);state['completed_experiments']+=entries
    state.update(status=status,updated_at=now,latest_report='reports/attack_phase31_report.md',next_experiments=[q['id'] for q in queue],
        new_decryptions=[],promising_candidates=[],session_budget={'phase':'thirtyfirst fixed-IV difference substitution',
            'max_compute_wall_seconds':1800,'max_experiment_wall_seconds':180,'memory_ceiling_mib':768,'workers':1,'background_jobs':False},
        scoring_gate='E085 exact algebraic transport of12 prior E083 controls and3 diagnostic nulls, no optimizer reruns. E08646 pages>=200runes plus19 original-C-space matched full-search nulls, IV0 only.',
        notes=['No previously unknown plaintext confirmed. All runes including first preserved with explicit zero initial value.',
            'Control reuse is replication through exact reduction, not12 fresh independent recoveries. Frozen model/search unchanged.',
            'Original C-space nulls preserve counts/endpoints/doublets and lexical endpoints; transformed nonzero-D counts not fixed.',
            'Nine shorter rune pages and numericLP2-50 preserved; no inference to nonzero IVs or short pages.',
            'Historical results preserved; no running research jobs.'])
    state['validation'].update(tests_passed=count,path='results/validation_phase31.txt',phase31={'bridge':bridge['validation'],'unknown':unknown['validation']})
    state['resources'].update(recorded_successful_experiment_runs=len(done),recorded_experiment_subprocess_wall_seconds=sum(e['wall_seconds'] for e in done),phase31_wall_seconds=seconds,phase31_supervised_seconds=supervised)
    state['failed_approaches'].append(f'E086 first differences+general substitution, IV0,46pages>=200runes: {unknown["exceedances"]}/19 original-C-space matched nulls >= winner, Bonferroni46={unknown["bonferroni46"]}. No supported decryption; arbitrary IVs untested.')
    save('research_state.json',state)
    hypotheses=load('hypotheses.json');h=next(h for h in hypotheses['hypotheses'] if h['id']=='H052')
    h.update(status='fixed_iv_controls_transported_'+('larger_null_pending' if pending else 'unknown_screen_negative'),experiments=['E085','E086'],
        limits='IV0 only; exact transport of prior E083 capability, not new independent controls.46pages>=200runes,19 original-C-space full-search nulls. Finite heuristic, no29! exclusion, unknown nonzero IVs and short pages remain untested.',
        result={'reused_controls_exact':12,'new_control_optimizer_runs':0,'unknown_pages':46,'exceedances':unknown['exceedances'],'nulls':19,
            'raw_p':unknown['raw_p'],'bonferroni46':unknown['bonferroni46'],'summary':'results/phase31_summary.json'})
    if not pending:
        assert not any(h['id']=='H053' for h in hypotheses['hypotheses'])
        hypotheses['hypotheses'].append({'id':'H053','status':'queued_untested',
            'claim':'An unknown page-initial value may affect difference-substitution inference through the first plaintext rune.',
            'basis':'E086 fixedIV0. For fixed S, changingIV changes only D0 and therefore only P0; all29 first-rune values are possible. This algebraic gap is not evidence of a cipher.',
            'mechanism':'P_i=S((C_i-C_(i-1))mod29), C_-1=IV in0..28. Profile all29 IVs per candidate S with explicit first-word scoring and source-preserving output.',
            'success_criterion':'Independent literal29-IV score checks, bounded benchmark, prospectively frozen fresh control criteria including first-rune identifiability/ambiguity, then matched full-search nulls and correction.',
            'limits':'Untested optimizer; no discarded first rune, no retrospective loosening of E086. Do not equate best first-letter likelihood with cryptographic identification.'})
    hypotheses.update(status=status,updated_at=now,next_queue=queue);save('hypotheses.json',hypotheses)
    winner=next(p for p in unknown['pages'] if p['page']==unknown['selected_page']);r=load(winner['output'])
    page=next(p for p in load('transcriptions/pages.json') if p['id']==winner['page']);ranked=[];seen=set()
    for candidate in sorted(r['result']['restarts'],key=lambda x:x['score'],reverse=True):
        if candidate['plaintext_runes'] not in seen:ranked.append(candidate);seen.add(candidate['plaintext_runes'])
    text=f'''# E086-Ausgaben: {winner['page']}

**Keine bestätigte Entschlüsselung.** Höchster Score unter 46 untersuchten Seiten;
{unknown['exceedances']}/19 vollständig optimierte passende Zufallstexte erreichen
mindestens denselben Score. Originale Worttrenner, Zeilen und Nicht-Runen erhalten.
Keine ergänzten Leerzeichen, ausgelassenen Runen oder Schreibkorrekturen.

Regel: `D_0=C_0; D_i=(C_i-C_(i-1))mod29; P_i=S[D_i]`.
Anfangswert `C_-1=0`; GP-Indizes 0..28. Rückweg: inverse Permutation und
fortlaufende Addition modulo 29 ab 0. Die Alternativen sind keine unabhängige Evidenz.
'''
    for k,candidate in enumerate(ranked[:3],1):
        plain=to_indices(candidate['plaintext_runes']);assert len(plain)==page['rune_count']
        it=iter(plain);layout=''.join(LATIN[next(it)] if RUNE_ALIASES.get(x,x) in RUNES else x for x in page['text_with_layout'])
        text+=f'\n## Rang {k}, Score {candidate["score"]:.6f}\n\n```text\n{layout}\n```\n\n```json\n'+json.dumps({'initial_value':0,'mapping_difference_to_plain':candidate['mapping_cipher_to_plain']},indent=2)+'\n```\n'
    text+=f'\n[Ergebnis](../{winner["output"]}), SHA-256 `{sha(winner["output"])}`.\n'
    (ROOT/'reports/phase31_selected_candidates.md').write_text(text,encoding='utf-8')
    pages='\n'.join(f'| {r["page"]} | {r["runes"]} | {r["score"]:.6f} |' for r in unknown['pages'])
    next_sentence=('Die eingefrorene Auswahl benötigt separat registrierte größere Nullkalibrierung.' if pending else
        'Als Nächstes wird die offene Anfangswertfrage geprüft: Für eine feste Permutation betrifft sie nur die erste Klartextrune. Ein Verfahren für alle 29 Werte muss vorab mit unabhängiger Scoreprüfung und ausdrücklich behandelter Mehrdeutigkeit validiert werden.')
    report=f'''# Forschungsserie 31: Differenzen und allgemeine Runensubstitution

Stand UTC: {now}. **Keine neue Entschlüsselung bestätigt.**

## Festgelegte reversible Regel

`C_-1=0`, `D_i=(C_i-C_(i-1))mod29`, `P_i=S(D_i)`.
S ist eine beliebige 29-Symbol-Permutation. Rückweg:
`C_i=(C_(i-1)+S^-1(P_i))mod29`. Die erste Rune wird ausdrücklich verarbeitet,
nicht als IV entfernt. Wortgrenzen bleiben erhalten. Der Startwert 0 ist eine
vorab gewählte Begrenzung, kein aus dem Rätsel abgeleiteter Befund.
Andere Anfangswerte und über Seiten laufende Zustände sind hier nicht getestet.
E015 untersuchte nur affine Abbildungen nach Differenzen; seine historischen
Ergebnisse bleiben unverändert. Die mathematischen Operationen sind bekannt.

## E085: Exakte Übertragung bestehender Kontrollen

Die zwölf bestandenen E083-Kontrollen werden zu synthetischen Chiffren dieser
neuen Familie integriert. Differenzbildung liefert exakt die bisherigen
Substitutionseingaben zurück. Deshalb wird die unveränderte Schlüsselsuche
**nicht erneut ausgeführt**. Das sind übertragene Kontrollen, keine zwölf neuen
unabhängigen Blindversuche. Drei vorhandene D-Raum-Kontrollnulls werden genauso
übertragen; sie sind keine neuen passenden C-Raum-Nullziehungen.

Separater Prüfer: Quellfenster und Schlüssel reproduziert, 245 Kandidatenscores
nachgerechnet, 245 vollständige kumulative Rückverschlüsselungen bestätigt.
435 algebraische Identitäten über alle 29 IVs geprüft; diese Matheprüfung
erweitert den unbekannten Angriff ausdrücklich nicht über IV 0 hinaus.
Training und Modell bleiben unverändert; X/XI/XII sind vom Fit ausgeschlossen,
aber das Emerson-Korpus wurde historisch bereits betrachtet.

## E086: Angriff auf unbekannte Seiten

Nach separater Kontrolle registriert: 46 LP2-Seiten ab 200 Runen, jeweils vor der
Substitutionssuche differenziert. Höchstens 24 Starts, 40 vollständige 406-Tausch-
Sweeps im Zeichenmodell, 40 im BOS/EOS-Wortmodell. Keine neuen Modellparameter.
Neun kurze Runenseiten und die numerische LP2-50 bleiben mit Originalinhalt und
Ausschlussgrund im Plan. Die originalen Wortendpunkte sind unverändert;
Quellanker aller 56 Forschungsseiten und zehn gepinnte Quelldateien geprüft.

| Seite | Runen | Höchster Score |
|---|---:|---:|
{pages}

Stärkste Ausgabe **{unknown['selected_page']}**, Score {unknown['score']:.6f}.
Auswahl und 46 Ergebnishashes vor den Nullziehungen fixiert. 19 unabhängige
Innenmischungen des **ursprünglichen C-Texts** erhalten Randrunen, genaue
Häufigkeiten, Anzahl gleicher Nachbarn und Originalwortgrenzen. Erst danach
wird differenziert und mit demselben seitenbezogenen Seed vollständig gesucht.
Die Häufigkeiten nichtnulliger Differenzen bleiben dabei nicht erhalten;
dieser Vergleich ist ausdrücklich ein C-Raum-Modell, kein zusätzlicher D-Raum-Test.

**{unknown['exceedances']}/19** Nullscores mindestens so hoch wie die Auswahl.
Plus-eins-p={unknown['raw_p']:.2f}; Bonferroni46={unknown['bonferroni46']:.2f}.
Mit 19 Nulltexten ist der kleinste korrigierte Wert bereits 1: grobes Screening,
kein Signifikanznachweis und keine belegte Entschlüsselung.

## Unabhängige Validierung und Grenzen

{unknown['validation']['independent_candidate_scores']} ausgegebene Kandidatenscores,
{unknown['validation']['independent_final_neighbor_scores']} letzte Nachbarscores und
{unknown['validation']['cumulative_original_cipher_reencryptions']} vollständige
Rückverschlüsselungen bis zum originalen C-Text bestätigt. Separate Literal-
Differenzen und kumulative Inversion, keine Produktions-Differenzfunktion.
Quellen, Null-Seeds und Auswahl geprüft. Zwischenpfade der Suchoptimierung
wurden nicht unabhängig implementiert; GP-Tokenisierung wird gemeinsam benutzt.

Endliche Heuristik, keine Ausschließung aller 29! Permutationen. Seitenränder
werden als Wortgrenzen angenommen. Nichtenglische oder nichtsprachliche Texte,
andere IVs und kurze Seiten bleiben außerhalb dieser Aussage. Sprachähnliche
Stücke sind ohne weitere Evidenz keine Lösung. Der E081-Kurztextfehler bleibt bestehen.

{count} Tests bestanden; 66 neue registrierte Aufgaben, davon eine Kontroll-
Übertragung ohne Optimizersuche. Experimentzeit {seconds:.3f} Sekunden;
überwachte Prozesszeit {supervised:.3f} Sekunden bei 1.800 Sekunden Budget.
Spitzenspeicher {peak/1024**2:.1f} MiB bei 768 MiB Grenze, ein Worker. Keine laufenden Jobs.

{next_sentence}

[Plan](../experiments/difference_substitution_plan.json),
[Angriffsplan](../experiments/difference_substitution_unknown_plan.json),
[Ergebnisse](../results/phase31_summary.json),
[Ausgaben mit Originalgrenzen](phase31_selected_candidates.md).
'''
    (ROOT/'reports/attack_phase31_report.md').write_text(report,encoding='utf-8')
    p=ROOT/'README.md';original=p.read_bytes().decode('utf-8');text=original.replace('\r\n','\n')
    a,b=text.index('Reproduzierbare Kryptanalyse'),text.index('Start:')
    text=text[:a]+f'Reproduzierbare Kryptanalyse des Liber Primus. **Keine neue Entschlüsselung\nnachgewiesen.** Serie 31: Differenzen plus allgemeine Substitution mit IV0,\n46 unbekannte Seiten direkt angegriffen; {unknown["exceedances"]}/19 Nullscores mindestens so hoch.\n\n'+text[b:]
    text=text.replace('reports/attack_phase30_report.md','reports/attack_phase31_report.md',1)
    text=text.replace('## Aktueller Stand\n\n','## Aktueller Stand\n\n- E085: zwölf vorhandene Kontrollen exakt auf die Differenzchiffre übertragen, keine Suchwiederholung.\n'+f'- E086: 46 Seiten, IV0, {unknown["exceedances"]}/19 passende C-Raum-Nullscores mindestens so hoch.\n',1)
    groups=len({e['experiment'].split('-')[0] for e in done})
    text=re.sub(r'- \d+ Tests bestanden; \d+ Experimentgruppen',f'- {count} Tests bestanden; {groups} Experimentgruppen',text,count=1)
    a=text.index('Nächste Priorität:');b=text.index('Kein Hintergrundprozess',a)
    text=text[:a]+'Nächste Priorität: '+next_sentence+'\n'+text[b:]
    before,after=original.splitlines(keepends=True),text.splitlines(keepends=True);out=[]
    matcher=difflib.SequenceMatcher(a=[x.rstrip('\r\n') for x in before],b=[x.rstrip('\r\n') for x in after],autojunk=False)
    for tag,a,b,c,d in matcher.get_opcodes():out.extend(before[a:b] if tag=='equal' else after[c:d])
    p.write_bytes(''.join(out).encode('utf-8'))
    save('checkpoints/phase31_complete.json',{'created_at':now,'status':status,'summary':'results/phase31_summary.json',
        'summary_sha256':sha('results/phase31_summary.json'),'experiments':entries})
    print({'status':status,'tests_passed':count,'seconds':seconds,'exceedances':unknown['exceedances']})


if __name__=='__main__':main()
