# Forschungsserie 26: Additive Konstante in verzögerter Rückkopplung

Stand UTC: 2026-10-31T12:14:43.995412+00:00. **Keine neue Entschlüsselung bestätigt.**

## Mechanismus und E071

`P_i=a*C_i+b*P_(i-m)+c mod29`, a,b1..28,c0..28,m4..32.
Der Anfangsschlüssel ist `(P-a*C-c)/b`, die Rückverschlüsselung `(P-b*queue-c)/a`.
Für b ungleich 1 gilt mit d=c/(1-b): `P_i=a*(base1_i+b^q*t_r)+d`.
Für b=1 gilt `P_i=a*(base1_i+t_r)+q*c`, q=floor(i/m).
Damit bleiben alle Anfangswerte vertreten. Die Sprachbewertung muss d bzw. q*c
berücksichtigen; diese Fälle waren nicht bereits durch c=0 erledigt.
Die affine Umparametrisierung ist keine mathematische Neuentdeckung.

E071 prüft 27608 Familien unabhängig durch direkte
Warteschlangen; maximale Abweichung 1.14e-13.
Die vollständige Vorauswahl auf 3.316 synthetischen Runen benötigt
3.963 Sekunden. Pro Eingabe werden 659.344 Familien
bewertet und pro Verzögerung 8 von 22.736 behalten. Danach folgen 232 heuristische
Optimierungen und 12 Viergramm-Verfeinerungen mit festen Seeds.

## E072: Kontrollen

Alle 16 Klartexte, Schlüssel und a/b/c-Werte exakt. Zwölf neue Schlüssel und
Konstanten verwenden bereits betrachtete, vom Training ausgeschlossene
Emerson-Blöcke; vier E068-Eingaben prüfen die geänderte Suche bei c=0.
Vier frische Fälle decken b=1 ab. Es handelt sich nicht um 16 unbekannte Testtexte.
Der diagnostische Nulltext erreicht -4.318019; daraus folgt kein p-Wert.

| Kontrolle | Runen | m | a | b | c | Vorauswahlrang | Ergebnis |
|---|---:|---:|---:|---:|---:|---:|---|
| 0 | 200 | 13 | 2 | 1 | 2 | 1 | exakt |
| 1 | 200 | 23 | 7 | 3 | 7 | 1 | exakt |
| 2 | 200 | 31 | 14 | 15 | 12 | 3 | exakt |
| 3 | 300 | 13 | 27 | 1 | 17 | 1 | exakt |
| 4 | 300 | 23 | 2 | 3 | 22 | 1 | exakt |
| 5 | 300 | 31 | 7 | 15 | 27 | 1 | exakt |
| 6 | 729 | 13 | 14 | 1 | 4 | 1 | exakt |
| 7 | 729 | 23 | 27 | 3 | 9 | 1 | exakt |
| 8 | 729 | 31 | 2 | 15 | 14 | 1 | exakt |
| 9 | 3316 | 13 | 7 | 1 | 19 | 1 | exakt |
| 10 | 3316 | 23 | 14 | 3 | 24 | 1 | exakt |
| 11 | 3316 | 32 | 27 | 15 | 1 | 1 | exakt |
| 12 | 200 | 13 | 2 | 3 | 0 | 1 | exakt |
| 13 | 300 | 13 | 27 | 3 | 0 | 1 | exakt |
| 14 | 729 | 13 | 14 | 3 | 0 | 1 | exakt |
| 15 | 3316 | 32 | 27 | 15 | 0 | 1 | exakt |

## E073: Direkter Angriff

46 Einzel-Seiten und 10 bestehende Seitengruppen; alle 55 unbekannten Runenseiten
sind vertreten. Gruppen und Seitenstarts sind hypothetische Chiffrengrenzen.
Innerhalb einer Gruppe läuft der Zustand ohne Reset weiter. Die Zahlenseite
LP2-50 bleibt in der Quellenfolge als leere Runenspanne erhalten.

| Eingabe | Runen | m | a | b | c | Score |
|---|---:|---:|---:|---:|---:|---:|
| LP2-00 | 262 | 32 | 9 | 7 | 9 | -4.049275 |
| LP2-01 | 266 | 32 | 27 | 10 | 23 | -4.079168 |
| LP2-02 | 201 | 31 | 19 | 23 | 2 | -3.664221 |
| LP2-03 | 217 | 31 | 1 | 22 | 24 | -3.817342 |
| LP2-04 | 261 | 30 | 26 | 16 | 14 | -4.110784 |
| LP2-05 | 263 | 32 | 11 | 27 | 22 | -4.115219 |
| LP2-07 | 208 | 32 | 1 | 2 | 5 | -3.698106 |
| LP2-08 | 255 | 31 | 27 | 2 | 10 | -4.032793 |
| LP2-09 | 268 | 32 | 19 | 15 | 25 | -4.046354 |
| LP2-10 | 263 | 31 | 19 | 3 | 28 | -4.097870 |
| LP2-11 | 273 | 32 | 19 | 11 | 21 | -4.211309 |
| LP2-12 | 261 | 32 | 13 | 6 | 11 | -4.131152 |
| LP2-13 | 272 | 32 | 8 | 5 | 16 | -4.134329 |
| LP2-16 | 267 | 32 | 18 | 16 | 25 | -3.983963 |
| LP2-17 | 273 | 29 | 21 | 3 | 6 | -4.186698 |
| LP2-18 | 260 | 31 | 13 | 2 | 26 | -3.973263 |
| LP2-19 | 271 | 32 | 28 | 11 | 9 | -4.215476 |
| LP2-20 | 269 | 32 | 3 | 4 | 25 | -4.087657 |
| LP2-21 | 273 | 32 | 24 | 27 | 11 | -4.178508 |
| LP2-23 | 213 | 31 | 2 | 7 | 24 | -3.744365 |
| LP2-24 | 270 | 32 | 9 | 15 | 7 | -4.112038 |
| LP2-25 | 273 | 31 | 4 | 14 | 11 | -4.208061 |
| LP2-26 | 265 | 29 | 7 | 6 | 21 | -4.181734 |
| LP2-27 | 234 | 32 | 11 | 9 | 15 | -3.869667 |
| LP2-28 | 269 | 32 | 4 | 8 | 15 | -4.076173 |
| LP2-29 | 277 | 30 | 20 | 22 | 26 | -4.242052 |
| LP2-30 | 263 | 31 | 21 | 5 | 15 | -4.040406 |
| LP2-31 | 269 | 32 | 11 | 2 | 9 | -4.145374 |
| LP2-33 | 214 | 31 | 7 | 5 | 8 | -3.866210 |
| LP2-34 | 261 | 32 | 15 | 25 | 17 | -4.136165 |
| LP2-35 | 271 | 32 | 25 | 27 | 20 | -4.175975 |
| LP2-36 | 238 | 32 | 11 | 15 | 13 | -3.926530 |
| LP2-37 | 228 | 31 | 27 | 15 | 28 | -3.891313 |
| LP2-38 | 228 | 32 | 25 | 16 | 9 | -3.977079 |
| LP2-39 | 240 | 31 | 28 | 21 | 10 | -4.005729 |
| LP2-40 | 231 | 29 | 1 | 24 | 1 | -3.941308 |
| LP2-41 | 273 | 31 | 4 | 18 | 19 | -4.149683 |
| LP2-42 | 272 | 30 | 22 | 4 | 18 | -4.186535 |
| LP2-43 | 274 | 31 | 25 | 19 | 13 | -4.210248 |
| LP2-44 | 273 | 30 | 14 | 14 | 10 | -4.171097 |
| LP2-45 | 270 | 31 | 10 | 20 | 5 | -4.169674 |
| LP2-46 | 270 | 32 | 3 | 6 | 25 | -4.224878 |
| LP2-47 | 274 | 32 | 8 | 2 | 18 | -4.174121 |
| LP2-48 | 271 | 32 | 7 | 23 | 13 | -4.130169 |
| LP2-52 | 263 | 30 | 27 | 7 | 2 | -4.176117 |
| LP2-54 | 232 | 31 | 27 | 2 | 9 | -3.904587 |
| LP2-00_02 | 729 | 32 | 2 | 2 | 2 | -5.266653 |
| LP2-03_07 | 1145 | 32 | 14 | 3 | 25 | -5.613541 |
| LP2-08_14 | 1729 | 32 | 23 | 4 | 24 | -5.910717 |
| LP2-15_22 | 1903 | 31 | 24 | 16 | 22 | -5.956971 |
| LP2-23_26 | 1021 | 31 | 16 | 4 | 6 | -5.545311 |
| LP2-27_32 | 1433 | 32 | 18 | 26 | 19 | -5.747922 |
| LP2-33_39 | 1680 | 31 | 25 | 20 | 20 | -5.894594 |
| LP2-40_53 | 3008 | 32 | 5 | 6 | 23 | -6.159527 |
| LP2-54_55 | 308 | 32 | 21 | 9 | 9 | -4.257299 |
| LP2-40_55 | 3316 | 32 | 28 | 13 | 3 | -6.196766 |

Stärkste Eingabe **LP2-02**, Score -3.664221.
Auswahl und alle 56 Ergebnishashes wurden vor den Nullversuchen fixiert.
Jeder Nulltext erhält seitenweise Häufigkeiten, Randrunen und die Zahl gleicher
Nachbarn und durchläuft den ganzen Optimierer. **3/19**
Nullscores mindestens so hoch; Plus-eins-p=0.20,
Bonferroni56=1.00. Mit 19 Nulltexten beträgt der kleinste
korrigierte Wert bereits 1: ein grober Vergleich, kein Signifikanznachweis.
Die Auswahl liefert keine belastbare sprachliche Evidenz über dieses Nullmodell hinaus.

## Prüfung und Grenzen

Quellbereiche, Schlüssel-Seeds, skalare Warteschlangen, Rückverschlüsselungen,
Kandidatenscores, Koordinatenmaxima und durchgehende Seitenzustände geprüft.
Alle 56 LP2-Forschungsseiten sind als wörtliche Layout-Abschnitte in den gespeicherten
Quellen verankert; die Prüfsummen aller 10 zugehörigen Quelldateien stimmen.
Die 732.540 Sprachmodell-Einträge sind separat durch skalare Wahrscheinlichkeiten
kontrolliert. Pro Angriff wurden sämtliche 232 behaltenen Familien sowie bei
Kontrollen die injizierte Familie direkt nachgerechnet. Die 659.344 vollständigen
Vorauswahlscores wurden mit dem Produktionsverfahren reproduziert; das ist
Replikation, keine zweite unabhängige Vollgitter-Implementierung. E071 liefert
die separate direkte Prüfung an 27.608 synthetischen Familien.

Die Suche behält nur 8 Familien je Verzögerung. Kontroll-Erfolge beweisen keine
Vollständigkeit. Ein größerer Parameterraum garantiert bei begrenzter Vorauswahl
keinen höheren Score als ältere Suchen. Keine ausgelassenen Runen oder unbekannten
Resets gesucht. Ein negatives heuristisches Ergebnis widerlegt die Chiffrenfamilie nicht.
Das Sprachmodell stammt aus englischer Emerson-Prosa; andere Sprachen, Zahlenfolgen
oder nichtsprachliche Klartexte werden durch diesen Angriff nicht zuverlässig erkannt.

136 Tests bestanden; 93 registrierte Aufgaben; 1983.962 Sekunden
erfolgreiche Experimentzeit bei 3.600 Sekunden Budget. E072/E073 höchster
abgetasteter Speicher 139.4 MiB, Grenze 768 MiB, ein Suchworker.
E071 hatte einen kooperativen 120-Sekunden-Deckel und begrenzte Arraygrößen;
für diesen Vorlauf wurde kein Betriebssystem-Speichermaximum aufgezeichnet.
Prüfzeiten sind gesondert in den Validierungsdateien enthalten. Keine laufenden Jobs.

Eine Dateinamenskollision mit dem historischen E019-Plan und dessen Testdatei
wurde entdeckt und bytegenau aus Git wiederhergestellt. Die tatsächlich von
E072 verwendeten Plan-/Runnerbytes sind separat archiviert. Kein früheres
Ergebnis und kein Experimentlog-Eintrag wurde umgeschrieben.
[Zuordnung und Reproduktionshinweis](../checkpoints/phase26_path_migration.json).

Nächste Priorität: Die noch offene Verzögerung von drei Runen untersuchen. Die neue Reduktion könnte eine begrenzte Suche ermöglichen; zuerst sind Kontrollen und ein Laufzeitbenchmark erforderlich. Dies ist noch ungetestet.

[Kontrollplan](../experiments/delayed_affine_feedback_plan.json),
[Angriffsplan](../experiments/affine_feedback_unknown_plan.json),
[Messübersicht](../results/phase26_summary.json),
[Kandidat mit Originalgrenzen](phase26_selected_candidate.md).
