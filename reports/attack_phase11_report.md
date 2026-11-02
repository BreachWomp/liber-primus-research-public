# Elfte Forschungsserie: Wortbewertung und fortschreitende Schlüssel

Stand (UTC): 2026-10-20T09:51:13.593977+00:00. **Keine neue Entschlüsselung bestätigt.**

## Direkter Angriff E037

Geprüft wurde `P_i = a*C_i + b*i² + c*i + d mod29`, i=0 am Seitenanfang.
a durchläuft 1–28, b,c,d jeweils 0–28. b=c=0 bleibt ausgespart,
weil konstante affine Ersetzungen bereits untersucht wurden.
**682.080 Regeln je Seite, 37.514.400 Regeln auf allen 55 ungelösten
Runenseiten.** LP2-50 bleibt als Zahlenseite erhalten.

Die Rückverschlüsselung ist `C_i = a^-1*(P_i-b*i²-c*i-d) mod29`.
Keine Rune wird entfernt oder ausgelassen. Keine F-Unterbrechung, Umordnung
oder behauptete Ergänzung. Die Schlüsselfolge hat modulo29 eine Periode, die 29 teilt.
Verschobene Indexursprünge und die Umkehr der Indexrichtung sind bereits in
den Koeffizienten enthalten; sie benötigen keine zusätzliche Suche.
Das ist eine kleine, prüfbare progressive Schlüsselfamilie, kein behaupteter
historischer Hinweis. Beliebige Perioden-29-Schlüssel werden dadurch nicht abgedeckt.

Drei synthetisch verschlüsselte bekannte Texte werden im vollständigen Suchraum
exakt als bestes Ergebnis gefunden, darunter ein linearer Fall mit b=0 und
der kurze LP2-57-Text. Der externe Viergramm-Score von E016 bleibt unverändert.
Kein LP-Text ist Trainingsmaterial; die Kontrolltexte wurden allerdings schon
in früheren Versuchen betrachtet. Dies ist Funktionsvalidierung, keine neue
historische Entschlüsselung.

Stärkster Treffer: **LP2-49**, Score -5.071744.
Regel: `{"a": 9, "b": 27, "c": 25, "d": 22}`.
Unveränderte Transliteration:

```text
RRENGNCTEAIPISTHEATHUICAILANYWOCNGYSEADGODAHLABUSHEOESHSLPEUNFSDRMGEUPHOEXT
```

Dieser Suchtreffer ist kein bestätigter Klartext. Vor den Zufallsversuchen
wurden Auswahl und alle Quellergebnis-Prüfsummen eingefroren.
19 unabhängige Zufallstexte erhalten exakt die Runenhäufigkeiten und die Anzahl
gleicher Nachbarpaare. Jeder durchläuft dieselbe vollständige Suche.
**9/19** erreichen mindestens den beobachteten Score.
Plus-eins-p=0.500; Bonferroni55=1.000.
Die 19 Replikate können korrigierte Signifikanz nicht auflösen.
Dieser Vergleich liefert keinen Anlass, den Treffer als Lösung weiterzuverfolgen.
Der Seitenfaktor ist keine projektweite Korrektur über alle bisherigen
explorativen Hypothesen. Ein negativer Befund widerlegt keine umfassendere
Verschlüsselungsfamilie.

[Plan](../experiments/quadratic_stream_plan.json),
[eingefrorene Auswahl](../experiments/quadratic_stream_selection.json).

## E036: Wortgrenzen beheben das Substitutionsproblem noch nicht

Vor E037 wurde der allgemeine Substitutionssolver mit dem unveränderten
E027-Wortmodell geprüft: `P(w|L)=(count(w)+20*Q(w))/(N_L+20)`.
Q ist das Zeichenmodell, jeweils am Wortanfang neu gestartet.
Training für Wörterbuch und Zeichenmodell ausschließlich auf Emerson I,
III–IX; X, XI, XII ausgeschlossen. Keine LP-Texte im Training.
Diese Kapitel sind gegenüber diesem Training zurückgehalten, wurden aber
schon in früheren Projektphasen verwendet; kein historisch frischer Blindtest.

Höchstens 24 Muster-/Häufigkeitsstarts, erst höchstens 40 vollständige
406-Tausch-Schritte nach Zeichenwertung, dann höchstens 40 nach Wortwertung.
Die endgültige Auswahl erfolgt nur nach Wortwertung.

| Kontrolle | Exakt richtige Runen | Vollständig |
|---|---:|---|
| LP1-03/04, DIVINITY-Text neu substituiert | 515/515 | ja |
| LP1-14/15, CIRCUMFERENCE-Text neu substituiert | 319/319 | ja |
| LP2-57, Direkttext neu substituiert | 94/95 | nein |

Bei LP2-57 wird Offset 25 von NG (Index 21) zu EA (Index 28) geändert.
Der korrekte Text erzielt -1.794298,
der falsche -1.755654.
Der Score bevorzugt den Fehler; zusätzliche Suchzeit allein kann diesen
Rankingfehler nicht beheben. Keine gezielte Modellanpassung an diese Rune.

18 externe Fenster aus X, XI, XII mit je 20 Wörtern und je 20 vorab gesäten
Ein-Runen-Mutationen: Wortscore **355/360**
korrekte Rangfolgen, Zeichenmodell **349/360**.
Das externe Teilkriterium besteht, die geforderte exakte Wiedergewinnung
aller drei LP-Kontrollen jedoch nicht. **Kein unbekannter Text wurde mit
diesem Substitutionssolver gesucht.**
Neun zusätzliche Optimierungsläufe auf Häufigkeits-permutierten Kontrolltexten
sind Fähigkeitsdiagnosen; sie konditionieren nicht auf gleiche Nachbarpaare
und tragen keinen Entdeckungs-p-Wert.

E036 hatte die Nummer E037 bedingt für eine nachfolgende Substitutionssuche
vorgesehen. Diese Bedingung trat nicht ein. E037 bezeichnet stattdessen
den separat festgelegten progressiven Schlüsselstrom mit eigenen Kontrollen.
Der historische E036-Plan wird unverändert erhalten.

[E036-Plan](../experiments/boundary_substitution_plan.json).

## Prüfung und nächster Angriff

**94 Tests bestanden.** Alle 193
gespeicherten E037-Kandidaten wurden unabhängig mit der skalaren Gleichung
entschlüsselt, rückverschlüsselt und neu bewertet. Alle
452 gespeicherten E036-Startläufe
beider Suchstufen wurden als Bijektionen und durch skalare Scores überprüft.
Alle Seeds der Kontrollverschlüsselungen, Mutationen und Zufallstexte wurden
reproduziert; die 18 Prüffenster auf originale Quellenpositionen zurückgeführt
und die Trennung ihrer Quellbereiche vom Training geprüft.
Ergebnis- und Abhängigkeitshashes stimmen.

76 Aufgaben, 365.341 Sekunden protokollierte
Experimentzeit; E037 einschließlich Wiederaufnahme und Reserve
425.845 Sekunden unter 650.
Phasenbudget 900, Einzelaufgabe 180 Sekunden, ein Prozess, begrenzte Arrays.
Keine laufenden Hintergrundjobs, keine neuen Fremdquellen oder Lösungsmeldungen.

Vor Beginn der Nullversuche wurde der Queue-Prozess einmal gestoppt, um einen
kopierten Seed-Vermerk für die Auswahldatei zu korrigieren. Der tatsächliche
Such-/Nullcode und sein vorab festgelegter Seed 3301037 blieben unverändert.
Der aktive LP2-52-Prozess scheiterte bei der Rückmeldung an die geschlossene
Pipe (`OSError(22)`); sein Fehlereintrag bleibt im Log. Dieser fehlgeschlagene
Versuch wurde wiederholt, alle erfolgreich abgeschlossenen Fingerprints
wurden übersprungen. Zusätzlich zu erfolgreichen Prozesszeiten und der neuen
Queuezeit sind 60 Sekunden Reserve für diesen fehlgeschlagenen Lauf
(5,875 Sekunden) und den alten Ablaufaufwand eingerechnet, keine als Messung
ausgegebene Zeit.
[Ablaufvermerk](../checkpoints/phase11_orchestration_interruption.json).

Als nächster direkter Ansatz sind beliebige wiederholte Runenschlüssel
außerhalb des bisherigen Katalogs von 381 Wörtern vorgesehen. Die bekannten
DIVINITY-/CIRCUMFERENCE-Lösungen liefern passende Kontrollen. Perioden 2–16,
Suchbudget und Zufallsvergleich werden vor Ausführung getrennt festgelegt;
heuristische Suche darf nicht als vollständige Prüfung von 29^Periode gelten.
Die allgemeine Substitution bleibt bis zu einer unabhängig begründeten
Verbesserung der Textbewertung zurückgestellt.

[Checkpoint](../checkpoints/phase11_complete.json),
[Messübersicht](../results/phase11_summary.json).
