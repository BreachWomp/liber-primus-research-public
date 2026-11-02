# Phase 13: Joint key and selective-F recovery

**No new decryption confirmed.** Historical report date: 2026-10-20T14:59:36.073719+00:00.

English editorial edition; the original report and raw results are preserved
unchanged. This edition consolidates repeated wording and navigation.

E040 reconstructs the actual DIVINITY and CIRCUMFERENCE ciphertexts exactly:
plaintext, keys, and F masks, with neither keys nor skip positions supplied.
This is improved replication of known solutions. E041 adds six external
350-rune controls from Emerson X–XII, random length-5/13 keys, both signs, and
every second plaintext F copied without key consumption. All six texts, keys,
and masks are exact. Nonzero key values avoid one kind of copied-F ambiguity.
Training remains on I and III–IX; these are not historically unseen corpora.

The rule is `P[i]=s*C[i]+K[j] mod29`, with optional copied F at ciphertext F.
Initial keys come from simple full-text schedules and the three longest
F-free spans of at least 32 runes, capped at 256. Periods 1–16 and both signs
produce twelve cyclically deduplicated starts. For a fixed key, dynamic
programming finds the exact best initial phase and F schedule. Equal states
require equal cursor and language context; the fourgram implementation is
bounded by eight states per cursor. Up to three rounds alternate key updates
(six coordinate sweeps) and schedule optimization. Key search remains heuristic.
The final penalty is key_length*ln29 plus ciphertext_F_count*ln2.

E042 attacks 55 unknown pages separately. LP2-49 scores -3.946618 after penalty
(-3.109299 language score), sign +1, with skips at zero-based offsets 3 and 33.
The full key and candidate are retained in the source report and results.
Three of nineteen independently shuffled matched nulls reach it: p=0.20,
Bonferroni55=1. Every null reconstructs its own F-free spans, keys, phases,
and masks. The candidate is not supported as plaintext.

**98 tests passed.** Separate checks cover 4,226 intermediate/final candidates,
1,044 starts and monotone trajectories, and 87 final schedule maxima via an
independent score-only Viterbi implementation. Tiny cases enumerate all phases
and skip subsets. Source windows, keys, masks, and 24 null sequences are
reproduced. Seventy-six tasks use 359.573 seconds; E042 orchestration is 319.066
within 650, phase budget 900.

## Preserved candidate outputs

These blocks are copied verbatim from the historical report, in its order.
They are search outputs, **not confirmed plaintext**. Their rules, selection
context, and full records are in the linked evidence.

```text
NOXFGHATGLARTYBYMIRPOPULBELEDWONOFGEONICACISMLEALISHEPDOTENEDSANEORE
```

## Evidence

- [Original frozen report](../../reports/attack_phase13_report.md) (historical wording, usually German).
- [Complete machine-readable phase summary](../../results/phase13_summary.json).
- [Checkpoint and resource accounting](../../checkpoints/phase13_complete.json).
- [All registered outcomes](../../experiment_log.jsonl), [hypotheses](../../hypotheses.json), and [English index](INDEX.md).

Additional original evidence: [joint_skip_plan.json](../../experiments/joint_skip_plan.json), [joint_skip_external_plan.json](../../experiments/joint_skip_external_plan.json), [joint_skip_unknown_plan.json](../../experiments/joint_skip_unknown_plan.json), [joint_skip_selection.json](../../experiments/joint_skip_selection.json), [phase13_complete.json](../../checkpoints/phase13_complete.json), [phase13_summary.json](../../results/phase13_summary.json).
