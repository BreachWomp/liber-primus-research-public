# Dritte Forschungsserie: Abschnittsschlüssel, Textschlüssel und Autokey

Stand (UTC): 2026-10-19 T09:41:13.152804+00:00. **Keine neue Entschlüsselung bestätigt.**
Die vollständigen stärksten Ausgaben wurden geprüft; keine enthält überzeugenden
zusammenhängenden Klartext. Alle Versuche bleiben mitsamt Rechenregel erhalten.
Frühere Berichte: [Serie1](research_report.md), [Serie2](attack_phase2_report.md).

## Tatsächliche Angriffe

| Versuch | Abgedeckter Suchraum | Ergebnis |
|---|---|---|
| E012 | Zehn eindeutige quellenbasierte LP2-Abschnitte; Primzahlen, p−1, φ(n); vier Vorzeichen; Start0–255; sämtliche F-Teilmengen exakt optimiert | Stärkster Abschnitt LP2-00–02: p=0,10; über zehn Abschnitte korrigiert1 |
| E013 | Alle 55 ungelösten Runenseiten mit allen gültigen Startstellen in41.522 Runen von Emersons Self-Reliance; zwei Kodierungen, vier Vorzeichen, keine/alleF | 36,336,608 Varianten; stärkste Seite LP2-49: p=0,125, seitenkorrigiert1 |
| E014 | Alle 29+841+24.389 Startschlüssel von 1–3 Runen; vier Vorzeichen, keine/alleF; alle 55 Seiten | 11,113,960 Varianten; LP2-55: p=0,375, seitenkorrigiert1 |
| E015 | P_i=a(C_i−C_(i−1))+b mod29, alle 812 invertierbaren affinen Abbildungen, jede der55 Seiten | 44.660 Varianten; globaler Modellvergleich p=0.48 |

Die Varianten sind stark verwandt; diese Zahlen sind keine Anzahl unabhängiger
Beweise. Bei E012 kommen zu 30.720 Start-/Vorzeichenkombinationen die durch dynamische
Programmierung optimierten F-Teilmengen hinzu. E014 enumeriert Anfangsklartexte;
für jedes Vorzeichenpaar entspricht jeder davon genau einem Startschlüssel.
Dies wurde gegen die direkte Autokey-Rechnung geprüft.

## Quellen und Grenzannahmen

Die eingefrorene relikd-Quelle gruppiert LP2-54/55 separat, der iddqd-Index
behandelt 54 als Unterabschnitt des Kapitels ab 40. Beide Einteilungen wurden vor
dem Lauf gespeichert; daraus ergeben sich zehn unterschiedliche Abschnitte.
Es wurde kein Abschnitt nach einem guten Score zugeschnitten.

LP2-50 wird mit ihrem Zahlenlayout und einer Nullbreite im Runenstrom erhalten.
**Null Schlüsselverbrauch ist hier eine Modellannahme**, keine Aussage über die
tatsächliche Funktion der Zahlenseite. Der Schlüssel und Sprachkontext laufen
über die übrigen Seitengrenzen weiter. Die Seitenstücke jeder Ausgabe bleiben
getrennt abrufbar.

Der Textschlüssel stammt aus der offiziellen [Gutenberg-Ausgabe 2944](https://www.gutenberg.org/ebooks/2944).
Originaldatei einschließlich Kopf-/Lizenztext, Abrufzeit und SHA-256 stehen in
[Quellenmanifest](../sources/emerson_manifest.json) und `data/raw/gutenberg/pg2944.txt`.
Ausgewählt wurde ausschließlich Self-Reliance einschließlich Epigraph und
wiederholtem Titel. Es handelt sich um eine **thematische Hypothese**, nicht um
einen belegten Cicada-Schlüssel.

Kodiert wurden ASCII-Buchstabenwörter mit der vorhandenen gierigen GP-Regel
innerhalb jedes Worts. Zwei Q-Regeln: Q→C bzw. QU→CW und übrigesQ→C. Die nicht
ASCII-Lateinbuchstaben æ und é werden dabei ausgelassen und ausdrücklich
inventarisiert; die Quelldatei wurde nicht verändert. Andere Schreibweisen,
Rückwärtsrichtung, andere Bücher oder beliebige F-Teilmengen sind nicht abgedeckt.

## Kontrollbefunde und Grenzen der Aussage

E012 verschlüsselt einen bekannten, vom Training ausgeschlossenen LP1-Text
künstlich mit einem fortlaufenden Schlüssel und teilt ihn in drei Seiten.
Die gespeicherte Regel reproduziert die Seiten exakt, einschließlich verbrauchter
Schlüsselstellen. Der Sprachscore wählt jedoch F48 stattF49 und erreicht nur
99.373% Runengenauigkeit. Das automatische
Entschlüsselungskriterium bleibt deshalb gesperrt.

Die synthetischen Kontrollfälle für E013, E014 und E015 werden im gesamten
jeweiligen Suchraum exakt als beste Ausgabe wiedergewonnen. Das zeigt
Erkennungsfähigkeit für diese konkreten Konstruktionen, nicht für jede
historische Chiffre. Bekannte LP2-56-Regressionsfehler bleiben unverändert.

E013/E014 verwenden39 unabhängige Vergleichstexte mit exakten Runenhäufigkeiten
und exakter Zahl direkt benachbarter gleicher Runen. Jeder wiederholt die volle
Schlüsselsuche; Bonferroni 55 berücksichtigt die Auswahl der besten Seite. Diese
kleine Stichprobe dient zum Prüfen von Scheinbefunden und könnte eine korrigierte
Signifikanz unter 0,05 gar nicht auflösen. Bei null Überschreitungen wäre eine
größere registrierte Folgeprüfung nötig; dazu kam es hier nicht.

E012 nutzt 39 Simulationen des schon festgelegten symmetrischen Markov-Modells,
mit unabhängigen Kettenstarts an den tatsächlichen Seitengrenzen. E015 nutzt 199
Simulationen und maximiert bei jedem Durchlauf über alle 55 Seiten und812 Abbildungen.
Diese Modelltests erhalten die beobachteten Symbolhäufigkeiten nicht exakt;
Schätzunsicherheit von q wird nicht fortgepflanzt. Nach zusätzlicher Bonferroni-
Korrektur über die vier Diagnosen lauten die Werte [1, 1, 1, 1].
Es handelt sich weiterhin um explorative Forschung am bereits betrachteten Korpus.

Die negative Differenzprüfung betrifft nur die angegebene affine Abbildung.
Sie widerlegt nicht jede Chiffre mit Rückkopplung. E015 erweitert den früheren
E010-Suchraum um weitere Steigungen und additive Konstanten; es ist keine
unabhängige Replikation einer neuen Entdeckung.

## Validierung, Ressourcen und Fortsetzung

57 Tests bestanden. 418 gespeicherte Kandidatenaufzeichnungen wurden
erneut vom kanonischen Ciphertext aus geprüft, zurückverschlüsselt und skalar
nachbewertet. Dazu gehören drei erneut gespeicherte Ausgaben des für E012
ausgewählten Nullvergleichs. Die korrekte Rückrechnung bestätigt die Regel,
nicht die sprachliche Echtheit.

Insgesamt 16 erfolgreiche Prozesse, 15 aktuelle Aufgaben,
451.791 Sekunden gemessene Experimentzeit innerhalb des 900 Sekunden-Budgets.
Längster Prozess: 179.245 Sekunden, Grenze 180.
NumPy 2.3.5; kleine feste Arrayblöcke und jeweils nur ein Forschungsprozess.
Downloads, Tests und Analyse sind nicht in dieser Rechenzeit enthalten.

Ein Kontrolllauf wurde versehentlich zweimal gerechnet: `180` und `180.0`
erzeugten unterschiedliche Fingerabdrücke bei wissenschaftlich gleichen Parametern.
Beide historischen Ereignisse bleiben erhalten und beide Laufzeiten werden gezählt;
sie gelten nicht als zwei unabhängige Kontrollen. Die wiederholten Aufrufe der
gespeicherten Kommandos verwenden anschließend den vorhandenen Fingerabdruck.

```sh
python scripts/run_section_phase.py
python experiments/running_key_attack.py
python experiments/short_seed_autokey.py
python experiments/differential_affine.py
python scripts/finalize_phase3.py
```

Vollständige Ergebnisse und Hashes: [Checkpoint](../checkpoints/phase3_complete.json),
[Experimentprotokoll](../experiment_log.jsonl), [Forschungsstand](../research_state.json).
Keine unbeaufsichtigten Prozesse laufen.

Als Nächstes: einen unabhängig trainierten Wort-/Sprachscore gegen die verbleibenden
Unterbrechungsfehler prüfen und damit längere unbekannte Autokey-Startschlüssel
in begrenzten, synthetisch kontrollierten Suchen angehen. Weitere Textschlüssel
sollen durch konkrete Quellenhinweise begründet werden.
