# Vierte Forschungsserie: Sprachmodell und längere Autokey-Schlüssel

Stand (UTC): 2026-10-19T12:37:30.387846+00:00. **Keine neue Entschlüsselung bestätigt.**
Der Fortschritt ist methodisch: Die bisherigen Fehler bei bekannten
F-Unterbrechungen werden mit einem unabhängig trainierten Sprachmodell behoben.
Der abgeschlossene Angriff auf unbekannte Autokey-Schlüssel liefert keinen
belastbaren Klartext. Die erneute selektive Schlüsselsuche ist separat ausgewiesen.

## Sprachmodell und Kontrollen (E016)

Die unveränderte, bereits gepinnte [Gutenberg-Ausgabe 2944](https://www.gutenberg.org/ebooks/2944)
liefert 265.129 Runen in 393 Absätzen aus elf Emerson-Essays.
Self-Reliance ist vollständig ausgeschlossen, weil dieser Text in E013 als
Schlüssel getestet wurde. Kein Liber-Primus-Klartext oder -Ciphertext wird zum
Training verwendet. Das [Quellenmanifest](../sources/emerson_manifest.json)
enthält Abrufzeit und SHA-256; Abschnittsgrenzen stehen in den Ergebnissen.

Die explizite Verarbeitung erweitert ae/oe-Ligaturen, entfernt kombinierende
Akzente nach NFKD, liest ASCII-Wörter, ersetzt QU durch CW und übriges Q durch C
und verwendet die vorhandene gierige GP-Kodierung innerhalb jedes Worts.
Nichtlateinische Buchstaben sind inventarisiert und werden nicht kodiert.
Absatzgrenzen werden beim N-Gramm-Training nicht überschritten. Die Quelldatei
selbst bleibt unverändert. Ein eigener Wortgrenzen-Score wurde nicht implementiert.

Zwei vorab festgelegte Backoff-Modelle (Ordnung 3 und 4, alpha=0,5, Stärke=5)
gewinnen **alle drei bekannten selektiven Kontrollfälle exakt** zurück:
DIVINITY, CIRCUMFERENCE und LP2-56. Einschließlich der richtigen F-Unterbrechungen;
LP2-56 verwendet ausschließlich die Unterbrechung an Runenoffset 56 (nullbasiert).
Mit bekannten Schlüsseln werden alle Phasen beziehungsweise Starts 0–255 durchsucht.

Bei je 200 Mutationen an acht unstrittigen Kontrolltexten wird der echte Text
1542/1600-mal (Ordnung 3) beziehungsweise 1563/1600-mal (Ordnung 4) höher bewertet.
Die Mutationen sind korreliert; dies sind deskriptive Werte, keine p-Werte.
Die früheren 1105/1200 Vergleiche betrafen einen anderen Kontrollumfang und sind
kein direkt vergleichbarer Ausgangswert. Alle LP-Kontrollen waren bereits bekannt:
unabhängige Trainingsdaten bedeuten **keine neue blinde Validierung**.

## Unbekannte Autokey-Startschlüssel (E017)

Alle 55 unbekannten LP2-Runenseiten wurden mit Schlüssellängen 4–12, vier
Vorzeichenkombinationen und den Regeln keine/alle F-Unterbrechungen geprüft.
Die Suche zerlegt die Klartextrückkopplung in zyklische Trigramm-Faktoren.
Pro Erweiterung bleiben höchstens 512 Pfade; alle zyklischen Schnitte werden
versucht, die besten 16 Kandidaten je Schnitt anschließend mit dem Viergramm-
Modell bewertet. **Dies ist eine begrenzte Heuristik, keine vollständige Suche
über alle 29^12 Schlüssel.**

Sechs synthetische Kontrollen (zwei bekannte LP1-Texte, jeweils zufällige Schlüssel
der Längen 4, 8 und 12; Seed 3301017) wurden im vollständigen Suchraster exakt
als beste Ausgabe gefunden. Der Suche wurden weder Schlüssel noch wahre Länge
übergeben. Die injizierten Kontrollen haben keine Unterbrechungen; sie validieren
nicht jede mögliche Unterbrechungsregel oder Textverteilung.

Stärkster unbekannter Kandidat: LP2-49, Score -3.303249.
Seine vollständige Ausgabe lautet:

```text
EANOFEREWROWDSTTOGAUOPANSGOSPLUISAFFELETAIDSLOWNFRALRIDSPASSYEBTWOF
```

Das ist kein zusammenhängender Klartext. Drei von 19 unabhängigen Zufallstexten
mit genau denselben Runenhäufigkeiten und derselben Anzahl benachbarter gleicher
Runen erreichen mindestens diesen Score. Jeder Zufallstext durchläuft dieselbe
vollständige Optimierung und Nachbewertung. Plus-eins-p=0,20, nach Bonferroni über
55 Seiten p=1. Die Auswahl zwischen den zwei Angriffsfamilien ändert das Ergebnis
nicht. Die geringe Zahl von Nullreplikaten könnte korrigierte Signifikanz ohnehin
nicht auflösen; bei null Überschreitungen wäre eine größere registrierte Prüfung nötig.
Seedlängen außerhalb 4–12, beliebige F-Teilmengen und Seitenfortsetzung bleiben offen.

## Erneute selektive Wort-/Zahlenstromsuche (E018)

381 kanonische Wortschlüsselzyklen mit allen Phasen, drei Zahlenströme
(Primzahlen, Primzahlen minus eins, ganzzahlige Totienten), Starts 0–255,
vier Vorzeichen und sämtliche F-Teilmengen werden mit dem neuen Viergramm-Score
geprüft. Die dynamische Programmierung optimiert die Unterbrechungen exakt
innerhalb dieses endlichen Rasters. Anders als E016 umfasst die Kontrolle den
gesamten Wort-/Zahlenstromkatalog: erneut **3/3 exakt**.

**Abdeckung: 35/55 Seiten abgeschlossen; übrige Seiten und Nullvergleich ausstehend. Das Budget beendet die Serie, nicht die wissenschaftliche Prüfung dieser Familie.**
Dies ist eine Wiederaufnahme von E007/E008 mit verändertem Trainingsmaterial
und Score, keine neue Chiffrenfamilie oder unabhängige Entdeckung.
Nicht kalibrierte Teilresultate gelten nicht als statistisch negativer Befund.
LP2-50 bleibt als Zahlenseite mit Layout im Korpus erhalten und wird hier nicht
als Runenseite analysiert.

## Validierung und Ressourcen

61 Tests bestanden. 306 gespeicherte Kandidatenaufzeichnungen wurden
mit einer separaten Rückrechnung erneut gegen ihren kanonischen Ciphertext
geprüft und skalar nachbewertet; bekannte Kontrollen wurden ebenfalls geprüft.
Die Rückrechnung beweist die angegebene Transformation, nicht die Echtheit des Klartexts.
Ausgabedateien und registrierte Abhängigkeiten stimmen mit ihren SHA-256 überein.

23 erfolgreiche Experimentprozesse, 878.050 Sekunden darin;
längster erfolgreicher Prozess 90.773 Sekunden.
Das Serienbudget beträgt 900 Sekunden, die Einzelgrenze 180 Sekunden.
Der 400-Sekunden-Rahmen für E018 endete während LP2-35–39 nach weiteren
8,646 Sekunden; diese unvollständige Gruppe wurde beendet und als abgebrochen
protokolliert. Sie wird bei der Fortsetzung erneut berechnet. Einschließlich
Orchestrierung, Abbruch und zwei Sekunden konservativer Beendigungsreserve
liegt die Serienabrechnung bei 891,052 Sekunden. Details im
[Budgetprotokoll](../checkpoints/phase4_budget.json); erfolgreiche Laufzeiten
werden darin nicht doppelt gezählt. Ein Forschungsprozess gleichzeitig; feste Beam-/Array-
Größen und begrenzter Modellcache. Tests, Datenlektüre und Dokumentation sind
nicht in der Experimentzeit enthalten. Keine Hintergrundaufgabe läuft weiter.

[Ergebnisübersicht](../results/phase4_summary.json),
[Checkpoint](../checkpoints/phase4_complete.json),
[Forschungsstand](../research_state.json),
[Experimentprotokoll](../experiment_log.jsonl).
Der Dateiname des Checkpoints bezeichnet die gespeicherte Serie; der Status
im Inhalt unterscheidet fertige Experimente von ausstehender Arbeit.

Zur Fortsetzung zuerst E018 mit unveränderten Parametern abschließen; der Runner
überspringt nachgewiesen fertige Fingerabdrücke. Danach: allgemeinere affine
Rückkopplung mit synthetischer Kontrollschranke und eine kleine, anhand der
Quellenbilder begründete Menge alternativer Leserichtungen prüfen.
Historische Berichte und erfolglose Ergebnisse bleiben erhalten.
