# Achtzehnte Forschungsserie: Initialisierung repariert und unbekannte Abschnitte geprüft

Stand (UTC): 2026-10-21T10:42:40.560060+00:00. **Keine neue Liber-Primus-Entschlüsselung bestätigt.**
Die neue Initialisierung löst alle sechs Kontrollen exakt, darunter den zuvor
gescheiterten 31-Runen-Schlüssel. Der unveränderte Solver wurde anschließend
direkt auf neun unbekannte Abschnittsgruppen angewandt.

## E052: Gemeinsame Schlüsselinitialisierung aus Fragmenten

Regel: `P_i = s*C_i + K_j mod29`, Vorzeichen ±1. Eine ausgewählte Chiffren-F
kann unverändert ausgegeben werden, ohne eine Schlüsselstelle zu verbrauchen.
Schlüssel und Sprachkontext laufen durch den gesamten Abschnitt. Nominale
Schlüssellängen 17–32; kürzere primitive Teiler können entstehen.

Zwölf längste F-freie Fragmente ab 16 Runen, jeweils höchstens 256 Runen,
werden gemeinsam ausgewertet. Ihre Schlüsselphasen sind zunächst unabhängig.
Pro Periode und Vorzeichen gibt es 16 feste Starts: alle Phasen null,
Positionen modulo Periode, Positionen abzüglich der halben Zahl vorausgehender
Chiffren-F sowie 13 zufällige Phasenvektoren aus festem Seed. Keine wahren
Schlüssel, Masken oder Längen werden an den Solver übergeben.

Zunächst bis zu 20 Wechsel zwischen exakten Unigramm-Schlüsselkoordinaten
und Phasen. Die zwei besten zyklisch unterschiedlichen Starts pro Familie
erhalten je drei Bigramm- und drei Viergrammrunden mit höchstens sechs
Koordinatendurchläufen. Für jede nominale Länge bleibt der beste Vorzeichen-
Kandidat erhalten; vier weitere Gegenzeichen-Kandidaten ergänzen die Auswahl.
Diese 20 Starts werden auf dem vollständigen Text mit exakter bedingter
F-Zeitplansuche und bis zu drei weiteren Schlüssel-/Zeitplanrunden verfeinert.

Der Volltextscore bleibt `mean(logp4) - (m*ln29 + F_count*ln2)/N`.
Der Poolscore berücksichtigt zusätzlich die freien Fragmentphasen. Seine
Sprachkontexte beginnen an jedem Fragment neu. Nur der Volltextscore bestimmt
die finale Kandidatenrangfolge.

| Prüfung | Kapitel | Schlüssellänge | Runen | Text, Schlüssel, Vorzeichen, F-Maske |
|---|---|---:|---:|---|
| Frisch | X | 17 | 1200 | exakt |
| Frisch | XI | 23 | 1200 | exakt |
| Frisch | XII | 31 | 1200 | exakt |
| Regression | X | 17 | 3316 | exakt |
| Regression | XI | 23 | 1200 | exakt |
| Regression | XII | 31 | 1200 | exakt |

Die frischen Bereiche sind die Kapitelrunen 4000:5200 aus Emerson X, XI, XII.
Die drei Regressionen übernehmen die E049-Eingaben unverändert. Training bleibt
I und III–IX mit 207.030 Runen; Quellbereiche sind disjunkt. Die Kapitel waren
bereits bekannt; dies ist keine historisch blinde Corpusprüfung. Sämtliche
Kontrollen kopieren jede zweite Klartext-F. Die Ergebnisse belegen deshalb
noch keine gleich gute Suche unter jeder beliebigen F-Verteilung.
Die Positivkontrollen umfassen 1200 und 3316 Runen; die Empfindlichkeit für
kürzere Eingaben im erlaubten Bereich ab 512 Runen ist damit nicht separat
kalibriert. Ein negativer Befund auf kurzen Abschnitten ist besonders schwach.

Besonders relevant: Die alte XII-Kontrolle verbessert sich von 59/1200
richtigen Runen in E049 beziehungsweise 78/1200 im adaptiven E051-Versuch
auf **1200/1200**, mit exakt richtigem Schlüssel und Zeitplan. Auch der
unabhängig neu verschlüsselte 31-Runen-Fall wird vollständig rekonstruiert.
Bei der alten XII-Kontrolle enthält noch keiner der gespeicherten Unigramm-,
Bigramm- oder Viergramm-Poolzustände den exakten Schlüssel. Er entsteht erst
bei der anschließenden Volltextoptimierung. Die neue Initialisierung liefert
hier einen ausreichend guten Ausgangspunkt; sie löst den Fall nicht allein.
Ein passender, vollständig neu optimierter diagnostischer Zufallstext hat
Score -5.842628; aus diesem einzelnen Vergleich wird kein
p-Wert abgeleitet. Alle früheren Fehlschläge bleiben unverändert gespeichert.

## E053: Direkter Angriff auf unbekannte Seiten

Nach bestandener unabhängiger Kontrollprüfung wurde ein eigener Plan
registriert: neun E012-Gruppen mit mindestens 512 Runen, unveränderter Solver,
unverändertes Training. LP2-54_55 allein liegt mit 308 Runen außerhalb der
Solvergrenze; beide Seiten sind in LP2-40_55 enthalten. Insgesamt werden alle
55 unbekannten Runenseiten erfasst. Die numerische Seite LP2-50 bleibt als
leerer Runenspanneneintrag erhalten. Die Gruppengrenzen sind Hypothesen und
keine authentifizierten Chiffrengrenzen.

| Abschnitt | Runen | bester primitiver Schlüssel | Score |
|---|---:|---:|---:|
| LP2-00_02 | 729 | 29 | -5.629978 |
| LP2-03_07 | 1145 | 32 | -5.795490 |
| LP2-08_14 | 1729 | 26 | -6.046129 |
| LP2-15_22 | 1903 | 31 | -6.041130 |
| LP2-23_26 | 1021 | 30 | -5.811430 |
| LP2-27_32 | 1433 | 31 | -5.933181 |
| LP2-33_39 | 1680 | 32 | -6.001530 |
| LP2-40_53 | 3008 | 27 | -6.186528 |
| LP2-40_55 | 3316 | 31 | -6.199601 |

Ausgewählt wurde **LP2-00_02** mit Score
**-5.629978**. Die Auswahl wurde vor dem ersten Nulltext
mit den Hashes aller neun beobachteten Ergebnisse eingefroren.

Jeder von 19 Nulltexten erhält seitenweise dieselben Runenhäufigkeiten,
Randrunen und die Anzahl gleicher Nachbarpaare. Der komplette Solver wird
einschließlich sämtlicher Starts, Längen und Vorzeichen neu ausgeführt.
**11 von 19** Nulltexten erreichen mindestens den
beobachteten Score. Roh-p = **0.60**, nach Bonferroni über
neun Abschnittsgruppen **1.00**.

Dieser Vergleich ist ein grobes Screening: Mit 19 Nulltexten kann der
korrigierte Wert niemals unter 0,45 fallen. Bei null Überschreitungen wäre
eine separat registrierte größere Kalibrierung nötig. Keine sprachähnliche
Ausgabe dieses Laufs wird als Entschlüsselung bezeichnet. Das Ergebnis
schließt die Chiffrenfamilie oder beliebige lange Schlüssel nicht aus.

## Unabhängige Prüfung und Ressourcen

111 Tests bestanden. Zusätzlich 36960
skalare Prüfungen gespeicherter Poolzustände und 3266
Volltextzustandsprüfungen einschließlich Rückverschlüsselung;
1120
Fragmentphasen-Maxima separat enumeriert und 35
Volltext-Zeitplanmaxima mit separatem Score-Viterbi bestätigt. Die Top-Auswahl
auf jeder Stufe, Quellbereiche, Zufallsschlüssel, Nulltexte und alle Ergebnis-
und Abhängigkeitshashes wurden nachgerechnet.

35 registrierte Aufgaben, 494.129 Sekunden erfolgreiche
Experimentzeit. Maximal 180 Sekunden je Aufgabe; E052-Budget 1260 Sekunden,
E053-Budget 1200 Sekunden; ein Experimentprozess. Gemessener höchster
abgetasteter Resident-/Private-Speicherwert 117.8 MiB,
Abbruchgrenze 768 MiB. Die Messung erfolgt alle 250 ms und ist kein Beweis
einer exakten kurzfristigen Spitzenbelegung. Originalquellen und historische
Ergebnisse bleiben unverändert; keine weiterlaufenden Forschungsprozesse.

Nächste priorisierte Prüfung: Lange gemeinsame Schlüssel mit eigener Startphase pro Seite prüfen: zuerst frische kurze und lange Kontrolltexte, neue Kontrollphasen und verschiedene F-Ausnahmeverteilungen, danach bei bestandenen Tests direkt die unbekannten Abschnitte.

[Kontrollplan](../experiments/fragment_initialization_plan.json),
[Angriffsplan](../experiments/fragment_initialization_unknown_plan.json),
[Messübersicht](../results/phase18_summary.json),
[Checkpoint](../checkpoints/phase18_complete.json).
