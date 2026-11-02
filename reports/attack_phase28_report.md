# Forschungsserie 28: Zwei Runen Rückkopplung mit affiner Konstante

Stand UTC: 2026-11-01T17:40:19.248411+00:00. **Keine neue Entschlüsselung bestätigt.**

## Verfahren und Rechenbudget

`P_i=a*C_i+b*P_(i-2)+c mod29`, a,b=1..28,c=0..28.
E025 untersuchte c=0 mit anderem Modell und Parameterumfang. Hier ist c=1..28
das neue Ziel; c=0 bleibt für Kontrollen und identische Suchbedingungen enthalten.
Die bekannte affine Algebra ist keine Neuentdeckung.

22.736 Familien werden nach maximalem Unigramm-Score sortiert, mit Rundung auf
neun Nachkommastellen und stabilen lexikographischen Gleichständen. Die besten
128 bleiben erhalten. Je Familie werden alle 29²=841 Anfangspaare gegen das
unveränderte externe Viergramm-Modell bewertet: 107.648 Präfixe pro Eingabe.
Die Präfixsuche ist exakt, die Familienauswahl heuristisch.
Keine ausgelassenen Runen, keine versteckten Resets.

E077 prüft 2.523 Scores durch unabhängige skalare Rekursion; maximale Abweichung
3.33e-16. Der Pilot mit 256 Familien und 277 Runen
dauert 2.451 Sekunden. Die lineare Hochrechnung
ergibt 217.7
Sekunden pro vollständigem Gitter bzw. 3.33
Stunden für 55 gleich lange Eingaben, ohne Nullkalibrierung. **Nur Schätzung,
kein durchgeführter Vollgitterlauf.** Die eingefrorene 128-Familien-Suche
benötigt bei 3.316 Zufallsrunen 14.536 Sekunden.

## E078: Kontrollen

16/16 Klartexte, Schlüssel und a/b/c exakt. Neue Zwei-Runen-Schlüssel auf bereits
betrachteten, vom Training ausgeschlossenen Emerson-Blöcken. Zwölf kurze Texte
bei c!=0 und vier Regressionen bei c=0. Teilweise verschachtelte Ausschnitte,
keine 16 unabhängigen ungesehenen Texte. Diagnostischer Kontroll-Nullscore
-5.259722, ohne p-Wert.

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

## E079: Direkter Angriff auf die unbekannten Seiten

Alle 55 unbekannten Runenseiten einzeln angegriffen, einschließlich kurzer
Seiten. LP2-50 bleibt mit Originalinhalt im Plan erhalten und wurde nicht
entschlüsselt. Layout und Runen aller 56 Forschungsseiten sind in den gepinnten
Quellen verankert; Quellprüfsummen und die deklarierte Runenvariante geprüft.

| Seite | Runen | a | b | c | Score |
|---|---:|---:|---:|---:|---:|
| LP2-00 | 262 | 5 | 13 | 11 | -5.982003 |
| LP2-01 | 266 | 19 | 24 | 4 | -5.971403 |
| LP2-02 | 201 | 28 | 23 | 17 | -5.792250 |
| LP2-03 | 217 | 3 | 20 | 26 | -5.811031 |
| LP2-04 | 261 | 21 | 27 | 17 | -6.015285 |
| LP2-05 | 263 | 11 | 18 | 23 | -6.004989 |
| LP2-06 | 196 | 19 | 14 | 0 | -5.801196 |
| LP2-07 | 208 | 10 | 12 | 4 | -5.827443 |
| LP2-08 | 255 | 4 | 4 | 1 | -5.969892 |
| LP2-09 | 268 | 22 | 22 | 25 | -5.862787 |
| LP2-10 | 263 | 3 | 8 | 25 | -5.897389 |
| LP2-11 | 273 | 17 | 9 | 22 | -5.937981 |
| LP2-12 | 261 | 9 | 22 | 15 | -5.966786 |
| LP2-13 | 272 | 28 | 15 | 9 | -5.979678 |
| LP2-14 | 137 | 9 | 18 | 15 | -5.511612 |
| LP2-15 | 159 | 10 | 27 | 2 | -5.703918 |
| LP2-16 | 267 | 3 | 27 | 11 | -6.046390 |
| LP2-17 | 273 | 16 | 25 | 24 | -5.972429 |
| LP2-18 | 260 | 6 | 2 | 6 | -5.990088 |
| LP2-19 | 271 | 20 | 3 | 24 | -5.986898 |
| LP2-20 | 269 | 14 | 14 | 15 | -5.951740 |
| LP2-21 | 273 | 21 | 15 | 17 | -5.873837 |
| LP2-22 | 131 | 21 | 10 | 11 | -5.367048 |
| LP2-23 | 213 | 17 | 4 | 6 | -5.770480 |
| LP2-24 | 270 | 25 | 7 | 3 | -5.996611 |
| LP2-25 | 273 | 15 | 5 | 6 | -5.945961 |
| LP2-26 | 265 | 8 | 11 | 14 | -5.926659 |
| LP2-27 | 234 | 2 | 20 | 14 | -5.891963 |
| LP2-28 | 269 | 18 | 4 | 17 | -5.906398 |
| LP2-29 | 277 | 2 | 12 | 3 | -6.006923 |
| LP2-30 | 263 | 24 | 14 | 9 | -5.999397 |
| LP2-31 | 269 | 14 | 11 | 1 | -5.920545 |
| LP2-32 | 121 | 7 | 28 | 7 | -5.514120 |
| LP2-33 | 214 | 22 | 26 | 10 | -5.879347 |
| LP2-34 | 261 | 16 | 5 | 0 | -5.939484 |
| LP2-35 | 271 | 8 | 7 | 27 | -5.906805 |
| LP2-36 | 238 | 25 | 28 | 21 | -5.879587 |
| LP2-37 | 228 | 22 | 21 | 24 | -5.838135 |
| LP2-38 | 228 | 17 | 25 | 19 | -5.706204 |
| LP2-39 | 240 | 22 | 27 | 14 | -5.976610 |
| LP2-40 | 231 | 17 | 6 | 24 | -5.807474 |
| LP2-41 | 273 | 25 | 4 | 8 | -6.024924 |
| LP2-42 | 272 | 12 | 28 | 14 | -5.962386 |
| LP2-43 | 274 | 23 | 13 | 25 | -5.872074 |
| LP2-44 | 273 | 23 | 2 | 1 | -6.014324 |
| LP2-45 | 270 | 4 | 27 | 20 | -5.942486 |
| LP2-46 | 270 | 24 | 5 | 8 | -5.908525 |
| LP2-47 | 274 | 21 | 27 | 25 | -5.970174 |
| LP2-48 | 271 | 1 | 21 | 26 | -5.928379 |
| LP2-49 | 66 | 1 | 22 | 2 | -4.842199 |
| LP2-51 | 92 | 24 | 21 | 11 | -5.144673 |
| LP2-52 | 263 | 22 | 26 | 28 | -5.975860 |
| LP2-53 | 179 | 16 | 15 | 9 | -5.724536 |
| LP2-54 | 232 | 28 | 6 | 7 | -5.957288 |
| LP2-55 | 76 | 25 | 26 | 21 | -5.145977 |

Stärkste Ausgabe: **LP2-49**, Score -4.842199.
Auswahl und alle 55 Ergebnishashes wurden vor den Nullversuchen fixiert.
19 unabhängig erzeugte Nulltexte erhalten Häufigkeiten, Randrunen und die
Anzahl gleicher Nachbarpaare. Jeder durchläuft die vollständige gleiche Suche.
**10/19** sind mindestens so hoch bewertet:
Plus-eins-p=0.55, Bonferroni55=1.00.
Schon der kleinste mit 19 Nulltexten erreichbare korrigierte Wert beträgt 1.
Dieser grobe Vergleich erlaubt keinen Signifikanznachweis.

## Unabhängige Prüfung und Grenzen

Eine getrennte Implementierung rekonstruiert den Klartext durch Warteschlangen,
ohne die affine Formel des Suchprogramms. Alle 9,903,616 Präfixscores der
128-Familien-Suche in 92 Aufgaben stimmen einschließlich kompletter Vektor-Prüfsummen. Quellen,
Seeds, beibehaltene Familienoptima, Kandidaten, Rückverschlüsselungen,
Nullziehungen und Auswahl geprüft. Die Sprachmodelltabellen wurden separat
gegen skalare Wahrscheinlichkeiten kontrolliert. Die vollständige Unigramm-
Vorauswahl wurde reproduziert; unabhängig direkt nachgerechnet wurden die
beibehaltenen Familien und Kontrollfamilien, nicht das gesamte Vorauswahlgitter.

Die verworfenen 22.608 Familien bleiben offen. Die Chiffrenklasse ist nicht
ausgeschlossen; der englische Prosa-Score kann andere Klartextarten übersehen.
Sprachähnliche Fragmente sind ohne weiteren Nachweis keine Entschlüsselung.

140 Tests bestanden; 92 registrierte Aufgaben; 193.279 Sekunden
Experimentzeit bei 1.800 Sekunden Budget, höchster abgetasteter Speicher
146.9 MiB bei 768 MiB Grenze, ein Suchworker. Prüfzeiten gesondert
in den Validierungsdateien. Historische Ergebnisse erhalten, keine laufenden Jobs.

Als Nächstes folgt die offene Substitutionssuche H031: zuerst die dokumentierte Fehlbewertung kurzer Kontrolltexte beheben, dann bei bestandenen Kontrollen direkt auf unbekannte Seiten anwenden.

[Plan](../experiments/delay_two_plan.json),
[Angriffsplan](../experiments/delay_two_unknown_plan.json),
[Ergebnisse](../results/phase28_summary.json),
[Ausgabe mit Originalgrenzen](phase28_selected_candidate.md).
