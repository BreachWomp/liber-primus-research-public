# Fünfzehnte Forschungsserie: Gemeinsamer Schlüssel mit Seiten-Neustart

Stand (UTC): 2026-10-20T20:44:45.264242+00:00. **Keine neue Entschlüsselung bestätigt.**

## Direkter Angriff auf unbekannte Abschnitte

E046 untersucht dieselben zehn gepinnten Seitengruppen mit einer neuen
Regel: `P_i=s*C_i+K_j mod29`, s=+1 oder −1, und **j beginnt auf jeder Seite
wieder bei null**. An einer Chiffren-F-Rune kann F kopiert werden, ohne
j zu erhöhen. Alle Seiten verwenden denselben orientierten Schlüssel.
Auch der Sprachkontext beginnt an jeder Seite neu. Seiten werden nicht
mit unabhängig angepassten Anfangsphasen ausgestattet.

| Gruppe | Runen | Bester penaliserter Score |
|---|---:|---:|
| LP2-00_02 | 729 | -5.912185 |
| LP2-03_07 | 1145 | -6.027666 |
| LP2-08_14 | 1729 | -6.156643 |
| LP2-15_22 | 1903 | -6.243878 |
| LP2-23_26 | 1021 | -6.047755 |
| LP2-27_32 | 1433 | -6.141726 |
| LP2-33_39 | 1680 | -6.228457 |
| LP2-40_53 | 3008 | -6.319841 |
| LP2-54_55 | 308 | -5.394358 |
| LP2-40_55 | 3316 | -6.297573 |

Gruppen aus den Quellen sind unbestätigte Chiffregrenzen. Alle Runen,
Quellverweise und Seitenoffsets bleiben erhalten. LP2-50 ist als leere
Runenspanne vorhanden; keine Aussage über die Entschlüsselung ihrer Zahlen.

## Suchverfahren und Kontrolle

Startschlüssel stammen aus den zwei längsten nichtleeren Seiten (maximal
1024 Runen) sowie den drei längsten F-freien Abschnitten innerhalb einzelner
Seiten (mindestens 32, maximal 256 Runen). Perioden 1–16, beide Vorzeichen,
vier Starts je E038-Familie; zwölf zyklisch deduplizierte Schlüssel behalten.
Für jeden Start wird zunächst die beste **gemeinsame** Phase aller Seiten
bestimmt: pro Phase die Summe exakter seitenweiser F-Zeitplanmaxima.
Diese Phase wird in den orientierten Schlüssel eingerechnet.
Danach bis zu drei Runden mit je maximal sechs gemeinsamen
Koordinatendurchläufen und exakter seitenweiser Zeitplanoptimierung bei
Phase null. Koordinatenänderungen werden über alle Seiten gemeinsam bewertet,
ohne Sprachfaktoren über Seitengrenzen hinweg zu bilden.

Score: `(Summe der seitenweisen logp4 - Schlüssellänge*ln29 - Anzahl F*ln2)/N`.
Nur ein gemeinsamer primitiver Schlüssel wird berechnet.
Schlüsselsuche und Startauswahl bleiben heuristisch. Die Zeitplansuche
ist exakt für den jeweiligen orientierten Schlüssel; spätere Runden
prüfen die gemeinsame Phase nicht nochmals separat.

E045 löst drei externe Kontrolltexte mit 3316, 1200 und 1200 Runen exakt,
einschließlich Schlüssel der Längen 5, 8, 13 und aller F-Unterbrechungen.
Die Chiffren werden mit Seiten-Neustart und neuen Zufallsschlüsseln erzeugt;
dem Solver werden weder Schlüssel noch Klartext oder Masken gegeben.
Die erste Kontrolle enthält dieselben Seitenlängen wie LP2-40 bis LP2-55,
einschließlich der leeren Zahlenseite. Training auf Emerson I, III–IX,
Kontrolltexte aus X, XI, XII; Quellbereiche disjunkt, historisch bereits
bekannte Kapitel. Ein zusätzlicher Null-Kontrolltext läuft vollständig durch
den Solver. Dies ist ein Funktionstest, keine neue Liber-Primus-Lösung.

## Ergebnis und Zufallsvergleich

Stärkster Suchtreffer: **LP2-54_55**, Score -5.394358,
Sprachwertung -5.205931. Vorzeichen -1,
gemeinsamer Schlüssel `[9, 25, 7, 14, 8, 10, 3, 1, 27, 7, 14, 10, 26, 3, 11, 19]`.
F-Skips als nullbasierte Offsets im gesamten Abschnitt: `[41, 195, 273]`.
Zur Rückverschlüsselung `C_i=s*(P_i-K_j) mod29` mit Seiten-Neustart;
gespeicherte Skips bleiben F.

```text
XGSLIHELHNLYCTHRAMNEOOETHCDEOEARCUMSPGGYMMWTDAFIPDSUFLLLIASOJXYAGFTMADIANUTHOWWNGOEAYDRESIHAUTHWILFBUPTMPLUBCEAUADBYSHDOBOIANGTNSREEGGTHSIPSDLEAHEAUYWRATHFFAOIAIOTBACADRRIGHRTHLTHPGWTALHGOCABLNGINUENGAURTGTRSBYJXYEORMFPIMTXDAANGTHDIDRUYEONIALEMHEAMLFABAWHITHPBFBRUASTHNGTHROUSMJUMNWOEAPEAWFFWTHGGURTTHEANOXFMGIANGLOELLSUFTHAXSSCEONGJUEXISBNDTNGFIER
```

**Unveränderte Suchausgabe, kein bestätigter Klartext.** Die Darstellung
verkettet nur die Ausgabe; Schlüsselcursor und Bewertung wurden seitenweise
zurückgesetzt. Vor dem Zufallsvergleich wurden Sieger und Quellergebnisse
mit Prüfsummen eingefroren. Jeder Nulltext bewahrt pro Seite Runenhäufigkeiten,
gleiche Nachbarpaare und die Randrunen. Innenpositionen werden unabhängig
permutiert und bis zur passenden Nachbarpaarzahl verworfen (maximal 100000).
Jeder Nulltext bestimmt seine eigenen Startabschnitte, Schlüssel, Phasen
und Masken mit dem vollständigen unveränderten Solver.

**1/19** Nulltexte erreichen mindestens den beobachteten
Score. Plus-eins-p=0.100, Bonferroni10=1.000.
Der Treffer ist dadurch nicht als Lösung gestützt.
19 Replikate erlauben keine Auflösung korrigierter Signifikanz. Die Korrektur
gilt für diese zehn Gruppen, nicht für das gesamte explorative Projekt.
Der negative Befund ist kein vollständiger Ausschluss beliebiger Schlüssel.

## Unabhängige Prüfung und Fortsetzung

103 Tests bestanden. 1680 Zwischen-/Endkandidaten,
396 Starts und 396 Suchverläufe skalar
neu berechnet, einschließlich Rückverschlüsselung. Separater Score-Viterbi
bestätigt die 33 seitenweisen Zeitplanmaxima der Sieger
bei festem orientierten Schlüssel. Kleine Tests prüfen den gemeinsamen
Phasenentscheid gegen vollständige Enumeration aller F-Teilmengen,
Sprachfaktoren gegen Einzelbewertungen und gemeinsame Koordinatenänderungen.
Alle Kontroll-Quellbereiche, Zufallsschlüssel und 20 Nulltexte aus festen Seeds
reproduziert; Ergebnis- und Abhängigkeitshashes stimmen.

30 Aufgaben, 254.226 Sekunden erfolgreiche Experimentzeit.
E046 einschließlich Ablaufaufwand 220.751 Sekunden unter 650;
Phasenlimit 900, je Prozess 180 Sekunden, ein Worker, maximal 4096 Runen.
Keine Quellen geändert oder fremden Lösungsmeldungen untersucht.

Nächste direkte Hypothese: gemeinsamer Schlüssel mit unbekannter Anfangsphase
pro Seite. Diese zusätzliche Freiheit braucht einen expliziten Phasenabzug,
neue Kontrollen und vollständige Nulloptimierung, bevor irgendein Treffer
als Evidenz gelten kann. Kontinuierliche und identische Seitenstarts sind
damit nicht einfach nochmals dieselbe Suche.

[Plan](../experiments/reset_key_unknown_plan.json),
[eingefrorene Auswahl](../experiments/reset_key_selection.json),
[Messübersicht](../results/phase15_summary.json),
[Checkpoint](../checkpoints/phase15_complete.json).
