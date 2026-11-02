"""Checkpoint independently verified constrained initialization and unknown scan."""
from collections import Counter
from datetime import datetime, timezone
import difflib
from fractions import Fraction
import json
import math
import re
import subprocess
import sys
from finalize_phase20 import ROOT, load, save, sha


def main():
    if (ROOT/'checkpoints/phase21_complete.json').exists():
        raise RuntimeError('Checkpoint already exists')
    base=load('results/phase21_constraints_validation.json')
    controls=load('results/phase21_hybrid_validation.json')
    unknown=load('results/phase21_hybrid_unknown_validation.json')
    assert controls['full_gate_passed'] and len(controls['controls'])==21
    assert unknown['unique_unknown_rune_pages']==55 and unknown['empty_pages_preserved']==['LP2-50']
    entries=base['entries']+controls['entries']+unknown['entries']
    events=[json.loads(x) for x in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    done=[e for e in events if e['status']=='completed'];by_fp={e['fingerprint']:e for e in done}
    for entry in entries:
        event=by_fp[entry['fingerprint']]
        assert sha(entry['output'])==entry['sha256']==event['output_sha256']
        for path,digest in event['input_dependencies'].items():assert sha(path)==digest,path
    old_log=subprocess.check_output(['git','show','HEAD:experiment_log.jsonl'],cwd=ROOT)
    assert (ROOT/'experiment_log.jsonl').read_bytes().startswith(old_log)
    tests=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,
                         capture_output=True,text=True,encoding='utf-8',timeout=60)
    output=tests.stdout+tests.stderr
    (ROOT/'results/validation_phase21.txt').write_text(output,encoding='utf-8')
    if tests.returncode:raise RuntimeError(output)
    count=int(re.search(r'Ran (\d+) tests',output)[1]);now=datetime.now(timezone.utc).isoformat()
    validation=Counter(base['validation']);validation.update(controls['validation']);validation.update(unknown['validation'])
    hard=load(next(r['output'] for r in base['controls'] if r['kind']=='regression' and r['index']==2))
    result=hard['result'];period=len(hard['source']['injected_key'])
    links=[e for c in result['phase_chains'] for e in c['links']]
    reduction=math.prod(Fraction(period,min(period,e['f_count']+1)) for e in links)
    canonical=lambda k:min(tuple(k[i:]+k[:i]) for i in range(len(k)))
    match=lambda s:s['sign']==hard['source']['injected_sign'] and canonical(s['key'])==canonical(hard['source']['injected_key'])
    audit={'control':'E058-regression-2','period':period,'fragments':len(result['pool_spans']),
        'page_chains':len(result['phase_chains']),'interval_F_counts':[e['f_count'] for e in links],
        'phase_assignment_reduction_numerator':reduction.numerator,'phase_assignment_reduction_denominator':reduction.denominator,
        'phase_assignment_reduction_factor':float(reduction),
        'exact_unigram_start_count':sum(match(r) for r in result['unigram_starts']),
        'exact_bigram_states':sum(match(s) for f in result['families'] for c in f['candidates'] for s in c['pool_trace'] if s['order']==2),
        'exact_fourgram_states':sum(match(s) for f in result['families'] for c in f['candidates'] for s in c['pool_trace'] if s['order']==4),
        'exact_final_key_count':sum(match(r['final']) for r in result['restarts']),
        'limits':'Descriptive phase-space count at evaluated true period, not a measured runtime speedup or proof of global key search.'}
    seconds=base['seconds']+controls['seconds']+unknown['seconds']
    interrupted_charge=unknown['interrupted_budget_charge_seconds'];assert seconds+interrupted_charge<3600
    summary={'E058_control_gate_passed':False,'E058_controls':base['controls'],'control_gate_passed':True,'controls':controls['controls'],'hard_control_audit':audit,
        'interrupted_budget_charge_seconds':interrupted_charge,'budget_accounted_seconds':seconds+interrupted_charge,
        'control_diagnostic_null_score':controls['null_score'],
        'unknown':{k:v for k,v in unknown.items() if k not in ('entries','validation','new_decryptions')},
        'validation':dict(validation),'tests_passed':count,'successful_tasks':len(entries),'seconds':seconds,
        'peak_sampled_bytes':max(base['peak_sampled_bytes'],controls['peak_sampled_bytes'],unknown['peak_sampled_bytes']),
        'control_validation_sha256':sha('results/phase21_hybrid_validation.json'),
        'unknown_validation_sha256':sha('results/phase21_hybrid_unknown_validation.json'),'new_decryptions':[]}
    save('results/phase21_summary.json',summary)
    pending=unknown['pending_larger_calibration']
    status='twentyfirst_batch_constraints_validated_'+('null_extension_pending' if pending else 'unknown_scan_no_supported_decryption')
    next_item=({'id':'H044','priority':1,'task':'Preregister larger selected-group null calibration with frozen E061 solver and selection; zero exceedances in19 is not sufficient evidence.'} if pending else
        {'id':'H045','priority':1,'task':'Extend the existing E017 affine-chain machinery to seed lengths13..32 with a preregistered bounded initializer. First reproduce shorter known controls and fresh13/23/31 cases plus matched nulls. Exact blind validation required before unknown pages; retain uncertain F schedules explicitly.'})
    queue=[next_item,{'id':'H031','priority':2,'task':'General substitution deferred pending independently justified scoring repair.'},
           {'id':'H023','priority':3,'task':'Delay3 feedback deferred pending feasible calibrated reduction.'}]
    state=load('research_state.json');existing={e['fingerprint'] for e in state['completed_experiments']}
    state['completed_experiments'] += [e for e in entries if e['fingerprint'] not in existing]
    state.update(status=status,updated_at=now,latest_report='reports/attack_phase21_report.md',
        next_experiments=[q['id'] for q in queue],new_decryptions=[],promising_candidates=[],
        session_budget={'phase':'twentyfirst constrained initialization and direct unknown search',
            'max_compute_wall_seconds':3600,'unknown_family_seconds':1800,'max_experiment_wall_seconds':180,
            'memory_ceiling_mib':768,'workers':1,'background_jobs':False},
        scoring_gate='E060 all21 hybrid blind controls exact including old hard31, fresh17/23/31, all deferred regressions and boundary-stress cases. E061 unknown scan and19 matched full-optimizer nulls independently verified.',
        notes=['No previously unknown plaintext confirmed. Direct cryptanalysis only.',
            'Ciphertext-derived constraints couple fragment phases only within original pages; full solver retains language context across pages.',
            '21 exact hybrid blind controls validate tested cases, not arbitrary keys or authentic LP cipher structure.',
            'Nine unknown groups cover55 rune pages; numeric LP2-50 retained.',
            '19 full selected-group null searches and Bonferroni9 correction; no new decryption claim.',
            'Leading-F ambiguity remains and alternatives are preserved.',
            'All source bytes and historical outcomes retained; no running research jobs.'])
    state['validation'].update(tests_passed=count,path='results/validation_phase21.txt',phase21=dict(validation))
    state['resources'].update(recorded_successful_experiment_runs=len(done),
        recorded_experiment_subprocess_wall_seconds=sum(e['wall_seconds'] for e in done),phase21_wall_seconds=seconds,phase21_interrupted_budget_charge_seconds=interrupted_charge)
    state['failed_approaches'].append('E058 constrained-only search:17/18 exact; old1200-key31 control fails49/1200. E060 subsequently preserves both candidate sets.')
    state['failed_approaches'].append(f'E061 long shared key with page-local phases, nine groups: {unknown["exceedances"]}/19 selected-group null exceedances; raw p={unknown["raw_p"]}, Bonferroni9={unknown["bonferroni9"]}. No confirmed decryption. E060 preserves both complementary initializer successes.')
    save('research_state.json',state)
    hypotheses=load('hypotheses.json');by_id={h['id']:h for h in hypotheses['hypotheses']}
    by_id['H043'].update(status='constrained_only_gate_failed17of18',experiments=['E058'],
        result=base,limits='Repairs old729-key31 but fails old1200-key31; E059 blocked. Hybrid continuation recorded separately under H044.')
    assert 'H044' not in by_id
    hypotheses['hypotheses'].append({'id':'H044','status':'hybrid_controls_passed_'+('larger_null_pending' if pending else 'unknown_screen_no_supported_candidate'),
        'claim':'Preserving both independent and constrained fragment-initializer candidates may recover complementary difficult cases.',
        'basis':'E05817/18 exact with a new regression; E057 and E058 have different failures.',
        'mechanism':'Frozen full E057 and E058 searches; stable union ranked by unchanged full-text score, explicit leading-F alternatives.',
        'experiments':['E060','E061'],'result':summary,
        'limits':'21 tested blind controls exact; no guarantee for every key/mask. Coarse selected-group null screening is not a decryption.'})
    for ident in ('H040','H041','H042'):
        by_id[ident]['follow_up']={'experiments':['E060','E061'],'result':'E060 all21 exact with hybrid initialization; prior outcomes unchanged. See phase21 report for unknown scan.'}
    if not pending:
        assert 'H045' not in by_id
        hypotheses['hypotheses'].append({'id':'H045','status':'queued_untested',
            'claim':'Plaintext-autokey seeds longer than the tested4..12 range may be recoverable using recurrence-constrained language initialization.',
            'basis':'E017 already implements affine-chain trigram factors and cyclic beam search for4..12-rune seeds. The13..32 range remains outside that completed search; the affine recurrence itself is not a new discovery.',
            'mechanism':'Reuse and independently check E017 affine_chain; benchmark a bounded unary initialization with coupled-factor refinement versus a fixed budget of existing cyclic-beam starts for13..32 seeds. Treat arbitrary F omissions as a separately calibrated extension.',
            'success_criterion':'Fixed seeds, finite length/sign families, fresh blind controls and shorter regressions; independent scalar recurrence/re-encryption and full null optimizer before unknown claims.',
            'limits':'Untested proposal; no E062 result. No claim that LP uses this recurrence or that skipped-F cursor rules transfer automatically.'})
    hypotheses.update(status=status,updated_at=now,next_queue=queue);save('hypotheses.json',hypotheses)
    control_table='\n'.join(f'| {r["kind"]} {r["index"]} | {r["key_length"]} | {r["runes"]} | exakt |' for r in controls['controls'])
    unknown_table='\n'.join(f'| {r["section"]} | {r["runes"]} | {r["key_length"]} | {r["score"]:.6f} |' for r in unknown['sections'])
    report=f'''# Forschungsserie 21: Fragmentabstände genutzt, unbekannte Seiten angegriffen

Stand (UTC): {now}. **Keine neue Entschlüsselung bestätigt.**
Die Kombination beider Initialisierungen löst alle 21 Blindkontrollen exakt, einschließlich des zuvor
mehrfach gescheiterten kurzen 31-Runen-Schlüssels. Danach wurde das Verfahren unverändert
auf neun LP2-Gruppen angewandt, die alle 55 unbekannten Runenseiten abdecken.

## E058: Exakte Abstandsbedingungen bei der Initialisierung

Bei zwei Fragmentstarts a<b derselben Seite gilt
`phase_b-phase_a = (b-a)-s (mod m)`. Die Zahl s der kopierten F im Intervall
liegt zwischen null und der Anzahl Chiffren-F in `[a,b)`. Diese Information
stammt ausschließlich aus dem Chiffretext. Bisher wurden Fragmentphasen
unabhängig gewählt; jetzt optimiert eine exakte Ketten-DP ihre zulässigen
Kombinationen. Unterschiedliche Seiten bleiben unabhängig. Lücken tragen
keinen Sprachscore zum Pool bei, ihre möglichen Cursorverschiebungen aber schon.

Unverändert: zwölf längste F-freie Fragmente ab 16, begrenzt auf 256 Runen;
nominale Perioden 17–32 und beide Vorzeichen. 64 Starts für kurze Eingaben,
sonst 16; vier beziehungsweise zwei behaltene Unigrammstarts. Die ersten drei
Starts nehmen keine, alle beziehungsweise die halbe Zahl möglicher F-Kopien
zwischen Fragmenten an; weitere Starts verwenden feste Zufallsseeds und
zulässige Abstände. Danach Bigramm-/Viergrammverfeinerung und 20 diversifizierte
Volltextstarts mit dem kontinuierlichen E056-Sprachkontext. Der bisherige
konservative Pool-Phasenabzug bleibt unverändert. Keine wahren Schlüssel,
Masken oder Phasen werden an den Solver gegeben.

Stufe A: schwierige E054-Regression plus drei frische natürliche Bereiche
aus Emerson X/XI/XII, Runen 16000:16729, Schlüssel 17/23/31, unabhängige
Seitenphasen und F-Kopierwahrscheinlichkeiten 0,25/0,50/0,75. Stufe B wurde
erst nach vier exakten Ergebnissen gestartet: elf weitere E054-Regressionen
und die drei E056-Grenzstresstests. Trainingskapitel bleiben I, III–IX.

E058 allein löst **17/18** Fälle, verfehlt jedoch die ältere 1200-Runen-
Kontrolle mit Schlüssel 31 (49/1200 richtig). Der dafür vorab geplante
Angriff E059 bleibt gesperrt und unausgeführt; sein Plan bleibt erhalten.

## E060: Beide Initialisierungen mit fester gemeinsamer Auswahl

Die unveränderten E057- und E058-Suchen laufen vollständig, ihre jeweils drei
besten Kandidaten werden nach demselben Volltextscore zusammengeführt.
Gleichstände behalten die Reihenfolge E058 vor E057; gleiche Klartexte werden
zusammengefasst. Keine Kontrolle entscheidet, welches Verfahren zugelassen
wird. Identische bereits geprüfte Suchläufe werden ausschließlich anhand von
Chiffretext, Seitenspannen, Training und eingefrorenen Code-/Ausgabehashes
wiederverwendet. Das spart Wiederholungen, ohne Lösungswissen einzuspeisen.

Zuerst beide schwierigen Fälle und drei neue natürliche Bereiche aus X/XI/XII,
Runen 16850:17579, dann alle übrigen 16 E058-Kontrollen. Neue Schlüssel, Phasen
und F-Kopien sind mit getrennten festen Seeds erzeugt. Diese Bereiche grenzen
an frühere Kontrollbereiche und sind keine unabhängige neue Textsammlung.
Alle **21 Hybridkontrollen** werden exakt rekonstruiert:

| Kontrolle | Schlüssel | Runen | Text/Schlüssel/Vorzeichen/Maske/Phasen |
|---|---:|---:|---|
{control_table}

Beim schwierigen Fall gibt es zwölf Fragmente in drei Seitenketten. Für die
tatsächliche Periode 31 sinkt die Zahl zulässiger Phasenbelegungen gegenüber
unabhängigen Fragmenten rechnerisch um Faktor {float(reduction):.1f}.
Das ist eine kombinatorische Zählung, keine gemessene Laufzeitbeschleunigung.
Der wahre Schlüssel erscheint in {audit['exact_unigram_start_count']} Unigramm-
und {audit['exact_bigram_states']} Bigrammzuständen; erst spätere Verfeinerung
liefert die vollständige Rekonstruktion. Die Suche bleibt heuristisch über
Schlüssel, auch wenn die bedingte Phasenoptimierung exakt ist.

Ein vollständiger passender Kontroll-Nullversuch hat Score
{controls['null_score']:.6f}; daraus allein wird kein p-Wert abgeleitet.

## E061: Direkter Angriff auf die unbekannten LP2-Abschnitte

Gemeinsamer zyklischer Schlüssel pro Gruppe, eigene Startphase je Seite,
optionale F-Kopien ohne Schlüsselverbrauch und durchlaufender Sprachkontext.
Gruppierung und zusammenhängender Klartext sind Hypothesen. LP2-50 bleibt als
leere Runenspanne erhalten; die Zahlendaten werden dadurch nicht entschlüsselt.
LP2-54/55 werden innerhalb LP2-40_55 erfasst. Kein Parameter wurde an die
unbekannten Ausgaben angepasst.

| Abschnitt | Runen | gefundene primitive Schlüssellänge | bester Score |
|---|---:|---:|---:|
{unknown_table}

Vor den Nullversuchen wurde die Auswahl des höchsten Scores samt allen
Ausgabehashes festgeschrieben: **{unknown['selected_section']}**. Dann wurden
19 unabhängige Zufallstexte dieses Abschnitts mit demselben vollständigen
Solver optimiert. Jeder behält je Seite Häufigkeiten, Endpunkte und Anzahl
benachbarter gleicher Runen. **{unknown['exceedances']}/19** erreichen mindestens
den beobachteten Score. Mit Plus-eins-Korrektur: Roh-p={unknown['raw_p']:.2f},
Bonferroni-Korrektur für die Auswahl unter neun Gruppen={unknown['bonferroni9']:.2f}.
Diese grobe Prüfung kann mit 19 Nullsuchen keinen kleinen korrigierten p-Wert
auflösen (Minimum 0,45). Sie bestätigt keinen Klartext und schließt die
gesamte Chiffrenfamilie bei einem unauffälligen Befund auch nicht aus.
Algebraisch gleich rückverschlüsselnde Anfangs-F-Alternativen bleiben sichtbar.

## Unabhängige Prüfung und Checkpoint

{count} Tests bestanden, darunter vollständige Enumeration kleiner
Phasenketten. Sämtliche gespeicherten Poolzustände und Volltextzustände
wurden skalar nachgerechnet. Eine separate rückwärts laufende Rekurrenz
bestätigt die bedingten Kettenmaxima; die Volltextmaxima, Originalquellbereiche,
Rückverschlüsselung, Zufallstexte und Auswahlkorrektur wurden ebenfalls geprüft.
Exakte Prüfzähler stehen in der Messübersicht.

{len(entries)} registrierte Aufgaben, {seconds:.3f} Sekunden Experimentzeit;
Vor E060 wurde das Gesamtbudget prospektiv auf 3600 Sekunden erweitert;
E058 bleibt innerhalb seiner ursprünglichen Grenze. Höchstens 180 Sekunden
pro Aufgabe, ein Worker.
Höchster abgetasteter Speicherwert {summary['peak_sampled_bytes']/1024**2:.1f} MiB
bei 768 MiB Grenze. Quellbytes und frühere Versuchsergebnisse unverändert;
kein weiterlaufender Forschungsprozess.

Der Lauf wurde zwischenzeitlich unterbrochen. 13 fertige Aufgaben wurden
über Hashprüfung übernommen; nur der unvollständige fünfte Nullfall und
die danach fehlenden Fälle wurden ausgeführt. Alte Prozessprotokolle bleiben
bytegleich erhalten. Für die ungemessene Dauer des abgebrochenen Versuchs
werden konservativ {interrupted_charge:.0f} Sekunden auf das Budget angerechnet
(zusätzlich zu den gemessenen erfolgreichen Läufen; keine behauptete Messzeit).

Nächster registrierter Arbeitsauftrag (noch kein Ergebnis): {next_item['task']}

[Abstandsplan](../experiments/constrained_fragment_plan.json),
[Hybridkontrollplan](../experiments/hybrid_fragment_plan.json),
[Angriffsplan](../experiments/hybrid_unknown_plan.json),
[Messübersicht](../results/phase21_summary.json),
[Checkpoint](../checkpoints/phase21_complete.json).
'''
    (ROOT/'reports/attack_phase21_report.md').write_text(report,encoding='utf-8')
    path=ROOT/'README.md';original=path.read_bytes().decode('utf-8');text=original.replace('\r\n','\n')
    a,b=text.index('Reproduzierbare Kryptanalyse'),text.index('Start:')
    text=text[:a]+('Reproduzierbare Kryptanalyse des Liber Primus. **Keine neue Entschlüsselung\n'
        'nachgewiesen.** Serie 21 löst mit kombinierter Fragmentinitialisierung alle\n'
        '21 Blindkontrollen exakt. Anschließend wurden neun unbekannte Gruppen\n'
        f'und 19 passende Zufallstexte geprüft: korrigiertes p={unknown["bonferroni9"]:.2f}.\n\n')+text[b:]
    text=text.replace('Start: [Aktueller Forschungsbericht](reports/attack_phase20_report.md)',
                      'Start: [Aktueller Forschungsbericht](reports/attack_phase21_report.md)')
    text=text.replace('- 118 Tests bestanden; 57 Experimentgruppen',f'- {count} Tests bestanden; 60 Experimentgruppen')
    text=text.replace('## Aktueller Stand\n\n','## Aktueller Stand\n\n'
        '- E058/E060: 17/18 mit Abstandsbedingungen; 21/21 mit beiden Initialisierungen.\n'
        f'- E061: alle 55 unbekannten Runenseiten in neun Gruppen geprüft; {unknown["exceedances"]}/19\n'
        f'  ausgewählte Nullscores mindestens so hoch, korrigiertes p={unknown["bonferroni9"]:.2f}. Keine neue Lösung.\n',1)
    before,after=original.splitlines(keepends=True),text.splitlines(keepends=True);out=[]
    matcher=difflib.SequenceMatcher(a=[x.rstrip('\r\n') for x in before],b=[x.rstrip('\r\n') for x in after],autojunk=False)
    for tag,a,b,c,d in matcher.get_opcodes():out.extend(before[a:b] if tag=='equal' else after[c:d])
    path.write_bytes(''.join(out).encode('utf-8'))
    save('checkpoints/phase21_complete.json',{'created_at':now,'status':status,
        'summary':'results/phase21_summary.json','summary_sha256':sha('results/phase21_summary.json'),'experiments':entries})
    print(json.dumps({'status':status,'tests_passed':count,'successful_tasks':len(entries),
        'seconds':seconds,'exceedances':unknown['exceedances'],'bonferroni9':unknown['bonferroni9']}))


if __name__=='__main__':main()
