# Phase 31: First differences followed by general substitution

**No new decryption confirmed.** Historical report date: 2026-11-02T16:57:03.709216+00:00.

English editorial edition; the original report and raw results are preserved
unchanged. This edition consolidates repeated wording and navigation.

The fixed reversible rule is

```text
C[-1] = 0
D[i] = (C[i] - C[i-1]) mod 29
P[i] = S(D[i])
C[i] = (C[i-1] + inverse(S)(P[i])) mod 29
```

S is a permutation of 29 symbols. The first rune is processed, not removed as
an IV. Original word boundaries remain. Initial value zero is a predeclared
restriction, not a clue inferred from the puzzle. Other IVs and cross-page
state are outside this attack. Earlier E015 tested only affine difference
maps; its outcomes remain unchanged. The operations are established mathematics.

E085 integrates the twelve passed E083 controls into synthetic difference
ciphers. Differencing returns their exact previous substitution inputs, so
the unchanged optimizer is **not rerun**. These are transported controls, not
twelve new blind searches. Three previous difference-space control nulls are
transported too; they are not new ciphertext-space null draws. A separate
checker verifies source windows, keys, 245 scores, 245 cumulative inverses,
and 435 identities across all 29 IVs. Algebraic checks across IVs do not
expand the unknown attack beyond zero. Training/model are unchanged.

E086 then attacks 46 pages of at least 200 runes, differencing before the
unchanged substitution search: at most 24 starts, forty 406-swap character
sweeps and forty word sweeps. Nine short rune pages and numeric LP2-50 remain
in the plan with exclusion reasons and original content. Source anchors for
all 56 research pages and ten source-file hashes are checked.

LP2-02 wins at **-7.555071**. Selection and output hashes are frozen before
nineteen independent **original-ciphertext-space** nulls. Interior shuffles
preserve endpoints, counts, adjacent matches, and original word boundaries.
Only then are they differenced and searched with the same page-specific seed.
Nonzero-difference frequencies are not held fixed: this is not an additional
difference-space null test. **9/19** scores reach the selected score: raw
plus-one p=0.50, Bonferroni46=1. Nineteen draws cannot resolve corrected
significance, so no new decryption is supported.

Separate validation checks **1,320 candidate scores, 535,920 final-neighbor
scores, and 1,320 complete cumulative re-encryptions** to original ciphertext.
Literal differences and cumulative inversion do not use the production
difference function. Sources, seeds, nulls, and selection are checked. GP
tokenization is shared; intermediate optimization trajectories are not
independently implemented. The heuristic does not exhaust 29! permutations.
Page edges are treated as word boundaries; short texts, other languages,
nonlinguistic content, and other IVs remain outside the conclusion.

**145 tests passed; 66 new tasks**, including one transported-control task
without optimizer search. Experiment time 255.932 seconds; monitored process
time 312.748 within 1,800. Peak memory 184.2 MiB against 768, one worker.
The next untested question is initial-value ambiguity: for a fixed permutation,
changing the IV affects only the first plaintext rune. A future all-IV method
must first validate its scoring and explicitly preserve that ambiguity.

## Recorded result tables

Values are preserved from the original report; headings and outcome labels
are rendered in English. These tables describe controls or search scores,
not independent discoveries.

| Page | Runes | Highest score |
|---|---:|---:|
| LP2-00 | 262 | -8.223982 |
| LP2-01 | 266 | -8.284429 |
| LP2-02 | 201 | -7.555071 |
| LP2-03 | 217 | -7.715733 |
| LP2-04 | 261 | -8.512162 |
| LP2-05 | 263 | -8.128765 |
| LP2-07 | 208 | -7.981767 |
| LP2-08 | 255 | -7.639698 |
| LP2-09 | 268 | -7.938683 |
| LP2-10 | 263 | -8.475421 |
| LP2-11 | 273 | -8.051339 |
| LP2-12 | 261 | -8.277417 |
| LP2-13 | 272 | -8.060434 |
| LP2-16 | 267 | -8.476086 |
| LP2-17 | 273 | -8.668955 |
| LP2-18 | 260 | -8.322923 |
| LP2-19 | 271 | -8.453831 |
| LP2-20 | 269 | -8.552878 |
| LP2-21 | 273 | -7.856105 |
| LP2-23 | 213 | -8.171361 |
| LP2-24 | 270 | -8.730881 |
| LP2-25 | 273 | -8.381671 |
| LP2-26 | 265 | -8.354422 |
| LP2-27 | 234 | -8.024870 |
| LP2-28 | 269 | -8.207586 |
| LP2-29 | 277 | -8.494215 |
| LP2-30 | 263 | -8.389047 |
| LP2-31 | 269 | -8.436131 |
| LP2-33 | 214 | -8.054343 |
| LP2-34 | 261 | -8.241893 |
| LP2-35 | 271 | -8.031256 |
| LP2-36 | 238 | -7.914627 |
| LP2-37 | 228 | -7.862157 |
| LP2-38 | 228 | -7.908442 |
| LP2-39 | 240 | -8.245986 |
| LP2-40 | 231 | -8.073526 |
| LP2-41 | 273 | -8.247909 |
| LP2-42 | 272 | -8.054328 |
| LP2-43 | 274 | -8.150681 |
| LP2-44 | 273 | -8.171149 |
| LP2-45 | 270 | -8.497033 |
| LP2-46 | 270 | -8.420472 |
| LP2-47 | 274 | -8.349559 |
| LP2-48 | 271 | -8.634877 |
| LP2-52 | 263 | -8.252686 |
| LP2-54 | 232 | -7.676338 |

## Evidence

- [Original frozen report](../../reports/attack_phase31_report.md) (historical wording, usually German).
- [Complete machine-readable phase summary](../../results/phase31_summary.json).
- [Checkpoint and resource accounting](../../checkpoints/phase31_complete.json).
- [All registered outcomes](../../experiment_log.jsonl), [hypotheses](../../hypotheses.json), and [English index](INDEX.md).

Additional original evidence: [difference_substitution_plan.json](../../experiments/difference_substitution_plan.json), [difference_substitution_unknown_plan.json](../../experiments/difference_substitution_unknown_plan.json), [phase31_summary.json](../../results/phase31_summary.json).

[English candidate appendix](phase31_candidates.md).
