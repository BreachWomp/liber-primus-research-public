"""Checkpoint independently verified E056/E057 without repeating experiments."""
from collections import Counter
from datetime import datetime, timezone
import difflib
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def save(path, value):
    (ROOT / path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def main():
    if (ROOT / 'checkpoints/phase20_complete.json').exists():
        raise RuntimeError('Checkpoint already exists; preserve completed outcomes')
    oracle = load('results/phase20_context_validation.json')
    blind = load('results/phase20_blind_validation.json')
    assert oracle['oracle_gate_passed'] and not blind['full_gate_passed']
    assert not blind['stage_A_passed'] and not blind['stage_B_executed']
    entries = [oracle['entry']] + blind['entries']
    events = [json.loads(x) for x in (ROOT / 'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    done = [e for e in events if e['status'] == 'completed']
    by_fingerprint = {e['fingerprint']: e for e in done}
    for entry in entries:
        event = by_fingerprint[entry['fingerprint']]
        assert entry['id'] == event['experiment']
        assert sha(entry['output']) == entry['sha256'] == event['output_sha256']
        assert event['wall_seconds'] < 180
        for path, digest in event['input_dependencies'].items():
            assert sha(path) == digest, path
    old_log = subprocess.check_output(['git', 'show', 'HEAD:experiment_log.jsonl'], cwd=ROOT)
    assert (ROOT / 'experiment_log.jsonl').read_bytes().startswith(old_log)
    tests = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'],
                           cwd=ROOT, capture_output=True, text=True, encoding='utf-8', timeout=60)
    output = tests.stdout + tests.stderr
    (ROOT / 'results/validation_phase20.txt').write_text(output, encoding='utf-8')
    if tests.returncode:
        raise RuntimeError(output)
    count = int(re.search(r'Ran (\d+) tests', output)[1])
    now = datetime.now(timezone.utc).isoformat()
    validation = Counter(oracle['validation'])
    validation.update(blind['validation'])
    summary = {
        'oracle_controls': oracle['controls'], 'oracle_exact_controls': sum(r['coupled_exact'] for r in oracle['controls']),
        'oracle_gate_passed': True, 'blind_controls': blind['controls'],
        'blind_exact_controls': sum(r['exact'] for r in blind['controls']), 'blind_controls_executed': 4,
        'stage_A_passed': False, 'stage_B_executed': False, 'deferred_stage_B_controls': 14,
        'full_gate_passed': False, 'diagnostic_blind_null_score': blind['null_score'],
        'validation': dict(validation), 'tests_passed': count, 'successful_tasks': len(entries),
        'seconds': oracle['seconds'] + blind['seconds'],
        'peak_sampled_bytes': max(oracle['peak_sampled_bytes'], blind['peak_sampled_bytes']),
        'unknown_sections_searched': 0, 'new_decryptions': []}
    assert summary['oracle_exact_controls'] == 15 and summary['blind_exact_controls'] == 3
    assert summary['seconds'] < 1500
    save('results/phase20_summary.json', summary)
    status = 'twentieth_batch_oracle_calibrated_blind_short_key_gate_failed'
    queue = [
        {'id': 'H043', 'priority': 1, 'task': 'Preregister initialization preserving within-page cursor constraints between fragments. Test the hard regression and fresh controls, then deferred regressions/stress cases before any unknown scan. No oracle inputs.'},
        {'id': 'H031', 'priority': 2, 'task': 'General substitution deferred pending independently justified scoring repair.'},
        {'id': 'H023', 'priority': 3, 'task': 'Delay3 feedback deferred pending feasible calibrated reduction.'}]
    state = load('research_state.json')
    existing = {r['fingerprint'] for r in state['completed_experiments']}
    state['completed_experiments'] += [r for r in entries if r['fingerprint'] not in existing]
    state.update(status=status, updated_at=now, latest_report='reports/attack_phase20_report.md',
                 next_experiments=[r['id'] for r in queue], new_decryptions=[], promising_candidates=[],
                 session_budget={'phase': 'twentieth continuous-context calibration and blind controls',
                     'max_compute_wall_seconds': 1500, 'max_experiment_wall_seconds': 180,
                     'control_memory_ceiling_mib': 768, 'workers': 1, 'background_jobs': False},
                 scoring_gate='E056 known-key oracle 15/15 exact; E057 blind stage A 3/4 exact. Stage B not executed; unknown scan blocked.',
                 notes=['No previously unknown plaintext confirmed. Direct cryptanalysis; no community claim audits.',
                     'Continuous language context fixes the known-key boundary misranking, not algebraic non-injectivity.',
                     'Five leading-F alternative pairs independently replayed and preserved.',
                     'Expanded short-input starts recover three fresh controls but fail the old 31-key control: 43/729 runes.',
                     'Fourteen stage B controls deferred by the frozen gate. No unknown scan in phase20.',
                     'H043 is an untested next hypothesis, not an experimental result.',
                     'Source bytes and historical results preserved; no background research jobs.'])
    state['validation'].update(tests_passed=count, path='results/validation_phase20.txt', phase20=dict(validation))
    state['resources'].update(recorded_successful_experiment_runs=len(done),
        recorded_experiment_subprocess_wall_seconds=sum(e['wall_seconds'] for e in done), phase20_wall_seconds=summary['seconds'])
    state['failed_approaches'].append('E057: 64 short-input starts and continuous full-text context give 3/4 exact stage A controls; old short31-key regression remains 43/729. Stage B and unknown scan blocked.')
    save('research_state.json', state)
    hypotheses = load('hypotheses.json')
    by_id = {h['id']: h for h in hypotheses['hypotheses']}
    by_id['H041'].update(status='oracle_calibrated_partial_blind_full_gate_blocked', experiments=['E056', 'E057'],
        result={'oracle_exact': 15, 'oracle_total': 15, 'blind_exact': 3, 'blind_total_executed': 4,
                'full_gate_passed': False, 'summary': 'results/phase20_summary.json'})
    by_id['H042'].update(status='expanded_starts_insufficient_on_hard_regression', experiments=['E057'],
        result={'fresh_exact': 3, 'fresh_total': 3, 'hard_regression_correct_runes': 43,
                'hard_regression_runes': 729, 'full_gate_passed': False, 'summary': 'results/phase20_summary.json'})
    assert 'H043' not in by_id
    hypotheses['hypotheses'].append({'id': 'H043', 'status': 'queued_untested',
        'claim': 'Preserving known within-page cursor constraints during initialization may improve short long-key recovery.',
        'basis': 'E057 expanded starts fail the old short31 case while known-key conditional optimization succeeds.',
        'mechanism': 'For fragment starts a<b in one page, phase_b-phase_a = (b-a)-s mod m, with 0<=s<=count(ciphertext F in [a,b)). Joint whole-page unigram DP or constrained fragment alignment could preserve this ciphertext-derived bound.',
        'success_criterion': 'Freeze parameters, seeds and budgets before execution. Exact blind hard-regression and fresh-control recovery followed by all deferred regressions/stress controls; matched full-solver nulls and independent validation before unknown escalation.',
        'limits': 'Untested proposal; no measured reduction or E058 result. The count bound is necessary, not sufficient, and does not remove leading-F ambiguity.'})
    hypotheses.update(status=status, updated_at=now, next_queue=queue)
    save('hypotheses.json', hypotheses)
    table = '\n'.join(f'| {r["kind"]} {r["index"]} | {r["key_length"]} | {r["correct_runes"]}/{r["runes"]} | {"exakt" if r["exact"] else "verfehlt"} |' for r in blind['controls'])
    report = f'''# Zwanzigste Forschungsserie: Sprachkontext und blinde Schlüsselsuche

Stand (UTC): {now}. **Keine neue Entschlüsselung bestätigt.**
E056 rekonstruiert bei vorgegebenem Schlüssel alle 15 Kontrollen exakt.
E057 findet ohne Lösungsvorgaben drei neue Kontrollen vollständig, verfehlt
aber den bekannten schwierigen Fall. Die vollständige Freigabe ist gescheitert;
unbekannte LP-Seiten wurden mit dieser Variante nicht untersucht.

## E056: Bedingte Optimierung mit bekanntem Schlüssel

Der Sprachkontext der letzten drei Klartextrunen bleibt über Seitenwechsel
erhalten, während jede Seite eine eigene Schlüsselphase wählen darf.
Die exakte dynamische Programmierung führt Schlüsselcursor und Sprachkontext
gemeinsam. Leere Seiten, insbesondere Spannen nach dem Vorbild LP2-50,
bleiben mit Phase null erhalten. Die bisherigen Komplexitätsstrafen bleiben.
Auch die nachfolgende Schlüsseloptimierung bewertet Sprachfenster über Grenzen.

Zwölf E054-Kontrollen bleiben unverändert. Drei neue, gezielt konstruierte
Grenzfälle stammen aus Emerson X/XI/XII, Runen 12000:12729, mit Schlüssellängen
17/23/31. Die zweite Grenze wird auf eine Nicht-F-Klartextrune gelegt und
Schlüsselstelle null bewusst gleich dieser Rune gesetzt. Das erzwingt dort
eine nicht kopierte Chiffren-F. Diese Fälle sind Stresstests, keine zufällige
Stichprobe allgemeiner Schlüssel. Seeds und Konstruktion stehen im festen Plan.

Der wahre Schlüssel und das Vorzeichen sind hier ausdrücklich vorgegeben;
F-Kopiermaske und Seitenphasen werden optimiert. Alle 15 Fälle werden exakt
rekonstruiert; das bisherige Ziel mit neuem Sprachkontext je Seite schafft
14/15. Alte unveränderte Baselines wurden wiederverwendet. Fünf alternative
Anfangs-F-Rezepte mit identischer Rückverschlüsselung bleiben gespeichert,
auch bei geringerem Sprachscore. Bessere Rangfolge beseitigt keine
algebraische Mehrdeutigkeit. Ein passender Nulltext wurde nur mit dem festen
bekannten Schlüssel bewertet; daraus folgt kein Signifikanznachweis.

## E057: Vorab gestufte Blindkontrollen

Für Eingaben bis 1024 Runen steigen Starts pro Periode/Vorzeichen von 16 auf
64 und behaltene Unigrammstarts von zwei auf vier. Größere Eingaben bleiben
unverändert. Perioden 17–32, beide Vorzeichen, 20 diversifizierte Volltextstarts,
höchstens drei gemeinsame Optimierungsrunden mit je sechs Schlüsseldurchläufen.
Die Fragmentinitialisierung bleibt seitengebunden; die Volltextsuche verwendet
den E056-Kontext. Schlüssel, Maske und Phasen werden nicht an den Solver gegeben.

Stufe A prüft zuerst den unveränderten kurzen E054-Fehler, dann drei natürliche
neue Texte aus X/XI/XII, Runen 14000:14729. Seitenlängen 262/266/201,
Schlüssel 17/23/31, unabhängige Zufallsphasen und F-Kopierwahrscheinlichkeiten
0,25/0,50/0,75; keine erzwungenen Grenzrunen. Trainingskapitel bleiben I, III–IX.
Alle vier Kontrollen und ein vollständiger passender Nullversuch wurden beendet.

| Kontrolle | Schlüssellänge | richtige Runen | Text/Schlüssel/Maske/Phasen |
|---|---:|---:|---|
{table}

Die bekannte schwierige Kontrolle bleibt mit 43/729 richtigen Runen ungelöst
(vorher 30/729). Daraus wird keine brauchbare Teilentschlüsselung abgeleitet.
Der einzelne diagnostische Nullscore beträgt {blind['null_score']:.9f}; kein
p-Wert wird berechnet. Wegen des Fehlers wurde Stufe B entsprechend dem Plan
nicht ausgeführt: elf weitere E054-Regressionen und drei E056-Stresstests
bleiben offen. Drei frische Erfolge ersetzen diese vollständige Kalibrierung nicht.

## Prüfung und Ressourcen

{count} Unit-Tests bestanden. Unabhängig nachgerechnet: 15.520 Poolzustände,
160 Fragmentphasen-Maxima, 474 gekoppelte Zustände, 21 vollständige bedingte
Maxima sowie fünf Anfangs-F-Alternativpaare. Quellbereiche, Rückverschlüsselung,
Seeds, Nullkonstruktion und Hashes wurden in separaten Verifikationsskripten geprüft.

Sechs registrierte Aufgaben; {summary['seconds']:.3f} Sekunden Experimentzeit.
Budget 1500 Sekunden insgesamt, 180 je Aufgabe, ein Worker. Höchster abgetasteter
Resident-/Private-Speicherwert {summary['peak_sampled_bytes']/1024**2:.1f} MiB
bei 768 MiB Abbruchgrenze. Keine fortlaufenden Hintergrundaufgaben.
Originalquellen und frühere Versuchsergebnisse bleiben unverändert.

## Nächste ungetestete Hypothese H043

Die Initialisierung behandelt Fragmentphasen bisher unabhängig. Innerhalb
derselben Seite gilt für Starts a<b notwendigerweise
`phase_b - phase_a = (b-a)-s (mod m)`, wobei s die kopierten F zwischen den
Starts zählt und durch die dortige Anzahl Chiffren-F begrenzt ist. Eine
gemeinsame Initialisierung könnte diese aus dem Chiffretext bekannte Bindung
nutzen. Das ist ein Vorschlag für einen neuen begrenzten Versuch; weder
Beschleunigung noch bessere Rekonstruktion wurden hierfür gemessen.

[Oracle-Plan](../experiments/context_phase_plan.json),
[Blindkontrollplan](../experiments/context_blind_plan.json),
[Messübersicht](../results/phase20_summary.json),
[Checkpoint](../checkpoints/phase20_complete.json).
'''
    (ROOT / 'reports/attack_phase20_report.md').write_text(report, encoding='utf-8')
    readme = ROOT / 'README.md'
    original = readme.read_bytes().decode('utf-8')
    text = original.replace('\r\n', '\n')
    a, b = text.index('Reproduzierbare Kryptanalyse'), text.index('Start:')
    text = text[:a] + ('Reproduzierbare Kryptanalyse des Liber Primus. **Keine neue Entschlüsselung\n'
        'nachgewiesen.** Serie 20 verbessert den Sprachkontext über Seitengrenzen:\n'
        '15/15 Kontrollen mit vorgegebenem Schlüssel exakt, aber nur 3/4 blinde\n'
        'Kontrollen. Der schwierige kurze Fall bleibt ungelöst; kein neuer Scan\n'
        'unbekannter Seiten mit dieser Variante.\n\n') + text[b:]
    text = text.replace('Start: [Aktueller Forschungsbericht](reports/attack_phase19_report.md)',
                        'Start: [Aktueller Forschungsbericht](reports/attack_phase20_report.md)')
    text = text.replace('- 114 Tests bestanden; 55 Experimentgruppen', f'- {count} Tests bestanden; 57 Experimentgruppen')
    text = text.replace('## Aktueller Stand\n\n', '## Aktueller Stand\n\n'
        '- E056/E057: Durchlaufender Sprachkontext behebt den bekannten Grenzfehler\n'
        '  bei vorgegebenem Schlüssel. Drei frische Blindkontrollen exakt, schwierige\n'
        '  Regression verfehlt; 14 weitere Kontrollen planmäßig zurückgestellt.\n', 1)
    before, after = original.splitlines(keepends=True), text.splitlines(keepends=True)
    matcher = difflib.SequenceMatcher(a=[x.rstrip('\r\n') for x in before],
                                     b=[x.rstrip('\r\n') for x in after], autojunk=False)
    out = []
    for tag, a, b, c, d in matcher.get_opcodes():
        out.extend(before[a:b] if tag == 'equal' else after[c:d])
    readme.write_bytes(''.join(out).encode('utf-8'))
    save('checkpoints/phase20_complete.json', {'created_at': now, 'status': status,
        'summary': 'results/phase20_summary.json', 'summary_sha256': sha('results/phase20_summary.json'),
        'experiments': entries, 'validation_files': {p: sha(p) for p in
            ['results/phase20_context_validation.json', 'results/phase20_blind_validation.json', 'results/validation_phase20.txt']}})
    print(json.dumps({'status': status, 'tests_passed': count, 'successful_tasks': len(entries),
                      'seconds': summary['seconds'], 'total_registered_completed': len(done)}))


if __name__ == '__main__':
    main()
