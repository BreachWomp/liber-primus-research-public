# Forschungsstand: Liber Primus

Stand: 2026-10-18T19:52:03.178045+00:00. **Keine neue Entschlüsselung nachgewiesen.** Die erste begrenzte
Forschungsserie mit fünf Experimenten ist abgeschlossen. Das Hauptziel bleibt offen.

## Belastbare Grundlagen

- 75 Seiten erfasst: LP1 mit 17, LP2 mit 58 Seiten. Die reine Zahlenseite LP2-50 bleibt enthalten.
- Zwei Transkriptionen stimmen bei allen 58 LP2-Runenfolgen überein: insgesamt 13.136 Runen,
  davon 12.956 auf den ungelösten Seiten LP2-00 bis LP2-55. Gemeinsame Herkunft der Quellen ist möglich.
- Neun bekannte Lösungsabschnitte exakt reproduziert. Acht stimmen auch mit dem kanonischen
  Korpus überein; ein LP1-Abschnitt enthält zwei dokumentierte WHO/WHAT-Abweichungen.
  Dieser Abschnitt wurde aus dem Sprachtraining ausgeschlossen.
- 36 Tests bestanden; Quelldateien sind durch Commit-IDs und SHA-256 festgelegt.
  Die historische Authentizität der ursprünglichen Cicada-Veröffentlichung ist noch nicht kryptographisch geprüft.

## Ergebnisse

| Experiment | Ergebnis | Zulässige Schlussfolgerung |
|---|---|---|
| [E001: benachbarte gleiche Runen](../results/E001-adjacency-dca9ed9aa460.json) | 86 von 12.901 Paaren; Erwartung 439,166; 9.999 Permutationen; p_MC=0,0001, Holm über 59 Tests=0,0059 | Bekannten Wiederholungsmangel unabhängig reproduziert; kein Nachweis einer bestimmten Chiffre |
| [E002: Markov-Vergleich](../results/E002-markov-heldout-7e729f4fda7a.json) | Lags 2–16 auf vorab bestimmten Testseiten: maxT p=0,6465 | Unter diesem eingeschränkten Modell kein zusätzlicher Befund; Parameterschätzfehler nicht fortgepflanzt |
| [E003: begrenzte Chiffrensuche](../results/E003-bounded-cipher-screen-c2e41025a0eb.json) | 113.448 Varianten, davon 110.432 auf ungelösten Seiten; beide LP2-Kontrollen exakt im Suchraum | Keine neue Lösung; schwaches Sprachmodell setzt die richtige LP2-56-Lösung nur auf Rang 2 |
| [E004: Prüfung eines Zufallssamplers](../results/E004-sampler-audit-7c4a6a3fc016.json) | Exaktes Gegenbeispiel mit 12 Zuständen; Totalvariationsabstand 5/21 | Nur akzeptierte Vertauschungen zu zählen verzerrt allgemein die angestrebte Gleichverteilung |
| [E005: Perioden 2–32](../results/E005-heldout-period-scan-4dcfc95b826f.json) | 434 Seiten-/Periodenkombinationen; 9.999 Simulationen; maxT p=0,3012 | Kein auffälliger Befund in diesem Suchraum; eingebauter Perioden-8-Kontrollfall wird erkannt |

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

Gespeicherte erfolgreiche Experimentprozesse: 6 einschließlich
eines dokumentierten E003-Wiederholungslaufs nach einer Codeänderung.
Ihre aufsummierte Laufzeit beträgt 30.905 Sekunden. Download-, Test-
und Analysezeit ist darin nicht enthalten. Kein Experiment überschritt seine
Grenze von höchstens 180 Sekunden; die Vergleichssimulationen arbeiten in begrenzten
Blöcken. Es läuft kein unbeaufsichtigter Hintergrundprozess.

Die Ergebnisse sind im [Experimentprotokoll](../experiment_log.jsonl),
[Forschungsstand](../research_state.json) und
[Checkpoint](../checkpoints/research_checkpoint_2026-10-18.json) gespeichert.
