# Sechste Forschungsserie: Quellenbilder, Leserichtungen und Zahlentabellen

Stand (UTC): 2026-10-19T17:40:46.443777+00:00. **Keine neue Entschlüsselung bestätigt.**
Die Zeilenstruktur von sieben Seiten wurde am Bild geprüft. Eine begrenzte
Leserichtungssuche auf vier unbekannten Runenseiten wurde mit bekannten Lösungen
und Zufallstexten validiert. Zusätzlich wurden Unterschiede zwischen drei
Transkriptionen der Zahlentabellen dokumentiert.

## Bildprüfung und explizite Grenzen

Geprüft wurden LP2-00, 49, 50, 51, 55, 56 und 57. Drei zusätzliche JPEGs wurden
aus dem schon gepinnten scream314-Commit geladen; übrige Bilder lagen bereits
im Quellenbestand. [Bildmanifest](../sources/layout_images_manifest.json) und
[Layoutprotokoll](../sources/layout_audit.json) enthalten URLs, Commit, Abrufzeit,
SHA-256, native Bildgröße und manuell gewählte Pixelregionen der Zeilen.
Die Regionen sind ungefähre Inspektionsbereiche, keine exakten Glyphensegmente.

Bestätigte Zeilenstruktur: LP2-00 zwölf Runenzeilen; LP2-49 drei Runenzeilen über
einer 10×8-Tabelle; LP2-50 eine 13×8-Tabelle ohne Runentext; LP2-51 neun Tabellenzeilen
zu je acht Zellen und vier Runenzeilen darunter; LP2-55 vier Runenzeilen.
LP2-56 hat drei plus zwei Runenzeilen mit einem Hash dazwischen, LP2-57 fünf.
Große Initialrunen werden ausdrücklich einmal der ersten Textzeile zugeordnet,
wie in der bestehenden Transkription. Das ist eine festgehaltene Zuordnungsregel.

Die Prüfung betrifft Zeilenanzahl, Reihenfolge und Endpunkte, **keine vollständige
unabhängige Transkription jeder Glyphe** und keinen Bildaudit des gesamten Buchs.
Die Schrift ist nicht gleichmäßig in Runenspalten gesetzt. Deshalb werden keine
künstlich aufgefüllten Rechtecke oder angeblich physischen Vertikalspalten erzeugt.
Quellenübereinstimmung beweist keine unabhängig authentifizierte Cicada-Herkunft.

## E021: acht Leserichtungen mit festem Chiffrenraster

LP2-00, 49, 51 und 55 waren vor den neuen Scores festgelegt. Acht bijektive
Permutationen: Zeilen von oben oder unten; innerhalb der Zeilen links nach rechts,
rechts nach links oder abwechselnd, mit beiden Anfangsrichtungen. Ungleiche
Zeilenlängen bleiben erhalten. Die Permutation erfolgt **vor** der Entschlüsselung;
Schlüsselphase und F-Unterbrechungen beziehen sich auf diesen Lesestrom.

Jede Route prüft alle 812 affinen Substitutionen, die beiden bekannten Schlüssel
DIVINITY und FIRFUMFERENFE mit allen Phasen sowie Primzahlen, p−1 und φ(n) mit
Starts 0–255. Bei den Schlüsselströmen werden vier Vorzeichen und sämtliche
F-Teilmengen exakt optimiert. Der externe Viergramm-Score bleibt unverändert.
Die normale Leserichtung dient als Referenz; die Schlüsselmenge ist kleiner
als der volle frühere Wortkatalog. E021 prüft weder beliebige Schlüssel noch
jede denkbare Transposition, Rückkopplung oder seitenübergreifende Kombination.

Die acht synthetisch umgeordneten LP2-56-Kontrollen werden jeweils im vollständigen
Suchraum exakt wiedergewonnen; die Route wird dem Sucher nicht verraten.
Zusammen mit LP2-57 ergibt das **9/9 exakte Kontrollen**. Die erwarteten Texte
sind bereits bekannt; dies validiert die Implementierung, keine neue historische Lösung.

Stärkster Kandidat: LP2-49, Route `top_snake_right`,
Score -5.304835. Vollständige unveränderte Ausgabe:

```text
OEFCNGLIAMAGMBAEDUSTHYWATHWIPTALEAUOIACHNGFAEYTEAPIACDMDCRNGPOREORNGBEENDXELEMCSF
```

13 von 19 unabhängigen Nulltexten erreichen mindestens diesen Score.
Plus-eins-p=0.700, nach konservativer Auswahlkorrektur über 55 Seiten
p=1.000. Kein korrigiert signifikanter Befund.
Die Nulltexte erhalten Runenhäufigkeiten und die Anzahl gleicher Nachbarrunen
in der ursprünglichen Speicherreihenfolge. Jeder durchläuft wieder alle acht
Routen und das gesamte Chiffrenraster. Die vier Seiten wurden auch aufgrund
früherer Scores ausgewählt; sie sind keine frische Zufallsstichprobe. Der Faktor
55 berücksichtigt diese Auswahl konservativ. Das Nullmodell erhält keine
Wortgrenzen oder andere höhere Struktur. 19 Replikate könnten korrigierte
Signifikanz nicht auflösen; null Überschreitungen würden eine größere Prüfung erfordern.

## E022: Zahlentabellen als Quellenproblem

Die Tabellen von LP2-49/50/51 enthalten zusammen **256 Zellen**. Die Base60-Deutung
steht bereits in der gepinnten Community-Quelle und wird hier nur reproduziert:
Alphabet `0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwx`,
Wert eines Paars = 60×Index des ersten Zeichens + Index des zweiten Zeichens.
Alle Werte der drei Transkriptionsvarianten liegen zwischen 0 und 255.
Das beweist weder einen Dateityp noch eine Verschlüsselung oder einen Schlüssel.

Es gibt **5 unterschiedliche Zellen** zwischen den Quellen:

| Seite | Zeile,Spalte (ab 1) | relikd / iddqd / scream314 | jeweilige Base60-Werte |
|---|---|---|---|
| LP2-49 | 6,6 | 1L / 1l / 1l | 81 / 107 / 107 |
| LP2-49 | 7,3 | 0L / 0l / 0l | 21 / 47 / 47 |
| LP2-50 | 11,6 | 0l / 0I / 0I | 47 / 18 / 18 |
| LP2-50 | 12,5 | 2s / 2S / 2S | 174 / 148 / 148 |
| LP2-51 | 8,7 | 3i / 3I / 3I | 224 / 198 / 198 |

Zusätzlich enthält die veröffentlichte Dezimaltabelle der scream314-Quelle
**9 Abweichungen** von der direkten Umrechnung ihrer eigenen
Base60-Zeichen. Die ursprüngliche Kennzeichnung einer Tabelle als fehlerhaft
wird als Quellenhinweis behandelt, nicht als Entscheidung über richtige Glyphen.
Details und alle drei vollständigen Varianten bleiben im
[E022-Ergebnis](../results/E022-numeric-source-audit-7f284cff4638.json) erhalten.

Die Konflikte sind **nicht aufgelöst**. Groß-/Kleinschreibung wird nicht automatisch
angeglichen. Bestehende kanonische Daten und historische Ergebnisse wurden nicht
verändert. E021 entschlüsselt ausschließlich den ausgewählten Runenstrom;
Tabellen, Hashes und Bilder bleiben erhalten, ohne sie als Runen oder zusätzlichen
Schlüsselverbrauch zu interpretieren. Das ist eine Begrenzung dieser Hypothese.

## Validierung und Fortsetzung

67 Tests bestanden; 39 gespeicherte Kandidaten wurden unabhängig
zurückverschlüsselt und über die inverse Route wieder an die ursprünglichen
Positionen gesetzt. Modellwerte wurden skalar nachgerechnet, Hashes geprüft.
E022 ist ein deterministischer Quellen-/Rechenvergleich; ein Zufallsmodell oder
p-Wert wäre dafür nicht sinnvoll. Es wird keine neu entdeckte Chiffre behauptet.

25 erfolgreiche Aufgaben, 272.814 Sekunden Experimentzeit innerhalb
des 900-Sekunden-Budgets; maximal 180 Sekunden je Prozess, ein Forschungsprozess.
Keine Hintergrundaufgabe läuft weiter. [Checkpoint](../checkpoints/phase6_complete.json),
[Übersicht](../results/phase6_summary.json), [Forschungsstand](../research_state.json).

Als Nächstes haben die widersprüchlichen Zahlenzeichen Priorität: mit Bildkoordinaten
prüfen, offene Alternativen erhalten und erst dann begrenzte Hypothesen für die
256 Werte festlegen. Längere allgemeine Rückkopplung bleibt eine getrennte Aufgabe.
