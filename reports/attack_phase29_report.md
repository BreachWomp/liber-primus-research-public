# Forschungsserie 29: Wortenden und allgemeine Substitution

Stand UTC: 2026-11-01T17:52:27.224779+00:00. **Keine neue Entschlüsselung. Keine unbekannten Seiten mit
diesem Verfahren durchsucht: Die festgeschriebene Kontrollbedingung scheitert.**

## E080: Ein vorab festgelegter Modellversuch

E036 bevorzugte im bekannten LP2-57-Kontrolltext TUNNELEA statt TUNNELNG.
Das neue Modell zählt Wortanfang und Wortende ausdrücklich: drei BOS-Marker,
29 Runen und ein EOS-Ereignis, Viergramm-Backoff mit alpha0,5 und Stärke 5.
Wortwahrscheinlichkeit `(count(w)+20*Q(w))/(N+20)`, Q einschließlich EOS.
Q lässt auch eine leere Emission zu; beobachtete Segmente bleiben nichtleer.
Keine zusätzlichen LP-Wörter, Rechtschreibregeln oder fallspezifischen Boni.
Das ist eine bekannte Sprachmodell-Technik, keine neue kryptographische Entdeckung.

Nur die gepinnten Emerson-Kapitel I,III,IV,V,VI,VII,VIII,IX trainieren das Modell.
II ausgeschlossen; X/XI/XII nicht zum Fit verwendet. Diese Texte wurden früher
bereits betrachtet: keine Behauptung eines historisch ungesehenen Testkorpus.
Wortgrenzen und GP-Tokenisierung bleiben wie zuvor; keine Apostroph-Zusammenführung,
keine erfundenen Seitenrandkorrekturen. Der Versuch wurde nach Kenntnis des
alten Fehlers entworfen, nicht blind gegenüber E036.

Bei allen 3 bekannten Kontrollen übertrifft die Wahrheit jede tatsächlich
verändernde einzelne Symbolvertauschung. 358/360 frische Ein-Runen-Mutationen
werden schlechter bewertet, beim alten Wortmodell 355/360. Beide Modelle
bewerten alle 342 Häufigkeits-Shuffles schlechter als ihre Ausgangstexte.
Keine p-Werte daraus: abhängige Sprachdiagnostik, kein optimierter Chiffrenangriff.
Eine getrennte Berechnung prüft 1944 Scores gegen neu
aus den Quellbereichen gezählte Ereignisse; max. Abweichung
5.33e-15. Tokenisierung ist bewusst gemeinsam,
Ereigniszählung und Wahrscheinlichkeitsrechnung sind getrennt implementiert.

## E081: Blind gegenüber frischen Schlüsseln

Neun neue zufällige 29-Runen-Substitutionen: drei LP-Regressionen sowie sechs
Quellfenster aus X/XI/XII. Neue Schlüssel und festgeschriebene Such-Seeds.
Die zuvor bekannte Wahrheit wird nicht an die Suche übergeben. Höchstens 24
unveränderte Wortmuster-/Häufigkeits-/Zufallsstarts, je 40 vollständige
406-Tausch-Schritte für Zeichen-Warmup und neue Wortbewertung. Keine zusätzlichen
Neustarts nach Sichtung von Fehlern. Drei identisch optimierte Kontrollnulls.

| Kontrolle | Runen | Richtige Positionen | Wahrheits-Score | Gefundener Score |
|---|---:|---:|---:|---:|
| 0 | 515 | 515/515 | -1.861097 | -1.861097 |
| 1 | 319 | 319/319 | -1.994198 | -1.994198 |
| 2 | 95 | 95/95 | -2.303467 | -2.303467 |
| 3 | 69 | 69/69 | -1.391832 | -1.391832 |
| 4 | 69 | 69/69 | -1.577202 | -1.577202 |
| 5 | 67 | 65/67 | -2.421091 | -2.321066 |
| 6 | 301 | 301/301 | -1.883484 | -1.883484 |
| 7 | 301 | 301/301 | -1.709405 | -1.709405 |
| 8 | 300 | 300/300 | -1.721807 | -1.721807 |

Der alte LP2-57-Fehler ist behoben:95/95. Insgesamt jedoch nur **8/9 exakt**.
Kontrolle 5 aus Kapitel XII scheitert mit 65/67: **TRAYS/PANS → TRAPS/YANS**.
TRAPS steht einmal im Training, TRAYS/PANS/YANS fehlen. Die Logbewertung
steigt durch TRAYS→TRAPS um 7,636 und sinkt durch PANS→YANS nur um 0,934.
Die falsche Abbildung hat daher einen höheren Gesamt-Score. Das ist ein
Bewertungsproblem; längere Suche kann den richtigen Text unter diesem Score
nicht zum global besten Kandidaten machen. E080s lokale Diagnose war kein
Ersatz für den unabhängigen Kontrolllauf auf weiteren Quellfenstern.

Die 3 vollständig optimierten Nullscores der 95-Runen-Kontrolle lauten
-6.019000, -5.845713, -5.579128.
Nur Fähigkeitsdiagnostik, keine Signifikanz- oder Entschlüsselungsaussage.
Die neun Texte sind keine neun unabhängigen Sprachkorpora.

## Nachprüfung und Entscheidung

235 Kandidaten-/Wahrheitsscores,
91756 abschließende Nachbarscores
und 226 Rückverschlüsselungen getrennt geprüft.
Alle ausgegebenen Abbildungen sind bijektiv. Quellfenster, Schlüssel-Seeds,
Nullziehungen, Auswahl unter Neustarts und letzte lokale Optima bestätigt.
Zwischenschritte und Initialisierungslogik wurden nicht unabhängig neu implementiert.
Nicht vorkommende Runen lassen sich aus einer Kontrolle nicht identifizieren;
Exaktheit gilt für Klartext und Abbildung der tatsächlich beobachteten Symbole.

Die vorab verlangten 9/9 werden nicht nachträglich abgeschwächt: **E082 wurde
nicht registriert oder ausgeführt.** Keine Anpassung des Modells an diesen
neuen Fehler innerhalb dieser Serie. Alle historischen E035/E036-Ergebnisse
bleiben erhalten; neue Kontrollen sind keine historischen Entschlüsselungen.

Fünf Kontrollen mit mindestens 200 Runen waren exakt. Das motiviert H051 als
separate, noch ungeprüfte Längeneinschränkung. Zunächst 12 neue, vorher festgelegte
Kontrollen mit 200/300/500/729 Runen. Erst bei vollständigem Erfolg wäre ein
direkter Angriff auf längere unbekannte Seiten zulässig. Der kurze Gegenbeleg
bleibt bestehen; seine Auslassung wird nicht als bestandener E081-Test gewertet.

142 Tests bestanden, 13 registrierte Aufgaben,28.111 Sekunden
Experimentzeit; maximale abgetastete Speichernutzung 167,0 MiB.
Budget 1.800 Sekunden, 180 je Aufgabe, 768 MiB, ein Worker. Nach dem fehlgeschlagenen
Gate beendet, kein weiterer Rechenaufwand für ungültige unbekannte Kandidaten.
Keine laufenden Forschungsprozesse.

[Modellplan](../experiments/terminated_substitution_plan.json),
[Kontrollplan](../experiments/terminated_controls_plan.json),
[Validierte Ergebnisse](../results/phase29_summary.json),
[Textvergleich mit Original-Wortgrenzen](phase29_control_comparison.md).
