"""Summarize validated, completed experiments without rewriting their history."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]


def load(path):return json.loads((ROOT/path).read_text(encoding="utf-8"))
def write(path,value):(ROOT/path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


def main():
    if (ROOT/"checkpoints/attack_phase2_complete.json").exists():
        raise RuntimeError("Initial finalizer is historical; use scripts/finalize_attack_checkpoint.py for phase two")
    now=datetime.now(timezone.utc).isoformat()
    checkpoint=load("checkpoints/latest_batch.json")
    records=checkpoint["records"]
    if len(records)!=5 or any(r["status"]!="completed" for r in records):
        raise RuntimeError("All five initial experiments must finish before finalizing")
    outputs={r["experiment"]:load(r["output"]) for r in records}
    for r in records:
        if hashlib.sha256((ROOT/r["output"]).read_bytes()).hexdigest()!=r["output_sha256"]:
            raise RuntimeError("Result checksum changed")
    validation=(ROOT/"results/validation.txt").read_text(encoding="utf-8")
    if not validation.rstrip().endswith("OK"):raise RuntimeError("Validation did not pass")
    test_count=int(re.search(r"Ran (\d+) tests",validation).group(1))
    events=[json.loads(line) for line in (ROOT/"experiment_log.jsonl").read_text(encoding="utf-8").splitlines()]
    completed=[event for event in events if event.get("status")=="completed"]
    total_wall=sum(event["wall_seconds"] for event in completed)
    adjacency=outputs["E001-adjacency"]["aggregate"]
    markov=outputs["E002-markov-heldout"]
    screen=outputs["E003-bounded-cipher-screen"]
    sampler=outputs["E004-sampler-audit"]
    period=outputs["E005-heldout-period-scan"]
    conclusions={
        "H001":("replicated_prior_art",f"86 observed stream doubles versus {adjacency['stream']['null_expectation_exact']:.6f} expected; within-family Holm p=0.0059."),
        "H002":("not_rejected_limited_model",f"Heldout lag2..16 global plug-in maxT p={markov['lag_family']['global_p_plugin']}; not cipher identification."),
        "H003":("screen_completed_scoring_gate_failed",f"{screen['variants_total']} recipes; no unknown page exceeds diagnostic control floor. Correct LP2-56 ranks second; no broad exclusion."),
        "H004":("exact_counterexample_verified",f"12-state example; accepted chain biased; stationary total variation {sampler['total_variation_degree_stationary_from_uniform']} from uniform."),
        "H005":("not_rejected_limited_model",f"{period['family_size']} heldout page/period cells; maxT p={period['global_p_plugin']}; injected period8 detected.")}
    queue=load("hypotheses.json")
    queue["updated_at"]=now
    queue["status"]="Initial five-experiment batch complete; follow-up priorities recorded. No new decryption."
    for h in queue["hypotheses"]:
        h["status"],h["result"]=conclusions[h["id"]]
    queue["next_queue"]=[
        {"id":"H006","priority":1,"task":"Image-audit all 86 observed adjacent repeats and boundary-sensitive runes.","gate":"Image hashes, exact page/rune locations, independent transcription disagreements."},
        {"id":"H007","priority":2,"task":"Calibrate language scoring with leave-one-section-out controls and new synthetic near misses.","gate":"Correct rank and character accuracy; do not tune on LP2-56 then call it heldout."},
        {"id":"H008","priority":3,"task":"Build a count/doublet-constrained proposal-count sampler with exact toy-case and mixing checks.","gate":"Uniform stationary measure, multiple starts, acceptance and autocorrelation diagnostics."},
        {"id":"H009","priority":4,"task":"Selective-F known-key searches and section-aligned prime/autokey variants after scorer calibration.","gate":"Bounded search, control reproduction, same search on matched nulls, new holdouts."}]
    write("hypotheses.json",queue)
    state=load("research_state.json")
    state.update(status="initial_batch_complete_no_new_decryption",updated_at=now,
        completed_experiments=[{"id":r["experiment"],"fingerprint":r["fingerprint"],"output":r["output"],"sha256":r["output_sha256"]} for r in records],
        next_experiments=[x["id"] for x in queue["next_queue"]],
        new_decryptions=[],promising_candidates=[],scoring_gate="failed_rank_one_on_LP2_56",
        known_solutions={"fixtures_exact":9,"fixtures_matching_canonical":8,"disputed_fixture":"LP1-06_09_atbash_shift"},
        validation={"tests_passed":test_count,"path":"results/validation.txt"},
        resources={"recorded_successful_experiment_runs":len(completed),"recorded_experiment_subprocess_wall_seconds":total_wall,
                   "scope":"Sum includes the documented E003 rerun after output/ranking implementation changes; excludes source retrieval, test runs and analyst time."},
        latest_report="reports/research_report.md",repository=load("reports/repository.json"),
        failed_approaches=["Treating every F as an interrupter fails the known LP2-56 control.",
                          "Ranking by the current sparse trigram model alone fails exact top-one recovery of LP2-56.",
                          "Fixed accepted-move constrained swaps do not guarantee a uniform null ensemble."],
        notes=["Primary decryption objective remains unresolved.","No unattended/background jobs or recurring automation are running.",
               "Initial experiment queue finished; next phase should use the saved priorities and skip identical completed fingerprints."])
    state["session_budget"]["initial_experiment_queue_size"]=5
    write("research_state.json",state)
    write("checkpoints/research_checkpoint_2026-10-18.json",state)
    links={r["experiment"]:"../"+r["output"] for r in records}
    report=f'''# Forschungsstand: Liber Primus

Stand: {now}. **Keine neue Entschlüsselung nachgewiesen.** Die erste begrenzte
Forschungsserie mit fünf Experimenten ist abgeschlossen. Das Hauptziel bleibt offen.

## Belastbare Grundlagen

- 75 Seiten erfasst: LP1 mit 17, LP2 mit 58 Seiten. Die reine Zahlenseite LP2-50 bleibt enthalten.
- Zwei Transkriptionen stimmen bei allen 58 LP2-Runenfolgen überein: insgesamt 13.136 Runen,
  davon 12.956 auf den ungelösten Seiten LP2-00 bis LP2-55. Gemeinsame Herkunft der Quellen ist möglich.
- Neun bekannte Lösungsabschnitte exakt reproduziert. Acht stimmen auch mit dem kanonischen
  Korpus überein; ein LP1-Abschnitt enthält zwei dokumentierte WHO/WHAT-Abweichungen.
  Dieser Abschnitt wurde aus dem Sprachtraining ausgeschlossen.
- {test_count} Tests bestanden; Quelldateien sind durch Commit-IDs und SHA-256 festgelegt.
  Die historische Authentizität der ursprünglichen Cicada-Veröffentlichung ist noch nicht kryptographisch geprüft.

## Ergebnisse

| Experiment | Ergebnis | Zulässige Schlussfolgerung |
|---|---|---|
| [E001: benachbarte gleiche Runen]({links['E001-adjacency']}) | 86 von 12.901 Paaren; Erwartung 439,166; 9.999 Permutationen; p_MC=0,0001, Holm über 59 Tests=0,0059 | Bekannten Wiederholungsmangel unabhängig reproduziert; kein Nachweis einer bestimmten Chiffre |
| [E002: Markov-Vergleich]({links['E002-markov-heldout']}) | Lags 2–16 auf vorab bestimmten Testseiten: maxT p=0,6465 | Unter diesem eingeschränkten Modell kein zusätzlicher Befund; Parameterschätzfehler nicht fortgepflanzt |
| [E003: begrenzte Chiffrensuche]({links['E003-bounded-cipher-screen']}) | 113.448 Varianten, davon 110.432 auf ungelösten Seiten; beide LP2-Kontrollen exakt im Suchraum | Keine neue Lösung; schwaches Sprachmodell setzt die richtige LP2-56-Lösung nur auf Rang 2 |
| [E004: Prüfung eines Zufallssamplers]({links['E004-sampler-audit']}) | Exaktes Gegenbeispiel mit 12 Zuständen; Totalvariationsabstand 5/21 | Nur akzeptierte Vertauschungen zu zählen verzerrt allgemein die angestrebte Gleichverteilung |
| [E005: Perioden 2–32]({links['E005-heldout-period-scan']}) | 434 Seiten-/Periodenkombinationen; 9.999 Simulationen; maxT p=0,3012 | Kein auffälliger Befund in diesem Suchraum; eingebauter Perioden-8-Kontrollfall wird erkannt |

Beim Wiederholungsmangel bleibt das Ergebnis auch innerhalb von Wörtern
(60 statt erwarteter 328,067) und innerhalb von Zeilen (82 statt 420,815) bestehen.
Die globale Markov- und Periodenprüfung bleibt auch nach gemeinsamer Holm-Korrektur
ohne Verwerfung (E002: 0,6465; E005: 0,6024). Nicht-Verwerfung beweist weder
Zufälligkeit noch Unlösbarkeit.

Der Chiffrenscan umfasst alle 812 affinen Abbildungen sowie Primzahl-Totientfolgen
mit Startoffset 0–28, beiden Vorzeichen und expliziten Unterbrechungsmasken
(keine, alle F, jedes einzelne F). Größere F-Teilmengen und abschnittsübergreifende
Schlüssel sind nicht abgedeckt. Die sechs unstrittigen LP1-Trainingsabschnitte
enthalten nur 2.019 Runen. Es gibt keine kalibrierten p-Werte für diese Sprachscores.

## Qualitätsbefunde und Grenzen

Die beiden LP1-Transkriptionen unterscheiden sich auf LP1-06 und LP1-07 an je
einer Stelle. Die punktuelle Bildprüfung stützt die gespeicherte iddqd-Lesart;
beide Varianten bleiben erhalten. Siehe [Transkriptionsprotokoll](transcription_discrepancy.md).

Die Samplerprüfung bezieht sich auf einen konkret eingefrorenen öffentlichen
Codepfad. Die allgemeine mathematische Erkenntnis ist bekannt; eine historische
Erstentdeckung wird nicht behauptet. Der Befund widerlegt keine sämtlichen
Ergebnisse dieses Projekts. Ein korrigierter Zähler beweist außerdem noch keine
ausreichende Durchmischung großer Seiten. Siehe [Methodenprüfung](methodology_review.md)
und [Vorarbeiten](prior_art.md).

## Nächste Forschungsprioritäten

1. Die 86 Wiederholungen anhand der Seitenbilder und einer unabhängigen Transkription prüfen.
2. Das Sprachmodell mit abschnittsweise getrennten Kontrollen und neuen künstlichen
   Fehlvarianten kalibrieren. LP2-56 ist künftig ein bekannter Regressionstest.
3. Einen bedingt zufälligen Vergleichssampler mit korrekter stationärer Verteilung
   und nachgewiesener Durchmischung entwickeln.
4. Erst danach selektive F-Unterbrechungen und abschnittsbezogene Schlüssel breiter durchsuchen.

## Reproduktion und Ressourcen

`python scripts/acquire_sources.py` rekonstruiert den Korpus aus den geprüften
lokalen Rohdateien; fehlende Dateien werden von festgelegten Versionen geladen.
`python scripts/run_batch.py --budget-seconds 900` prüft die Tests und führt nur
Experimente mit neuen Eingaben/Parametern/Code-Fingerabdrücken aus.
`python scripts/finalize_checkpoint.py` aktualisiert Bericht und Forschungsstand.

Gespeicherte erfolgreiche Experimentprozesse: {len(completed)} einschließlich
eines dokumentierten E003-Wiederholungslaufs nach einer Codeänderung.
Ihre aufsummierte Laufzeit beträgt {total_wall:.3f} Sekunden. Download-, Test-
und Analysezeit ist darin nicht enthalten. Kein Experiment überschritt seine
Grenze von höchstens 180 Sekunden; die Vergleichssimulationen arbeiten in begrenzten
Blöcken. Es läuft kein unbeaufsichtigter Hintergrundprozess.

Die Ergebnisse sind im [Experimentprotokoll](../experiment_log.jsonl),
[Forschungsstand](../research_state.json) und
[Checkpoint](../checkpoints/research_checkpoint_2026-10-18.json) gespeichert.
'''
    (ROOT/"reports/research_report.md").write_text(report,encoding="utf-8")
    print(json.dumps({"report":"reports/research_report.md","tests":test_count,"recorded_experiment_wall_seconds":total_wall,"new_decryptions":0}))


if __name__=="__main__":main()
