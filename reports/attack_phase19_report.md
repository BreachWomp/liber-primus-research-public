# Neunzehnte Forschungsserie: Lange Schlüssel mit Seitenphasen

Stand (UTC): 2026-10-21T15:29:02.227402+00:00. **Keine neue Entschlüsselung bestätigt.**
10 von zwölf Kontrollen werden vollständig rekonstruiert.
Die nicht bestandenen Kontrollen blockieren den Angriff auf unbekannte Seiten
mit dieser Variante. Die bereits abgeschlossene Serie 18 bleibt unverändert.

## E054: Neue Regel und vorab festgelegte Prüfung

Gemeinsamer Schlüssel, nominal 17–32 Runen, Vorzeichen ±1. Jede Seite darf
an einer eigenen Schlüsselphase beginnen; ihr Sprachkontext beginnt neu.
Eine ausgewählte Chiffren-F wird ohne Schlüsselverbrauch kopiert.
Die erste nichtleere Seite hat Phase null als Darstellungskonvention;
leere Zahlenseiten bleiben erhalten und haben Phase null.

E052-Initialisierung unverändert bis auf die notwendige Seitengrenze:
F-freie Startfragmente dürfen nun keine Seite überqueren. Zwölf längste
Fragmente ab 16 Runen, je maximal 256; 16 Starts pro Periode/Vorzeichen,
Unigramm-, Bigramm-, Viergrammfolge, 20 diversifizierte Volltextstarts.
Dann exakte bedingte Phasen-/F-Suche je Seite und bis zu drei gemeinsame
Schlüssel-/Zeitplanrunden. Der Score bestraft zusätzlich die freien
Seitenphasen: `(sum_page(logp4)-m*ln29-F_count*ln2-(G-1)*ln(m))/N`.

Sechs neue Quellbereiche: Emerson X, XI, XII jeweils Runen 6000:6729 und
8000:11316. Schlüssel 17, 23, 31; Seitenlängen wie LP2-00_02 beziehungsweise
LP2-40_55, einschließlich des leeren LP2-50-Spanneneintrags. Unabhängige
Zufallsphasen und Bernoulli-Kopie jeder Klartext-F mit p=0,25/0,50/0,75.
Feste getrennte Seeds für Schlüssel/Phasen und Masken. Training weiter
I, III–IX; Originalbereiche unabhängig nachgerechnet und disjunkt.
Hinzu kommen alle sechs E052-Eingaben unverändert; ihre bekannten
Seitenphasen werden nur zur Auswertung aus dem durchlaufenden Cursor
abgeleitet und nicht an den Solver übergeben.

| Kontrolle | Kapitel | Schlüssel | richtige Runen | Text/Schlüssel/Maske/Phasen |
|---|---|---:|---:|---|
| Neu 0 | X | 17 | 728/729 | verfehlt |
| Neu 1 | XI | 23 | 729/729 | exakt |
| Neu 2 | XII | 31 | 30/729 | verfehlt |
| Neu 3 | X | 17 | 3316/3316 | exakt |
| Neu 4 | XI | 23 | 3316/3316 | exakt |
| Neu 5 | XII | 31 | 3316/3316 | exakt |
| Regression 0 | X | 17 | 1200/1200 | exakt |
| Regression 1 | XI | 23 | 1200/1200 | exakt |
| Regression 2 | XII | 31 | 1200/1200 | exakt |
| Regression 3 | X | 17 | 3316/3316 | exakt |
| Regression 4 | XI | 23 | 1200/1200 | exakt |
| Regression 5 | XII | 31 | 1200/1200 | exakt |

Ein vollständiger passender Nulltext zur kurzen 31-Kontrolle hat Score
-5.555361. Ein einzelner diagnostischer Nullvergleich
erhält keinen p-Wert. Die kurzen Positivkontrollen schließen die bisherige
Kalibrierungslücke sichtbar nicht vollständig: langes Gelingen garantiert
kein kurzes Gelingen. Der korrekte 17-Schlüssel der ersten Kontrolle wird
gefunden, aber eine Rune an Position 262, dem Beginn der zweiten Seite,
anders bewertet. Der kurze 31-Fall verfehlt den Schlüssel und hat nur 30/729
richtige Runen. Die Fehler werden nicht als Ausschluss dieser Chiffre gedeutet.

## E055: Explizite Oracle-Diagnose und echte Mehrdeutigkeit des Modells

Nach Beobachtung der Fehler separat registriert; keine nachträgliche
Parameteranpassung und kein unbekannter Text. Nur für fehlgeschlagene
Kontrollen wird der wahre Schlüsselzyklus samt Vorzeichen an die exakte
Phasen-/F-Optimierung übergeben. Das ist eine Diagnose mit Lösungswissen.

| Kontrolle | Oracle: richtige Runen | Wahrer Score | Oracle-Score | Oracle minus wahr |
|---|---:|---:|---:|---:|
| fresh 0 | 728/729 | -2.19370452 | -2.19317037 | 0.00053415 |
| fresh 2 | 729/729 | -2.32779446 | -2.32779446 | 0.00000000 |

Positive Score-Differenz bedeutet: Selbst bei bekanntem Schlüssel bevorzugt
dieses Sprachziel eine abweichende Ausgabe. Ein exakter Oracle bei zugleich
verfehlter blinder Suche zeigt dagegen einen Suchengpass. Keines dieser
Oracle-Ergebnisse zählt als eigenständige Entschlüsselung.

Unabhängig vom Score gibt es eine konkrete algebraische Mehrdeutigkeit.
Beginnt eine nicht erste Seite mit Chiffren-F, also `C_0=0`, gilt:

* Normal entschlüsseln bei Phase `p`: erste Klartextrune `K[p]`, danach Cursor `p+1`.
* F kopieren bei Phase `p+1`: erste Klartextrune `0`, danach ebenfalls Cursor `p+1`.

Alle folgenden Runen verwenden dieselben Schlüsselstellen. Beide Varianten
erzeugen bei Rückverschlüsselung exakt denselben Chiffretext. Die inverse
Änderung entfernt eine Kopie und verschiebt die Startphase um minus eins.
Der Schlüssel selbst bleibt gleich. Damit ist die Abbildung bei frei
wählbaren Seitenphasen und optionaler Anfangs-F-Kopie ohne Zusatzinformation
nicht eindeutig umkehrbar. Es handelt sich um eine Eigenschaft des geprüften
Modells, nicht um einen Nachweis der tatsächlichen Liber-Primus-Chiffre.

Für alle passenden Seitenanfänge in allen zwölf Kontrollen wurden
**2 solche Paare** gespeichert und unabhängig rückverschlüsselt.
Jedes Paar unterscheidet sich in genau einer Klartextrune. Sprachbewertung
kann zwischen ihnen wählen, beseitigt diese algebraische Mehrdeutigkeit aber
nicht. Solche Alternativen müssen ausdrücklich sichtbar bleiben.

## Validierung, Grenzen und nächste Versuche

114 Tests bestanden. 13728 skalare
Poolzustandsprüfungen, 1172 Volltext-
zustandsprüfungen, 416 unabhängig
enumerierte Fragmentphasen-Maxima und 13
vollständige bedingte Phasen-/Zeitplanprüfungen. Zusätzlich 2
Oracle-Maxima und 2 Mehrdeutigkeitspaare separat bestätigt.
Originaltextbereiche, Seeds, Seiten einschließlich leerer Spannen, Nulltext,
Auswahlregeln, Hashes und Rückverschlüsselungen geprüft.

14 registrierte Aufgaben, 395.494 Sekunden Experimentzeit;
Budget 1200, maximal 180 je Aufgabe, ein Worker. E054-Speicherüberwachung
alle 250 ms: höchster abgetasteter Resident-/Private-Wert
127.3MiB bei Abbruchgrenze 768 MiB.
E055 ist eine begrenzte deterministische Diagnose. Keine Quellbytes oder
historischen Ergebnisse verändert; keine weiterlaufenden Forschungsprozesse.

Nächste Schritte: Sprachkontext über Seitenwechsel hinweg prüfen und dabei
mehrdeutige Anfangs-F-Varianten ausdrücklich erhalten. Separat braucht die
kurze 31-Schlüsselsuche eine vorab begrenzte bessere Initialisierung, geprüft
an frischen Fällen. Kein stilles Abschwächen der bestandenen Kontrollkriterien
und kein Hochstufen sprachähnlicher Ausgaben zu Lösungen.

[Kontrollplan](../experiments/long_phase_plan.json),
[Diagnoseplan](../experiments/long_phase_diagnostic_plan.json),
[Messübersicht](../results/phase19_summary.json),
[Checkpoint](../checkpoints/phase19_complete.json).
