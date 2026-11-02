# Zehnte Forschungsserie: Rückkopplung und allgemeine Runen-Ersetzung

Stand (UTC): 2026-10-20T09:32:00.344537+00:00. **Keine neue Entschlüsselung bestätigt.**

## E034: Eine bisher offene Erweiterung vollständig geprüft

Die Regel lautet `P_i = a*C_i + b*P_(i-1) + d mod 29`, mit einem unbekannten
Anfangswert `P_-1 = K`. a, b und d durchlaufen jeweils 1–28, K alle 29 Werte.
**636.608 Regeln je Seite; 35.013.440 Regeln auf allen 55 ungelösten Runenseiten.**
LP2-50 bleibt als reine Zahlenseite erhalten. Jede Rune einschließlich der ersten
wird bewertet. Kein F-Skip, keine Umordnung und keine seitenübergreifende Fortsetzung.

E019 hatte den konstanten Term explizit ausgeschlossen. `d=0` bleibt daher hier
ausgespart; seine Koeffizientenfälle wurden in E019 und E014 behandelt. Für b≠1
kann d durch eine Klartextverschiebung absorbiert werden, für b=1 kumuliert es.
Das motiviert die endliche Erweiterung, liefert aber keinen historischen Schlüssel.

Mit x=P0 berechnet die Suche die Basisfolgen
`S0=0, q0=1, t0=0`, danach
`S_i=C_i+b*S_(i-1), q_i=b*q_(i-1), t_i=1+b*t_(i-1)`.
Dann ist `P_i=a*S_i+q_i*x+d*t_i`. Der Schlüssel
`K=b^-1*(x-a*C0-d)` ist für feste a,b,d bijektiv zu x.
Diese Formel funktioniert auch für b=1; es gibt keine Division durch b−1.
Die Rückverschlüsselung `C_i=a^-1*(P_i-b*P_(i-1)-d)` ist eindeutig.

Drei synthetisch verschlüsselte bekannte Texte werden im vollständigen Suchraum
jeweils exakt als bestes Ergebnis zurückgewonnen; eine Kontrolle verwendet b=1.
Kontrollen sind Funktionsprüfungen, keine historische Entschlüsselung.
Der externe Viergramm-Score von E016 bleibt unverändert; keine LP-Texte im
Training und keine Anpassung an unbekannte Ausgaben.

[Festgelegter Plan](../experiments/offset_feedback_plan.json).

## Ergebnis und Zufallsvergleich

Stärkster Suchtreffer: **LP2-49**, Score -5.051735.
Unveränderte Transliteration:

```text
THPTSWIOCUMFNTESIFLOGYWOFWNGFGOECWSOEFAEATHLOGRPBRHEGOOAHFUAURROOSMWWTHEOE
```

Regel: `{"a": 6, "b": 12, "d": 26, "initial_key": 28, "initial_plaintext": 2, "F_policy": "none"}`.
Dies ist ein gespeicherter Suchtreffer, **kein bestätigter Klartext**.

Vor Beginn der Zufallsversuche wurden Seitenauswahl und alle Ergebnisprüfsummen
eingefroren. 19 unabhängige Zufallstexte erhalten exakt die Runenhäufigkeiten
und die Anzahl gleicher Nachbarpaare der gewählten Seite. Jeder durchläuft
denselben vollständigen Suchraum von 636.608 Regeln.

**7/19** erreichen mindestens den beobachteten Score.
Plus-eins-p=0.400; Bonferroni über 55 Seiten=1.000.
19 Replikate können korrigierte Signifikanz nicht auflösen.
Dieser Befund begründet keine größere Kalibrierung des Treffers.
Die Untersuchung folgt früheren explorativen Familien; der Seitenfaktor ist
keine projektweite Bestätigungskorrektur und das Korpus kein frischer Blindtest.

[Eingefrorene Auswahl](../experiments/offset_feedback_selection.json).

## E035: Allgemeine Runen-Ersetzung – zwei Kontrolltexte exakt

Zusätzlich wurde ein begrenzter Prototyp für beliebige bijektive Ersetzungen der
29 Runen geprüft. Anders als affine Abbildungen kann er auch nichtlineare
Permutationen darstellen. Wörter mit gleichem Wiederholungsmuster liefern
Startbelegungen aus dem unveränderten externen Wörterbuch. Diese sind Suchstarts,
keine behaupteten Klartextwörter oder erzwungenen Lösungen.

Höchstens 24 deduplizierte Starts, je höchstens 40 Verbesserungsschritte; pro
Schritt werden alle 406 Vertauschungen zweier Schlüsselwerte bewertet.
Dies ist eine begrenzte heuristische Suche, keine vollständige Prüfung von 29!.
Kein Test auf unbekannten Seiten.

| Kontrolltext | Korrekte Runen | Vollständig |
|---|---:|---|
| LP1-03/04, bekannte DIVINITY-Lösung, neu zufällig substituiert | 515/515 | ja |
| LP1-14/15, bekannte CIRCUMFERENCE-Lösung, neu zufällig substituiert | 319/319 | ja |
| LP2-57, bekannter Direkttext, neu zufällig substituiert | 93/95 | nein |

Beim kurzen Kontrolltext bewertet das feste Viergramm-Modell die falsche Ausgabe
mit -1.906461 sogar höher als den korrekten Text
(-1.931762). Betroffen sind Runenoffsets 25 und 80.
Damit liegt nachweislich eine Grenze des Ranking-Scores vor. Mehr Laufzeit allein
kann den richtigen Text unter diesem unveränderten Ziel nicht zum Maximum machen.
**Exaktes Kontroll-Gate verfehlt, deshalb keine unbekannte Seite mit E035 gesucht.**

Je Kontrolltext wurden drei zufällige Vergleichstexte mit identischen
Runenhäufigkeiten und Segmentendpunkten durch denselben Optimierer verarbeitet.
Diese neun Fähigkeitsdiagnosen konditionieren ausdrücklich **nicht** auf gleiche
Nachbarpaare und tragen keinen Entdeckungs-p-Wert. Ein späterer Angriff braucht
eine vorab festgelegte, stärkere vollständige Nullkalibrierung.
Die bekannten Kontrolltexte wurden früher bereits betrachtet; keine blinde
historische Validierung und keine neue Entschlüsselung.

[Prototyp-Plan](../experiments/substitution_prototype_plan.json).

## Unabhängige Prüfung und Rechenbudget

**89 Tests bestanden.** Der skalare Prüfer reproduziert alle **193
gespeicherten E034-Kandidaten** durch Entschlüsselung und Rückverschlüsselung und
berechnet ihre Scores erneut. Die Testfälle vergleichen die vektorisierte
Suche mit vollständiger unabhängiger Enumeration eines kleinen Gitters.
Basisformeln und Invertierbarkeit werden für alle nichtnulligen Koeffizienten
geprüft. Zusätzlich wurden alle 225 gespeicherten E035-Startläufe als
vollständige Bijektionen, durch Rückverschlüsselung und durch skalare Neubewertung
kontrolliert. Alle 19 E034-Zufallstexte wurden aus den festgelegten Seeds unabhängig
bis zur ersten akzeptierten Permutation reproduziert.

Alle Ergebnis- und Abhängigkeitshashes stimmen. Historische Ergebnisse bleiben
erhalten, das Experimentprotokoll wurde ausschließlich ergänzt. Keine neuen
Fremdquellen oder Lösungsmeldungen untersucht.

76 Aufgaben, 334.773 Sekunden protokollierte Experimentzeit, E034 davon
327.674 Sekunden.
Queue 328.542 Sekunden plus 16.476
Sekunden bereits abgeschlossener Kontrolllauf, unter 750 Sekunden Familienbudget.
180 Sekunden je Aufgabe, ein Prozess; höchstens 2048 Kandidatenzeilen gleichzeitig.
Kein Hintergrundprozess bleibt aktiv.

## Nächster direkter Ansatz

Den E035-Substitutionsprototyp
mit einem separat festgelegten externen Wortgrenzen-Score weiterprüfen.
Die zwei längeren Kontrollen zeigen, dass der Ansatz praktisch ganze Texte
zurückgewinnen kann; die kurze Kontrolle verhindert derzeit die Eskalation.
Wörterbuchlücken dürfen nicht als Widerlegung ausgegeben werden.
Ein vollständiger Zufallsvergleich muss vor einer größeren Seitensuche finanzierbar
sein. Abstand-drei-Rückkopplung bleibt wegen des höheren Aufwands zurückgestellt.

[Checkpoint](../checkpoints/phase10_complete.json), [Messübersicht](../results/phase10_summary.json).
