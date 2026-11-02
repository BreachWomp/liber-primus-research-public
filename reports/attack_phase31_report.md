# Forschungsserie 31: Differenzen und allgemeine Runensubstitution

Stand UTC: 2026-11-02T16:57:03.709216+00:00. **Keine neue Entschlüsselung bestätigt.**

## Festgelegte reversible Regel

`C_-1=0`, `D_i=(C_i-C_(i-1))mod29`, `P_i=S(D_i)`.
S ist eine beliebige 29-Symbol-Permutation. Rückweg:
`C_i=(C_(i-1)+S^-1(P_i))mod29`. Die erste Rune wird ausdrücklich verarbeitet,
nicht als IV entfernt. Wortgrenzen bleiben erhalten. Der Startwert 0 ist eine
vorab gewählte Begrenzung, kein aus dem Rätsel abgeleiteter Befund.
Andere Anfangswerte und über Seiten laufende Zustände sind hier nicht getestet.
E015 untersuchte nur affine Abbildungen nach Differenzen; seine historischen
Ergebnisse bleiben unverändert. Die mathematischen Operationen sind bekannt.

## E085: Exakte Übertragung bestehender Kontrollen

Die zwölf bestandenen E083-Kontrollen werden zu synthetischen Chiffren dieser
neuen Familie integriert. Differenzbildung liefert exakt die bisherigen
Substitutionseingaben zurück. Deshalb wird die unveränderte Schlüsselsuche
**nicht erneut ausgeführt**. Das sind übertragene Kontrollen, keine zwölf neuen
unabhängigen Blindversuche. Drei vorhandene D-Raum-Kontrollnulls werden genauso
übertragen; sie sind keine neuen passenden C-Raum-Nullziehungen.

Separater Prüfer: Quellfenster und Schlüssel reproduziert, 245 Kandidatenscores
nachgerechnet, 245 vollständige kumulative Rückverschlüsselungen bestätigt.
435 algebraische Identitäten über alle 29 IVs geprüft; diese Matheprüfung
erweitert den unbekannten Angriff ausdrücklich nicht über IV 0 hinaus.
Training und Modell bleiben unverändert; X/XI/XII sind vom Fit ausgeschlossen,
aber das Emerson-Korpus wurde historisch bereits betrachtet.

## E086: Angriff auf unbekannte Seiten

Nach separater Kontrolle registriert: 46 LP2-Seiten ab 200 Runen, jeweils vor der
Substitutionssuche differenziert. Höchstens 24 Starts, 40 vollständige 406-Tausch-
Sweeps im Zeichenmodell, 40 im BOS/EOS-Wortmodell. Keine neuen Modellparameter.
Neun kurze Runenseiten und die numerische LP2-50 bleiben mit Originalinhalt und
Ausschlussgrund im Plan. Die originalen Wortendpunkte sind unverändert;
Quellanker aller 56 Forschungsseiten und zehn gepinnte Quelldateien geprüft.

| Seite | Runen | Höchster Score |
|---|---:|---:|
| LP2-00 | 262 | -8.223982 |
| LP2-01 | 266 | -8.284429 |
| LP2-02 | 201 | -7.555071 |
| LP2-03 | 217 | -7.715733 |
| LP2-04 | 261 | -8.512162 |
| LP2-05 | 263 | -8.128765 |
| LP2-07 | 208 | -7.981767 |
| LP2-08 | 255 | -7.639698 |
| LP2-09 | 268 | -7.938683 |
| LP2-10 | 263 | -8.475421 |
| LP2-11 | 273 | -8.051339 |
| LP2-12 | 261 | -8.277417 |
| LP2-13 | 272 | -8.060434 |
| LP2-16 | 267 | -8.476086 |
| LP2-17 | 273 | -8.668955 |
| LP2-18 | 260 | -8.322923 |
| LP2-19 | 271 | -8.453831 |
| LP2-20 | 269 | -8.552878 |
| LP2-21 | 273 | -7.856105 |
| LP2-23 | 213 | -8.171361 |
| LP2-24 | 270 | -8.730881 |
| LP2-25 | 273 | -8.381671 |
| LP2-26 | 265 | -8.354422 |
| LP2-27 | 234 | -8.024870 |
| LP2-28 | 269 | -8.207586 |
| LP2-29 | 277 | -8.494215 |
| LP2-30 | 263 | -8.389047 |
| LP2-31 | 269 | -8.436131 |
| LP2-33 | 214 | -8.054343 |
| LP2-34 | 261 | -8.241893 |
| LP2-35 | 271 | -8.031256 |
| LP2-36 | 238 | -7.914627 |
| LP2-37 | 228 | -7.862157 |
| LP2-38 | 228 | -7.908442 |
| LP2-39 | 240 | -8.245986 |
| LP2-40 | 231 | -8.073526 |
| LP2-41 | 273 | -8.247909 |
| LP2-42 | 272 | -8.054328 |
| LP2-43 | 274 | -8.150681 |
| LP2-44 | 273 | -8.171149 |
| LP2-45 | 270 | -8.497033 |
| LP2-46 | 270 | -8.420472 |
| LP2-47 | 274 | -8.349559 |
| LP2-48 | 271 | -8.634877 |
| LP2-52 | 263 | -8.252686 |
| LP2-54 | 232 | -7.676338 |

Stärkste Ausgabe **LP2-02**, Score -7.555071.
Auswahl und 46 Ergebnishashes vor den Nullziehungen fixiert. 19 unabhängige
Innenmischungen des **ursprünglichen C-Texts** erhalten Randrunen, genaue
Häufigkeiten, Anzahl gleicher Nachbarn und Originalwortgrenzen. Erst danach
wird differenziert und mit demselben seitenbezogenen Seed vollständig gesucht.
Die Häufigkeiten nichtnulliger Differenzen bleiben dabei nicht erhalten;
dieser Vergleich ist ausdrücklich ein C-Raum-Modell, kein zusätzlicher D-Raum-Test.

**9/19** Nullscores mindestens so hoch wie die Auswahl.
Plus-eins-p=0.50; Bonferroni46=1.00.
Mit 19 Nulltexten ist der kleinste korrigierte Wert bereits 1: grobes Screening,
kein Signifikanznachweis und keine belegte Entschlüsselung.

## Unabhängige Validierung und Grenzen

1320 ausgegebene Kandidatenscores,
535920 letzte Nachbarscores und
1320 vollständige
Rückverschlüsselungen bis zum originalen C-Text bestätigt. Separate Literal-
Differenzen und kumulative Inversion, keine Produktions-Differenzfunktion.
Quellen, Null-Seeds und Auswahl geprüft. Zwischenpfade der Suchoptimierung
wurden nicht unabhängig implementiert; GP-Tokenisierung wird gemeinsam benutzt.

Endliche Heuristik, keine Ausschließung aller 29! Permutationen. Seitenränder
werden als Wortgrenzen angenommen. Nichtenglische oder nichtsprachliche Texte,
andere IVs und kurze Seiten bleiben außerhalb dieser Aussage. Sprachähnliche
Stücke sind ohne weitere Evidenz keine Lösung. Der E081-Kurztextfehler bleibt bestehen.

145 Tests bestanden; 66 neue registrierte Aufgaben, davon eine Kontroll-
Übertragung ohne Optimizersuche. Experimentzeit 255.932 Sekunden;
überwachte Prozesszeit 312.748 Sekunden bei 1.800 Sekunden Budget.
Spitzenspeicher 184.2 MiB bei 768 MiB Grenze, ein Worker. Keine laufenden Jobs.

Als Nächstes wird die offene Anfangswertfrage geprüft: Für eine feste Permutation betrifft sie nur die erste Klartextrune. Ein Verfahren für alle 29 Werte muss vorab mit unabhängiger Scoreprüfung und ausdrücklich behandelter Mehrdeutigkeit validiert werden.

[Plan](../experiments/difference_substitution_plan.json),
[Angriffsplan](../experiments/difference_substitution_unknown_plan.json),
[Ergebnisse](../results/phase31_summary.json),
[Ausgaben mit Originalgrenzen](phase31_selected_candidates.md).
