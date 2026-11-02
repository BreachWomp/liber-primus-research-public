# Phase 5: Completed selective search and affine plaintext feedback

**No new decryption confirmed.** Historical report date: 2026-10-19T12:49:04.023538+00:00.

English editorial edition; the original report and raw results are preserved
unchanged. This edition consolidates repeated wording and navigation.

E018 completes all 55 pages, with 381 primitive word-key cycles, all phases,
three number streams, offsets 0–255, four signs, and exact optimization over
F subsets. Eight completed tasks are skipped; the previously aborted group
is rerun. Existing reports and abort records are unchanged. The three known
controls remain exact. Selected LP2-49 scores -5.305280; 9/19 matched nulls
reach it, giving raw p=0.50 and Bonferroni55=1.

E019 tests `P[i]=a*C[i]+b*P[i-1] mod29`, with unknown `P[-1]=K`.
Nonzero a,b are searched except the four sign pairs already covered; all
29 initial values are tried. This gives 780 coefficient pairs, 22,620 rules
per page, and 1,244,100 rules across 55 pages. Reparameterization by initial
plaintext is bijective and is checked against scalar enumeration. Three
synthetic controls, including LP2-57, recover exactly. No additive offset,
F interruption, or cross-page state is included.

The initial selected LP2-55 result has 0/19 null exceedances, which gives
raw p=0.05 and no corrected significance. The declared escalation freezes
the candidate `(a=5,b=20,K=13)` and search, then E020 runs **4,000 fresh nulls**
in twenty fixed batches (seed 3301020 plus batch index), without early stopping
or pooling with the initial nineteen. Each null repeats the full search.
There are 115 exceedances: fresh raw p=0.02899275181204699, page-adjusted 1,
also 1 after accounting for the two attack families. The candidate is not
coherent plaintext and remains unedited.

Nulls preserve exact rune counts and adjacent-equality count, but not word
boundaries or higher-order structure. Corrections apply within this phase,
not globally over the exploratory project. **63 tests passed; 354 candidate
records were independently re-encrypted and rescored.** Twenty-nine successful
processes took 436.118 seconds; orchestration took 443.589, within 900 seconds.
Arrays hold at most 812 candidate rows. LP2-50 remains preserved and excluded
from rune-only inputs.

## Preserved candidate outputs

These blocks are copied verbatim from the historical report, in its order.
They are search outputs, **not confirmed plaintext**. Their rules, selection
context, and full records are in the linked evidence.

```text
RHRIBWTAOTHOTAECETNGPAEFIHPDIANAYDIBHUFCALUNORJUWHAMSNMYNGUXSIBSCDWEYRDL
```

```text
BUEAUYSHIAYSEONCDCPETEACEEOFATPLTHTYCACYFHOUIROEOPUTOCHERDHTESIALROCUUXSCCNGINCITHNNIA
```

## Evidence

- [Original frozen report](../../reports/attack_phase5_report.md) (historical wording, usually German).
- [Complete machine-readable phase summary](../../results/phase5_summary.json).
- [Checkpoint and resource accounting](../../checkpoints/phase5_complete.json).
- [All registered outcomes](../../experiment_log.jsonl), [hypotheses](../../hypotheses.json), and [English index](INDEX.md).

Additional original evidence: [phase5_summary.json](../../results/phase5_summary.json), [phase5_complete.json](../../checkpoints/phase5_complete.json).
