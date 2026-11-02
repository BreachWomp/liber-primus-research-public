# Sprachähnliche Ausgabe einer bekannten Kontrolle, Serie 29

**Kein Text einer neu entschlüsselten LP-Seite.** Dies ist ein absichtlich
verschlüsselter Emerson-Kontrolltext, dessen Lösung vorab bekannt ist.
Die Schlüsselsuche erhält nur Chiffre und Wortgrenzen. Trenner entsprechen
den festgelegten Quellwortgrenzen; GP-Schreibungen bleiben unverändert.

Quelle: Kapitel XII, Absatz 1, Zeichenbereich
[395179, 396102] der unveränderten UTF-8-dekodierten Quelldatei.

Richtiger Text:
```text
GIUE / TO / BARROWS / TRAYS / AND / PANS / GRACE / AND / GLIMMER / OF / ROMANCE / BRNG / THE / MOONLIGHT / INTO
```

Bestbewertete, falsche Ausgabe:
```text
GIUE / TO / BARROWS / TRAPS / AND / YANS / GRACE / AND / GLIMMER / OF / ROMANCE / BRNG / THE / MOONLIGHT / INTO
```

65/67 Runen stimmen. Score richtig -2.421091301, falsch
-2.321066389; höher gilt im Modell als besser.
Der Tausch P/Y erzeugt TRAPS statt TRAYS und YANS statt PANS.
TRAPS kommt einmal im Training vor, die drei anderen Wörter keinmal.
Die Belohnung für TRAPS überwiegt die Verschlechterung PANS→YANS.
Das ist ein konkret nachgewiesener Bewertungsfehler, keine neue Lösung.

[Vollständiger Lauf](../results/E081-control-5-acb6c1a444ff.json), SHA-256 `5694b5a39177ad169796a4aa1bb1a57d2029da95a7bef44bfe2a84ac41503acc`.
Die genaue reversible 29-Runen-Abbildung steht in `result.top.mapping_cipher_to_plain`.
