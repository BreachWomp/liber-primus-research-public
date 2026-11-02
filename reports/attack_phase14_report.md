# Vierzehnte Forschungsserie: Gemeinsamer Schlüssel über Seitengrenzen

Stand (UTC): 2026-10-20T20:36:36.732511+00:00. **Keine neue Entschlüsselung bestätigt.**

## Direkter Angriff

E044 prüft zehn bereits gepinnte Seitengruppierungen. Diese sind ausdrücklich
Hypothesen über Chiffregrenzen, keine authentifizierten Abschnitte.
Regel: `P_i=s*C_i+K_j mod29`, s=+1 oder −1; an einer Chiffren-F-Rune kann
alternativ F kopiert werden, ohne den Schlüsselcursor zu erhöhen.
Schlüssel, Cursor und Sprachkontext laufen über die Seitengrenzen weiter.
Alle Seiten und Quellverweise bleiben als exakte Runenoffsets erhalten.
Die Zahlenseite LP2-50 ist als leere Runenspanne enthalten; dass ihre Zahlen
keinen Schlüsselwert verbrauchen, ist eine explizite Modellannahme.

| Gruppe | Runen | Bester penaliserter Score |
|---|---:|---:|
| LP2-00_02 | 729 | -5.959599 |
| LP2-03_07 | 1145 | -6.157623 |
| LP2-08_14 | 1729 | -6.250240 |
| LP2-15_22 | 1903 | -6.247081 |
| LP2-23_26 | 1021 | -6.075823 |
| LP2-27_32 | 1433 | -6.158250 |
| LP2-33_39 | 1680 | -6.234422 |
| LP2-40_53 | 3008 | -6.348909 |
| LP2-54_55 | 308 | -5.334024 |
| LP2-40_55 | 3316 | -6.377496 |

Für Eingaben bis 1024 Runen bleibt der E040-Solver unverändert. Bei längeren
Eingaben erzeugen die ersten und letzten 1024 Runen sowie die drei längsten
F-freien Abschnitte Schlüsselstarts. Perioden 1–16, beide Vorzeichen,
höchstens zwölf zyklisch deduplizierte Starts. Bis zu drei Runden wechseln
Schlüsselkoordinaten-Verbesserung und exakte F-Zeitplanoptimierung ab.
Alle Endbewertungen verwenden den gesamten Abschnitt.
Die Schlüsselsuche ist heuristisch; exakt ist nur die Zeitplanoptimierung
bei festem Schlüssel. Score unverändert:
`mean(logp4) - (primitive_key_length*ln29 + ciphertext_F_count*ln2)/N`.

## Kontrollen und Zufallsvergleich

E043 rekonstruiert drei externe Kontrolltexte mit 3316, 1200 und 1200 Runen
exakt: Klartext, Schlüssel und F-Masken. Schlüssel zufällig mit Längen 5, 8,
13; kein Schlüssel oder Zeitplan wird dem Solver übergeben. Die erste
Kontrolle verwendet die Seitenlängen von LP2-40 bis LP2-55 einschließlich
der leeren Zahlenseite. Die beiden historischen E040-Ergebnisse werden
gegen kanonische LP1-Seiten erneut reproduziert, ohne identische Suchen
zu wiederholen. Das sind Kontrollen und Replikationen, keine neuen LP-Lösungen.
Training auf Emerson I, III–IX (207030 Runen), Kontrollen aus X, XI, XII;
Quellbereiche sind disjunkt, die Kapitel waren historisch bereits vorhanden.
Ein zusätzlicher Kontroll-Nulltext durchläuft die gesamte Suche.

Stärkster unbekannter Abschnitt: **LP2-54_55**, Score
-5.334024, Sprachwertung -5.145597.
Vorzeichen 1, Schlüssel `[14, 18, 0, 25, 8, 21, 18, 25, 13, 12, 11, 19, 17, 18, 2, 18]`,
F-Skips (nullbasierte Offsets im gesamten Abschnitt) `[41, 65, 257, 273]`.
Die Rückverschlüsselung lautet `C_i=s*(P_i-K_j) mod29`, an Skips F.

```text
NHNGMGDOGOICONMNPRCABFDTOEALNGAPTHIAABHILYACOTFNEOGEALPBODNAPLWFTPAEPAYMIFNDJYJOTADOBIACMPONDWDIAATHOEWITHOFEAROEJAMIUIARSYDRPICFJUIISFEPNGCTHUYNOOTHYPWJLANGLYYPOEMEJOEUNNALSPXEBXFIAHNGONMPIETEAENUAILLNEUPFTHEOMCNACGONDLEDFYSWOTARIALJMROEBAUEJOWOUUIDNGELEAWEAFXEINGOOEECCONGRYADIARNGTLUBEOYNGGUFOAHUUNGFITAETHYPSTHFMYYDEOXWIEATHIAEYHOURLORTHEPLEASEYCUEGLEA
```

**Suchausgabe, kein bestätigter Klartext.** Auswahl und Ergebnis-Prüfsummen
wurden vor den Nullversuchen eingefroren. Jeder Nulltext erhält pro Seite
Runenhäufigkeiten, die Zahl gleicher Nachbarpaare und die beiden Randrunen.
Damit bleiben auch Gleichheiten an Seitenübergängen erhalten. Innenpositionen
werden unabhängig gleichverteilt permutiert und bis zur passenden
Nachbarpaarzahl verworfen; maximal 100000 Versuche je Seite.
Jeder Nulltext sucht seine eigenen Fenster, Schlüssel, Phasen und Masken.

**1/19** Nulltexte erreichen mindestens den beobachteten
Score. Plus-eins-p=0.100, Bonferroni10=1.000.
Der Treffer wird durch diesen Vergleich nicht als Lösung gestützt.
19 Replikate reichen nicht zur Auflösung korrigierter Signifikanz.
Die Korrektur gilt für diese Familie mit zehn Gruppen, nicht projektweit.
Überlappende Gruppen sind für die Bonferroni-Schranke zulässig.

## Reproduzierbarkeit und nächster Angriff

100 Tests bestanden. 1764 Zwischen-/Endkandidaten,
420 Schlüsselstarts und 420
Suchverläufe unabhängig skalar geprüft, einschließlich Rückverschlüsselung.
Ein separater Score-Viterbi reproduziert 35
Zeitplanmaxima. Kontrolltexte aus Originalbereichen, Schlüssel und alle
20 neuen Nulltexte aus festen Seeds reproduziert; alle Abhängigkeitshashes stimmen.
30 Aufgaben, 261.961 Sekunden erfolgreiche Experimentzeit;
E044 mit Ablaufaufwand 219.695 Sekunden unter 650.
Phasenbudget 900, je Prozess 180 Sekunden, ein Worker, maximal 4096 Runen.
Keine Quellen verändert, keine Lösungsmeldungen fremder Autoren untersucht.

Nächste direkte Hypothese: derselbe Schlüssel in mehreren Seiten, dessen
Cursor an jeder Seite auf den Anfang zurückgesetzt wird. Das unterscheidet
sich sowohl vom kontinuierlichen Schlüssel hier als auch von getrennten
Seitenschlüsseln in E042. Vor dem unbekannten Material werden feste Parameter
und positive Kontrollen mit solchen Seitenresets benötigt.

[Plan](../experiments/section_key_unknown_plan.json),
[eingefrorene Auswahl](../experiments/section_key_selection.json),
[Messübersicht](../results/phase14_summary.json),
[Checkpoint](../checkpoints/phase14_complete.json).
