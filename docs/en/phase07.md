# Phase 7: Glyph evidence, numeric diagnostics, and delay-two feedback

**No new decryption confirmed.** Historical report date: 2026-10-19T17:56:16.716925+00:00.

English editorial edition; the original report and raw results are preserved
unchanged. This edition consolidates repeated wording and navigation.

E023 uses sixteen unresampled image crops and comparison glyphs to support
readings `1l`, `0l`, `0I`, `2S`, and `3I` for the five disputed cells. Lowercase
l measures 73–74 pixels versus uppercase I at 67; uppercase S measures 69–71
versus lowercase s at 44–45. Thresholds 32/128/224 were a sensitivity check
chosen after inspection, not a validated OCR system. A separate correction
overlay matches the existing iddqd tokens. Original bytes and alternatives
remain intact. This is one visual reader, not a second independent reading or
an exhaustive transcription. The nine decimal inconsistencies remain recorded.

E024 interprets the 256 values in page/row order. Byte SHA-256 is
`3b9b07d9a26e6d55c432d94d2661fdff3c2b348daed06821f2bdb23184a4b290`.
There are 161 distinct values, 127 equal unordered pairs, no equal neighbors,
and empirical entropy 7.169655 bits. Four fixed tests compare 9,999 IID-uniform
byte sequences (seed 3301024): collision deviation p=1; adjacent repeats
p=0.6362; maximum bit imbalance p=0.9663; column-sum dispersion p=0.2879.
All Bonferroni4 values are 1 and all four positive controls pass. These tests
do not prove randomness, encryption, or a file type.

E025 tests `P[i]=a*C[i]+b*P[i-2] mod29` with two free initial values, nonzero
coefficients excluding four previously tested sign pairs. There are 655,980
rules per page and 36,078,900 across 55 pages. Initial-plaintext coordinates
are a bijection to keys, not a heuristic reduction. At most 2,048 candidates
are held together. Three synthetic controls are exact. Selected LP2-49 scores
-5.025140; 7/19 full matched-null searches reach it: raw p=0.40, adjusted 1.
No F skips, offsets, routes, or cross-page continuation are included.
Delay three is mathematically prepared but **not searched** in this phase.

**73 tests passed; 174 saved candidates were independently rescored and
re-encrypted.** Seventy-seven completed tasks used 320.634 seconds, including
318.785 for E025, within its 650-second and the phase's 900-second budgets.

## Preserved candidate outputs

These blocks are copied verbatim from the historical report, in its order.
They are search outputs, **not confirmed plaintext**. Their rules, selection
context, and full records are in the linked evidence.

```text
JTSTBAEIMSHNGWHAYNDHAUELTAESTHCOEOEYENGEGEOAYDIACJAXLLETOYADYTFEADWHIATCHNEL
```

## Evidence

- [Original frozen report](../../reports/attack_phase7_report.md) (historical wording, usually German).
- [Complete machine-readable phase summary](../../results/phase7_summary.json).
- [Checkpoint and resource accounting](../../checkpoints/phase7_complete.json).
- [All registered outcomes](../../experiment_log.jsonl), [hypotheses](../../hypotheses.json), and [English index](INDEX.md).

Additional original evidence: [contact_sheet.png](../../sources/glyph_crops/contact_sheet.png), [glyph_crop_manifest.json](../../sources/glyph_crop_manifest.json), [glyph_observations.json](../../sources/glyph_observations.json), [phase7_complete.json](../../checkpoints/phase7_complete.json), [phase7_summary.json](../../results/phase7_summary.json).
