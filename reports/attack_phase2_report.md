# Direkte Entschlüsselungsversuche: zweite Forschungsserie

Stand (UTC): 2026-10-19T09:21:02.072379+00:00. **Keine neue Entschlüsselung nachgewiesen.**
Alle 55 ungelösten LP2-Runenseiten wurden in vier weiteren Chiffrensuchen geprüft.
LP2-50 bleibt als Zahlenseite im Korpus; diese Runenangriffe sind darauf nicht anwendbar.
Die erste Serie bleibt im [historischen Bericht](research_report.md) erhalten.

## Ergebnisse und Umfang

| Versuch | Tatsächlich untersuchter Suchraum | Ergebnis |
|---|---|---|
| E006 | Sechs getrennte LP1-Trainings-/Testabschnitte; 1.200 lokale Fehlvarianten; bekannte Schlüssel mit sämtlichen F-Teilmengen | Wahrer Text in 1.105 Fällen höher bewertet; ein Unterbrechungskontrollfall exakt, zwei nicht exakt |
| E007 | 381 primitive Schlüsselzyklen aus bekannten Wörtern, beide Wortreihenfolgen, alle Startphasen, vier Vorzeichen; 83,820 Schlüssel-/Vorzeichenaufgaben, 472,340 Phasen-/Vorzeichenkombinationen | Kein bestätigter Klartext |
| E008 | Primzahlen, p−1 und φ(n); Startoffset 0–255, vier Vorzeichen; 168,960 Start-/Vorzeichenkombinationen | Kein bestätigter Klartext |
| E009 | Gleiche vollständige E007/E008-Suche auf jeweils 39 bedingt zufälligen Fassungen der ausgewählten Seiten LP2-55 und LP2-49 | p=0,25 bzw. 0,95; Bonferroni über 55 Seiten jeweils 1 |
| E010 | Ciphertext-Autokey: Perioden 1–64, vier Vorzeichen, mindestens 60 Runen hinter dem unbekannten Präfix; 13.516 Varianten | Globaler Modellvergleich über 999 Simulationen: p=0,464; synthetischer Kontrolltext exakt wiedergefunden |
| E011 | Plaintext-Autokey: 390 unveränderte Wortschlüssel einschließlich Rückwärtsfassungen, vier Vorzeichen, keine oder sämtliche F-Unterbrechungen; 171.600 Varianten | Ausgewählte LP2-49/55: p=0,15/0,375, seitenkorrigiert jeweils 1; synthetischer Kontrolltext exakt wiedergefunden |

E007 und E008 optimieren **sämtliche Teilmengen der F-Unterbrechungen** exakt
unter dem festgelegten Sprachmodell. F wird bei einer Unterbrechung unverändert
kopiert und verbraucht kein Schlüsselelement. Die Suche vereinigt nur Zustände mit
gleichem Schlüsselzeiger und gleichem Sprachkontext; sie benutzt keinen Beam-Cutoff.
Die kombinatorischen F-Masken sind in den oben genannten Zählungen nicht als
einzeln ausgeführte Versuche gezählt. Das Schema gilt nur für diese konkrete Familie.

E010 berechnet für i≥d die Folge P_i=(a·C_i+b·C_(i−d)) mod29. Das unbekannte
Präfix bleibt ausdrücklich offen. E011 hängt dagegen den gewonnenen Klartext
an den Startschlüssel an. Primitive Zyklusverkürzung wäre dort falsch; deshalb
werden die ursprünglichen 390 Wortschlüssel verwendet, nicht die 381 Vigenère-Zyklen.

## Kontrollen und Interpretation

Das Sprachmodell ist ein normalisiertes Trigramm-Backoff-Modell mit α=0,5 und
Stärke 5. Die Parameter wurden vor der Serie gespeichert. Die bekannte
CIRCUMFERENCE-Unterbrechungsregel wird mit separat trainiertem Modell exakt
gewonnen. Beim DIVINITY-Abschnitt stimmen 98,835 % der Runen; sechs sind falsch.
Auf LP2-56 bevorzugt der Score weiter F an Position 51 statt der richtigen 56.
LP2-56 ist ein bekannter Regressionstest und kein neuer Blindtest.

Die 1.105 von 1.200 erfolgreichen Mutationsvergleichen entsprechen 92,08 %,
sind aber korreliert. Das ist eine deskriptive Diagnose und kein Signifikanztest.
Ein hoher Score allein darf folglich keine Entschlüsselung bestätigen.

Die E009/E011-Vergleichstexte erhalten die exakten Runenhäufigkeiten und die
Zahl direkt benachbarter gleicher Runen. Unabhängige gleichverteilte Mischungen
werden verworfen, bis die Wiederholungszahl passt. Für diese kurzen Seiten ist
dies praktikabel und vermeidet das frühere Problem akzeptierter MCMC-Schritte.
Jeder Vergleich wiederholt die vollständige betreffende Schlüsselsuche;
Bonferroni über 55 Seiten berücksichtigt die Seitenauswahl. 39 Wiederholungen
können nach dieser Korrektur keine Signifikanz unter 0,05 auflösen. Hier dienen
sie zur Prüfung offensichtlicher Scheinbefunde, nicht zum Nachweis einer Lösung.

E010 maximiert in jeder Simulation über sämtliche Seiten, Perioden und
Vorzeichen. Sein symmetrisches Markov-Modell berücksichtigt den allgemeinen
Wiederholungsmangel, aber nicht die exakten Runenhäufigkeiten; die Unsicherheit
des geschätzten Parameters q wird nicht fortgepflanzt. Die Zusatzkorrektur über
die fünf neuen diagnostischen p-Werte wäre ebenfalls überall 1. Es wird keine
globale Entdeckung über die aufeinanderfolgenden Forschungsserien behauptet.

Die vollständigen besten Ausgaben enthalten keinen zusammenhängenden
überzeugenden Klartext. Sie bleiben als Kandidaten mit Rechenregel gespeichert.
Die Negativbefunde grenzen diese festen Suchräume und dieses Sprachmodell ein;
sie schließen Vigenère oder Autokey im Allgemeinen nicht aus.

## Reproduktion und Prüfung

```sh
python scripts/run_attack_phase.py --mode all --budget-seconds 900
python experiments/conditional_attack_null.py --page LP2-55 --seed 330100955
python experiments/conditional_attack_null.py --page LP2-49 --seed 330100949
python experiments/ciphertext_autokey_scan.py
python experiments/plaintext_autokey_attack.py
python scripts/finalize_attack_checkpoint.py
```

Die Runner überspringen identische abgeschlossene Fingerabdrücke mit gültiger
Ergebnisprüfsumme. Parameter, Quellen-Hashes, Seeds und Ergebnisse stehen im
[append-only Experimentprotokoll](../experiment_log.jsonl); vollständige Dateien
sind im [Checkpoint](../checkpoints/attack_phase2_complete.json) referenziert.
Die alten Ergebnisse und der erste Bericht wurden nicht umgeschrieben.

48 Tests bestanden. Zusätzlich wurden 550 gespeicherte Kandidaten
gegen den kanonischen Quelltext unabhängig nachgerechnet, bei vollständigen
Kandidaten auch zurückverschlüsselt. Scores wurden nochmals skalar geprüft.
Das bestätigt die Rechenregeln, **nicht** die sprachliche Richtigkeit der Ausgaben.

Diese Serie umfasst 115 abgeschlossene Prozesse mit zusammen
361.871 Sekunden gemessener Experimentzeit. Jeder Versuch hatte eine
Grenze von 180 Sekunden, die Serie eine Rechengrenze von 900 Sekunden. Simulationen
arbeiten seitenweise bzw. in Blöcken von 128. Die DP hält einen endlichen Zustandsraum
aus Schlüsselzeiger und zwei Runen Kontext; der Sprachcache ist auf 100.000 Einträge
begrenzt. Download-, Test- und Analysezeit sind separat. Keine Hintergrundarbeit läuft.

## Nächste direkte Angriffe

1. Schlüsselverbrauch über vorab quellenbegründete Seitengrenzen hinweg verfolgen,
   insbesondere Primzahl-/Totientfolgen mit F-Unterbrechungen.
2. Laufende Textschlüssel aus eingefrorenen öffentlichen Texten mit festgelegter
   Runenkodierung prüfen; Bücher und Offsetbereiche vor dem Lauf festlegen.
3. Plaintext-Autokey mit unbekannten Startschlüsseln bzw. selektiven F-Masken
   untersuchen, zuerst mit verdeckten synthetischen Schlüsseln kontrollieren.

Die größere Bildprüfung wurde entsprechend der Nutzerpriorität zurückgestellt.
Neue glyphenspezifische Behauptungen erfordern weiterhin die Originalbildprüfung.
