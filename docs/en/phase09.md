# Phase 9: Two-step ciphertext feedback and a failed scoring gate

**No new decryption confirmed.** Historical report date: 2026-10-20T09:17:01.804533+00:00.

English editorial edition; the original report and raw results are preserved
unchanged. This edition consolidates repeated wording and navigation.

E033 tests `P[i-2]=a*C[i]+b*C[i-1]+c*C[i-2]+d mod29`, with nonzero a,c and
all b,d, excluding four earlier sign cases. There are 659,340 rules per page
and 36,263,700 across 55 pages. The first two ciphertext runes are initial
values, not recovered plaintext. The inverse is
`C[i]=a^-1*(P[i-2]-b*C[i-1]-c*C[i-2]-d) mod29`. No F skips, routes, or
cross-page state are included. Three controls are exact under the unchanged
E016 fourgram score. LP2-49 scores -5.015058 with a=28,b=0,c=22,d=13 and
IV=[27,18]. Six of nineteen matched nulls reach it: raw p=0.35, adjusted 1.

E030 completes a previously begun boundary-scoring benchmark. Models train on
Emerson I and III–IX (207,030 runes), excluding X–XII for this comparison,
although those texts had already been used historically. It tests 62 intact
and clipped windows, 23 apostrophe paragraphs, eight known controls, 6,440
single-rune changes, and 3,059 count-preserving shuffles.

| Mutation condition | Whole-word / split apostrophe | Character edges / joined apostrophe |
|---|---:|---:|
| Apostrophe word | 448/460 | 452/460 |
| Other in apostrophe paragraphs | 450/460 | 450/460 |
| Clipped edge | 995/1240 | 1030/1240 |
| Clipped interior | 1222/1240 | 1222/1240 |
| Intact edge | 1229/1240 | 1203/1240 |
| Intact interior | 1221/1240 | 1221/1240 |

The alternative improves genuine fragments but harms complete edge words.
Its known-control rate is 93.21%, below the fixed 95% gate, so it is **not
adopted** in E033. These are descriptive, correlated diagnostics.
Historical E031/E032 compare five numeric readings and a pinned public claim
repository. None reproduces the alternate claimed digest; the named binary
and analyzer are absent at the inspected commit, which says nothing about
older versions. Two preview readings conflict with image evidence. This
side investigation stops; no new community-claim audit is planned.

**84 tests passed.** Separate checks cover 193 candidates, 19,320 benchmark
scores, source windows, mutations, null counts, and hashes. Seventy-eight tasks
used 347.378 seconds, of which E033 used 343.844 under its 750-second limit.

## Preserved candidate outputs

These blocks are copied verbatim from the historical report, in its order.
They are search outputs, **not confirmed plaintext**. Their rules, selection
context, and full records are in the linked evidence.

```text
TOOLHEALSANIPFEBUFIHODEAEENNTHNGDDSOLSPOINTHTIUEARDIPMEOITHOBGHNGOWYOEYCNF
```

## Evidence

- [Original frozen report](../../reports/attack_phase9_report.md) (historical wording, usually German).
- [Complete machine-readable phase summary](../../results/phase9_summary.json).
- [Checkpoint and resource accounting](../../checkpoints/phase9_complete.json).
- [All registered outcomes](../../experiment_log.jsonl), [hypotheses](../../hypotheses.json), and [English index](INDEX.md).

Additional original evidence: [cipher_filter_plan.json](../../experiments/cipher_filter_plan.json), [cipher_filter_selection.json](../../experiments/cipher_filter_selection.json), [manifest.json](../../sources/claim_repository_2026-10-20/manifest.json), [files_manifest.json](../../sources/claim_repository_2026-10-20/files_manifest.json), [phase9_complete.json](../../checkpoints/phase9_complete.json), [phase9_summary.json](../../results/phase9_summary.json).
