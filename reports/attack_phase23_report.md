# Forschungsserie 23: Autokey über Seitengrenzen

Stand (UTC): 2026-10-23T11:03:38.159082+00:00. **Keine neue Entschlüsselung bestätigt.**
Vier neue lange Kontrollfälle wurden exakt rekonstruiert. Die unveränderte
Suche lief danach auf zehn bestehenden LP2-Gruppen, die sämtliche 55 unbekannten
Runenseiten abdecken. Die Seitengruppen sind Hypothesen, keine bestätigten
Grenzen einer Chiffre.

## E064: Fortlaufenden Schlüsselstrom auf längeren Texten kalibriert

Der E062-Solver bleibt bytegleich: Startschlüssel mit 4–32 Runen, vier
Vorzeichenpaare, keine ausgelassenen Runen, beide Initialisierungen und alle
nachfolgenden Auswahl- und Verfeinerungsschritte. Neu ist ausschließlich die
Anwendung auf längere, fortlaufende Texte über Seitenwechsel hinweg.
Weder Schlüssel noch Klartextrückkopplung oder Sprachkontext werden zurückgesetzt.

Vier Kontrollen mit jeweils 3.316 Runen verwenden neue Zufallsschlüssel
der Längen 13/23/31/32 und alle vier Vorzeichenpaare. Die Texte stammen aus
bereits betrachteten Bereichen der vom Training ausgeschlossenen Emerson-Kapitel
X/XI/XII. Es sind neue Schlüssel, keine neue unabhängige Textsammlung.
Die künstlichen Seitenlängen entsprechen LP2-40_55 und enthalten eine leere
Spanne nach dem Vorbild LP2-50. Diese verbraucht keine Runen oder Schlüsselwerte.

| Neue Kontrolle | Runen | Startschlüssellänge | Klartext/Schlüssel/Vorzeichen |
|---|---:|---:|---|
| 0 | 3316 | 13 | exakt |
| 1 | 3316 | 23 | exakt |
| 2 | 3316 | 31 | exakt |
| 3 | 3316 | 32 | exakt |

Die zwölf exakten kürzeren E062-Kontrollen wurden über unveränderte Quell-,
Code-, Ausgabe- und Validierungshashes übernommen; ihre Suche wurde nicht
wiederholt. Damit sind vier neue Erfolge und zwölf wiederverwendete Erfolge
dokumentiert. Der komplette Optimierer auf einem pro Seite passenden
diagnostischen Zufallstext erreicht Score -6.248616.
Aus diesem einzelnen Vergleich wird kein p-Wert abgeleitet.

## E065: Unbekannte Seitengruppen direkt angegriffen

Alle zehn bereits festgelegten E012-Gruppen wurden geprüft, einschließlich
der überlappenden Alternativen LP2-40_53, LP2-54_55 und LP2-40_55.
Die kleinste Gruppe hat 308 Runen und liegt im bereits kalibrierten Bereich;
die größte hat 3.316. Dadurch sind auch die in Serie 22 wegen ihrer Kürze
ausgelassenen einzelnen Runenseiten hier innerhalb von Gruppen vertreten.
Originalreihenfolge, Seitenkennungen und Quellreferenzen bleiben erhalten.
Die Zahlen von LP2-50 werden durch die leere Runenspanne nicht entschlüsselt.

| Gruppe | Runen | gefundene Startschlüssellänge | Score |
|---|---:|---:|---:|
| LP2-00_02 | 729 | 32 | -5.378248 |
| LP2-03_07 | 1145 | 29 | -5.701465 |
| LP2-08_14 | 1729 | 31 | -5.960524 |
| LP2-15_22 | 1903 | 30 | -6.014723 |
| LP2-23_26 | 1021 | 30 | -5.669823 |
| LP2-27_32 | 1433 | 32 | -5.823195 |
| LP2-33_39 | 1680 | 31 | -5.906238 |
| LP2-40_53 | 3008 | 32 | -6.244209 |
| LP2-54_55 | 308 | 31 | -4.471883 |
| LP2-40_55 | 3316 | 32 | -6.261514 |

Die höchste Bewertung erhielt **LP2-54_55**. Diese Auswahl
wurde mit den Hashes aller zehn Ergebnisse vor dem Zufallsvergleich fixiert.
19 unabhängige Nulltexte erhalten pro Seite Häufigkeiten, Randrunen und die
Zahl gleicher Nachbarn; leere Spannen bleiben erhalten. Jeder Nulltext durchläuft
denselben vollständigen Optimierer einschließlich aller internen Entscheidungen.

**14/19** Nullscores erreichen mindestens den beobachteten
Wert. Plus-eins-p=0.75, Bonferroni-Korrektur für die Auswahl
unter zehn Gruppen=1.00. Mit 19 Vergleichen ist der
kleinste mögliche korrigierte Wert 0,50; das ist ein grober Vergleich und kein
Signifikanznachweis. Die Suche bleibt heuristisch und die Gruppierung ungesichert.
Ein negativer Befund schließt andere Chiffren oder Fortsetzungsregeln nicht aus.

## Unabhängige Prüfung und Ressourcen

126 Unit-Tests bestanden. Die unabhängige Prüfung rekonstruiert Quellbereiche
aus den erhaltenen Textbytes, berechnet gespeicherte Scores und bedingte
Koordinatenmaxima nach und prüft Rückverschlüsselungen. Zusätzlich wird eine
rollende Schlüsselwarteschlange ausdrücklich über jede Seitengrenze geführt;
an leeren Seiten muss ihr Zustand unverändert bleiben. Alle Nulltexte, Seeds,
Auswahlregeln und Prüfsummen wurden separat nachvollzogen.

34 neue registrierte Aufgaben, 657.460 Sekunden gemessene
erfolgreiche Experimentzeit. Budget 3000 Sekunden pro Serie, höchstens 180 pro
Aufgabe, ein Worker. Höchster abgetasteter Speicherwert
104.1 MiB bei 768 MiB Grenze.
Originalquellen, frühere Ergebnisse und der E062-Solver bleiben unverändert.
Es läuft kein Forschungsprozess weiter.

Nächster ungetesteter Schritt: ein begrenzter Test von Rückkopplungsfaktoren außer +1 und −1, modulo 29, bei Verzögerungen 4–32. Zuerst muss eine feste Auswahl der zu untersuchenden Familien an Kontrollen bestehen; die Arbeiten für kürzere Verzögerungen bleiben ausdrücklich Vorwissen.

[Kontrollplan](../experiments/autokey_section_plan.json),
[Angriffsplan](../experiments/autokey_section_unknown_plan.json),
[Messübersicht](../results/phase23_summary.json),
[Checkpoint](../checkpoints/phase23_complete.json).
