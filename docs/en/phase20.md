# Phase 20: Carried language context and staged blind controls

**No new decryption confirmed.** Historical report date: 2026-10-21T15:52:31.019557+00:00.

English editorial edition; the original report and raw results are preserved
unchanged. This edition consolidates repeated wording and navigation.

E056 keeps the last three plaintext runes across page boundaries while each
page can choose its key phase. Exact DP tracks cursor and language context
together; empty pages remain. It checks twelve unchanged E054 controls and
three deliberately constructed boundary stress cases at 12000:12729 in
Emerson X–XII. True key and sign are supplied, while phases and masks are
searched. **15/15 are exact**, versus 14/15 for page-reset context. These are
known-key diagnostics. Five alternative initial-F recipes with identical
re-encryption remain visible even when their language score is lower.

E057 increases starts on inputs up to 1,024 runes from sixteen to sixty-four
per period/sign, retaining four unigram starts rather than two. Larger inputs
are unchanged. Blind Stage A includes the hard old length-31 case plus three
fresh natural 729-rune windows at 14000:14729, lengths 17/23/31, random page
phases, and F-copy probabilities 0.25/0.50/0.75. All three fresh cases are
exact, but the regression recovers only 43/729 (previously 30/729). One full
matched null scores -5.513590576 without a p-value. The predeclared gate fails;
Stage B's eleven other regressions and three stress cases are deferred.
**No unknown-page scan runs.** Three fresh successes do not replace the gate.

**118 tests passed.** Separate validation covers 15,520 pool states, 160
fragment-phase maxima, 474 coupled states, 21 conditional full maxima, five
ambiguity pairs, sources, seeds, and hashes. Six tasks take 253.685 seconds
within 1,500, maximum 180 per task; sampled peak 129.0 MiB against 768.

The next untested proposal constrains fragment phases using ciphertext:
for starts a<b on one page, `phase_b-phase_a=(b-a)-s mod m`, where copied-F
count s lies between zero and the number of ciphertext F symbols in the gap.
No speedup or improved recovery was claimed before testing that proposal.

## Recorded result tables

Values are preserved from the original report; headings and outcome labels
are rendered in English. These tables describe controls or search scores,
not independent discoveries.

| Control | Key length | Correct runes | Text/key/mask/phases |
|---|---:|---:|---|
| regression 2 | 31 | 43/729 | failed |
| fresh 0 | 17 | 729/729 | exact |
| fresh 1 | 23 | 729/729 | exact |
| fresh 2 | 31 | 729/729 | exact |

## Evidence

- [Original frozen report](../../reports/attack_phase20_report.md) (historical wording, usually German).
- [Complete machine-readable phase summary](../../results/phase20_summary.json).
- [Checkpoint and resource accounting](../../checkpoints/phase20_complete.json).
- [All registered outcomes](../../experiment_log.jsonl), [hypotheses](../../hypotheses.json), and [English index](INDEX.md).

Additional original evidence: [context_phase_plan.json](../../experiments/context_phase_plan.json), [context_blind_plan.json](../../experiments/context_blind_plan.json), [phase20_summary.json](../../results/phase20_summary.json), [phase20_complete.json](../../checkpoints/phase20_complete.json).
