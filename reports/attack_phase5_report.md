# Fünfte Forschungsserie: selektive Schlüsselsuche und affine Rückkopplung

Stand (UTC): 2026-10-19T12:49:04.023538+00:00. **Keine neue Entschlüsselung bestätigt.**
Die in Serie vier begonnene Wort-/Zahlenstromsuche ist einschließlich Nullvergleich
abgeschlossen. Zusätzlich wurde eine vorher festgelegte Erweiterung der
Klartext-Rückkopplung implementiert, kontrolliert und geprüft.

## E018 abgeschlossen

Alle 55 unbekannten Runenseiten wurden mit 381 kanonischen Wortschlüsselzyklen,
allen Phasen, drei Zahlenstromfamilien, Starts 0–255, vier Vorzeichen und
sämtlichen F-Unterbrechungsteilmengen geprüft. Die Optimierung dieser endlichen
Schlüsselräume ist exakt. Das externe Viergramm-Modell stammt unverändert aus
E016; bekannte Kontrollen DIVINITY, CIRCUMFERENCE und LP2-56 bleiben 3/3 exakt.
Das ist eine erneute Prüfung früherer Familien mit verbessertem Score, keine
unabhängige Entdeckung. Quellen und Normalisierung stehen im
[vorherigen Bericht](attack_phase4_report.md).

Acht bereits fertige Aufgaben wurden über ihre Fingerabdrücke übersprungen:
Kontrollen und sieben Seitengruppen. Die früher abgebrochene Gruppe LP2-35–39
wurde neu gerechnet; sie hatte kein vollständiges Ergebnis. Die historischen
Abbruchdaten, Berichte und Checkpoints wurden nicht umgeschrieben.

Die stärkste Seite ist LP2-49, Score -5.305280.
9 von 19 Zufallstexten erreichen mindestens denselben Score:
Plus-eins-p=0.5, nach Auswahl aus 55 Seiten p=1.
Vollständige Kandidatenausgabe, ausdrücklich **kein bestätigter Klartext**:

```text
RHRIBWTAOTHOTAECETNGPAEFIHPDIANAYDIBHUFCALUNORJUWHAMSNMYNGUXSIBSCDWEYRDL
```

## E019: zusätzliche Multiplikatoren bei Klartext-Rückkopplung

Geprüfte Regel: P_i = a C_i + b P_(i−1) modulo 29, mit einem unbekannten
Startwert P_(-1)=K. a und b durchlaufen 1–28; K durchläuft 0–28.
Die vier bereits durch E014/E017 abgedeckten Vorzeichenpaare werden ausgespart.
Es verbleiben 780 Koeffizientenpaare und 22.620 Varianten je Seite.
Diese Erweiterung ist mathematisch motiviert; es gibt keinen Quellenbeleg
für einen bestimmten Multiplikator.

Die endliche Suche verwendet P_0=x, S_0=0 und S_i=C_i+b S_(i−1):
P_i=a S_i+b^i x. Der zugehörige Schlüssel ist K=b^(-1)(x−a C_0).
Damit entspricht jeder getestete Anfangsklartext genau einem Startschlüssel.
Diese Umformung erlaubt eine vollständige Vektorsuche; sie wurde gegen eine
unabhängige skalare Enumeration aller Koeffizienten und Schlüssel geprüft.
Alle 780 Paare wurden außerdem mit mehreren Schlüsseln auf Umkehrbarkeit getestet.

Drei synthetische Kontrollen verwenden bekannte, nicht im externen Training
enthaltene LP-Texte: DIVINITY mit (a,b)=(5,11), CIRCUMFERENCE mit (13,7),
LP2-57 mit (28,3). Die Schlüssel stammen aus Seed 3301019. Die Suche erhält
keinen wahren Schlüssel oder Multiplikator. Ergebnis: 3/3 exakt.
Die Texte wurden zuvor betrachtet; dies ist keine neue blinde historische Validierung.

Alle 55 Seiten, 1.244.100 vollständige Koeffizienten-/Schlüsselvarianten. Stärkste Seite LP2-55: 115/4000 neue Nullwerte mindestens ebenso hoch; p=0.02899275181204699, seitenkorrigiert 1.

## E020: vorgeschriebene Nachprüfung des ersten auffälligen Scores

Im ersten E019-Vergleich lagen 0 von 19 Nullwerten über dem Score von LP2-55.
Der resultierende Rohwert p=0,05 war wegen der Seitenauswahl kein signifikanter
Befund. Gemäß der vorab festgelegten Eskalationsregel wurden Ciphertext,
Kandidat (a=5, b=20, K=13), Score und vollständige Suchroutine eingefroren.

Vor der Nachprüfung wurden 4.000 neue Nulltexte in 20 festen Chargen zu je 200
registriert (Seed 3301020 plus Chargenindex). Es gab keinen frühen Abbruch
und keine Vermischung mit den ersten 19 Nulltexten. Die größere Kalibrierung
verwendet weiterhin die vollständige unveränderte Optimierung je Nulltext;
sie bewertet nicht nur den einmal gefundenen Schlüssel. Ergebnis:
115 Überschreitungen, frischer Plus-eins-p=0.028993,
nach 55 Seiten p=1.000000, nach den beiden Angriffsfamilien
p=1.000000. Dies liefert keinen korrigiert signifikanten Befund.

Die eingefrorene Ausgabe bleibt unverändert und ist kein verständlicher Klartext:

```text
BUEAUYSHIAYSEONCDCPETEACEEOFATPLTHTYCACYFHOUIROEOPUTOCHERDHTESIALROCUUXSCCNGINCITHNNIA
```

Die Regel enthält keine additive Konstante, keine F-Unterbrechungen, nur einen
Startwert und keinen über Seitengrenzen fortlaufenden Zustand. Negative Resultate
betreffen ausschließlich diesen vollständig angegebenen Raum. Weitergehende
Autokey-Familien werden dadurch nicht ausgeschlossen.

## Zufallsvergleich und Auswahlkorrektur

Die Nulltexte entstehen durch unabhängige Permutationen mit exakten
Runenhäufigkeiten und exakt derselben Anzahl direkt benachbarter gleicher Runen.
Unpassende Permutationen werden verworfen. Jeder akzeptierte Text durchläuft
denselben vollständigen Suchraum wie die ausgewählte Seite. Bonferroni über
55 Seiten berücksichtigt die Seitenauswahl; zusätzlich wird die Auswahl zwischen
E018 und E019 mit Faktor zwei ausgewiesen. Alle Werte stehen in der
[Ergebnisübersicht](../results/phase5_summary.json).
Das Nullmodell bewahrt keine Wortgrenzen oder sonstige höherstufige Struktur.
Die Korrektur gilt für diese Serie, nicht global für alle früheren explorativen
Hypothesen am wiederholt betrachteten Korpus.

19 Nulltexte erlauben keine korrigierte Signifikanz unter 0,05. Diese erste Stufe
prüft Scheinbefunde; E020 führt die vorgeschriebene größere Folgeprüfung aus.
Eine korrekte Rückverschlüsselung allein ist kein Beleg
für echte Sprache. Es wurde kein Klartext durch freie Nachbearbeitung erzeugt.

## Validierung und Fortsetzung

63 Tests bestanden; 354 Kandidatenaufzeichnungen erneut von den
kanonischen Ciphertexten aus zurückverschlüsselt und skalar nachbewertet.
Quell- und Ergebnishashes stimmen mit den registrierten Abhängigkeiten überein.
LP2-50 bleibt als Zahlenseite im Korpus erhalten und wird in diesen Runensuchen
nicht als Eingabetext verwendet.

29 neue erfolgreiche Prozesse, 436.118 Sekunden gemessene
Experimentzeit; längster Prozess 57.061 Sekunden.
Orchestrierung einschließlich Fingerabdruckprüfung:
443.589 Sekunden. Neues Serienbudget
900 Sekunden, Einzelgrenze 180 Sekunden, ein Forschungsprozess gleichzeitig.
E019 hält höchstens 812 Kandidatenzeilen gleichzeitig; Modellarray 29^4 und
begrenzter Cache. Keine Hintergrundaufgaben laufen weiter.

[Checkpoint](../checkpoints/phase5_complete.json),
[Forschungsstand](../research_state.json), [Hypothesen](../hypotheses.json),
[append-only Experimentprotokoll](../experiment_log.jsonl).

Die nächste Priorität ist eine gezielte Prüfung der Quellenbilder und
Zeilenstruktur, bevor eine kleine feste Menge alternativer Leserichtungen
getestet wird. Weitere Textschlüssel brauchen konkrete Quellenhinweise.
Längere allgemeine Rückkopplung wird zunächst auf Aufwand und äquivalente
bereits geprüfte Fälle untersucht.
