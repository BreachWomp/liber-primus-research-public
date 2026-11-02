# Forschungsserie 24: Allgemeine Klartextrückkopplung

Stand (UTC): 2026-10-24T19:57:03.785747+00:00. **Keine neue Entschlüsselung bestätigt.**
16 Kontrollen exakt; anschließend 46 einzelne unbekannte LP2-Seiten und zehn
bestehende Seitengruppen direkt angegriffen. Originalquellen und alte Ergebnisse
bleiben unverändert. Es wurden keine unbelegten Community-Lösungen untersucht.

## Mechanismus und festgelegte Begrenzung

E066/E067 prüfen `P_i = a*C_i + b*P_(i-m) mod 29` mit `a=+1/-1`,
`b=1..28`, `m=4..32`. Der Anfangsschlüssel ergibt sich aus den ersten m
Klartextsymbolen durch Multiplikation mit dem modularen Inversen von b.
Alle Kettenkoeffizienten werden modulo 29 reduziert, damit lange Ketten nicht
überlaufen. Das verallgemeinert die frühere Suche; die affine Algebra und
frühere Tests kurzer Verzögerungen sind keine neue Entdeckung.

Pro Eingabe werden 1.624 Familien nach maximaler Unigramm-Bewertung geprüft.
Innerhalb jeder Schlüssellänge bleiben genau vier der 56 Koeffizientenpaare
erhalten. Für diese 116 Familien folgen die festen E062-Budgets für zwei
Initialisierungen, Trigramm- und Viergramm-Verfeinerung. Die Suche ist heuristisch;
eine erfolgreiche Kontrolle garantiert nicht, dass jede echte Familie erhalten bleibt.

## E066: Blindkontrollen und diagnostischer Nulltext

Zwölf neue Zufallsschlüssel verschlüsseln 200/300/729/3.316 Runen aus den
vom Training ausgeschlossenen Emerson-Kapiteln X/XI/XII. Die Textbereiche
wurden bereits zuvor betrachtet. Vier alte E062-Kontrolleingaben werden mit
dem geänderten Algorithmus neu bearbeitet; sie sind weder neue Texte noch
unverändert übernommene Suchläufe. Bei allen 16 Kontrollen stimmen Klartext,
Schlüssel und beide Koeffizienten exakt; die richtige Familie steht jedes Mal
auf Rang eins. Die alten Vorzeichen -1 werden als Restklasse 28 dargestellt.

| Kontrolle | Runen | m | a | b | Rang | Ergebnis |
|---|---:|---:|---:|---:|---:|---|
| 0 | 200 | 13 | 1 | 2 | 1 | exakt |
| 1 | 200 | 23 | -1 | 7 | 1 | exakt |
| 2 | 200 | 31 | 1 | 14 | 1 | exakt |
| 3 | 300 | 13 | -1 | 27 | 1 | exakt |
| 4 | 300 | 23 | 1 | 2 | 1 | exakt |
| 5 | 300 | 31 | -1 | 7 | 1 | exakt |
| 6 | 729 | 13 | 1 | 14 | 1 | exakt |
| 7 | 729 | 23 | -1 | 27 | 1 | exakt |
| 8 | 729 | 31 | 1 | 2 | 1 | exakt |
| 9 | 3316 | 13 | -1 | 7 | 1 | exakt |
| 10 | 3316 | 23 | 1 | 14 | 1 | exakt |
| 11 | 3316 | 31 | -1 | 27 | 1 | exakt |
| 12 | 300 | 13 | 1 | 28 | 1 | exakt |
| 13 | 300 | 23 | 1 | 1 | 1 | exakt |
| 14 | 300 | 31 | -1 | 28 | 1 | exakt |
| 15 | 300 | 4 | -1 | 1 | 1 | exakt |

Ein vollständiger diagnostischer Nulllauf erhält Randrunen, Häufigkeiten
und die Zahl gleicher Nachbarn. Score: -4.370513.
Aus diesem einzelnen Vergleich wird kein p-Wert abgeleitet.

## E067: Unbekannte Seiten und Fortsetzungen

46 Seiten mit mindestens 200 Runen werden einzeln untersucht; die zehn
bestehenden Gruppen ergänzen die Hypothese eines über Seitengrenzen
fortlaufenden Stroms. Zusammen vertreten sie alle 55 unbekannten Runenseiten.
Die Gruppengrenzen bleiben unbestätigt. LP2-50 bleibt mit Quellreferenzen als
leere Runenspanne erhalten; ihre Zahlen sind damit nicht entschlüsselt.

| Eingabe | Runen | m | a | b | Score |
|---|---:|---:|---:|---:|---:|
| LP2-00 | 262 | 32 | 1 | 2 | -4.131477 |
| LP2-01 | 266 | 31 | 1 | 26 | -4.206277 |
| LP2-02 | 201 | 28 | 1 | 16 | -3.851236 |
| LP2-03 | 217 | 31 | -1 | 11 | -3.942263 |
| LP2-04 | 261 | 32 | -1 | 21 | -4.158939 |
| LP2-05 | 263 | 32 | 1 | 2 | -4.178662 |
| LP2-07 | 208 | 32 | -1 | 9 | -3.868290 |
| LP2-08 | 255 | 32 | -1 | 3 | -4.073740 |
| LP2-09 | 268 | 31 | 1 | 22 | -4.254368 |
| LP2-10 | 263 | 32 | 1 | 18 | -4.051974 |
| LP2-11 | 273 | 31 | -1 | 18 | -4.231844 |
| LP2-12 | 261 | 32 | 1 | 4 | -4.070675 |
| LP2-13 | 272 | 30 | -1 | 14 | -4.231557 |
| LP2-16 | 267 | 31 | -1 | 10 | -4.222351 |
| LP2-17 | 273 | 32 | -1 | 18 | -4.235019 |
| LP2-18 | 260 | 30 | 1 | 15 | -4.052775 |
| LP2-19 | 271 | 32 | 1 | 25 | -4.125543 |
| LP2-20 | 269 | 32 | 1 | 14 | -4.190049 |
| LP2-21 | 273 | 31 | -1 | 26 | -4.246181 |
| LP2-23 | 213 | 30 | 1 | 2 | -3.866832 |
| LP2-24 | 270 | 30 | 1 | 7 | -4.150421 |
| LP2-25 | 273 | 32 | 1 | 17 | -4.299808 |
| LP2-26 | 265 | 31 | -1 | 17 | -4.221266 |
| LP2-27 | 234 | 30 | 1 | 22 | -4.064949 |
| LP2-28 | 269 | 32 | 1 | 21 | -4.150839 |
| LP2-29 | 277 | 32 | 1 | 25 | -4.248184 |
| LP2-30 | 263 | 32 | 1 | 20 | -4.175627 |
| LP2-31 | 269 | 32 | 1 | 12 | -4.152636 |
| LP2-33 | 214 | 31 | -1 | 17 | -3.805311 |
| LP2-34 | 261 | 31 | -1 | 2 | -4.185525 |
| LP2-35 | 271 | 31 | -1 | 21 | -4.264313 |
| LP2-36 | 238 | 32 | 1 | 16 | -4.086932 |
| LP2-37 | 228 | 31 | 1 | 10 | -3.901837 |
| LP2-38 | 228 | 31 | -1 | 23 | -4.000890 |
| LP2-39 | 240 | 30 | 1 | 4 | -4.063001 |
| LP2-40 | 231 | 32 | 1 | 3 | -4.007789 |
| LP2-41 | 273 | 30 | -1 | 6 | -4.249645 |
| LP2-42 | 272 | 31 | -1 | 5 | -4.250808 |
| LP2-43 | 274 | 30 | -1 | 2 | -4.283470 |
| LP2-44 | 273 | 32 | 1 | 15 | -4.248809 |
| LP2-45 | 270 | 32 | -1 | 17 | -4.226142 |
| LP2-46 | 270 | 32 | -1 | 9 | -4.225147 |
| LP2-47 | 274 | 32 | 1 | 11 | -4.306360 |
| LP2-48 | 271 | 32 | -1 | 23 | -4.208994 |
| LP2-52 | 263 | 32 | -1 | 2 | -4.216905 |
| LP2-54 | 232 | 32 | 1 | 22 | -3.985976 |
| LP2-00_02 | 729 | 32 | -1 | 24 | -5.394302 |
| LP2-03_07 | 1145 | 32 | -1 | 21 | -5.661851 |
| LP2-08_14 | 1729 | 30 | 1 | 19 | -5.935204 |
| LP2-15_22 | 1903 | 32 | -1 | 14 | -5.975291 |
| LP2-23_26 | 1021 | 32 | 1 | 21 | -5.603544 |
| LP2-27_32 | 1433 | 32 | 1 | 14 | -5.796041 |
| LP2-33_39 | 1680 | 32 | -1 | 14 | -5.939370 |
| LP2-40_53 | 3008 | 31 | 1 | 23 | -6.214282 |
| LP2-54_55 | 308 | 30 | 1 | 24 | -4.384546 |
| LP2-40_55 | 3316 | 31 | 1 | 23 | -6.246616 |

Die stärkste Eingabe ist **LP2-33** mit Score
-3.805311. Ihre Auswahl und sämtliche 56 Ergebnishashes wurden
vor den Nullversuchen fixiert. 19 Nulltexte bewahren pro Originalseite
Häufigkeiten, Randrunen und gleiche Nachbarn. Jeder durchläuft die gesamte
Vorauswahl und Optimierung erneut; interne Auswahl wird dadurch berücksichtigt.

**2/19** Nullscores erreichen mindestens den beobachteten
Wert. Plus-eins-p=0.15, Bonferroni für 56 ausgewählte
Eingabehypothesen=1.00. Bei nur 19 Nullversuchen kann
der korrigierte Wert hier niemals unter 1 fallen. Dies ist eine grobe
Aussortierung, kein Signifikanztest mit ausreichender Auflösung. Nulltrefferzahl
null würde eine separat registrierte größere Kalibrierung verlangen.

## Unabhängige Prüfung und Ressourcen

Eine separate Schlüsselwarteschlange rekonstruiert Quellenkontrollen,
Kandidaten und Rückverschlüsselungen. Die Vorauswahl wird aus unabhängigen
Queue-Dekodierungen nachgerechnet; gespeicherte Sprachscores, Auswahl,
bedingte Koordinatenmaxima, Seitenübergänge und Nullgenerator werden geprüft.
Zusätzlich sind alle 85376 Startpräfixe
aus den festgelegten Seeds unabhängig rekonstruiert.
129 Unit-Tests bestanden, einschließlich aller 28 Rückkopplungsfaktoren
auf langen Ketten und unabhängiger Prüfung der Trigrammfaktoren.

92 registrierte Aufgaben, 986.144 Sekunden erfolgreiche
Experimentzeit; höchster abgetasteter Prozessspeicher
113.2 MiB. Festgelegtes Budget: 3.000
Sekunden Experimentzeit, 180 pro Aufgabe, 768 MiB, ein Worker. Keine laufenden Jobs.
Die unabhängigen Prüfzeiten stehen zusätzlich in den Validierungsdateien.

Nächster ungetesteter Schritt: auch den Chiffrekoeffizienten a über alle Nichtnullwerte erweitern, zunächst begrenzt und an Kontrollen kalibriert.

[Kontrollplan](../experiments/general_feedback_plan.json),
[Angriffsplan](../experiments/general_feedback_unknown_plan.json),
[Messübersicht](../results/phase24_summary.json),
[Sprachähnliche Stücke mit Originalgrenzen](phase24_language_fragments.md),
[Checkpoint](../checkpoints/phase24_complete.json).
