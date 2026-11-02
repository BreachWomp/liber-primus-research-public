"""Independent boundary-collision/oracle audit and phase19 checkpoint."""
from collections import Counter
from datetime import datetime,timezone
import difflib
import json
import math
from pathlib import Path
import re
import subprocess
import sys
from verify_phase19 import PageVerifier,load,sha,to_indices,to_runes,scalar_replay,schedule_optimum
ROOT=Path(__file__).resolve().parents[1]
def save(path,value):(ROOT/path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def main():
    if (ROOT/'checkpoints/phase20_complete.json').exists():raise RuntimeError('Newer checkpoint exists')
    control=load('results/phase19_control_validation.json');assert not control['gate_passed']
    events=[json.loads(x) for x in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    done=[e for e in events if e['status']=='completed'];latest={e['experiment']:e for e in done}
    event=latest['E055-long-page-phase-diagnosis'];diagnostic=load(event['output'])
    entries=control['entries']+[{'id':event['experiment'],'fingerprint':event['fingerprint'],'output':event['output'],'sha256':event['output_sha256']}]
    for entry in entries:
        e=latest[entry['id']];assert sha(entry['output'])==entry['sha256']==e['output_sha256'] and e['wall_seconds']<180
        for path,digest in e['input_dependencies'].items():assert sha(path)==digest,path
    v=PageVerifier();oracles=[];expected_pairs=[];sources={}
    for record in diagnostic['controls']:
        source_run=load(record['control_output']);source=source_run['source'];sources[record['control_output']]=source
        truth=to_indices(source['truth_runes']);spans=source['page_spans'];cipher=source['ciphertext_indices'];key=source['injected_key'];m=len(key)
        assert record['original_exact']==source_run['exact']
        truth_language=sum(v.language(truth[s['start']:s['end']],4) for s in spans if s['runes'])/len(cipher)
        penalty=(m*math.log(29)+cipher.count(0)*math.log(2)+(sum(s['runes']>0 for s in spans)-1)*math.log(m))/len(cipher)
        assert abs(truth_language-penalty-record['truth_score'])<1e-9
        assert record['found_score']==source_run['result']['top'][0]['score']
        if source_run['exact']:assert 'known_key_oracle' not in record
        else:
            oracle=record['known_key_oracle'];row=oracle['result'];v.page_spans=spans;v.stream_row(cipher,row)
            optimum=sum(s['runes']*schedule_optimum(cipher[s['start']:s['end']],key,source['injected_sign'],v.model) for s in spans if s['runes'])/len(cipher)
            assert abs(optimum-row['language_score'])<1e-9
            plain=to_indices(row['plaintext_runes']);expected={'plaintext_exact':plain==truth,'key_exact':row['key']==key,
                'mask_exact':row['skip_positions']==source['injected_skips'],'phases_exact':row['page_phases']==source['injected_phases']}
            assert oracle['checks']==expected and oracle['exact']==all(expected.values())
            errors=[i for i,(a,b) in enumerate(zip(plain,truth)) if a!=b]
            assert oracle['error_positions']==errors and oracle['correct_runes']==len(truth)-len(errors)
            assert abs(oracle['oracle_minus_truth']-(row['score']-record['truth_score']))<1e-9
            assert oracle['truth_inputs']==['injected_key_cycle','injected_sign']
            oracles.append({'kind':record['kind'],'index':record['index'],'runes':len(truth),
                'oracle_exact':oracle['exact'],'oracle_correct_runes':oracle['correct_runes'],'error_positions':errors,
                'truth_score':record['truth_score'],'found_score':record['found_score'],'oracle_score':row['score'],
                'oracle_minus_truth':oracle['oracle_minus_truth']})
        first=next(i for i,s in enumerate(spans) if s['runes'])
        expected_pairs += [(record['control_output'],j) for j,s in enumerate(spans) if j!=first and s['runes'] and cipher[s['start']]==0]
    assert len(sources)==12 and len(oracles)==sum(not r['exact'] for r in control['controls'])
    assert [(r['control_output'],r['page_index']) for r in diagnostic['boundary_collisions']]==expected_pairs
    collisions=[]
    for record in diagnostic['boundary_collisions']:
        source=sources[record['control_output']];cipher=source['ciphertext_indices'];spans=source['page_spans'];key=source['injected_key'];sign=source['injected_sign']
        j=record['page_index'];a=spans[j]['start'];original_skips=source['injected_skips'];original_phases=source['injected_phases']
        expected_skips=sorted(set(original_skips)^{a});expected_phases=original_phases[:]
        expected_phases[j]=(expected_phases[j]+(-1 if a in original_skips else 1))%len(key)
        assert record['alternative_skips']==expected_skips and record['alternative_phases']==expected_phases
        assert record['ciphertext_position']==a and cipher[a]==0
        assert record['original_copied']==(a in original_skips)
        assert record['original_phase']==original_phases[j] and record['alternative_phase']==expected_phases[j]
        truth=v.page_plain(cipher,spans,key,sign,original_skips,original_phases)
        alternative=v.page_plain(cipher,spans,key,sign,expected_skips,expected_phases)
        assert [i for i,(x,y) in enumerate(zip(truth,alternative)) if x!=y]==[a]
        assert to_runes(truth)==source['truth_runes'] and to_runes(alternative)==record['alternative_plaintext_runes']
        assert record['original_symbol']==truth[a] and record['alternative_symbol']==alternative[a] and record['ciphertext_identical']
        penalty=(len(key)*math.log(29)+cipher.count(0)*math.log(2)+(sum(s['runes']>0 for s in spans)-1)*math.log(len(key)))/len(cipher)
        for field,plain in (('truth_score',truth),('alternative_score',alternative)):
            score=sum(v.language(plain[s['start']:s['end']],4) for s in spans if s['runes'])/len(cipher)-penalty
            assert abs(score-record[field])<1e-9
        collisions.append({k:record[k] for k in ('control_output','page_index','ciphertext_position','original_copied','original_phase','alternative_phase','original_symbol','alternative_symbol','truth_score','alternative_score')})
    assert collisions and diagnostic['unknown_sections_searched']==0 and diagnostic['new_decryptions']==[]
    tests=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=60)
    output=tests.stdout+tests.stderr;(ROOT/'results/validation_phase19.txt').write_text(output,encoding='utf-8')
    if tests.returncode:raise RuntimeError(output)
    count=int(re.search(r'Ran (\d+) tests',output)[1]);now=datetime.now(timezone.utc).isoformat()
    validation=Counter(control['validation']);validation.update(v.counts)
    summary={'controls':control['controls'],'gate_passed':False,'exact_controls':sum(r['exact'] for r in control['controls']),
        'diagnostic_null_score':control['null_score'],'known_key_oracles':oracles,'boundary_collisions':collisions,
        'validation':dict(validation),'independent_oracle_optima':len(oracles),'independent_collision_replays':len(collisions),
        'tests_passed':count,'successful_tasks':14,'seconds':control['seconds']+event['wall_seconds'],
        'peak_sampled_control_bytes':control['peak_sampled_bytes'],'unknown_sections_searched':0,'new_decryptions':[]}
    assert summary['seconds']<1200;save('results/phase19_summary.json',summary)
    status='nineteenth_batch_controls_failed_boundary_ambiguity_and_short_key_search'
    queue=[{'id':'H041','priority':1,'task':'Preregister finite-context language scoring across page boundaries while key phases may reset. Preserve and report algebraically equivalent leading-F alternatives. Calibrate on fresh paired boundary controls and E054 regressions; do not silently relax exact-control gates.'},
           {'id':'H042','priority':2,'task':'Improve short long-key initialization with a fixed, bounded restart/fragment strategy. E054729-rune31-key failure needs fresh varied-F controls and old regressions before unknown escalation; no key/mask/phase oracle in search.'},
           {'id':'H031','priority':3,'task':'General substitution remains deferred pending independently justified scoring repair.'},
           {'id':'H023','priority':4,'task':'Delay3 feedback remains deferred pending feasible calibrated reduction.'}]
    state=load('research_state.json');existing={r['fingerprint'] for r in state['completed_experiments']}
    state['completed_experiments'] += [r for r in entries if r['fingerprint'] not in existing]
    state.update(status=status,updated_at=now,latest_report='reports/attack_phase19_report.md',next_experiments=[r['id'] for r in queue],
        new_decryptions=[],promising_candidates=[],
        session_budget={'phase':'nineteenth long page-phase controls and boundary diagnosis','max_compute_wall_seconds':1200,
            'max_experiment_wall_seconds':180,'control_memory_ceiling_mib':768,'workers':1,'background_jobs':False},
        scoring_gate=f'E054 {summary["exact_controls"]}/12 controls exact; failed gate blocks unknown scan. E055 records explicitly known-key oracles and algebraic page-start collisions.',
        notes=['No previously unknown plaintext confirmed.','Direct cryptanalysis only; no unsupported community claim audits.',
            'E054 has new729/3316-rune controls,random pagephases and Bernoulli F copying, plus six E052 regressions.',
            'No unknown ciphertexts scanned in phase19 after control failure.',
            'Independent pagephase plus optional leadingF copy is not injective without extra information; retained alternatives are not new decryptions.',
            'E055 supplies known keys only for labelled diagnosis; oracle recovery is not blind solving.',
            'All source bytes and historical outcomes retained. No running research process remains.'])
    state['validation'].update(tests_passed=count,path='results/validation_phase19.txt',phase19=summary['validation'],phase19_collisions_verified=len(collisions))
    state['resources'].update(recorded_successful_experiment_runs=len(done),recorded_experiment_subprocess_wall_seconds=sum(e['wall_seconds'] for e in done),phase19_wall_seconds=summary['seconds'])
    message=f'E054 long page-local phases: {summary["exact_controls"]}/12 exact; short17-key boundary error and short31-key search failure block unknown scan. E055 reversible leadingF collisions preserved.'
    if message not in state['failed_approaches']:state['failed_approaches'].append(message)
    save('research_state.json',state)
    hypotheses=load('hypotheses.json');h=next(r for r in hypotheses['hypotheses'] if r['id']=='H040')
    h.update(status='control_gate_failed_boundary_and_short_key',experiments=['E054','E055'],result=summary,
        limits='Synthetic successes do not validate all short inputs. Free page phases and optional initialF copying permit distinct plaintexts with identical ciphertext; language ranking is not unique cryptographic identification.')
    hypotheses['hypotheses'] += [
        {'id':'H041','status':'queued','claim':'Retaining language context across key-phase page boundaries may reduce boundary misranking while preserving explicit equivalent alternatives.',
         'basis':'E054 fresh0 finds true key but misranks one page-initialF; E055 supplies a reversible ambiguity proof.',
         'mechanism':'Exact finite-context DP across boundaries, with key-phase choice at each page and separately reported leading-F alternatives.',
         'success_criterion':'Preregister fresh paired controls with preserved context plus old E054 regressions; exact objective replay and honest ambiguity labels. No unknown scan on failed gate.',
         'limits':'No language model can make a non-injective rule uniquely invertible for all plaintexts. This is a ranking/representation change, not proof of the LP cipher.'},
        {'id':'H042','status':'queued','claim':'Short long-key searches may need a different bounded initialization than the validated long-input solver.',
         'basis':'E054 fresh2 has729runes,key31 and copiedF probability.75; only30runes correct despite long31-key cases succeeding.',
         'mechanism':'Preregister a limited multistart or fragment-selection change without target plaintext access, test fresh short controls and previous regressions.',
         'success_criterion':'Exact non-oracle recovery on new short/long varied-F cases; retain boundary ambiguities and matched full-optimizer nulls before unknown claims.',
         'limits':'Hypothesis motivated by a failed control; avoid tuning to its known key or reporting oracle diagnostics as success.'}]
    hypotheses.update(status=status,updated_at=now,next_queue=queue);save('hypotheses.json',hypotheses)
    table='\n'.join(f'| {"Neu" if r["kind"]=="fresh" else "Regression"} {r["index"]} | {r["chapter"]} | {r["key_length"]} | {r["correct_runes"]}/{r["runes"]} | {"exakt" if r["exact"] else "verfehlt"} |' for r in control['controls'])
    oracle_table='\n'.join(f'| {r["kind"]} {r["index"]} | {r["oracle_correct_runes"]}/{r["runes"]} | {r["truth_score"]:.8f} | {r["oracle_score"]:.8f} | {r["oracle_minus_truth"]:.8f} |' for r in oracles)
    report=f'''# Neunzehnte Forschungsserie: Lange Schlüssel mit Seitenphasen

Stand (UTC): {now}. **Keine neue Entschlüsselung bestätigt.**
{summary['exact_controls']} von zwölf Kontrollen werden vollständig rekonstruiert.
Die nicht bestandenen Kontrollen blockieren den Angriff auf unbekannte Seiten
mit dieser Variante. Die bereits abgeschlossene Serie 18 bleibt unverändert.

## E054: Neue Regel und vorab festgelegte Prüfung

Gemeinsamer Schlüssel, nominal 17–32 Runen, Vorzeichen ±1. Jede Seite darf
an einer eigenen Schlüsselphase beginnen; ihr Sprachkontext beginnt neu.
Eine ausgewählte Chiffren-F wird ohne Schlüsselverbrauch kopiert.
Die erste nichtleere Seite hat Phase null als Darstellungskonvention;
leere Zahlenseiten bleiben erhalten und haben Phase null.

E052-Initialisierung unverändert bis auf die notwendige Seitengrenze:
F-freie Startfragmente dürfen nun keine Seite überqueren. Zwölf längste
Fragmente ab16 Runen, je maximal256; 16 Starts pro Periode/Vorzeichen,
Unigramm-, Bigramm-, Viergrammfolge, 20 diversifizierte Volltextstarts.
Dann exakte bedingte Phasen-/F-Suche je Seite und bis zu drei gemeinsame
Schlüssel-/Zeitplanrunden. Der Score bestraft zusätzlich die freien
Seitenphasen: `(sum_page(logp4)-m*ln29-F_count*ln2-(G-1)*ln(m))/N`.

Sechs neue Quellbereiche: Emerson X, XI, XII jeweils Runen6000:6729 und
8000:11316. Schlüssel17,23,31; Seitenlängen wie LP2-00_02 beziehungsweise
LP2-40_55, einschließlich des leeren LP2-50-Spanneneintrags. Unabhängige
Zufallsphasen und Bernoulli-Kopie jeder Klartext-F mit p=0,25/0,50/0,75.
Feste getrennte Seeds für Schlüssel/Phasen und Masken. Training weiter
I,III–IX; Originalbereiche unabhängig nachgerechnet und disjunkt.
Hinzu kommen alle sechs E052-Eingaben unverändert; ihre bekannten
Seitenphasen werden nur zur Auswertung aus dem durchlaufenden Cursor
abgeleitet und nicht an den Solver übergeben.

| Kontrolle | Kapitel | Schlüssel | richtige Runen | Text/Schlüssel/Maske/Phasen |
|---|---|---:|---:|---|
{table}

Ein vollständiger passender Nulltext zur kurzen31-Kontrolle hat Score
{control['null_score']:.6f}. Ein einzelner diagnostischer Nullvergleich
erhält keinen p-Wert. Die kurzen Positivkontrollen schließen die bisherige
Kalibrierungslücke sichtbar nicht vollständig: langes Gelingen garantiert
kein kurzes Gelingen. Der korrekte17-Schlüssel der ersten Kontrolle wird
gefunden, aber eine Rune an Position262, dem Beginn der zweiten Seite,
anders bewertet. Der kurze31-Fall verfehlt den Schlüssel und hat nur30/729
richtige Runen. Die Fehler werden nicht als Ausschluss dieser Chiffre gedeutet.

## E055: Explizite Oracle-Diagnose und echte Mehrdeutigkeit des Modells

Nach Beobachtung der Fehler separat registriert; keine nachträgliche
Parameteranpassung und kein unbekannter Text. Nur für fehlgeschlagene
Kontrollen wird der wahre Schlüsselzyklus samt Vorzeichen an die exakte
Phasen-/F-Optimierung übergeben. Das ist eine Diagnose mit Lösungswissen.

| Kontrolle | Oracle: richtige Runen | Wahrer Score | Oracle-Score | Oracle minus wahr |
|---|---:|---:|---:|---:|
{oracle_table}

Positive Score-Differenz bedeutet: Selbst bei bekanntem Schlüssel bevorzugt
dieses Sprachziel eine abweichende Ausgabe. Ein exakter Oracle bei zugleich
verfehlter blinder Suche zeigt dagegen einen Suchengpass. Keines dieser
Oracle-Ergebnisse zählt als eigenständige Entschlüsselung.

Unabhängig vom Score gibt es eine konkrete algebraische Mehrdeutigkeit.
Beginnt eine nicht erste Seite mit Chiffren-F, also `C_0=0`, gilt:

* Normal entschlüsseln bei Phase `p`: erste Klartextrune `K[p]`, danach Cursor `p+1`.
* F kopieren bei Phase `p+1`: erste Klartextrune `0`, danach ebenfalls Cursor `p+1`.

Alle folgenden Runen verwenden dieselben Schlüsselstellen. Beide Varianten
erzeugen bei Rückverschlüsselung exakt denselben Chiffretext. Die inverse
Änderung entfernt eine Kopie und verschiebt die Startphase um minus eins.
Der Schlüssel selbst bleibt gleich. Damit ist die Abbildung bei frei
wählbaren Seitenphasen und optionaler Anfangs-F-Kopie ohne Zusatzinformation
nicht eindeutig umkehrbar. Es handelt sich um eine Eigenschaft des geprüften
Modells, nicht um einen Nachweis der tatsächlichen Liber-Primus-Chiffre.

Für alle passenden Seitenanfänge in allen zwölf Kontrollen wurden
**{len(collisions)} solche Paare** gespeichert und unabhängig rückverschlüsselt.
Jedes Paar unterscheidet sich in genau einer Klartextrune. Sprachbewertung
kann zwischen ihnen wählen, beseitigt diese algebraische Mehrdeutigkeit aber
nicht. Solche Alternativen müssen ausdrücklich sichtbar bleiben.

## Validierung, Grenzen und nächste Versuche

{count} Tests bestanden. {validation['pool_records_recomputed']} skalare
Poolzustandsprüfungen, {validation['stream_records_recomputed']} Volltext-
zustandsprüfungen, {validation['independent_pool_phase_optima']} unabhängig
enumerierte Fragmentphasen-Maxima und {validation['independent_stream_optima']}
vollständige bedingte Phasen-/Zeitplanprüfungen. Zusätzlich {len(oracles)}
Oracle-Maxima und {len(collisions)} Mehrdeutigkeitspaare separat bestätigt.
Originaltextbereiche, Seeds, Seiten einschließlich leerer Spannen, Nulltext,
Auswahlregeln, Hashes und Rückverschlüsselungen geprüft.

14 registrierte Aufgaben, {summary['seconds']:.3f} Sekunden Experimentzeit;
Budget1200, maximal180 je Aufgabe, ein Worker. E054-Speicherüberwachung
alle250ms: höchster abgetasteter Resident-/Private-Wert
{control['peak_sampled_bytes']/1024**2:.1f}MiB bei Abbruchgrenze768MiB.
E055 ist eine begrenzte deterministische Diagnose. Keine Quellbytes oder
historischen Ergebnisse verändert; keine weiterlaufenden Forschungsprozesse.

Nächste Schritte: Sprachkontext über Seitenwechsel hinweg prüfen und dabei
mehrdeutige Anfangs-F-Varianten ausdrücklich erhalten. Separat braucht die
kurze31-Schlüsselsuche eine vorab begrenzte bessere Initialisierung, geprüft
an frischen Fällen. Kein stilles Abschwächen der bestandenen Kontrollkriterien
und kein Hochstufen sprachähnlicher Ausgaben zu Lösungen.

[Kontrollplan](../experiments/long_phase_plan.json),
[Diagnoseplan](../experiments/long_phase_diagnostic_plan.json),
[Messübersicht](../results/phase19_summary.json),
[Checkpoint](../checkpoints/phase19_complete.json).
'''
    for old,new in {'ab16':'ab 16','maximal256':'maximal 256','Runen6000':'Runen 6000','Schlüssel17,23,31':'Schlüssel 17, 23, 31','I,III–IX':'I, III–IX','kurzen31':'kurzen 31','korrekte17':'korrekte 17','Position262':'Position 262','kurze31':'kurze 31','nur30/729':'nur 30/729','Budget1200':'Budget 1200','maximal180':'maximal 180','alle250ms':'alle 250 ms','Abbruchgrenze768MiB':'Abbruchgrenze 768 MiB'}.items():report=report.replace(old,new)
    (ROOT/'reports/attack_phase19_report.md').write_text(report,encoding='utf-8')
    readme=ROOT/'README.md';original=readme.read_bytes().decode('utf-8');text=original.replace('\r\n','\n');a=text.index('Reproduzierbare Kryptanalyse');b=text.index('Start:',a)
    text=text[:a]+('Reproduzierbare Kryptanalyse des Liber Primus. **Keine neue Entschlüsselung\n'
        f'nachgewiesen.** Die neunzehnte Forschungsserie prüft lange Schlüssel mit\neigenen Seitenphasen: {summary["exact_controls"]}/12 Kontrollen exakt. Ein kurzer Suchfehler und\n'
        'eine nachgewiesene Mehrdeutigkeit am Seitenanfang blockieren diese Variante\nfür unbekannte Seiten. Serie18 bleibt als direkter Angriff dokumentiert.\n\n')+text[b:]
    text=text.replace('Start: [Aktueller Forschungsbericht](reports/attack_phase18_report.md)','Start: [Aktueller Forschungsbericht](reports/attack_phase19_report.md)')
    text=text.replace('- 111 Tests bestanden; 53 Experimentgruppen',f'- {count} Tests bestanden; 55 Experimentgruppen')
    text=text.replace('## Aktueller Stand\n\n','## Aktueller Stand\n\n'+
        f'- E054/E055: {summary["exact_controls"]}/12 Kontrollen mit langen Schlüsseln und Seitenphasen exakt;\n'
        f'  {len(collisions)} Anfangs-F-Mehrdeutigkeitspaare rückverschlüsselt. Kein neuer unbekannter Scan.\n',1)
    before=original.splitlines(keepends=True);after=text.splitlines(keepends=True);out=[]
    matcher=difflib.SequenceMatcher(a=[x.rstrip('\r\n') for x in before],b=[x.rstrip('\r\n') for x in after],autojunk=False)
    for tag,a,b,c,d in matcher.get_opcodes():out.extend(before[a:b] if tag=='equal' else after[c:d])
    readme.write_bytes(''.join(out).encode('utf-8'))
    save('checkpoints/phase19_complete.json',{'created_at':now,'status':status,'summary':'results/phase19_summary.json',
         'summary_sha256':sha('results/phase19_summary.json'),'experiments':entries})
    print(json.dumps({'status':status,'exact_controls':summary['exact_controls'],'tests_passed':count,
         'seconds':summary['seconds'],'oracles':oracles,'collisions':len(collisions),'validation':dict(validation)}))


if __name__=='__main__':main()
