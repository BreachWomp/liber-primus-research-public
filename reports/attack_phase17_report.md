# Siebzehnte Forschungsserie: Lange Schlüssel und ein nachgewiesener Suchengpass

Stand (UTC): 2026-10-21T10:24:33.561076+00:00. **Keine neue Entschlüsselung bestätigt.**
Die neue Suche wurde wegen eines verfehlten Kontrollkriteriums nicht auf
unbekannte Liber-Primus-Seiten angewandt.

## E049: Schlüssel mit nominell 17–32 Runen

Regel unverändert: `P_i=s*C_i+K_j mod29`, s=±1, selektive Chiffren-F-Kopie
ohne Cursorverbrauch. Schlüssel und Sprachkontext laufen durch den gesamten
Text. Der Kandidatenscore bleibt `mean(logp4)-(m*ln29+F_count*ln2)/N`.
Nominelle Perioden 17–32; keine neue nominelle Suche über 1–16.
Kürzere primitive Teiler können bei der Optimierung entstehen.

Startfenster: ganzer Text bis 1.024 Runen, sonst erste/letzte 1.024, dazu drei
längste F-freie Abschnitte ab 64 Runen, begrenzt auf 512. Vier E038-Starts
pro Familie, zwölf zyklisch deduplizierte Schlüsselstarts. Exakte F-Suche
über alle Phasen bei festem Schlüssel; bis zu drei Runden aus sechs
Koordinatendurchläufen und erneuter Zeitplanoptimierung.
Eingaben 512–4096 Runen, maximal 32 Schlüsselstellen und 256 DP-Zustände.

| Kapitel | Schlüssellänge | Runen | Text, Schlüssel und F-Maske |
|---|---:|---:|---|
| X | 17 | 3316 | exakt |
| XI | 23 | 1200 | exakt |
| XII | 31 | 1200 | fehlgeschlagen |

Kontrolltexte und Quellbereiche stammen aus E043; neue nichtnullige
Zufallsschlüssel, Vorzeichen +1, −1, +1; jede zweite Klartext-F wird kopiert.
Training weiterhin Emerson I, III–IX, Kontrollen X, XI, XII, disjunkte
Originalbereiche. Bereits bekannte Kapitel, keine historisch blinde Prüfung.
Ein XI-Nulltext durchläuft den vollständigen Solver mit erhaltenen
seitenweisen Runenhäufigkeiten, Randrunen und gleichen Nachbarpaaren.

## E050: Ursache unterscheiden

Bei der 31-Runen-Kontrolle sind nur **59/1200 Runen** richtig.
Der tatsächliche Klartext hat Score **-2.309824**, der gefundene
Kandidat **-5.810931**: ein Unterschied von
**3.501106 zugunsten des richtigen Textes**.
Der echte Schlüssel ist weder unter den zwölf Startschlüsseln noch unter
deren Endschlüsseln. Alle zwölf Starts stammen aus demselben nur 65 Runen
langen F-freien Abschnitt. Bei den erfolgreichen 17/23-Kontrollen entsteht
der genaue Schlüssel ebenfalls erst durch die nachfolgenden Verbesserungen.

Zwei ausdrücklich mit Lösungswissen unterstützte Diagnosen:

* Vorgegebener Schlüssel samt Vorzeichen: exakte F-Maske wiedergefunden.
* Vorgegebene Länge 31 und richtige F-Maske der ersten 1.024 Runen:
  Schlüsselwerte und Präfixtext exakt gefunden.

Diese Oracle-Versuche sind **keine eigenständige Entschlüsselung**.
Sie zeigen, dass die richtige Ausgabe besser bewertet wird und die
Teiloptimierer mit den genannten Hilfen funktionieren. Der blinde
Suchlauf findet den Schlüssel dennoch nicht; daraus folgt kein Ausschluss
langer Schlüssel als tatsächlicher Chiffre.

## E051: Begrenzter Reparaturversuch

Vor dem Lauf separat registrierte, ausdrücklich adaptive Änderung:
zwölf längste F-freie Fragmente ab 16 Runen, je maximal 256, gemeinsam auswerten.
Jedes Fragment darf bei einer anderen Schlüsselphase beginnen. Die bisherigen
zwölf Starts werden durch zwei Runden gemeinsamer Koordinaten- und exakter
Phasenoptimierung verbessert, danach erfolgt die bisherige vollständige
F-Zeitplansuche auf dem Originaltext. Keine korrekten Schlüsselwerte oder
Masken an den Solver. Auswahl und Parameter wurden aber nach Kenntnis des
E049-Fehlers festgelegt; das ist keine unabhängige Kontrollprüfung.

12 Fragmente, zusammen 512 Runen.
Reparatur exakt: **False**;
78/1200 richtige Runen, Score -5.870172.
Ein passender Nulltext mit vollständiger Neuoptimierung hat
Score -5.770010. Diese einzelne Diagnose erhält keinen p-Wert.
Der Reparaturversuch erfüllt die Voraussetzung für unbekannte Seiten nicht.

## Validierung und nächste Richtung

108 Tests bestanden. 342 Zwischen-/Endkandidaten,
72 Starts und 72 Suchverläufe skalar
nachgerechnet und rückverschlüsselt. Zusätzlich 72
Fragmentzustände einschließlich Phasen, Bewertungen und bedingten Maxima
geprüft; 6 vollständige Suchausgaben mit separatem
Score-Viterbi bestätigt. Kontrolltexte, neue Schlüssel und beide Nulltexte
aus Originalbereichen beziehungsweise Seeds reproduziert. Alle Ergebnis-
und Abhängigkeitshashes stimmen.

3 Experimente, 162.750 Sekunden erfolgreiche Experimentzeit;
je maximal 180, Phasenbudget 900, ein Worker. Keine Quellbytes verändert,
keine alten Ergebnisse überschrieben, keine Hintergrundprozesse.

Nächster Ansatz ist eine andere Initialisierung der langen Schlüssel:
mehrere deterministische Starts pro Periode, zunächst gemeinsame
Einzelrunen-Häufigkeiten und unbekannte Fragmentphasen, danach Viergramme.
Das muss an frischen Kontrollbereichen und den bisherigen Regressionen
bestehen. Weitere Anpassung nur an denselben fehlgeschlagenen Klartext
wäre kein belastbarer Fortschritt.

[E049-Plan](../experiments/long_key_plan.json),
[Oracle-Diagnoseplan](../experiments/long_key_diagnostic_plan.json),
[Reparaturplan](../experiments/pooled_long_key_plan.json),
[Messübersicht](../results/phase17_summary.json),
[Checkpoint](../checkpoints/phase17_complete.json).
