# Forschungsserie 27: Rückkopplung mit drei Runen Verzögerung

Stand UTC: 2026-11-01T09:06:01.671314+00:00. **Keine neue Entschlüsselung bestätigt.**

## E074/E075: Verfahren und Kontrollen

`P_i=a*C_i+b*P_(i-3)+c mod29`, a,b=1..28,c=0..28.
Die bekannte affine Reduktion bewertet 22.736 Parameterfamilien nach Unigrammen.
16 bleiben erhalten. Für jede davon werden sämtliche 29³ = 24.389
Anfangspräfixe gegen das unveränderte externe Viergramm-Modell bewertet.
Diese Präfixsuche ist exakt; die Auswahl der Parameterfamilien ist es nicht.
Es gibt keine ausgelassenen Runen oder versteckten Resets.

E074 vergleicht 73.167 Präfixscores mit einer getrennten skalaren Rekursion;
der längste Durchsatztest mit 3.316 Zufallsrunen dauert rund 36 Sekunden.
Die zwölf neuen kurzen Kontrollen verwenden 66/95/200/300 Runen aus bereits
betrachteten, vom Training ausgeschlossenen Emerson-Blöcken. Vier neue
Verschlüsselungen bei c=0 prüfen 200/300/729/3.316 Runen und die alten Vorzeichenpaare.
Die Schlüssel sind neu; die Textausschnitte sind teilweise verschachtelt und
keine 16 unabhängigen unbekannten Texte. Alle Klartexte, Schlüssel und a/b/c-Werte exakt.
Diagnostischer Kontroll-Nullscore -5.079480, ohne p-Wert.

| Kontrolle | Runen | a | b | c | Vorauswahlrang | Ergebnis |
|---|---:|---:|---:|---:|---:|---|
| 0 | 66 | 2 | 1 | 2 | 1 | exakt |
| 1 | 66 | 7 | 3 | 7 | 1 | exakt |
| 2 | 66 | 14 | 15 | 12 | 1 | exakt |
| 3 | 95 | 27 | 28 | 17 | 1 | exakt |
| 4 | 95 | 2 | 1 | 22 | 1 | exakt |
| 5 | 95 | 7 | 3 | 27 | 1 | exakt |
| 6 | 200 | 14 | 15 | 4 | 1 | exakt |
| 7 | 200 | 27 | 28 | 9 | 1 | exakt |
| 8 | 200 | 2 | 1 | 14 | 1 | exakt |
| 9 | 300 | 7 | 3 | 19 | 1 | exakt |
| 10 | 300 | 14 | 15 | 24 | 1 | exakt |
| 11 | 300 | 27 | 28 | 1 | 1 | exakt |
| 12 | 200 | 1 | 1 | 0 | 1 | exakt |
| 13 | 300 | 1 | 28 | 0 | 1 | exakt |
| 14 | 729 | 28 | 1 | 0 | 1 | exakt |
| 15 | 3316 | 28 | 28 | 0 | 1 | exakt |

## E076: Alle unbekannten Runenseiten einzeln

55 Seiten einschließlich der kurzen Abschnitte direkt geprüft. LP2-50 bleibt
mit Originalinhalt und Quellenreferenzen im Plan erhalten, ohne Runenangriff.
Das Seitenlayout aller 56 Forschungsseiten ist wörtlich in den gepinnten
Quelldateien verankert; alle zehn zugehörigen Dateihashes stimmen.

| Seite | Runen | a | b | c | Score |
|---|---:|---:|---:|---:|---:|
| LP2-00 | 262 | 19 | 12 | 20 | -5.841415 |
| LP2-01 | 266 | 8 | 20 | 8 | -5.949304 |
| LP2-02 | 201 | 2 | 7 | 3 | -5.613873 |
| LP2-03 | 217 | 3 | 16 | 28 | -5.729440 |
| LP2-04 | 261 | 4 | 14 | 24 | -5.844781 |
| LP2-05 | 263 | 24 | 24 | 21 | -5.879382 |
| LP2-06 | 196 | 1 | 20 | 0 | -5.575591 |
| LP2-07 | 208 | 3 | 11 | 25 | -5.822003 |
| LP2-08 | 255 | 23 | 10 | 0 | -5.926910 |
| LP2-09 | 268 | 24 | 26 | 1 | -5.927997 |
| LP2-10 | 263 | 17 | 12 | 22 | -5.895116 |
| LP2-11 | 273 | 21 | 8 | 3 | -5.827590 |
| LP2-12 | 261 | 20 | 3 | 15 | -5.967409 |
| LP2-13 | 272 | 4 | 15 | 25 | -5.885759 |
| LP2-14 | 137 | 8 | 5 | 22 | -5.437004 |
| LP2-15 | 159 | 21 | 17 | 16 | -5.637875 |
| LP2-16 | 267 | 12 | 25 | 9 | -5.664610 |
| LP2-17 | 273 | 6 | 15 | 20 | -5.866045 |
| LP2-18 | 260 | 14 | 7 | 14 | -5.926975 |
| LP2-19 | 271 | 9 | 7 | 9 | -5.873445 |
| LP2-20 | 269 | 21 | 15 | 18 | -5.873747 |
| LP2-21 | 273 | 24 | 25 | 26 | -5.872333 |
| LP2-22 | 131 | 13 | 24 | 5 | -5.389070 |
| LP2-23 | 213 | 9 | 4 | 22 | -5.680699 |
| LP2-24 | 270 | 17 | 2 | 4 | -5.867857 |
| LP2-25 | 273 | 26 | 26 | 9 | -5.915938 |
| LP2-26 | 265 | 14 | 5 | 4 | -5.940363 |
| LP2-27 | 234 | 26 | 16 | 22 | -5.818414 |
| LP2-28 | 269 | 21 | 16 | 21 | -5.846769 |
| LP2-29 | 277 | 12 | 18 | 7 | -5.940384 |
| LP2-30 | 263 | 17 | 28 | 18 | -5.936974 |
| LP2-31 | 269 | 20 | 10 | 21 | -5.951627 |
| LP2-32 | 121 | 22 | 10 | 19 | -5.465029 |
| LP2-33 | 214 | 9 | 16 | 26 | -5.833597 |
| LP2-34 | 261 | 2 | 14 | 21 | -5.841120 |
| LP2-35 | 271 | 27 | 19 | 13 | -5.893688 |
| LP2-36 | 238 | 25 | 6 | 0 | -5.830767 |
| LP2-37 | 228 | 14 | 11 | 23 | -5.862702 |
| LP2-38 | 228 | 20 | 8 | 12 | -5.756881 |
| LP2-39 | 240 | 3 | 23 | 20 | -5.891836 |
| LP2-40 | 231 | 9 | 20 | 8 | -5.860458 |
| LP2-41 | 273 | 1 | 7 | 13 | -5.862887 |
| LP2-42 | 272 | 22 | 19 | 16 | -6.006777 |
| LP2-43 | 274 | 22 | 14 | 17 | -5.923317 |
| LP2-44 | 273 | 22 | 14 | 0 | -5.971032 |
| LP2-45 | 270 | 9 | 1 | 6 | -5.948426 |
| LP2-46 | 270 | 17 | 15 | 25 | -5.975992 |
| LP2-47 | 274 | 3 | 1 | 21 | -5.896238 |
| LP2-48 | 271 | 11 | 13 | 12 | -5.848145 |
| LP2-49 | 66 | 17 | 18 | 20 | -4.762790 |
| LP2-51 | 92 | 9 | 22 | 16 | -5.086863 |
| LP2-52 | 263 | 9 | 9 | 10 | -5.894641 |
| LP2-53 | 179 | 8 | 28 | 11 | -5.621518 |
| LP2-54 | 232 | 28 | 13 | 6 | -5.862804 |
| LP2-55 | 76 | 8 | 3 | 3 | -4.709924 |

Stärkste Seite **LP2-55**, Score -4.709924.
Auswahl und alle 55 Ergebnishashes wurden vor den Nullversuchen fixiert.
19 unabhängig erzeugte Nulltexte erhalten Häufigkeiten, Randrunen und gleiche
Nachbarpaare. Sie durchlaufen dieselbe vollständige Vorauswahl und Präfixsuche.
**1/19** erzielen mindestens denselben Score:
Plus-eins-p=0.10, Bonferroni55=1.00.
Der kleinste korrigierte p-Wert mit 19 Nulltexten beträgt bereits 1.
Das ist ein grober Vergleich, kein Signifikanznachweis.

## Validierung und Grenzen

Eine zweite Implementierung berechnet die Klartexte als explizite Warteschlangen,
ohne die affine Formel des Suchprogramms. Alle 35.900.608 Präfixscores der
92 Suchläufe stimmen einschließlich ihrer vollständigen Vektor-Prüfsummen.
Sämtliche behaltenen Familienoptima, Quellbereiche, Schlüssel-Seeds, Kandidaten,
Rückverschlüsselungen, Nullziehungen und die Auswahl wurden geprüft.
Die Sprachmodelltabellen sind separat gegen skalare Wahrscheinlichkeiten kontrolliert.
Die vollständige Unigramm-Vorauswahl wurde reproduziert; direkt nachgerechnet
wurden die behaltenen Familien und die Kontrollfamilien. Vollständige
Scorevektor-Prüfung bedeutet keine unabhängige Vollgitter-Prüfung der Vorauswahl.

Die verworfenen 22.720 Familien bleiben außerhalb der exakten Präfixsuche.
Das negative Ergebnis schließt die Chiffrenklasse nicht aus. Der englische
Prosa-Score kann andere Sprachen oder nichtsprachliche Klartexte übersehen.
Die affine Algebra ist keine Neuentdeckung; E025 und die früheren Verzögerungen
bleiben historische Ergebnisse und werden nicht als neue Entschlüsselungen gezählt.

138 Tests bestanden; 92 registrierte Aufgaben; 349.583 Sekunden
Experimentzeit bei 1.800 Sekunden Budget; höchster abgetasteter Speicher
134.6 MiB bei 768 MiB Grenze, ein Suchworker.
Prüfzeiten stehen gesondert in den Validierungsdateien. Keine laufenden Jobs.

Als nächste ungetestete Lücke folgt Verzögerung zwei mit einer von null verschiedenen Konstante, zunächst mit Laufzeitbenchmark und Kontrollen.

[Plan](../experiments/delay_three_plan.json),
[Angriffsplan](../experiments/delay_three_unknown_plan.json),
[Ergebnisse](../results/phase27_summary.json),
[Ausgabe mit Originalgrenzen](phase27_selected_candidate.md).
