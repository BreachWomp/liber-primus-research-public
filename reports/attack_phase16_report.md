# Sechzehnte Forschungsserie: Gemeinsamer Schlüssel, verschiedene Seitenanfänge

Stand (UTC): 2026-10-20T20:52:45.789129+00:00. **Keine neue Entschlüsselung bestätigt.**

## Regel und direkter Angriff

E048 untersucht die zehn gepinnten E012-Seitengruppen mit
`P_i=s*C_i+K[(phase_page+j) mod m] mod29`, s=±1. Jede Seite beginnt bei
einer eigenen unbekannten Schlüsselposition. Ein Chiffren-F kann F kopieren,
ohne j zu erhöhen. Schlüssel gemeinsam, Sprachkontext pro Seite neu.
Gruppen bleiben unbestätigte Chiffregrenzen. Alle Quellrunen, Seitenoffsets
und die leere Runenspanne der Zahlenseite LP2-50 bleiben erhalten.

| Gruppe | Runen | Bester penaliserter Score |
|---|---:|---:|
| LP2-00_02 | 729 | -5.884705 |
| LP2-03_07 | 1145 | -6.075798 |
| LP2-08_14 | 1729 | -6.115033 |
| LP2-15_22 | 1903 | -6.130898 |
| LP2-23_26 | 1021 | -5.975088 |
| LP2-27_32 | 1433 | -6.079707 |
| LP2-33_39 | 1680 | -6.098128 |
| LP2-40_53 | 3008 | -6.262252 |
| LP2-54_55 | 308 | -5.567525 |
| LP2-40_55 | 3316 | -6.281567 |

Startschlüssel: zwei längste Seiten (maximal 1.024 Runen) und drei längste
F-freie Abschnitte innerhalb einer Seite (32–256 Runen). E038-Suche mit
Perioden 1–16, beiden Vorzeichen und vier Starts; zwölf zyklisch verschiedene
Schlüssel behalten. Exakte seitenweise Suche über alle Phasen und F-Masken,
danach bis zu drei Runden aus sechs gemeinsamen Koordinatendurchläufen
und erneuter Phasen-/Maskenoptimierung. Schlüsselsuche bleibt heuristisch.

Der Schlüssel wird so gedreht, dass die erste nichtleere Seite Phase 0 hat.
Andere Phasen werden entsprechend angepasst; leere Seiten haben Phase 0.
Das entfernt eine redundante globale Drehung. Vor dem Angriff fester Score:
`[sum(page logp4) - m*ln29 - cipherFcount*ln2 - (G-1)*ln(m)]/N`,
mit primitivem Schlüssellänge m und G nichtleeren Seiten. Der Phasenabzug
berechnet die zusätzlich zugelassenen Anfangspositionen; er ist kein Beweis
gegen Überanpassung und ersetzt den Zufallsvergleich nicht.

## Kontrollfähigkeit und Ergebnis

E047 rekonstruiert drei externe Kontrolltexte mit 3.316, 1.200 und 1.200 Runen exakt:
**Klartext, Schlüssel, sämtliche Seitenphasen und F-Unterbrechungen.**
Zufallsschlüssel mit Längen 5, 8, 13, Vorzeichen +1, −1, +1; Seitenphasen zufällig,
erste nichtleere Phase 0. Keine dieser Vorgaben wird dem Solver mitgegeben.
Kontrolltexte aus Emerson X, XI, XII, Training ausschließlich I, III–IX;
Original-Quellbereiche disjunkt. Diese Kapitel waren historisch bereits
bekannt, daher keine Behauptung einer historisch blinden Prüfung.
Ein weiterer vollständiger Kontroll-Nullversuch dient der Diagnose.

Stärkster unbekannter Abschnitt: **LP2-54_55**,
Score -5.567525, Sprachwertung -5.392394.
Vorzeichen -1, Schlüssel `[27, 22, 5, 18, 5, 26, 23, 15, 8, 0, 22, 14, 1, 20]`.
F-Skips als nullbasierte Runenoffsets im gesamten Abschnitt:
`[247, 257, 273]`.

| Seite | Anfangsphase |
|---|---:|
| LP2-54 | 0 |
| LP2-55 | 2 |

Rückverschlüsselung: `C_i=s*(P_i-K[(phase_page+j) mod m]) mod29`,
F-Skips unverändert. Ausgabe nur zur Nachprüfbarkeit verkettet:

```text
OOPAWANCETHEAUNMLIASTHICTHPIOEWGLSTHNNEOTHWPLMYGWIALUNGEWOSAYOLDNTHTHDMRRJMSIATFIANMMAJWMAGBWLEAJFGSLASSNGFFBBTIREATUTSREOLHAEAEFLHRFFEYAWTHEPRUIRNETHRRBEIRCUTEDGEOEAFBERSOEATGSROYTEADOEBBEOMNOYEADFFOENGSNGUPMNETHBTRAELAPFIFMSSNALRETATMLOSNGMNGPCMDIPAWNREJODABJLLFGOEBEPOESTTFLSOEAEXRLNFLINEXUAECSFTIHNGFCYCOOEXEATBFOMIFGTIACCTHSTEAEOCSLOFMAUINMONTYTNGBFA
```

**Suchausgabe, kein bestätigter Klartext.** Sieger und alle Ergebnis-Prüfsummen
vor Nullgenerierung eingefroren. Pro Seite erhalten die Nulltexte exakte
Runenhäufigkeiten, Randrunen und gleiche Nachbarpaare. Innenpositionen werden
unabhängig gleichverteilt permutiert und bis zur passenden Nachbarpaarzahl
verworfen (maximal 100.000). Jeder Nulltext durchläuft den vollständigen Solver
mit eigener Auswahl von Startabschnitten, Schlüsseln, Phasen und Masken.

**18/19** erreichen mindestens den beobachteten Score.
Plus-eins-p=0.950; Bonferroni10=1.000.
Kein durch diesen Vergleich gestützter Lösungskandidat.
19 Replikate können korrigierte Signifikanz nicht auflösen. Korrektur nur
für diese zehn Gruppen, nicht projektweit. Kein allgemeiner Ausschluss
beliebiger Schlüssel oder Chiffregrenzen.

## Prüfung und Fortsetzung

106 Tests bestanden. 1676 Kandidatenaufzeichnungen,
396 Starts und 396 Suchverläufe unabhängig
skalar nachgerechnet, einschließlich Rückverschlüsselung, Phasen und Kosten.
Separater Score-Viterbi reproduziert die bedingten Phasen-/Maskenmaxima
aller 33 Suchausgaben. Kleine Tests enumerieren alle Phasen
und Masken vollständig und prüfen die globale Drehungsinvarianz.
Quellbereiche, Zufallsschlüssel, Phasen und alle 20 neuen Nulltexte aus Seeds
reproduziert; Ergebnis- und Abhängigkeitshashes stimmen.

30 Aufgaben, 234.441 Sekunden erfolgreiche Experimentzeit;
E048 mit Ablaufaufwand 209.470 Sekunden unter 650.
Phasenbudget 900, maximal 180 je Prozess, ein Worker, 4.096 Runen/16 Seiten.
Keine neuen Fremdquellen, keine Änderungen an Quellen oder historischen Ergebnissen.

Nächste direkte Hypothese: längere periodische Schlüssel mit 17–32 Runen.
Die bisherigen beliebigen Schlüsselsuchen endeten bei 16. Dieser offene
Bereich ist kein positiver Hinweis; vor unbekannten Texten sind längere
Kontrollen, ein begrenzter Solver und Nullkalibrierung innerhalb des Rechenbudgets erforderlich.

[Plan](../experiments/phase_key_unknown_plan.json),
[Auswahl](../experiments/phase_key_selection.json),
[Messübersicht](../results/phase16_summary.json),
[Checkpoint](../checkpoints/phase16_complete.json).
