# Zwanzigste Forschungsserie: Sprachkontext und blinde Schlüsselsuche

Stand (UTC): 2026-10-21T15:52:31.019557+00:00. **Keine neue Entschlüsselung bestätigt.**
E056 rekonstruiert bei vorgegebenem Schlüssel alle 15 Kontrollen exakt.
E057 findet ohne Lösungsvorgaben drei neue Kontrollen vollständig, verfehlt
aber den bekannten schwierigen Fall. Die vollständige Freigabe ist gescheitert;
unbekannte LP-Seiten wurden mit dieser Variante nicht untersucht.

## E056: Bedingte Optimierung mit bekanntem Schlüssel

Der Sprachkontext der letzten drei Klartextrunen bleibt über Seitenwechsel
erhalten, während jede Seite eine eigene Schlüsselphase wählen darf.
Die exakte dynamische Programmierung führt Schlüsselcursor und Sprachkontext
gemeinsam. Leere Seiten, insbesondere Spannen nach dem Vorbild LP2-50,
bleiben mit Phase null erhalten. Die bisherigen Komplexitätsstrafen bleiben.
Auch die nachfolgende Schlüsseloptimierung bewertet Sprachfenster über Grenzen.

Zwölf E054-Kontrollen bleiben unverändert. Drei neue, gezielt konstruierte
Grenzfälle stammen aus Emerson X/XI/XII, Runen 12000:12729, mit Schlüssellängen
17/23/31. Die zweite Grenze wird auf eine Nicht-F-Klartextrune gelegt und
Schlüsselstelle null bewusst gleich dieser Rune gesetzt. Das erzwingt dort
eine nicht kopierte Chiffren-F. Diese Fälle sind Stresstests, keine zufällige
Stichprobe allgemeiner Schlüssel. Seeds und Konstruktion stehen im festen Plan.

Der wahre Schlüssel und das Vorzeichen sind hier ausdrücklich vorgegeben;
F-Kopiermaske und Seitenphasen werden optimiert. Alle 15 Fälle werden exakt
rekonstruiert; das bisherige Ziel mit neuem Sprachkontext je Seite schafft
14/15. Alte unveränderte Baselines wurden wiederverwendet. Fünf alternative
Anfangs-F-Rezepte mit identischer Rückverschlüsselung bleiben gespeichert,
auch bei geringerem Sprachscore. Bessere Rangfolge beseitigt keine
algebraische Mehrdeutigkeit. Ein passender Nulltext wurde nur mit dem festen
bekannten Schlüssel bewertet; daraus folgt kein Signifikanznachweis.

## E057: Vorab gestufte Blindkontrollen

Für Eingaben bis 1024 Runen steigen Starts pro Periode/Vorzeichen von 16 auf
64 und behaltene Unigrammstarts von zwei auf vier. Größere Eingaben bleiben
unverändert. Perioden 17–32, beide Vorzeichen, 20 diversifizierte Volltextstarts,
höchstens drei gemeinsame Optimierungsrunden mit je sechs Schlüsseldurchläufen.
Die Fragmentinitialisierung bleibt seitengebunden; die Volltextsuche verwendet
den E056-Kontext. Schlüssel, Maske und Phasen werden nicht an den Solver gegeben.

Stufe A prüft zuerst den unveränderten kurzen E054-Fehler, dann drei natürliche
neue Texte aus X/XI/XII, Runen 14000:14729. Seitenlängen 262/266/201,
Schlüssel 17/23/31, unabhängige Zufallsphasen und F-Kopierwahrscheinlichkeiten
0,25/0,50/0,75; keine erzwungenen Grenzrunen. Trainingskapitel bleiben I, III–IX.
Alle vier Kontrollen und ein vollständiger passender Nullversuch wurden beendet.

| Kontrolle | Schlüssellänge | richtige Runen | Text/Schlüssel/Maske/Phasen |
|---|---:|---:|---|
| regression 2 | 31 | 43/729 | verfehlt |
| fresh 0 | 17 | 729/729 | exakt |
| fresh 1 | 23 | 729/729 | exakt |
| fresh 2 | 31 | 729/729 | exakt |

Die bekannte schwierige Kontrolle bleibt mit 43/729 richtigen Runen ungelöst
(vorher 30/729). Daraus wird keine brauchbare Teilentschlüsselung abgeleitet.
Der einzelne diagnostische Nullscore beträgt -5.513590576; kein
p-Wert wird berechnet. Wegen des Fehlers wurde Stufe B entsprechend dem Plan
nicht ausgeführt: elf weitere E054-Regressionen und drei E056-Stresstests
bleiben offen. Drei frische Erfolge ersetzen diese vollständige Kalibrierung nicht.

## Prüfung und Ressourcen

118 Unit-Tests bestanden. Unabhängig nachgerechnet: 15.520 Poolzustände,
160 Fragmentphasen-Maxima, 474 gekoppelte Zustände, 21 vollständige bedingte
Maxima sowie fünf Anfangs-F-Alternativpaare. Quellbereiche, Rückverschlüsselung,
Seeds, Nullkonstruktion und Hashes wurden in separaten Verifikationsskripten geprüft.

Sechs registrierte Aufgaben; 253.685 Sekunden Experimentzeit.
Budget 1500 Sekunden insgesamt, 180 je Aufgabe, ein Worker. Höchster abgetasteter
Resident-/Private-Speicherwert 129.0 MiB
bei 768 MiB Abbruchgrenze. Keine fortlaufenden Hintergrundaufgaben.
Originalquellen und frühere Versuchsergebnisse bleiben unverändert.

## Nächste ungetestete Hypothese H043

Die Initialisierung behandelt Fragmentphasen bisher unabhängig. Innerhalb
derselben Seite gilt für Starts a<b notwendigerweise
`phase_b - phase_a = (b-a)-s (mod m)`, wobei s die kopierten F zwischen den
Starts zählt und durch die dortige Anzahl Chiffren-F begrenzt ist. Eine
gemeinsame Initialisierung könnte diese aus dem Chiffretext bekannte Bindung
nutzen. Das ist ein Vorschlag für einen neuen begrenzten Versuch; weder
Beschleunigung noch bessere Rekonstruktion wurden hierfür gemessen.

[Oracle-Plan](../experiments/context_phase_plan.json),
[Blindkontrollplan](../experiments/context_blind_plan.json),
[Messübersicht](../results/phase20_summary.json),
[Checkpoint](../checkpoints/phase20_complete.json).
