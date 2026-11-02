# Phase 11: Word-scored substitution and progressive keys

**No new decryption confirmed.** Historical report date: 2026-10-20T09:51:13.593977+00:00.

English editorial edition; the original report and raw results are preserved
unchanged. This edition consolidates repeated wording and navigation.

E037 tests `P[i]=a*C[i]+b*i^2+c*i+d mod29`, starting i=0 on each page.
a=1–28; b,c,d=0–28; constant affine cases b=c=0 are excluded. This gives
682,080 rules per page and 37,514,400 across 55 pages. Index shifts and index
reversal are already represented in the coefficients. The key period divides
29, but arbitrary period-29 keys are not covered. Three controls, including
a linear b=0 case and LP2-57, are exact. LP2-49 scores -5.071744 with
a=9,b=27,c=25,d=22; 9/19 fully searched matched nulls reach it: p=0.50,
Bonferroni55=1. No corrected evidence supports the candidate.

E036 first tests the substitution solver using the fixed E027 word formula,
trained on Emerson I and III–IX. Up to 24 starts receive forty character-score
and forty word-score sweeps, each with all 406 swaps. Final selection uses the
word score. Long controls are exact (515/515,319/319), but LP2-57 is 94/95:
offset 25 changes NG to EA. Wrong score -1.755654 exceeds truth -1.794298.
On eighteen external windows, the word score wins 355/360 mutation comparisons
versus 349/360 for character scoring. The external diagnostic passes, but the
required three exact LP controls do not. **No unknown substitution attack runs.**
The historical E036 plan conditionally reserved E037 for that attack; because
the gate failed, E037 instead names the separately planned progressive family.
The old plan remains unchanged.

**94 tests passed; 193 E037 candidates and 452 E036 starts were checked.**
Source windows, disjoint training, keys, mutations, null seeds, and hashes are
verified. Seventy-six tasks take 365.341 experiment seconds. Before nulls, a
queue was stopped to correct a copied seed annotation; actual search/null code
and seed 3301037 were unchanged. LP2-52 failed while writing to the closed pipe
(`OSError(22)`), then was rerun; completed fingerprints were skipped. The failure
and conservative sixty-second reserve remain in the accounting. E037 accounts
for 425.845 seconds within 650; phase budget 900.

## Preserved candidate outputs

These blocks are copied verbatim from the historical report, in its order.
They are search outputs, **not confirmed plaintext**. Their rules, selection
context, and full records are in the linked evidence.

```text
RRENGNCTEAIPISTHEATHUICAILANYWOCNGYSEADGODAHLABUSHEOESHSLPEUNFSDRMGEUPHOEXT
```

## Evidence

- [Original frozen report](../../reports/attack_phase11_report.md) (historical wording, usually German).
- [Complete machine-readable phase summary](../../results/phase11_summary.json).
- [Checkpoint and resource accounting](../../checkpoints/phase11_complete.json).
- [All registered outcomes](../../experiment_log.jsonl), [hypotheses](../../hypotheses.json), and [English index](INDEX.md).

Additional original evidence: [quadratic_stream_plan.json](../../experiments/quadratic_stream_plan.json), [quadratic_stream_selection.json](../../experiments/quadratic_stream_selection.json), [boundary_substitution_plan.json](../../experiments/boundary_substitution_plan.json), [phase11_orchestration_interruption.json](../../checkpoints/phase11_orchestration_interruption.json), [phase11_complete.json](../../checkpoints/phase11_complete.json), [phase11_summary.json](../../results/phase11_summary.json).
