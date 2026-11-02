# Phase 12: Unknown periodic rune keys

**No new decryption confirmed.** Historical report date: 2026-10-20T14:42:20.534880+00:00.

English editorial edition; the original report and raw results are preserved
unchanged. This edition consolidates repeated wording and navigation.

E038/E039 learn arbitrary key values rather than selecting among 381 words:
`P[i]=s*C[i]+K[j] mod29`, s=±1, periods 1–16. F is either never interrupted
or always copied without advancing j. Each sign/policy/period uses four starts
and at most twelve bigram then twelve fourgram coordinate sweeps, trying all
29 values per coordinate. Local factor updates are exact; global key search
is heuristic. Final score subtracts `primitive_key_length*ln29` before dividing
by rune count. This description-length penalty is not a probability of truth.

E038 recovers the actual DIVINITY and CIRCUMFERENCE keys and text with their
**interruption schedules supplied**. These are not blind skip-recovery tests.
Six fresh synthetic 200-rune controls from Emerson X–XII, with key lengths 5
and 13 and both signs, are exact without supplied periods or keys. Training
uses I and III–IX (207,030 runes); the corpus was previously seen historically.
Three fully optimized matched control nulls are capability diagnostics only.

E039 attacks all 55 rune pages, 64 families and four starts per page. LP2-49
is selected with penalized score -3.981681, language score -3.165367, sign +1,
all-F policy, and primitive key length 16. Five of nineteen fully optimized
count/adjacency-matched nulls reach it: raw p=0.30, Bonferroni55=1. Each null
derives its own F positions and selects its own family. The result does not
exclude arbitrary periodic keys or selective interruptions.

**96 tests passed.** A scalar checker verifies 5,631 saved family maxima and
top candidates from 85 outputs, including inverses, key periods, schedules,
and penalties. Source windows and all 22 null sequences are independently
reconstructed. Seventy-five tasks take 192.481 successful experiment seconds;
E039 including orchestration is 193.075 within 650, phase budget 900.

## Preserved candidate outputs

These blocks are copied verbatim from the historical report, in its order.
They are search outputs, **not confirmed plaintext**. Their rules, selection
context, and full records are in the linked evidence.

```text
EDIFFFATRSARBABYMMANYCULSPLEACONOFSOCRYACHIMLFEISHIARMYHENTESAITORE
```

## Evidence

- [Original frozen report](../../reports/attack_phase12_report.md) (historical wording, usually German).
- [Complete machine-readable phase summary](../../results/phase12_summary.json).
- [Checkpoint and resource accounting](../../checkpoints/phase12_complete.json).
- [All registered outcomes](../../experiment_log.jsonl), [hypotheses](../../hypotheses.json), and [English index](INDEX.md).

Additional original evidence: [periodic_key_plan.json](../../experiments/periodic_key_plan.json), [periodic_key_unknown_plan.json](../../experiments/periodic_key_unknown_plan.json), [periodic_key_selection.json](../../experiments/periodic_key_selection.json), [phase12_complete.json](../../checkpoints/phase12_complete.json), [phase12_summary.json](../../results/phase12_summary.json).
