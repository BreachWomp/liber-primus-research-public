# Dreizehnte Forschungsserie: Schlüssel und F-Unterbrechungen gemeinsam finden

Stand (UTC): 2026-10-20T14:59:36.073719+00:00. **Keine neue Entschlüsselung bestätigt.**

## Fortschritt an überprüfbaren Kontrollen

E040 rekonstruiert die tatsächlichen Chiffren der bekannten Abschnitte
LP1-03/04 (DIVINITY) und LP1-14/15 (CIRCUMFERENCE) vollständig:
**Klartext, Schlüssel und dokumentierte F-Unterbrechungen stimmen exakt.**
Weder Schlüssel noch Unterbrechungspositionen wurden dem Solver übergeben.
Die Eingaben sind dieselben auf die Quellen zurückgeführten Chiffren wie zuvor.
Das ist eine verbesserte Replikation bekannter Lösungen, keine neue
historische Entschlüsselung.

E041 prüft denselben unveränderten Solver an sechs externen Texten aus
Emerson X, XI, XII, je 350 Runen. Zufällige Schlüssel der Längen 5 und 13,
beide Vorzeichen; jede zweite Klartext-F-Rune wird kopiert und verbraucht
keinen Schlüsselwert. Alle anderen Positionen werden regulär verschlüsselt.
Diese Regel dient nur der kontrollierten Herstellung der Chiffre; der
Solver erhält weder Regel, Klartext, Schlüssel noch Zeitplan.
**Alle sechs Texte, Schlüssel und Unterbrechungsmasken exakt.**
Nichtnullige eingesetzte Schlüsselwerte vermeiden hier die Mehrdeutigkeit
zwischen einem kopierten F und einer normal verschlüsselten F-Chiffrenrune.

Training weiter ausschließlich auf I, III–IX: 207.030 Runen, keine LP-Texte
und keine Kapitel X, XI, XII. Die Quellen waren in früheren Forschungsserien
bereits vorhanden; keine Behauptung einer historisch neuen Blindprüfung.
Zwei historische und drei externe Kontroll-Nulltexte durchlaufen ebenfalls
den vollständigen Optimierer, als Fähigkeitsdiagnose ohne Entdeckungs-p-Wert.

[Historischer Kontrollplan](../experiments/joint_skip_plan.json),
[externer Kontrollplan](../experiments/joint_skip_external_plan.json).

## Wie die gemeinsame Suche funktioniert

Regel: `P_i = s*C_i + K_j mod29`, s=+1 oder −1. An einer Chiffrenrune F=0
darf alternativ F kopiert werden, ohne j weiterzuschalten.
Jede Quellrune bleibt im bewerteten Text erhalten.

Schlüsselstarts stammen aus dem ganzen Text unter den zwei einfachen
Zeitplänen sowie aus den drei längsten maximalen F-freien Abschnitten
mit mindestens 32 Runen, jeweils auf höchstens 256 Runen begrenzt.
In einem F-freien Abschnitt kann kein solcher Skip auftreten.
Perioden 1–16 und beide Vorzeichen werden geprüft; primitive Schlüssel
werden unter zyklischer Rotation dedupliziert, zwölf Starts behalten.
Die Rangfolge benutzt die feste Sprachwertung mit Schlüssellängenabzug.
Das ist keine Garantie, dass der richtige Schlüssel unter diesen zwölf ist.

Für jeden festen Schlüssel findet dynamische Programmierung den global
besten F-Zeitplan und die beste Anfangsphase. Zusammenführen darf sie nur
Zustände mit gleichem Schlüsselcursor und gleichem Sprachkontext.
Bei einem Viergramm-Modell reichen höchstens acht Zustände je Cursor:
Die letzten drei binären F-Entscheidungen und der Cursor bestimmen den
Kontext. Die gemessenen Zustandszahlen wurden gegen diese Schranke geprüft.

Danach wechseln sich höchstens drei Runden aus Schlüsselverbesserung
bei festem Zeitplan und erneuter exakter Zeitplanoptimierung ab.
Je Schlüsselrunde höchstens sechs Koordinatendurchläufe, jeweils alle
29 Werte pro Schlüsselstelle. **Die Schlüsselsuche bleibt heuristisch;
exakt ist die Zeitplanoptimierung bei festem Schlüssel.**

Endbewertung:
`(Summe logp − primitive Schlüssellänge*ln29 − Anzahl Chiffren-F*ln2)/Runenzahl`.
Der letzte Term rechnet eine binäre Entscheidung je möglicher F-Stelle an;
er ist innerhalb derselben Seite konstant. Keine gefittete Skip-Wahrscheinlichkeit.
Dies ist ein Beschreibungslängen-Kriterium, keine Wahrscheinlichkeit,
dass ein Suchtreffer richtig ist.

## E042: Angriff auf alle 55 unbekannten Runenseiten

Der unveränderte Solver wurde auf LP2-00 bis LP2-55 angewandt; die Zahlenseite
LP2-50 bleibt erhalten und wird nicht als Runenchiffre behandelt.
Keine Kandidatenanpassung der Parameter, keine vorgegebenen Klartextwörter.
Seiten werden in diesem Versuch einzeln mit eigenem Cursor behandelt.

Stärkster Suchtreffer: **LP2-49**,
Bewertungswert -3.946618, reine Sprachwertung -3.109299.
Vorzeichen 1, Schlüsselindizes `[11, 14, 3, 15, 15, 14, 11, 25, 28, 18, 2, 26, 11, 21, 20, 24]`.
Kopierte F-Positionen (nullbasierte Runenoffsets): `[3, 33]`.
Die Rückverschlüsselung ist an aktiven Stellen
`C_i=s*(P_i-K_j) mod29`; an den gespeicherten Skip-Positionen bleibt F stehen.

```text
NOXFGHATGLARTYBYMIRPOPULBELEDWONOFGEONICACISMLEALISHEPDOTENEDSANEORE
```

Unveränderte Suchausgabe, **kein bestätigter Klartext**.
Die Seite und alle Quellergebnis-Prüfsummen wurden vor Nullgenerierung
eingefroren. 19 unabhängige Zufallstexte erhalten exakt Runenhäufigkeiten
und die Zahl gleicher Nachbarpaare. Jeder sucht seine eigenen F-freien
Abschnitte, Schlüsselstarts, Phasen und Unterbrechungsmasken mit demselben
vollständigen Optimierer.

**3/19** erreichen mindestens den beobachteten Wert.
Plus-eins-p=0.200, Bonferroni55=1.000.
Der Treffer wird dadurch nicht als Lösung gestützt.
19 Replikate können korrigierte Signifikanz nicht auflösen. Die Seitenkorrektur
ist keine projektweite Korrektur über alle bisherigen explorativen Familien.
Ein negativer Befund widerlegt keine beliebigen Schlüssel oder andere
Unterbrechungszeichen.

[Angriffsplan](../experiments/joint_skip_unknown_plan.json),
[eingefrorene Auswahl](../experiments/joint_skip_selection.json).

## Unabhängige Prüfung und weitere Richtung

**98 Tests bestanden.**
4226 gespeicherte Zwischen-/Endkandidaten
und 1044 Schlüsselstarts wurden durch skalare
Entschlüsselung, Rückverschlüsselung und Neubewertung geprüft.
1044 Suchverläufe haben konsistente, nicht fallende Scores.
Für die Sieger aller 87 Suchausgaben wurde
das globale Zeitplanmaximum mit einem separaten, nur Scores speichernden
Viterbi-Prüfer erneut berechnet. Kleine Tests vergleichen alle Phasen und
Skip-Teilmengen vollständig durch Enumeration.

Externe Klartexte wurden auf Original-Quellbereiche zurückgeführt,
Trainingsüberschneidungen ausgeschlossen und alle Schlüssel,
Kontrollmasken sowie 24 Zufallsfolgen aus den festen Seeds reproduziert.
Alle Ergebnis- und Abhängigkeitshashes stimmen.
76 Aufgaben, 359.573 Sekunden erfolgreiche
Experimentzeit. E042 einschließlich Ablaufaufwand
319.066 Sekunden unter 650;
Phasenbudget 900, maximal 180 je Aufgabe, ein Prozess.
Keine neuen Fremdquellen oder Lösungsmeldungen, keine verbleibenden Hintergrundjobs.

Als nächste direkte Hypothese ist ein gemeinsamer Schlüssel über
Seitengrenzen vorgesehen. Die historischen Kontrolltexte erstrecken sich
ebenfalls über mehrere Seiten. Bereits gepinnte E012-Gruppierungen können
dafür explizite Prüfhypothesen liefern; sie sind keine authentifizierten
Chiffregrenzen. Längere Eingaben, Kontrollen und vollständige Nulloptimierung
müssen vor dem Angriff separat begrenzt und festgelegt werden.

[Checkpoint](../checkpoints/phase13_complete.json),
[Messübersicht](../results/phase13_summary.json).
