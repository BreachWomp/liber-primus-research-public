# Forschungsserie 25: Beide Koeffizienten erweitert

Stand (UTC): 2026-10-25T17:26:01.790412+00:00. **Keine neue Entschlüsselung bestätigt.**
16 Kontrollen exakt; anschließend46 Einzel-Seiten und 10 Seitengruppen direkt
angegriffen. Keine Community-Lösungsbehauptungen untersucht.

## E068: Umfang und Kalibrierung

Die Regel lautet `P_i=a*C_i+b*P_(i-m) mod29`, jetzt mit beiden Koeffizienten
`a,b=1..28` und `m=4..32`. Die Rückverschlüsselung braucht das Inverse von a,
der Anfangsschlüssel das Inverse von b. Der negative Faktor -1 wird als 28 gespeichert.
Die affine Algebra und frühere Tests kurzer Verzögerungen sind keine neue Entdeckung.

22.736 Familien werden pro Eingabe bewertet. Pro Schlüssellänge bleiben8 von784
Koeffizientenpaaren erhalten; für232 Familien folgen die festgelegten Suchbudgets
aus E066. Die Vorauswahl verwendet Häufigkeitstabellen: Multiplizieren mit a
permutiert die 29 möglichen Präfixwerte. Dadurch kann dieselbe Unigramm-Bewertung
schneller berechnet werden. Die unabhängige Prüfung zählt keine solchen Tabellen,
sondern setzt die Symbole direkt in die Formel ein. Bewertungsdifferenzen müssen
unter 1e-7 liegen. Die Rangfolge verwendet auf 9 Nachkommastellen gerundete Scores,
danach die vorab festgelegte Reihenfolge. Es bleibt eine heuristische Suche.
Die größere Parameterliste garantiert keinen höheren Score auf jeder Eingabe:
Die begrenzte Vorauswahl kann frühere Familien verwerfen, und neue feste Seeds
können andere lokale Maxima liefern. Frühere Ergebnisse bleiben separat erhalten.

Zwölf neue Schlüssel verschlüsseln bereits betrachtete, vom Training ausgeschlossene
Emerson-Abschnitte mit 200/300/729/3.316 Runen. Vier E066-Eingaben sind Regressionen
für den geänderten Algorithmus. Alle 16 liefern den vollständigen Klartext sowie
Schlüssel und Koeffizienten exakt. Ein vollständiger diagnostischer Nulllauf erreicht
-4.263207; daraus wird kein p-Wert berechnet.

| Kontrolle | Runen | m | a | b | Vorauswahlrang | Ergebnis |
|---|---:|---:|---:|---:|---:|---|
| 0 | 200 | 13 | 2 | 3 | 1 | exakt |
| 1 | 200 | 23 | 7 | 8 | 1 | exakt |
| 2 | 200 | 31 | 14 | 15 | 1 | exakt |
| 3 | 300 | 13 | 27 | 3 | 1 | exakt |
| 4 | 300 | 23 | 2 | 8 | 1 | exakt |
| 5 | 300 | 31 | 7 | 15 | 1 | exakt |
| 6 | 729 | 13 | 14 | 3 | 1 | exakt |
| 7 | 729 | 23 | 27 | 8 | 1 | exakt |
| 8 | 729 | 31 | 2 | 15 | 1 | exakt |
| 9 | 3316 | 13 | 7 | 3 | 1 | exakt |
| 10 | 3316 | 23 | 14 | 8 | 1 | exakt |
| 11 | 3316 | 32 | 27 | 15 | 1 | exakt |
| 12 | 200 | 31 | 1 | 14 | 1 | exakt |
| 13 | 300 | 31 | 28 | 7 | 1 | exakt |
| 14 | 729 | 31 | 1 | 2 | 1 | exakt |
| 15 | 3316 | 31 | 28 | 27 | 1 | exakt |

## E069: Originaltexte und passende Nulltexte

46 einzelne LP2-Seiten ab 200 Runen und 10 bestehende Seitengruppen bilden 56
Eingabehypothesen. Die Gruppen vertreten alle 55 unbekannten Runenseiten; sie
sind keine bestätigten Chiffrengrenzen. In Gruppen läuft der Schlüsselstrom
über Seitenwechsel fort. LP2-50 bleibt mit Quellreferenzen als leere Runenspanne
erhalten; ihre Zahlen werden nicht entschlüsselt.

| Eingabe | Runen | m | a | b | Score |
|---|---:|---:|---:|---:|---:|
| LP2-00 | 262 | 32 | 13 | 11 | -4.080898 |
| LP2-01 | 266 | 32 | 7 | 13 | -4.168375 |
| LP2-02 | 201 | 32 | 24 | 13 | -3.626664 |
| LP2-03 | 217 | 31 | 16 | 13 | -3.906549 |
| LP2-04 | 261 | 29 | 13 | 11 | -4.110637 |
| LP2-05 | 263 | 32 | 21 | 11 | -4.152556 |
| LP2-07 | 208 | 30 | 2 | 14 | -3.753534 |
| LP2-08 | 255 | 32 | 18 | 3 | -4.088323 |
| LP2-09 | 268 | 32 | 14 | 23 | -4.222930 |
| LP2-10 | 263 | 32 | 1 | 18 | -4.051974 |
| LP2-11 | 273 | 32 | 25 | 8 | -4.101359 |
| LP2-12 | 261 | 32 | 1 | 4 | -4.070675 |
| LP2-13 | 272 | 32 | 17 | 6 | -4.167353 |
| LP2-16 | 267 | 32 | 27 | 4 | -4.218172 |
| LP2-17 | 273 | 31 | 22 | 7 | -4.164952 |
| LP2-18 | 260 | 31 | 14 | 26 | -3.972368 |
| LP2-19 | 271 | 32 | 21 | 7 | -4.106423 |
| LP2-20 | 269 | 32 | 9 | 9 | -4.206273 |
| LP2-21 | 273 | 32 | 25 | 5 | -4.097373 |
| LP2-23 | 213 | 31 | 8 | 17 | -3.868836 |
| LP2-24 | 270 | 32 | 23 | 10 | -4.131706 |
| LP2-25 | 273 | 32 | 2 | 11 | -4.199825 |
| LP2-26 | 265 | 32 | 27 | 4 | -4.214270 |
| LP2-27 | 234 | 32 | 22 | 22 | -3.951126 |
| LP2-28 | 269 | 31 | 14 | 3 | -4.188659 |
| LP2-29 | 277 | 30 | 14 | 3 | -4.140196 |
| LP2-30 | 263 | 32 | 7 | 6 | -4.142521 |
| LP2-31 | 269 | 32 | 10 | 24 | -4.171938 |
| LP2-33 | 214 | 32 | 7 | 14 | -3.776675 |
| LP2-34 | 261 | 30 | 21 | 5 | -4.043842 |
| LP2-35 | 271 | 31 | 14 | 7 | -4.188216 |
| LP2-36 | 238 | 30 | 16 | 4 | -3.973433 |
| LP2-37 | 228 | 31 | 4 | 6 | -3.945966 |
| LP2-38 | 228 | 32 | 9 | 22 | -3.866804 |
| LP2-39 | 240 | 32 | 26 | 17 | -3.990545 |
| LP2-40 | 231 | 32 | 25 | 22 | -3.945449 |
| LP2-41 | 273 | 31 | 26 | 8 | -4.147062 |
| LP2-42 | 272 | 32 | 10 | 7 | -4.155618 |
| LP2-43 | 274 | 32 | 13 | 19 | -4.201716 |
| LP2-44 | 273 | 32 | 12 | 4 | -4.255692 |
| LP2-45 | 270 | 32 | 1 | 26 | -4.259561 |
| LP2-46 | 270 | 32 | 27 | 23 | -4.186894 |
| LP2-47 | 274 | 32 | 23 | 6 | -4.223040 |
| LP2-48 | 271 | 32 | 23 | 6 | -4.189409 |
| LP2-52 | 263 | 32 | 26 | 19 | -4.171327 |
| LP2-54 | 232 | 32 | 21 | 7 | -3.941735 |
| LP2-00_02 | 729 | 31 | 4 | 27 | -5.290033 |
| LP2-03_07 | 1145 | 32 | 15 | 14 | -5.639260 |
| LP2-08_14 | 1729 | 32 | 4 | 16 | -5.885758 |
| LP2-15_22 | 1903 | 32 | 15 | 4 | -5.939762 |
| LP2-23_26 | 1021 | 32 | 7 | 21 | -5.563707 |
| LP2-27_32 | 1433 | 32 | 21 | 15 | -5.821308 |
| LP2-33_39 | 1680 | 32 | 7 | 25 | -5.924589 |
| LP2-40_53 | 3008 | 32 | 8 | 5 | -6.192441 |
| LP2-54_55 | 308 | 30 | 19 | 10 | -4.377280 |
| LP2-40_55 | 3316 | 32 | 22 | 19 | -6.225445 |

Stärkste Eingabe: **LP2-02**, Score -3.626664.
Auswahl und alle 56 Ergebnishashes wurden vor den ersten 19 Nullversuchen fixiert.
Keiner dieser 19 Nullscores übertraf die Auswahl; die separat registrierte
Nachprüfung E070 ergänzt daher 99 frische Nulltexte. Die ursprünglichen
Ergebnisse bleiben unverändert erhalten.
Jeder Nulltext erhält pro Seite Häufigkeiten, Randrunen und die Zahl gleicher
Nachbarn und durchläuft die vollständige Vorauswahl und Optimierung.
**5/99 frische** Nullscores erreichen mindestens den beobachteten Wert.
Plus-eins-p=0.06; Bonferroni56=1.00.
Die p-Werte verwenden ausschließlich die 99 frischen Vergleiche. Die ersten 19
werden nicht zu einem adaptiv gestoppten p-Wert zusammengelegt. Der kleinste
mögliche korrigierte Wert dieser Nachprüfung beträgt 0,56.
Dies ist ein grober Vergleich, kein Signifikanznachweis mit ausreichender Auflösung.
Eine Nulltrefferzahl von null verlangt eine gesondert registrierte größere Kalibrierung.

## Validierung und Grenzen

Unabhängige Quellenrekonstruktion, modulare Warteschlangen, Rückverschlüsselung,
direkte Familienbewertung, Kandidatenscores, Koordinatenmaxima und Seitenübergänge
sind geprüft. Alle 732.540 Sprachmodell-Tabelleneinträge wurden durch separate
skalare Wahrscheinlichkeitsrechnung kontrolliert; Sequenzscores wurden zusätzlich
an sechs Längen mit zwei Modellordnungen gegengeprüft. Alle 354496 Startpräfixe wurden aus den Seeds
reproduziert. 131 Tests bestanden; insbesondere alle 784 Koeffizientenpaare
an zwei Verzögerungen und Histogramm-Bewertungen gegen direkte Enumeration.

191 registrierte Aufgaben, 3004.272 Sekunden erfolgreiche Experimentzeit;
höchster abgetasteter Prozessspeicher 165.0 MiB.
Budget 3.600 Sekunden Experimentzeit, 180 pro Aufgabe, 768 MiB, ein Worker.
Validierungszeiten stehen zusätzlich in den Prüfdateien. Keine laufenden Jobs.
Quellbytes, alte Programme und historische Ergebnisse bleiben unverändert.
Die Kontrollen beweisen keine vollständige Suche über alle Schlüssel, Texte oder Grenzen.

Nächster ungetesteter Schritt: eine begrenzte Erweiterung um eine additive Konstante, einschließlich Sonderfall b=1, zuerst an Kontrollen.

[Kontrollplan](../experiments/bilinear_feedback_plan.json),
[Angriffsplan](../experiments/bilinear_feedback_unknown_plan.json),
[Plan der frischen Nullversuche](../experiments/bilinear_feedback_more_null_plan.json),
[Messübersicht](../results/phase25_summary.json),
[Kandidat mit Originalgrenzen](phase25_selected_candidate.md),
[Checkpoint](../checkpoints/phase25_complete.json).
