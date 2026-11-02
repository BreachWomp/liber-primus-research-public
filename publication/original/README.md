# Liber Primus Research

Reproduzierbare Kryptanalyse des Liber Primus. **Keine neue Entschlüsselung
nachgewiesen.** Serie 31: Differenzen plus allgemeine Substitution mit IV0,
46 unbekannte Seiten direkt angegriffen; 9/19 Nullscores mindestens so hoch.

Start: [Aktueller Forschungsbericht](reports/attack_phase31_report.md),
[Forschungsstand](research_state.json), [Hypothesen](hypotheses.json).
Die [erste](reports/research_report.md) und [zweite Forschungsserie](reports/attack_phase2_report.md) bleiben historisch erhalten.

## Aktueller Stand

- E085: zwölf vorhandene Kontrollen exakt auf die Differenzchiffre übertragen, keine Suchwiederholung.
- E086: 46 Seiten, IV0, 9/19 passende C-Raum-Nullscores mindestens so hoch.
- E083: 12/12 neue Kontrollen für längere allgemeine Substitution exakt.
- E084: 46 Seiten direkt geprüft, 15/19 passende Nullscores mindestens so hoch.
- E080: explizite Wortenden, 358/360 Mutationen richtig bewertet; getrennte Nachrechnung.
- E081: 8/9 Substitutionskontrollen exakt; neuer 67-Runen-Gegenbeleg, keine unbekannten Seiten angegriffen.
- E077/E078:128 vorausgewählte Familien, je841 Präfixe exakt;16/16 Kontrollen bestanden.
- E079:55 Seiten, 10/19 Nullscores mindestens so hoch; keine neue Lösung.
- E074/E075: exakte Präfixsuche innerhalb 16 vorausgewählter Familien;16/16 Kontrollen exakt.
- E076:55 einzelne Seiten, 1/19 Nullscores mindestens so hoch; keine neue Lösung.
- E071/E072: affine Konstante und Sonderfall b=1 geprüft;16/16 Kontrollen exakt.
- E073:56 Eingaben, 3/19 Nullscores mindestens so hoch; keine neue Lösung.
- E068: alle 16 Kontrollen exakt; 22.736 Familien pro Eingabe, direkte Gegenprüfung der Vorauswahl.
- E069/E070: 56 Eingabehypothesen, 5/99 frische Nullscores mindestens so hoch; keine neue Lösung.


- E066: alle 16 Kontrollen exakt; unabhängige Prüfung der Vorauswahl und Rückverschlüsselung.
- E067: 56 Eingabehypothesen, 2/19 Nullscores mindestens so hoch; keine neue Lösung.
- E064: vier neue 3316-Runen-Kontrollen exakt; zwölf E062-Kontrollen unverändert übernommen.
- E065: zehn Gruppen mit allen 55 unbekannten Runenseiten; 14/19 Nullscores
  mindestens so hoch wie die stärkste Gruppe. Keine bestätigte Entschlüsselung.
- E062: 12/12 Autokey-Kontrollen exakt; Abweichung beim Nullgenerator erkannt,
  historisch erhalten und durch separaten plankonformen Lauf ergänzt.
- E063: 46 unbekannte Seiten geprüft, 6/19 Nullscores mindestens so hoch.
- E058/E060: 17/18 mit Abstandsbedingungen; 21/21 mit beiden Initialisierungen.
- E061: alle 55 unbekannten Runenseiten in neun Gruppen geprüft; 13/19
  ausgewählte Nullscores mindestens so hoch, korrigiertes p=1.00. Keine neue Lösung.
- E056/E057: Durchlaufender Sprachkontext behebt den bekannten Grenzfehler
  bei vorgegebenem Schlüssel. Drei frische Blindkontrollen exakt, schwierige
  Regression verfehlt; 14 weitere Kontrollen planmäßig zurückgestellt.
- E054/E055: 10/12 Kontrollen mit langen Schlüsseln und Seitenphasen exakt;
  2 Anfangs-F-Mehrdeutigkeitspaare rückverschlüsselt. Kein neuer unbekannter Scan.
- E052 repariert die gemeinsame Initialisierung langer Schlüssel: alle sechs
  frischen Kontrollen und Regressionen exakt; früherer 31-Runen-Fehler behoben.
- E053 prüft neun unbekannte Gruppen mit 19 vollständigen Nullsuchen: 11/19
  Nullscores mindestens so hoch; korrigiertes p=1.00, keine neue Lösung.
- 75 Seiten katalogisiert; alle 58 LP2-Runenfolgen zwischen zwei Quellen abgeglichen.
- Neun bekannte Lösungsabschnitte exakt reproduziert. Ein LP1-Kontrollabschnitt
  enthält zwei dokumentierte Quellenabweichungen und ist vom Sprachtraining ausgeschlossen.
- 145 Tests bestanden; 84 Experimentgruppen mit Prüfsummen und festen Parametern.
- Wiederholungsmangel repliziert: 86 benachbarte gleiche Runen statt erwarteter 439,166.
- 113.448 affine/Primzahl-Totient-Varianten geprüft, einschließlich bekannter Kontrollfälle.
- Alle 55 ungelösten Runenseiten mit 381 Schlüsselzyklen und drei Zahlenfolgen
  geprüft; sämtliche F-Unterbrechungsteilmengen im jeweiligen Suchraum exakt optimiert.
- Weitere 13.516 Ciphertext-Autokey- und 171.600 Plaintext-Autokey-Varianten geprüft.
- 550 gespeicherte Kandidaten unabhängig nachgerechnet. Die stärksten Sprachscores
  sind im jeweiligen Zufallsvergleich unauffällig; kein Kandidat als Lösung bestätigt.
- In Serie drei zusätzlich zehn Abschnittsgruppierungen, 36.336.608 Textschlüssel-
  Varianten, 11.113.960 kurze Autokey-Varianten und 44.660 Differenzabbildungen geprüft.
  Weitere 418 Kandidatenaufzeichnungen nachgerechnet; kein belastbarer neuer Treffer.
- Exakter mathematischer Nachweis eines Bias in einem geprüften externen Zufallssampler.
- Neues extern trainiertes Sprachmodell: 265.129 Runen, keine LP-Texte im Training;
  DIVINITY, CIRCUMFERENCE und LP2-56 werden einschließlich F-Unterbrechungen exakt gefunden.
- Längere unbekannte Autokey-Startschlüssel (4–12 Runen): sechs synthetische Kontrollen
  exakt, alle 55 unbekannten Runenseiten geprüft; stärkster Kandidat im Nullvergleich p=0,20.
- E018 wiederholt die selektive Wort-/Zahlenstromsuche mit dem verbesserten Score:
  alle 55 Seiten abgeschlossen, stärkster Kandidat im Nullvergleich p=0,50.
- E019 prüft 1.244.100 weitere vollständige Rückkopplungsvarianten; drei synthetische
  Kontrollen exakt. In E020 erreichen 115 von 4.000 frischen Zufallstexten mindestens
  den LP2-55-Score: Roh-p≈0,029, seitenkorrigiert 1. Weitere 354 Kandidatenaufzeichnungen
  wurden nachgerechnet; keine neue Lösung bestätigt.
- E021 prüft acht Leserichtungen auf vier unbekannten Runenseiten. Neun bekannte
  Kontrollfälle exakt; stärkster Kandidat im Nullvergleich p=0,70, korrigiert 1.
  Weitere 39 Kandidatenaufzeichnungen unabhängig nachgerechnet.
- Bildprüfung der Zeilenstruktur auf sieben Seiten; E022 dokumentiert fünf
  abweichende Tabellenzellen zwischen Quellen und neun inkonsistente veröffentlichte
  Dezimalumrechnungen. Alle historischen Varianten bleiben erhalten.
- E023 stützt die fünf strittigen Lesarten anhand von 16 Bildausschnitten und
  Zeichenhöhen. Separate Korrekturschicht; keine vollständige Neutranskription
  und keine zweite unabhängige Bildlesung. Kanonische Daten bleiben unverändert.
- E024: vier feste Strukturtests der 256 Zahlenwerte gegen 9.999 Zufallsfolgen
  ohne auffälligen Befund; daraus folgt kein Beweis einer Verschlüsselung.
- E025 erweitert affine Klartext-Rückkopplung auf Abstand zwei: 36.078.900 Regeln
  auf 55 unbekannten Runenseiten, drei Kontrolltexte exakt. Stärkster Kandidat
  im Nullvergleich p=0,40, korrigiert 1; 174 Kandidaten unabhängig nachgerechnet.
- E026 prüft 75 Layouts: Wortgrenzen der unbekannten Runenseiten stimmen in
  54 Fällen zwischen den Quellen überein. Das abweichende Zeichen auf LP2-35
  ist im Bild sichtbar und als separate Entscheidung dokumentiert.
- E027: fester externer Wortscore mit 1.582/1.600 korrekten Mutationsrangfolgen
  gegenüber 1.568 beim bisherigen Score. Drei bekannte Schlüsselkontrollen exakt;
  deskriptiver Vergleich, keine unabhängige historische Entschlüsselung.
- E028 prüft die affine/Wort-/Zahlenstromfamilie mit dem neuen Score auf 55 Seiten;
  vier Kontrollen im vollständigen Suchraum exakt. Stärkster Kandidat im
  Nullvergleich p=0,20, korrigiert 1; 180 Kandidaten einschließlich E027 unabhängig
  nachgerechnet. Seitenrandfragmente bleiben eine Modellgrenze.
- E029 prüft Teilbehauptungen einer öffentlichen Lösungsmeldung: bestehende
  Bytefolge und zwei arithmetische Fakten reproduziert, kein neuer Klartext bestätigt.
  Herkunft der zusätzlich behaupteten Binärdatei bleibt ungeklärt.
- E030: Die pauschale Zeichenwertung an Seitenrändern hilft bei abgeschnittenen
  Wörtern, schadet aber vollständigen Wörtern und verfehlt das vorab gesetzte Gate.
  Sie wird nicht in den nächsten Angriff übernommen.
- E031/E032 bleiben als abgeschlossene Quellenprüfungen archiviert.
  Auf ausdrücklichen Nutzerwunsch keine weitere Verfolgung unbelegter Lösungsmeldungen.
- E033 prüft 659.340 reversible Regeln je unbekannter Runenseite:
  `P_(i-2)=a*C_i+b*C_(i-1)+c*C_(i-2)+d mod29`.
  Drei synthetische Kontrollen exakt; vollständiger Suchraum auf 55 Seiten und
  identischer Suchraum in den Zufallsvergleichen. Die ersten zwei Quellrunen
  dienen als Initialwerte, für sie wird kein Klartext behauptet.
  36.263.700 Regeln auf unbekannten Seiten; stärkster Treffer LP2-49,
  Nullvergleich p=0,35, seitenkorrigiert 1. 193 Kandidaten unabhängig nachgerechnet;
  keine neue Lösung bestätigt.
- E034 schließt die bisher ausgesparte Konstante in
  `P_i=a*C_i+b*P_(i-1)+d mod29` ein: 35.013.440 Regeln auf allen 55 unbekannten
  Runenseiten, drei synthetische Kontrollen exakt. LP2-49 ist im Nullvergleich
  unauffällig (p=0,40, korrigiert 1); 193 Kandidaten unabhängig nachgerechnet.
- E035: Allgemeine bijektive Runen-Ersetzung, gestartet aus externen Wortmustern.
  Zwei synthetische Kontrolltexte exakt (515/515 und 319/319 Runen), kurzer Text
  93/95. Dort bevorzugt der Sprachscore nachweislich die falsche Ausgabe.
  Kontroll-Gate verfehlt, keine unbekannte Seite mit diesem Prototyp untersucht.
  225 gespeicherte Startläufe unabhängig geprüft.
- E036: Wortgrenzen-Bewertung verbessert die kurze Substitutionskontrolle auf
  94/95 Runen, bevorzugt aber weiterhin eine falsche Rune. Beide langen
  Kontrollen exakt; 355/360 korrekte externe Mutationsrangfolgen.
  Das vollständige Gate bleibt verfehlt, keine unbekannte Substitutionssuche.
  452 gespeicherte Startläufe beider Bewertungsstufen unabhängig geprüft.
- E037: Quadratisch fortschreitende Schlüssel, 37.514.400 Regeln auf allen
  55 unbekannten Runenseiten. Drei synthetische Kontrollen exakt; stärkster
  Treffer LP2-49 im Nullvergleich p=0,50, seitenkorrigiert 1.
  193 Kandidaten unabhängig nachgerechnet; keine neue Lösung bestätigt.
- E038: Beliebige periodische Schlüssel direkt aus Runen gelernt. Zwei
  historische Schlüssel mit vorgegebenen F-Unterbrechungen und sechs externe
  synthetische Kontrollen ohne diese Hilfe exakt wiedergewonnen.
- E039: Derselbe Solver auf allen 55 unbekannten Runenseiten; Perioden 1–16,
  beide Vorzeichen, keine oder sämtliche F-Unterbrechungen. Vier Starts je
  Kombination, fester Abzug für die Schlüssellänge; heuristische Suche.
  Stärkster Treffer LP2-49: p=0,30, seitenkorrigiert 1.
  5.631 Kandidatenaufzeichnungen unabhängig nachgerechnet; keine neue Lösung.
- E040/E041: Schlüssel und selektive F-Zeitpläne gemeinsam gefunden.
  Beide tatsächlichen historischen Chiffren und sechs externe synthetische
  Kontrollen exakt in Klartext, Schlüssel und Unterbrechungsmasken,
  ohne vorgegebene Schlüssel oder Skip-Positionen.
- E042: Derselbe gemeinsame Solver auf allen 55 unbekannten Runenseiten.
  Stärkster Treffer LP2-49: p=0,20, seitenkorrigiert 1.
  4.226 Zwischen-/Endkandidaten und 1.044 Schlüsselstarts nachgerechnet;
  87 bedingte Zeitplanmaxima durch einen separaten Prüfer bestätigt.
  Keine neue historische Entschlüsselung.
- E043/E044: Drei lange Kontrollen exakt; zehn unbekannte Seitengruppen
  mit gemeinsamem kontinuierlichem Schlüssel geprüft. LP2-54/55: p=0,10,
  gruppenkorrigiert 1. Weitere 1.764 Kandidaten und 35 Zeitplanmaxima geprüft.
- E045/E046: Gemeinsamer Schlüssel mit Seiten-Neustart; drei externe
  Kontrollen exakt in Text, Schlüssel und F-Maske. Zehn unbekannte Gruppen
  geprüft, 1/19 Nulltexte erreicht den stärksten Score; kein belegter Klartext.
  1.680 Kandidatenaufzeichnungen und 33 Zeitplanmaxima unabhängig geprüft.
- E047/E048: Gemeinsame Schlüssel mit unabhängigen Seitenphasen; alle drei
  Kontrollen exakt in Text, Schlüssel, Phasen und F-Masken. Zehn unbekannte
  Gruppen geprüft; LP2-54/55: p=0,95, gruppenkorrigiert 1.
  1.676 Kandidatenaufzeichnungen und 33 bedingte Maxima unabhängig geprüft.
- E049: Nominelle Perioden 17–32; Schlüssel und F-Masken bei 17 und 23
  exakt, bei 31 nur 59/1.200 Runen richtig. Kontrollkriterium verfehlt.
- E050: Richtiger Klartext bewertet sich deutlich besser; mit vorgegebenem
  Schlüssel oder richtiger Maske/Periode funktionieren die Teiloptimierer.
  Ausdrückliche Oracle-Diagnose, keine eigenständige Entschlüsselung.
- E051: Adaptiver Reparaturversuch mit zwölf gemeinsam ausgewerteten
  F-freien Fragmenten scheitert ebenfalls. Keine unbekannten Seiten untersucht.
  342 Kandidaten und 72 Fragmentzustände unabhängig geprüft.
- Keine automatische Einstufung von Kandidaten als entschlüsselt.

## Reproduktion

Getestet mit Python 3.12.14 und NumPy 2.3.5. Die Kernbibliothek benötigt nur die
Python-Standardbibliothek; die Experimente benötigen NumPy.

```sh
python -m pip install -r requirements-research.txt
python scripts/acquire_sources.py
python -m unittest discover -s tests -v
python -m pip install -r requirements-image-analysis.txt
python experiments/long_key_controls.py
python experiments/long_key_diagnostic.py
python experiments/pooled_long_key_diagnostic.py
python scripts/finalize_phase17.py
```

Die Quellen liegen bereits im Repository. Der Download erfolgt nur für fehlende
Dateien oder mit ausdrücklich gesetztem `--refresh`. Bestehende Prüfsummen
werden vor der Wiederverwendung kontrolliert. Fremder Quellcode wird als
Beweismaterial gespeichert und nicht ausgeführt.

Der Batch überspringt abgeschlossene Läufe mit identischem Code, Input,
Parametern und unveränderter Ergebnisdatei. Historische Läufe bleiben im
append-only [Experimentprotokoll](experiment_log.jsonl). Um dieselbe Berechnung
unabhängig zu wiederholen, lässt sich das entsprechende Experiment direkt mit
einem **neuen** Ausgabepfad starten; genaue Parameter stehen im Protokoll.

```sh
python experiments/adjacency.py --replicates 9999 --seed 330120261018 --timeout-seconds 120 --output results/independent-adjacency.json
```

## Aufbau

| Verzeichnis | Inhalt |
|---|---|
| `data/raw/` | Unveränderte Quelltexte, Transkriptionen und ausgewählte Seitenbilder |
| `sources/` | URLs, gepinnte Commits, SHA-256, Abrufzeitpunkte und Vergleichsprotokolle |
| `transcriptions/` | LP1/LP2-Seiten mit Layout, Runenfolgen und dokumentierten Abweichungen |
| `known_solutions/` | Kontrollfälle mit erwarteten Runen und expliziten Unterbrechungspositionen |
| `src/liberprimus/` | Alphabet, Chiffren, Statistik, Sprachscore und begrenzte Suchverfahren |
| `experiments/` | Ausführbare, begrenzte Experimente |
| `results/` | Vollständige Messwerte, gespeicherte Kandidaten und Validierungsprotokoll |
| `checkpoints/` | Fortsetzbarer Forschungsstand |
| `reports/` | Forschungsauftrag, Quellenprüfung, Methodenprüfung und Ergebnisse |
| `tests/` | Bekannte Lösungen, Rechen- und Suchkontrollen |

Die Kernbibliothek unterstützt Gematria Primus, Modulo-29-Abbildungen,
Substitution, Vigenère, Autokey, Primzahl-Totientfolgen, Spaltentranspositionen,
Cribs, Häufigkeiten, IC, Entropie, N-Gramme, Lag-/Periodenstatistik und
Seitenvergleiche. Begrenzte Suchbausteine für Simulated Annealing, genetische
Verfahren, Beam Search und endliche Constraints sind implementiert und getestet.
Diese Bausteine sind keine Behauptung, dass alle Chiffrenfamilien bereits
erfolgreich oder erschöpfend auf dem Buch geprüft wurden.

## Evidenz und Fortsetzung

LP2-Seiten 00–55 sind Forschungsziele, LP2-56 und LP2-57 bekannte Kontrollen.
Die reine Zahlenseite LP2-50 ist im Korpus enthalten, aber von Runenstatistiken
ausgenommen. Seitenübergreifende Nachbarschaftspaare werden nicht erfunden.

Quellenübereinstimmung beweist keine unabhängige Herkunft. Die historische
Authentizität der Cicada-Veröffentlichung wurde nicht kryptographisch bestätigt.
Fremdmaterial bleibt seinen jeweiligen Quellen zugeordnet; dieses Repository
erteilt dafür keine neue Lizenz.

Nächste Priorität: Als Nächstes wird die offene Anfangswertfrage geprüft: Für eine feste Permutation betrifft sie nur die erste Klartextrune. Ein Verfahren für alle 29 Werte muss vorab mit unabhängiger Scoreprüfung und ausdrücklich behandelter Mehrdeutigkeit validiert werden.
Kein Hintergrundprozess oder Zeitplan ist aktiv.
Vor Fortsetzung [AGENTS.md](AGENTS.md) und den aktuellen Forschungsstand lesen.

