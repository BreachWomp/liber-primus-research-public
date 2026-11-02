# Forschungsserie 30: Allgemeine Substitution auf längeren Seiten

Stand UTC: 2026-11-02T16:40:59.828205+00:00. **Keine neue Entschlüsselung bestätigt.**

## E083: Neue prospektive Kontrollen

E081s kurzer Gegenbeleg bleibt unverändert. Diese Serie prüft einen getrennten
Bereich ab 200 Runen. Modell, Wortendmarkierung und Suchverfahren sind unverändert:
höchstens 24 Starts, 40 vollständige 406-Tausch-Sweeps im Zeichenmodell und 40 im
BOS/EOS-Wortmodell. Kein Training auf LP-Texten oder den Kontrollkapiteln X/XI/XII.

Zwölf andere Quellfenster, vier unterschiedliche Absätze je ausgeschlossenem
Kapitel. Zielpräfixe 200/300/500/729 Runen; das letzte Wort bleibt vollständig.
Neue Schlüssel, vorher festgelegte Such-Seeds. Die Texte sind vom Fit getrennt,
aber das Korpus wurde historisch bereits betrachtet. Alle 12 Klartexte sowie
die Abbildung der beobachteten Symbole exakt. Fehlende Symbole sind nicht identifizierbar.
Die drei Kontrollnulls werden mit der gleichen vollständigen Suche bearbeitet;
sie sind Fähigkeitsdiagnostik ohne Signifikanzbehauptung.

| Kontrolle | Tatsächliche Runen | Ergebnis |
|---|---:|---|
| 0 | 204 | exakt |
| 1 | 202 | exakt |
| 2 | 200 | exakt |
| 3 | 302 | exakt |
| 4 | 306 | exakt |
| 5 | 300 | exakt |
| 6 | 502 | exakt |
| 7 | 501 | exakt |
| 8 | 502 | exakt |
| 9 | 729 | exakt |
| 10 | 730 | exakt |
| 11 | 730 | exakt |

## E084: Direkter Angriff und Vergleich

Nach unabhängiger Kontrollprüfung separat registriert: 46 unbekannte LP2-Seiten
mit mindestens 200 Runen. LP2-06/14/15/22/32/49/51/53/55 sind unterhalb der
Längenschwelle; LP2-50 hat keine Runen. Alle zehn ausgeschlossenen Seiten sind
mit Originalinhalt und Grund im Plan erhalten, nicht als entschlüsselt gezählt.
Die originalen lexikalischen Endpunkte stimmen mit dem bestehenden E026-Audit.
Die Quellanker aller 56 Forschungsseiten und zehn gepinnten Quelldateien geprüft.

| Seite | Runen | Höchster Score |
|---|---:|---:|
| LP2-00 | 262 | -8.374165 |
| LP2-01 | 266 | -8.329508 |
| LP2-02 | 201 | -7.593870 |
| LP2-03 | 217 | -7.937095 |
| LP2-04 | 261 | -8.534356 |
| LP2-05 | 263 | -8.172128 |
| LP2-07 | 208 | -7.843328 |
| LP2-08 | 255 | -8.085536 |
| LP2-09 | 268 | -8.184199 |
| LP2-10 | 263 | -8.628011 |
| LP2-11 | 273 | -8.240970 |
| LP2-12 | 261 | -8.629749 |
| LP2-13 | 272 | -8.576536 |
| LP2-16 | 267 | -8.348967 |
| LP2-17 | 273 | -8.776102 |
| LP2-18 | 260 | -8.601251 |
| LP2-19 | 271 | -8.399239 |
| LP2-20 | 269 | -8.585996 |
| LP2-21 | 273 | -8.324868 |
| LP2-23 | 213 | -8.193999 |
| LP2-24 | 270 | -8.622101 |
| LP2-25 | 273 | -8.490720 |
| LP2-26 | 265 | -8.394674 |
| LP2-27 | 234 | -8.006875 |
| LP2-28 | 269 | -8.391627 |
| LP2-29 | 277 | -8.788314 |
| LP2-30 | 263 | -8.376002 |
| LP2-31 | 269 | -8.653233 |
| LP2-33 | 214 | -8.263463 |
| LP2-34 | 261 | -8.394862 |
| LP2-35 | 271 | -8.184933 |
| LP2-36 | 238 | -8.037089 |
| LP2-37 | 228 | -8.298782 |
| LP2-38 | 228 | -7.946292 |
| LP2-39 | 240 | -8.174641 |
| LP2-40 | 231 | -8.290054 |
| LP2-41 | 273 | -8.514098 |
| LP2-42 | 272 | -8.350804 |
| LP2-43 | 274 | -8.094489 |
| LP2-44 | 273 | -8.243901 |
| LP2-45 | 270 | -8.432947 |
| LP2-46 | 270 | -8.649761 |
| LP2-47 | 274 | -8.378877 |
| LP2-48 | 271 | -8.568998 |
| LP2-52 | 263 | -8.445979 |
| LP2-54 | 232 | -8.313762 |

Stärkste Ausgabe **LP2-02**, Score -7.593870.
Seitenwahl und 46 Ergebnishashes vor Nullziehungen eingefroren. Jeder der 19
unabhängigen Nulltexte erhält Randrunen, Häufigkeiten, Wortgrenzen und die Anzahl
gleicher Nachbarpaare; maximal 100.000 Rejection-Vorschläge. Dieselbe vollständige
Schlüsselsuche einschließlich Initialisierung mit demselben seitenbezogenen Seed.
**15/19** erreichen mindestens den beobachteten Score.
Plus-eins-p=0.80, Bonferroni46=1.00.
Mit 19 Nulltexten beträgt bereits der kleinste erreichbare korrigierte Wert 1:
grobes Screening, kein Signifikanznachweis und keine Entschlüsselung.

## Prüfung, Grenzen und Ressourcen

Kontrollen: 257 unabhängige Scores,
99470 letzte Nachbarscores,
245 Rückverschlüsselungen.
Unbekannte Seiten und Nulltexte: 1326 Scores,
538356 letzte Nachbarscores,
1326 Rückverschlüsselungen.
Quellbereiche, Auswahl, Seeds und Nullziehungen geprüft. Der separate Prüfer zählt
Sprachereignisse neu aus den Quellbereichen; GP-Tokenisierung gemeinsam verwendet.
Die gesamte interne Optimierungstrajektorie wurde nicht unabhängig implementiert.
Endliche Heuristik, keine Ausschließung aller 29! Abbildungen. Englisches Prosa-
Modell und Wortgrenzenannahme können andere Klartexte übersehen. E081s kurze
Fehlbewertung bleibt ein dokumentiertes Risiko; keine Übertragung auf kurze Seiten.

Ein erster Start scheiterte **vor Registry und Suche** an einem falsch benannten
Benchmark-Verweis. Auf die vorhandene Phase-29-Validierung korrigiert; ursprüngliches
Fehlerprotokoll erhalten, Wiederholung mit eigenem Log. Keine Chiffrenparameter geändert.

142 Tests bestanden, 80 registrierte abgeschlossene Aufgaben. Experimentzeit
243.626 Sekunden; überwachte Prozesszeit einschließlich Startfehler
295.176 Sekunden bei 1.800 Sekunden Budget. Spitzenwert 170.0 MiB
bei 768 MiB Grenze, ein Worker. Keine laufenden Jobs.

Nächster Ansatz H052: allgemeine Substitution auf modularen Differenzen. E015 deckte nur affine Abbildungen ab. Vor dem Angriff müssen Anfangswert, Seitenrand und Rückverschlüsselung ausdrücklich festgelegt und kontrolliert werden.

[Kontrollplan](../experiments/long_substitution_controls_plan.json),
[Angriffsplan](../experiments/long_substitution_unknown_plan.json),
[Ergebnisse](../results/phase30_summary.json),
[Ausgaben mit Originalgrenzen](phase30_selected_candidates.md).
