# Neunte Forschungsserie: Direkter Angriff mit Geheimtext-Rückkopplung

Stand (UTC): 2026-10-20T09:17:01.804533+00:00. **Keine neue Entschlüsselung bestätigt.**

## E033: Zwei vorherige Geheimtextrunen als Rückkopplung

Nach ausdrücklicher Nutzerpräzisierung liegt die Priorität auf dem Lösen der
unbekannten Seiten. Weitere Prüfungen unbelegter Community-Lösungsmeldungen sind
nicht eingeplant. Die bereits abgeschlossenen Quellenprüfungen bleiben erhalten.

Neue endliche Familie: `P_(i-2) = a*C_i + b*C_(i-1) + c*C_(i-2) + d mod 29`.
Dabei sind a,c ungleich null; b,d durchlaufen ganz Z29. Vier bereits in E010
enthaltene reine Vorzeichenfälle sind ausgeschlossen. Das ergibt
**659.340 Regeln je Seite, 36.263.700 Regeln auf allen 55 ungelösten Runenseiten.**
LP2-50 bleibt als Zahlenseite erhalten. Die ersten zwei Geheimtextrunen sind
Initialwerte; für diese Positionen wird kein Klartext behauptet. Die inverse Regel
`C_i = a^-1*(P_(i-2)-b*C_(i-1)-c*C_(i-2)-d)` reproduziert den Originaltext exakt.

Der Wiederholungsmangel motiviert Rückkopplungsmodelle, legt diese Formel aber
nicht historisch fest. Keine F-Unterbrechung, Umordnung oder Seitenfortsetzung.
Alle Koeffizienten werden vollständig geprüft; keine heuristische Vorauswahl.
Score: unverändertes externes Viergramm-Modell von E016. Keine Anpassung an
unbekannte Kandidaten. Drei synthetisch verschlüsselte bekannte Texte werden im
gesamten Suchraum jeweils exakt als bestes Ergebnis zurückgewonnen.

Stärkster Suchtreffer: **LP2-49**, Score -5.015058.
Unveränderte Transliteration des Suffixes:

```text
TOOLHEALSANIPFEBUFIHODEAEENNTHNGDDSOLSPOINTHTIUEARDIPMEOITHOBGHNGOWYOEYCNF
```

Regel: `{"a": 28, "b": 0, "c": 22, "d": 13, "iv": [27, 18], "unrecovered_prefix_runes": 2, "F_policy": "none"}`.
Diese Ausgabe ist ein gespeicherter Suchtreffer, **keine Entschlüsselung**.

Nach eingefrorener Seitenauswahl durchliefen 19 unabhängige Zufallstexte dieselben
659.340 Regeln. Jeder erhält exakt die Runenhäufigkeiten und die Anzahl gleicher
Nachbarpaare der gewählten Seite; identische Behandlung der zwei Anfangspositionen.
**6/19** erreichen mindestens den beobachteten Score. Plus-eins-p=0.350,
Bonferroni über 55 Seiten=1.000. Diese kleine Kalibrierung kann
korrigierte Signifikanz nicht auflösen. Eine größere Prüfung ist
durch diesen Befund nicht begründet.

[Vorab festgelegter Plan](../experiments/cipher_filter_plan.json),
[eingefrorene Auswahl](../experiments/cipher_filter_selection.json).

## E030: Bereits begonnene Score-Prüfung abgeschlossen

Beide Sprachmodelle wurden nur auf Emerson-Kapiteln I und III–IX trainiert,
insgesamt 207030 Runen. X–XII wurden für diese
Prüfung ausgeschlossen. Frühere Experimente hatten diese Kapitel bereits verwendet;
es ist kein historisch ungesehener Blindtest. 62 Textfenster jeweils vollständig
und beidseitig gekürzt, 23 Apostroph-Absätze, acht bekannte Kontrolltexte
(sechs zusätzlich gekürzt). Insgesamt 6.440 Ein-Runen-Veränderungen und 3.059
häufigkeitserhaltende Zufallsfolgen; alle Ergebnisse beider festen Alternativen
gespeichert. Abhängige Messungen, deskriptiv, kein Signifikanznachweis.

| Bedingung / veränderte Region | Vollständige Wortwertung / getrennte Apostrophe | Zeichenwertung am Rand / verbundene Apostrophe |
|---|---:|---:|
| apostrophe / apostrophe_word | 448/460 | 452/460 |
| apostrophe / other | 450/460 | 450/460 |
| clipped / edge | 995/1240 | 1030/1240 |
| clipped / interior | 1222/1240 | 1222/1240 |
| intact / edge | 1229/1240 | 1203/1240 |
| intact / interior | 1221/1240 | 1221/1240 |

Die pauschale Randkorrektur steigert bei echten Fragmenten die Trefferquote um
2,82 Prozentpunkte, verschlechtert sie bei vollständigen Randwörtern aber um
2,10 Punkte. Die bekannte Kontrollrate der Alternative beträgt
93.21 % statt der verlangten
mindestens 95 %. **Vorab festgelegtes Gate verfehlt; keine Übernahme in E033.**
Das Apostrophverbinden liefert nur vier zusätzliche richtige Entscheidungen bei
460 gezielten Veränderungen. Kein hinreichender Grund für eine neue Gesamtsuche.
Beim Verbinden bleiben die pro Teilwort kodierten Runen unverändert.

## Bereits abgeschlossene Quellenprüfungen E031/E032

Fünf vorhandene Lesarten der 256 Tabellenbytes wurden deterministisch verglichen.
Keine entspricht dem behaupteten alternativen Digest. Die aktuelle öffentliche
Projektstruktur wurde am Commit `f71dadd835c4d2b71dba80ed555494013a35c843` gepinnt;
sie enthält die behauptete Binärdatei und den benannten Analyzer nicht.
Das ist kein Beweis über frühere Dateistände. Herkunft weiterhin ungeklärt.
Die Byte-Vorschauen widersprechen zudem zwei bereits bildgeprüften `3I`-Lesarten
auf LP2-49 r4c2 und LP2-51 r8c7. Kanonische Daten bleiben unverändert.
Diese Nebenuntersuchung wird auf Nutzerwunsch nicht fortgesetzt.

[Gesicherter Quellenstand](../sources/claim_repository_2026-10-20/manifest.json),
[gesicherte Textdateien](../sources/claim_repository_2026-10-20/files_manifest.json).

## Validierung und nächste direkte Angriffe

**84 Tests bestanden.** 193 Suchkandidaten unabhängig vorwärts
und rückwärts berechnet und mit dem skalaren Sprachmodell nachbewertet.
19320 E030-Scores aus unabhängig implementierten Wahrscheinlichkeitsformeln
nachgerechnet; Trainingsausschluss, Quellanker, Veränderungen und Nullhäufigkeiten
geprüft. Alle neuen Ergebnis- und Abhängigkeitshashes stimmen.

78 abgeschlossene Aufgaben, 347.378 Sekunden protokollierte
Experimentzeit, davon E033 343.844 Sekunden unter der 750-Sekunden-Grenze.
Ein Forschungsprozess, höchstens 180 Sekunden je Aufgabe, Phasengrenze 900 Sekunden.
Kein Hintergrundprozess bleibt aktiv.

Nächste Priorität: weitere begrenzte
Klartext-Rückkopplung mit exakt überprüften Kontrollen und vollständigem
Zufallsvergleich. Schlüssel- oder Leserichtungsbeschränkungen sollen sich auf
die tatsächlichen Liber-Primus-Quellen stützen.

[Checkpoint](../checkpoints/phase9_complete.json), [Messübersicht](../results/phase9_summary.json).
