# Zwölfte Forschungsserie: beliebige wiederholte Runenschlüssel

Stand (UTC): 2026-10-20T14:42:20.534880+00:00. **Keine neue Entschlüsselung bestätigt.**

## Was der neue Angriff abdeckt

Die bisherigen 381 Schlüsselwörter begrenzten die Schlüsselwerte auf einen
Katalog. E038/E039 lernen stattdessen jeden Schlüsselwert direkt aus den
Runen: `P_i = s*C_i + K_j mod29`, s=+1 oder −1. Der Schlüsselcursor j läuft
zyklisch. Geprüft werden Perioden 1–16, wobei 1 als einfache Vergleichsvariante
enthalten ist. Keine Wörter oder Klartextanfänge werden vorgegeben.

Zwei feste Regeln für F=0: keine Unterbrechung oder jedes F kopieren und den
Schlüsselcursor dort nicht weiterschalten. Das ist noch keine Suche über
beliebige F-Teilmengen. Alle Quellrunen bleiben im bewerteten Text erhalten.
Die Rückverschlüsselung lautet für aktive Positionen
`C_i = s*(P_i-K_j) mod29`; kopierte Positionen bleiben F.

Je Vorzeichen, F-Regel und Periode vier Starts: Spaltenmaximum unter dem
Unigramm-Modell, ein gestörter Start und zwei Zufallsstarts.
Je Start höchstens 12 Koordinatendurchläufe mit Bigrammen und anschließend
12 mit Viergrammen. Pro Koordinate werden alle 29 Schlüsselwerte geprüft.
Die lokalen Score-Änderungen umfassen alle betroffenen Kontextfaktoren,
auch diejenigen neben kopierten F-Runen, und sind mathematisch exakt.
Die globale Schlüsselsuche bleibt **heuristisch**, kein Durchsuchen von
29^Periode.

Endgültige Bewertung:
`(Summe der Viergramm-Logwahrscheinlichkeiten − primitive Schlüssellänge*ln29)/Runenzahl`.
Der feste Längenabzug vermindert den Vorteil längerer, flexiblerer Schlüssel.
Er ist ein Beschreibungslängen-Kriterium, keine Wahrscheinlichkeit dafür,
dass ein Text richtig ist. Kürzere primitive Wiederholungen werden erkannt.
Die Suche innerhalb einer festen Periode optimiert die Sprachwertung;
der Längenabzug wird auf die endgültigen Kandidaten angewandt.

## E038: acht Kontrollen exakt

Die tatsächlichen Chiffren der bekannten Abschnitte LP1-03/04 (DIVINITY) und
LP1-14/15 (CIRCUMFERENCE) werden samt Schlüssel exakt wiedergewonnen.
**Ihre dokumentierten F-Unterbrechungen wurden dabei vorgegeben.**
Dies prüft unbekannte Schlüssel bei bekanntem Zeitplan; es beweist keine
Wiedergewinnung der Unterbrechungspositionen.

Sechs weitere Kontrollen: die ersten zwei geeigneten Absätze aus Emerson
X, XI, XII, jeweils die ersten 200 Runen, mit zufälligen Schlüsseln der
Länge 5 beziehungsweise 13 und beiden Vorzeichen. Bei diesen Kontrollen
werden Schlüssel, Periode, Vorzeichen und F-Regel gesucht. Alle sechs
Texte werden ohne vorgegebene Unterbrechungen exakt gefunden.

Training ausschließlich auf I, III–IX: **207.030 Runen**, keine LP-Texte
und keine Kapitel X, XI, XII. Die Quellen wurden schon in früheren Serien
verwendet; dies ist eine aktuelle Trainingstrennung, kein historisch neuer
Blindtest. Das Wortmodell aus E036 wird hier nicht verwendet.

Drei zusätzliche, vollständig optimierte Kontroll-Nulltexte erhalten
Runenhäufigkeiten und die Zahl gleicher Nachbarpaare. Sie dienen nur als
Fähigkeitsdiagnose, ohne Entdeckungs-p-Wert.

[Kontrollplan](../experiments/periodic_key_plan.json).

## E039: alle 55 unbekannten Runenseiten

Pro Seite 64 Kombinationen aus Vorzeichen, F-Regel und nominaler Periode,
je vier Starts. LP2-50 bleibt als Zahlenseite erhalten.
Keine Quellenänderung, keine vorgegebenen Schlüssel und keine
Unterbrechungs-Orakel bei den unbekannten Seiten.

Stärkster Suchtreffer: **LP2-49**.
Bewertungswert mit Längenabzug -3.981681,
reine Sprachwertung -3.165367.
Vorzeichen 1, F-Regel `all_F`,
primitive Schlüssellänge 16.
Schlüssel als Runenindizes: `[20, 5, 28, 9, 7, 14, 11, 23, 23, 18, 2, 27, 9, 21, 20, 24]`.

```text
EDIFFFATRSARBABYMMANYCULSPLEACONOFSOCRYACHIMLFEISHIARMYHENTESAITORE
```

Dies ist eine unveränderte Suchausgabe, **kein bestätigter Klartext**.
Seitenauswahl und Ergebnisprüfsummen wurden vor den Nullversuchen eingefroren.
19 unabhängige Zufallstexte erhalten genau die Runenhäufigkeiten und die Zahl
gleicher Nachbarpaare dieser Seite. Jeder durchläuft wieder alle 64 Familien
und vier Starts; die F-Positionen werden aus jedem Zufallstext neu bestimmt.
So werden auch die flexible Schlüsselwahl und die F-Regel ausgewählt.

**5/19** erreichen mindestens den beobachteten Bewertungswert.
Plus-eins-p=0.300, Bonferroni55=1.000.
Der Treffer ist dadurch nicht als Lösung gestützt.
19 Replikate können korrigierte Signifikanz nicht auflösen.
Die Seitenkorrektur ist keine projektweite Bestätigung über alle früheren
Versuchsfamilien. Der Befund widerlegt weder beliebige wiederholte Schlüssel
noch selektiv unterbrochene Schlüsselströme.

[Angriffsplan](../experiments/periodic_key_unknown_plan.json),
[eingefrorene Auswahl](../experiments/periodic_key_selection.json).

## Unabhängige Prüfung und nächster Schritt

**96 Tests bestanden.**
Alle **5631 gespeicherten Familienmaxima und
Top-Kandidaten** aus 85 Suchausgaben wurden
mit einem skalaren Prüfer rückverschlüsselt und neu bewertet, einschließlich
Schlüsselperioden, F-Zeitplan und Längenabzug. Die lokalen Faktoränderungen
wurden durch Tests gegen vollständiges Neuberechnen sämtlicher 29
Nachbarschlüssel geprüft.
Alle Kontrolltexte sind auf Quellpositionen zurückgeführt; externe
Trainingsbereiche und Prüffenster überschneiden sich nicht. Die sechs
Verschlüsselungen und alle 22 Zufallsfolgen wurden aus ihren Seeds
unabhängig reproduziert. Ergebnis- und Abhängigkeitshashes stimmen.

75 registrierte Aufgaben,
192.481 Sekunden erfolgreiche Experimentzeit.
E039 einschließlich Ablaufaufwand 193.075 Sekunden,
unter dem Familienbudget von 650 Sekunden; Gesamtbudget 900,
maximal 180 je Aufgabe, ein Prozess. Keine Hintergrundjobs bleiben aktiv.

Der nächste direkte Ansatz ist die gemeinsame Suche nach Schlüssel
**und** selektiven F-Unterbrechungen. Die beiden tatsächlichen historischen
Chiffren liefern dafür strenge Kontrollen: Beide enthalten sowohl
übersprungene als auch normal verschlüsselte F-Runen. Ein neuer Solver muss
die Texte samt Zeitplan ohne vorgegebene Skip-Positionen wiedergewinnen,
bevor er auf unbekannte Seiten angesetzt wird.

[Checkpoint](../checkpoints/phase12_complete.json),
[Messübersicht](../results/phase12_summary.json).
