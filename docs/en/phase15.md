# Phase 15: A shared key reset at each page

**No new decryption confirmed.** Historical report date: 2026-10-20T20:44:45.264242+00:00.

English editorial edition; the original report and raw results are preserved
unchanged. This edition consolidates repeated wording and navigation.

E046 uses the same ten section hypotheses but resets key cursor j to zero and
language context at each page. All pages share one oriented key; independent
page phases are not yet allowed. Optional ciphertext F can be copied without
key consumption. LP2-50 remains a retained empty rune span.

| Group | Runes | Penalized score |
|---|---:|---:|
| LP2-00_02 | 729 | -5.912185 |
| LP2-03_07 | 1145 | -6.027666 |
| LP2-08_14 | 1729 | -6.156643 |
| LP2-15_22 | 1903 | -6.243878 |
| LP2-23_26 | 1021 | -6.047755 |
| LP2-27_32 | 1433 | -6.141726 |
| LP2-33_39 | 1680 | -6.228457 |
| LP2-40_53 | 3008 | -6.319841 |
| LP2-54_55 | 308 | -5.394358 |
| LP2-40_55 | 3316 | -6.297573 |

Keys are initialized from the two longest nonempty pages and three F-free spans,
periods 1–16 and both signs, retaining twelve cyclically deduplicated starts.
Each starts with the best shared phase, computed from exact per-page schedule
scores; that phase is absorbed into the key. Up to three rounds perform common
coordinate updates and exact page schedule optimization at phase zero.
The phase is not separately reoptimized later. Key search remains heuristic;
one shared primitive-key penalty and all F-decision penalties are charged.

E045 recovers three new reset-key controls of 3,316/1,200/1,200 runes, keys
5/8/13 and all masks exactly. The first uses the actual LP2-40–55 page lengths.
Training and control source ranges are disjoint but historically seen. One
control null is fully optimized. Selected LP2-54_55 scores -5.394358
(-5.205931 language score), sign -1. One of nineteen full matched-null searches
reaches it: p=0.10, Bonferroni10=1. Nulls preserve per-page counts, boundary
runes, and adjacent matches. This provides no evidence of a new solution.

**103 tests passed.** Independent checks cover 1,680 candidates, 396 starts
and trajectories, 33 page schedule maxima, source windows, keys, and twenty
nulls. Thirty tasks use 254.226 experiment seconds; E046 orchestration is
220.751 within 650, phase limit 900, one worker, maximum 4,096 runes.

## Preserved candidate outputs

These blocks are copied verbatim from the historical report, in its order.
They are search outputs, **not confirmed plaintext**. Their rules, selection
context, and full records are in the linked evidence.

```text
XGSLIHELHNLYCTHRAMNEOOETHCDEOEARCUMSPGGYMMWTDAFIPDSUFLLLIASOJXYAGFTMADIANUTHOWWNGOEAYDRESIHAUTHWILFBUPTMPLUBCEAUADBYSHDOBOIANGTNSREEGGTHSIPSDLEAHEAUYWRATHFFAOIAIOTBACADRRIGHRTHLTHPGWTALHGOCABLNGINUENGAURTGTRSBYJXYEORMFPIMTXDAANGTHDIDRUYEONIALEMHEAMLFABAWHITHPBFBRUASTHNGTHROUSMJUMNWOEAPEAWFFWTHGGURTTHEANOXFMGIANGLOELLSUFTHAXSSCEONGJUEXISBNDTNGFIER
```

## Evidence

- [Original frozen report](../../reports/attack_phase15_report.md) (historical wording, usually German).
- [Complete machine-readable phase summary](../../results/phase15_summary.json).
- [Checkpoint and resource accounting](../../checkpoints/phase15_complete.json).
- [All registered outcomes](../../experiment_log.jsonl), [hypotheses](../../hypotheses.json), and [English index](INDEX.md).

Additional original evidence: [reset_key_unknown_plan.json](../../experiments/reset_key_unknown_plan.json), [reset_key_selection.json](../../experiments/reset_key_selection.json), [phase15_summary.json](../../results/phase15_summary.json), [phase15_complete.json](../../checkpoints/phase15_complete.json).
