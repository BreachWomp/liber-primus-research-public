# Forschungsserie 22: Längere Autokey-Startschlüssel direkt geprüft

Stand (UTC): 2026-10-22T17:45:25.481371+00:00. **Keine neue Entschlüsselung bestätigt.**
Zwölf Blindkontrollen wurden exakt rekonstruiert. Danach lief dieselbe Suche
auf 46 unbekannten LP2-Seiten; der stärkste Kandidat wurde gegen 19 vollständig
optimierte Zufallstexte geprüft.

## E062: Suchverfahren und Kalibrierung

Untersucht wird `P_i = cs*C_i + ks*P_(i-m) (mod 29)` nach einem unbekannten
Startschlüssel der Länge m. Beide Vorzeichen sind jeweils +1 oder -1.
Alle Runen verbrauchen einen Schritt, einschließlich F. Die affine Darstellung
jeder Restklasse durch ihre erste Klartextrune stammt bereits aus E014/E017;
sie wird hier wiederverwendet und nicht als neue Entdeckung bezeichnet.

E017 erfasste Längen 4–12. Die neue Suche erfasst 4–32 mit vier Vorzeichenpaaren,
also 116 Familien pro Eingabe. Acht Häufigkeitsstarts je Familie werden durch
bis zu sechs vollständige Koordinatendurchläufe auf dem Trigrammziel
verbessert. Daneben läuft eine feste Beam-Suche mit Breite 128, zwei Schnitten
und zwei behaltenen Pfaden pro Schnitt. Beide Mengen werden nach Viergrammen
bewertet; die zwölf besten unterschiedlichen Startkombinationen werden jeweils
bis zu sechs vollständige Koordinatendurchläufe weiter verbessert.
Das ist eine begrenzte Heuristik, kein globaler Optimalitätsbeweis.

Trainiert wird unverändert auf Emerson I, III–IX. Kontrolltexte stammen aus
X/XI/XII, mit separat festgelegten Textbereichen und neuen Zufallsschlüsseln
aus allen 29 Symbolen. Die Kapitel sind historisch bekannt; die Fälle sind
keine unabhängige neue Textsammlung. Die kurzen Schlüssel 4/8/12 sind frische
Regressionstests, keine erneute Ausführung der historischen E017-Kontrollen.

| Kontrolle | Runen | Startschlüssellänge | Klartext |
|---|---:|---:|---|
| 0 | 300 | 13 | exakt |
| 1 | 300 | 23 | exakt |
| 2 | 300 | 31 | exakt |
| 3 | 300 | 4 | exakt |
| 4 | 300 | 8 | exakt |
| 5 | 300 | 12 | exakt |
| 6 | 200 | 13 | exakt |
| 7 | 200 | 23 | exakt |
| 8 | 200 | 31 | exakt |
| 9 | 729 | 13 | exakt |
| 10 | 729 | 23 | exakt |
| 11 | 729 | 31 | exakt |

Alle zwölf Fälle rekonstruieren den vollständigen Klartext; auch die injizierten
Rezepte wurden separat geprüft. Vor der abschließenden Verfeinerung liefert
der Häufigkeitszweig 11/12 und der Beam-Zweig 12/12 exakte
Spitzenkandidaten. Dies ist ein beschreibender Vergleich unterschiedlicher
fester Rechenbudgets, keine Aussage über gleiche Laufzeit oder allgemeine Güte.

### Dokumentierte Abweichung beim diagnostischen Nullversuch

E062-null-2 verwendete versehentlich den bereits vorhandenen Generator für
vollständige Permutationen. Er erhält Häufigkeiten und die Zahl gleicher
Nachbarn, aber nicht die im Plan vorgeschriebenen Randrunen. Die unabhängige
Prüfung hat diese Abweichung erkannt. Ausgabe und Protokoll bleiben unverändert;
der Score -4.352205 wird nicht als
plankonformer Vergleich verwendet. Der separat registrierte Lauf
E062-null-endpoints erhält zusätzlich beide Randrunen und erreicht
-4.317967. Er verwendet denselben Solver und denselben Seed.
Erst nach seiner unabhängigen Prüfung wurde E063 gestartet. Aus einzelnen
diagnostischen Nullversuchen wird kein p-Wert abgeleitet.

## E063: Unbekannte Seiten und Zufallsvergleich

46 unbekannte LP2-Seiten mit mindestens 200 Runen wurden einzeln untersucht.
Neun kürzere Runenseiten sind außerhalb des getesteten Längenbereichs und
wurden in dieser Serie nicht angegriffen. LP2-50 bleibt als Zahlenseite ohne
Runen ausdrücklich erfasst. Vollständige Seiten- und Ausschlusslisten samt
Quellreferenzen stehen im Plan und der Messübersicht. Keine Quellnormalisierung
und keine nachträgliche Anpassung der Suchparameter.

Die fünf höchsten Scores sind:

| Seite | Runen | gefundene Startschlüssellänge | Score |
|---|---:|---:|---:|
| LP2-02 | 201 | 29 | -3.809125 |
| LP2-07 | 208 | 31 | -3.919218 |
| LP2-38 | 228 | 32 | -3.937625 |
| LP2-33 | 214 | 31 | -3.940715 |
| LP2-23 | 213 | 32 | -3.969634 |

Nach allen 46 Seiten wurde **LP2-02** ausgewählt und die
Auswahl samt Ausgabehashes vor den Nullversuchen festgeschrieben. Jede der
19 unabhängigen Permutationen erhält Häufigkeiten, Randrunen und die Zahl
benachbarter gleicher Runen; jede durchläuft alle 116 Familien und dieselbe
abschließende Auswahl und Verfeinerung. **6/19** erreichen
mindestens den beobachteten Score. Plus-eins-p=0.35;
Bonferroni-Korrektur für 46 Seiten=1.00.
Mit nur 19 Nullversuchen kann diese Korrektur keinen signifikanten Wert liefern.
Ein solcher Grobvergleich ist ein Filter gegen zufällige Sprachähnlichkeit;
er bestätigt keinen Klartext und schließt die Chiffrenfamilie nicht aus.

## Prüfung, Ressourcen und nächster Schritt

126 Unit-Tests bestanden. Separater Verifikationscode rekonstruiert die
Klartexte durch eine skalare Schlüsselwarteschlange, prüft Rückverschlüsselung,
Quellbereiche, feste Seeds, gespeicherte Scores, bedingte Koordinatenmaxima und
die Auswahlkorrektur. Einzelne ungeänderte historische Ergebnisse wurden nicht
erneut berechnet. Die genaue Zahl aller Prüfungen steht in der Messübersicht.

79 registrierte Aufgaben, 497.708 Sekunden gemessene erfolgreiche
Experimentzeit. Budget 2400 Sekunden pro Serie, höchstens 180 pro Aufgabe;
ein Worker, höchster abgetasteter Speicherwert 102.7 MiB
bei 768 MiB Grenze. Keine weiterlaufenden Forschungsprozesse.

Nächster Vorschlag, noch ungetestet: Autokey ohne Neustart über vorhandene Seitengruppen hinweg. Zuerst sind längere Kontrollen erforderlich; die Gruppierung selbst bleibt eine Hypothese.

[Kontrollplan](../experiments/autokey_extended_plan.json),
[Nullkorrektur](../experiments/autokey_endpoint_null_plan.json),
[Angriffsplan](../experiments/autokey_extended_unknown_plan.json),
[Messübersicht](../results/phase22_summary.json),
[Checkpoint](../checkpoints/phase22_complete.json).
