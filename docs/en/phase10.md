# Phase 10: Additive feedback and a general substitution prototype

**No new decryption confirmed.** Historical report date: 2026-10-20T09:32:00.344537+00:00.

English editorial edition; the original report and raw results are preserved
unchanged. This edition consolidates repeated wording and navigation.

E034 adds the previously excluded nonzero constant:
`P[i]=a*C[i]+b*P[i-1]+d mod29`, `P[-1]=K`, a,b,d=1–28, K=0–28.
There are 636,608 rules per page and 35,013,440 across 55 pages. All runes are
scored; there are no skips, routes, or cross-page state. With x=P0, basis
recurrences give `P[i]=a*S[i]+q[i]*x+d*t[i]`, and
`K=b^-1*(x-a*C0-d)`. This is valid at b=1 without dividing by b−1.
Three synthetic controls, including b=1, are exact. LP2-49 scores -5.051735
with a=6,b=12,d=26,K=28; 7/19 full matched nulls reach it: p=0.40, adjusted 1.

E035 prototypes arbitrary bijective 29-symbol substitution. Word-pattern and
frequency starts are hypotheses, not supplied plaintext. At most 24 deduplicated
starts and forty improvement sweeps evaluate all 406 pair swaps. This does not
exhaust 29! permutations. Two long controls recover 515/515 and 319/319 runes;
LP2-57 recovers only 93/95. Its wrong candidate scores -1.906461 versus
-1.931762 for truth, a ranking failure at offsets 25 and 80. More search cannot
make truth the global maximum under that objective. **The control gate fails;
no unknown page is attacked with this solver.** Nine optimized control shuffles
preserve counts and endpoints, not adjacent matches; they carry no discovery
p-value. The controls were already known historically.

**89 tests passed.** All 193 E034 candidates and 225 E035 starts are separately
rescored and re-encrypted; bijections, scalar small-grid enumeration, basis
formulas, and null seeds are checked. Seventy-six tasks use 334.773 seconds,
including 327.674 for E034. Its queue plus completed control remains within
750 seconds, phase budget 900, one process and bounded arrays.

## Preserved candidate outputs

These blocks are copied verbatim from the historical report, in its order.
They are search outputs, **not confirmed plaintext**. Their rules, selection
context, and full records are in the linked evidence.

```text
THPTSWIOCUMFNTESIFLOGYWOFWNGFGOECWSOEFAEATHLOGRPBRHEGOOAHFUAURROOSMWWTHEOE
```

## Evidence

- [Original frozen report](../../reports/attack_phase10_report.md) (historical wording, usually German).
- [Complete machine-readable phase summary](../../results/phase10_summary.json).
- [Checkpoint and resource accounting](../../checkpoints/phase10_complete.json).
- [All registered outcomes](../../experiment_log.jsonl), [hypotheses](../../hypotheses.json), and [English index](INDEX.md).

Additional original evidence: [offset_feedback_plan.json](../../experiments/offset_feedback_plan.json), [offset_feedback_selection.json](../../experiments/offset_feedback_selection.json), [substitution_prototype_plan.json](../../experiments/substitution_prototype_plan.json), [phase10_complete.json](../../checkpoints/phase10_complete.json), [phase10_summary.json](../../results/phase10_summary.json).
