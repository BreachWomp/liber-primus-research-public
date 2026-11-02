# Forschungsserie 21: Fragmentabstände genutzt, unbekannte Seiten angegriffen

Stand (UTC): 2026-10-22T17:22:58.761128+00:00. **Keine neue Entschlüsselung bestätigt.**
Die Kombination beider Initialisierungen löst alle 21 Blindkontrollen exakt, einschließlich des zuvor
mehrfach gescheiterten kurzen 31-Runen-Schlüssels. Danach wurde das Verfahren unverändert
auf neun LP2-Gruppen angewandt, die alle 55 unbekannten Runenseiten abdecken.

## E058: Exakte Abstandsbedingungen bei der Initialisierung

Bei zwei Fragmentstarts a<b derselben Seite gilt
`phase_b-phase_a = (b-a)-s (mod m)`. Die Zahl s der kopierten F im Intervall
liegt zwischen null und der Anzahl Chiffren-F in `[a,b)`. Diese Information
stammt ausschließlich aus dem Chiffretext. Bisher wurden Fragmentphasen
unabhängig gewählt; jetzt optimiert eine exakte Ketten-DP ihre zulässigen
Kombinationen. Unterschiedliche Seiten bleiben unabhängig. Lücken tragen
keinen Sprachscore zum Pool bei, ihre möglichen Cursorverschiebungen aber schon.

Unverändert: zwölf längste F-freie Fragmente ab 16, begrenzt auf 256 Runen;
nominale Perioden 17–32 und beide Vorzeichen. 64 Starts für kurze Eingaben,
sonst 16; vier beziehungsweise zwei behaltene Unigrammstarts. Die ersten drei
Starts nehmen keine, alle beziehungsweise die halbe Zahl möglicher F-Kopien
zwischen Fragmenten an; weitere Starts verwenden feste Zufallsseeds und
zulässige Abstände. Danach Bigramm-/Viergrammverfeinerung und 20 diversifizierte
Volltextstarts mit dem kontinuierlichen E056-Sprachkontext. Der bisherige
konservative Pool-Phasenabzug bleibt unverändert. Keine wahren Schlüssel,
Masken oder Phasen werden an den Solver gegeben.

Stufe A: schwierige E054-Regression plus drei frische natürliche Bereiche
aus Emerson X/XI/XII, Runen 16000:16729, Schlüssel 17/23/31, unabhängige
Seitenphasen und F-Kopierwahrscheinlichkeiten 0,25/0,50/0,75. Stufe B wurde
erst nach vier exakten Ergebnissen gestartet: elf weitere E054-Regressionen
und die drei E056-Grenzstresstests. Trainingskapitel bleiben I, III–IX.

E058 allein löst **17/18** Fälle, verfehlt jedoch die ältere 1200-Runen-
Kontrolle mit Schlüssel 31 (49/1200 richtig). Der dafür vorab geplante
Angriff E059 bleibt gesperrt und unausgeführt; sein Plan bleibt erhalten.

## E060: Beide Initialisierungen mit fester gemeinsamer Auswahl

Die unveränderten E057- und E058-Suchen laufen vollständig, ihre jeweils drei
besten Kandidaten werden nach demselben Volltextscore zusammengeführt.
Gleichstände behalten die Reihenfolge E058 vor E057; gleiche Klartexte werden
zusammengefasst. Keine Kontrolle entscheidet, welches Verfahren zugelassen
wird. Identische bereits geprüfte Suchläufe werden ausschließlich anhand von
Chiffretext, Seitenspannen, Training und eingefrorenen Code-/Ausgabehashes
wiederverwendet. Das spart Wiederholungen, ohne Lösungswissen einzuspeisen.

Zuerst beide schwierigen Fälle und drei neue natürliche Bereiche aus X/XI/XII,
Runen 16850:17579, dann alle übrigen 16 E058-Kontrollen. Neue Schlüssel, Phasen
und F-Kopien sind mit getrennten festen Seeds erzeugt. Diese Bereiche grenzen
an frühere Kontrollbereiche und sind keine unabhängige neue Textsammlung.
Alle **21 Hybridkontrollen** werden exakt rekonstruiert:

| Kontrolle | Schlüssel | Runen | Text/Schlüssel/Vorzeichen/Maske/Phasen |
|---|---:|---:|---|
| regression 0 | 31 | 729 | exakt |
| regression 14 | 31 | 1200 | exakt |
| fresh 0 | 17 | 729 | exakt |
| fresh 1 | 23 | 729 | exakt |
| fresh 2 | 31 | 729 | exakt |
| regression 1 | 17 | 729 | exakt |
| regression 2 | 23 | 729 | exakt |
| regression 3 | 31 | 729 | exakt |
| regression 4 | 17 | 729 | exakt |
| regression 5 | 23 | 729 | exakt |
| regression 6 | 17 | 3316 | exakt |
| regression 7 | 23 | 3316 | exakt |
| regression 8 | 31 | 3316 | exakt |
| regression 9 | 17 | 1200 | exakt |
| regression 10 | 23 | 1200 | exakt |
| regression 11 | 31 | 1200 | exakt |
| regression 12 | 17 | 3316 | exakt |
| regression 13 | 23 | 1200 | exakt |
| regression 15 | 17 | 729 | exakt |
| regression 16 | 23 | 729 | exakt |
| regression 17 | 31 | 729 | exakt |

Beim schwierigen Fall gibt es zwölf Fragmente in drei Seitenketten. Für die
tatsächliche Periode 31 sinkt die Zahl zulässiger Phasenbelegungen gegenüber
unabhängigen Fragmenten rechnerisch um Faktor 119536775.5.
Das ist eine kombinatorische Zählung, keine gemessene Laufzeitbeschleunigung.
Der wahre Schlüssel erscheint in 0 Unigramm-
und 0 Bigrammzuständen; erst spätere Verfeinerung
liefert die vollständige Rekonstruktion. Die Suche bleibt heuristisch über
Schlüssel, auch wenn die bedingte Phasenoptimierung exakt ist.

Ein vollständiger passender Kontroll-Nullversuch hat Score
-5.476413; daraus allein wird kein p-Wert abgeleitet.

## E061: Direkter Angriff auf die unbekannten LP2-Abschnitte

Gemeinsamer zyklischer Schlüssel pro Gruppe, eigene Startphase je Seite,
optionale F-Kopien ohne Schlüsselverbrauch und durchlaufender Sprachkontext.
Gruppierung und zusammenhängender Klartext sind Hypothesen. LP2-50 bleibt als
leere Runenspanne erhalten; die Zahlendaten werden dadurch nicht entschlüsselt.
LP2-54/55 werden innerhalb LP2-40_55 erfasst. Kein Parameter wurde an die
unbekannten Ausgaben angepasst.

| Abschnitt | Runen | gefundene primitive Schlüssellänge | bester Score |
|---|---:|---:|---:|
| LP2-00_02 | 729 | 31 | -5.538402 |
| LP2-03_07 | 1145 | 31 | -5.759327 |
| LP2-08_14 | 1729 | 32 | -5.929138 |
| LP2-15_22 | 1903 | 31 | -5.961106 |
| LP2-23_26 | 1021 | 30 | -5.638826 |
| LP2-27_32 | 1433 | 28 | -5.843719 |
| LP2-33_39 | 1680 | 31 | -5.940864 |
| LP2-40_53 | 3008 | 25 | -6.072220 |
| LP2-40_55 | 3316 | 32 | -6.103820 |

Vor den Nullversuchen wurde die Auswahl des höchsten Scores samt allen
Ausgabehashes festgeschrieben: **LP2-00_02**. Dann wurden
19 unabhängige Zufallstexte dieses Abschnitts mit demselben vollständigen
Solver optimiert. Jeder behält je Seite Häufigkeiten, Endpunkte und Anzahl
benachbarter gleicher Runen. **13/19** erreichen mindestens
den beobachteten Score. Mit Plus-eins-Korrektur: Roh-p=0.70,
Bonferroni-Korrektur für die Auswahl unter neun Gruppen=1.00.
Diese grobe Prüfung kann mit 19 Nullsuchen keinen kleinen korrigierten p-Wert
auflösen (Minimum 0,45). Sie bestätigt keinen Klartext und schließt die
gesamte Chiffrenfamilie bei einem unauffälligen Befund auch nicht aus.
Algebraisch gleich rückverschlüsselnde Anfangs-F-Alternativen bleiben sichtbar.

## Unabhängige Prüfung und Checkpoint

124 Tests bestanden, darunter vollständige Enumeration kleiner
Phasenketten. Sämtliche gespeicherten Poolzustände und Volltextzustände
wurden skalar nachgerechnet. Eine separate rückwärts laufende Rekurrenz
bestätigt die bedingten Kettenmaxima; die Volltextmaxima, Originalquellbereiche,
Rückverschlüsselung, Zufallstexte und Auswahlkorrektur wurden ebenfalls geprüft.
Exakte Prüfzähler stehen in der Messübersicht.

69 registrierte Aufgaben, 2041.652 Sekunden Experimentzeit;
Vor E060 wurde das Gesamtbudget prospektiv auf 3600 Sekunden erweitert;
E058 bleibt innerhalb seiner ursprünglichen Grenze. Höchstens 180 Sekunden
pro Aufgabe, ein Worker.
Höchster abgetasteter Speicherwert 162.9 MiB
bei 768 MiB Grenze. Quellbytes und frühere Versuchsergebnisse unverändert;
kein weiterlaufender Forschungsprozess.

Der Lauf wurde zwischenzeitlich unterbrochen. 13 fertige Aufgaben wurden
über Hashprüfung übernommen; nur der unvollständige fünfte Nullfall und
die danach fehlenden Fälle wurden ausgeführt. Alte Prozessprotokolle bleiben
bytegleich erhalten. Für die ungemessene Dauer des abgebrochenen Versuchs
werden konservativ 185 Sekunden auf das Budget angerechnet
(zusätzlich zu den gemessenen erfolgreichen Läufen; keine behauptete Messzeit).

Nächster registrierter Arbeitsauftrag (noch kein Ergebnis): Extend the existing E017 affine-chain machinery to seed lengths13..32 with a preregistered bounded initializer. First reproduce shorter known controls and fresh13/23/31 cases plus matched nulls. Exact blind validation required before unknown pages; retain uncertain F schedules explicitly.

[Abstandsplan](../experiments/constrained_fragment_plan.json),
[Hybridkontrollplan](../experiments/hybrid_fragment_plan.json),
[Angriffsplan](../experiments/hybrid_unknown_plan.json),
[Messübersicht](../results/phase21_summary.json),
[Checkpoint](../checkpoints/phase21_complete.json).
