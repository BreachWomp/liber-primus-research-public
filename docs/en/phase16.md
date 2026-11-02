# Phase 16: A shared key with independent page phases

**No new decryption confirmed.** Historical report date: 2026-10-20T20:52:45.789129+00:00.

English editorial edition; the original report and raw results are preserved
unchanged. This edition consolidates repeated wording and navigation.

E048 tests ten section hypotheses using
`P[i]=s*C[i]+K[(page_phase+j) mod m] mod29`, with optional copied F and a
fresh language context per page. The first nonempty page is normalized to phase
zero by a global key rotation; empty pages also use zero. Periods 1–16, twelve
starts, and three alternating key/schedule rounds remain bounded heuristics.
Given a key, each page's phase and F mask are optimized exactly. The fixed
score subtracts `m*ln29 + F_count*ln2 + (G-1)*ln(m)` for G nonempty pages.
Charging extra phases does not replace null calibration.

E047 recovers three new controls of 3,316/1,200/1,200 runes with keys 5/8/13,
random page phases, both signs, and all masks exactly. Training and control
ranges are disjoint within previously seen Emerson chapters. One complete
control null is diagnostic. On unknown inputs, LP2-54_55 is selected at
-5.567525 (language score -5.392394), sign -1, primitive key length 14,
page phases 0 and 2, skips 247/257/273. Eighteen of nineteen full matched null
searches reach its score: raw p=0.95, Bonferroni10=1. Nulls retain per-page
counts, boundary runes, and adjacent matches. No candidate is supported as
a solution; other key lengths and grouping rules remain unexcluded.

**106 tests passed.** Separate validation covers 1,676 candidates, 396 starts
and trajectories, 33 conditional phase/mask maxima, global rotation invariance,
and twenty new nulls. Thirty tasks take 234.441 seconds; E048 with orchestration
209.470 within 650. Phase budget 900, one worker, maximum 4,096 runes/16 pages.
All ten group scores and full key data remain in the linked complete results.

## Recorded result tables

Values are preserved from the original report; headings and outcome labels
are rendered in English. These tables describe controls or search scores,
not independent discoveries.

| Group | Runes | Best penalized score |
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

| Page | Initial phase |
|---|---:|
| LP2-54 | 0 |
| LP2-55 | 2 |

## Preserved candidate outputs

These blocks are copied verbatim from the historical report, in its order.
They are search outputs, **not confirmed plaintext**. Their rules, selection
context, and full records are in the linked evidence.

```text
OOPAWANCETHEAUNMLIASTHICTHPIOEWGLSTHNNEOTHWPLMYGWIALUNGEWOSAYOLDNTHTHDMRRJMSIATFIANMMAJWMAGBWLEAJFGSLASSNGFFBBTIREATUTSREOLHAEAEFLHRFFEYAWTHEPRUIRNETHRRBEIRCUTEDGEOEAFBERSOEATGSROYTEADOEBBEOMNOYEADFFOENGSNGUPMNETHBTRAELAPFIFMSSNALRETATMLOSNGMNGPCMDIPAWNREJODABJLLFGOEBEPOESTTFLSOEAEXRLNFLINEXUAECSFTIHNGFCYCOOEXEATBFOMIFGTIACCTHSTEAEOCSLOFMAUINMONTYTNGBFA
```

## Evidence

- [Original frozen report](../../reports/attack_phase16_report.md) (historical wording, usually German).
- [Complete machine-readable phase summary](../../results/phase16_summary.json).
- [Checkpoint and resource accounting](../../checkpoints/phase16_complete.json).
- [All registered outcomes](../../experiment_log.jsonl), [hypotheses](../../hypotheses.json), and [English index](INDEX.md).

Additional original evidence: [phase_key_unknown_plan.json](../../experiments/phase_key_unknown_plan.json), [phase_key_selection.json](../../experiments/phase_key_selection.json), [phase16_summary.json](../../results/phase16_summary.json), [phase16_complete.json](../../checkpoints/phase16_complete.json).
