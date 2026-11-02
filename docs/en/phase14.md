# Phase 14: A shared continuous key across page boundaries

**No new decryption confirmed.** Historical report date: 2026-10-20T20:36:36.732511+00:00.

English editorial edition; the original report and raw results are preserved
unchanged. This edition consolidates repeated wording and navigation.

E044 tests ten pinned source-based section hypotheses, with a shared periodic
key, cursor, and language context continuing across pages. Optional F copying
does not advance the cursor. LP2-50 is a zero-width rune span; ignoring its
numbers for key consumption is a stated model assumption, not a discovery.

| Group | Runes | Penalized score |
|---|---:|---:|
| LP2-00_02 | 729 | -5.959599 |
| LP2-03_07 | 1145 | -6.157623 |
| LP2-08_14 | 1729 | -6.250240 |
| LP2-15_22 | 1903 | -6.247081 |
| LP2-23_26 | 1021 | -6.075823 |
| LP2-27_32 | 1433 | -6.158250 |
| LP2-33_39 | 1680 | -6.234422 |
| LP2-40_53 | 3008 | -6.348909 |
| LP2-54_55 | 308 | -5.334024 |
| LP2-40_55 | 3316 | -6.377496 |

For long inputs, first/last 1,024-rune windows and three F-free spans initialize
the unchanged bounded key search. Periods 1–16, both signs, twelve starts,
three alternating rounds; only fixed-key schedule optimization is exact.
E043 recovers three external controls of 3,316/1,200/1,200 runes with key
lengths 5/8/13, including the LP2-40–55 page-length pattern and empty numeric
page. Two earlier historical controls are checked without rerunning identical
searches. One optimized control null is diagnostic.

Selected LP2-54_55 has language score -5.145597 and penalized score -5.334024.
One of nineteen matched section nulls reaches it: raw p=0.10, Bonferroni10=1.
Nulls fix each page's counts, adjacent matches, and boundary runes; interior
shuffles are accepted conditionally (cap 100,000), preserving cross-page matches.
Each null repeats the entire optimizer. Overlap between groups does not
invalidate the Bonferroni bound, but this is not a project-wide correction.

**100 tests passed.** Checks cover 1,764 candidates, 420 starts/trajectories,
35 separate Viterbi maxima, and twenty new nulls. Thirty tasks take 261.961
seconds; E044 orchestration 219.695 within 650. Maximum input 4,096 runes,
phase budget 900, one worker.

## Preserved candidate outputs

These blocks are copied verbatim from the historical report, in its order.
They are search outputs, **not confirmed plaintext**. Their rules, selection
context, and full records are in the linked evidence.

```text
NHNGMGDOGOICONMNPRCABFDTOEALNGAPTHIAABHILYACOTFNEOGEALPBODNAPLWFTPAEPAYMIFNDJYJOTADOBIACMPONDWDIAATHOEWITHOFEAROEJAMIUIARSYDRPICFJUIISFEPNGCTHUYNOOTHYPWJLANGLYYPOEMEJOEUNNALSPXEBXFIAHNGONMPIETEAENUAILLNEUPFTHEOMCNACGONDLEDFYSWOTARIALJMROEBAUEJOWOUUIDNGELEAWEAFXEINGOOEECCONGRYADIARNGTLUBEOYNGGUFOAHUUNGFITAETHYPSTHFMYYDEOXWIEATHIAEYHOURLORTHEPLEASEYCUEGLEA
```

## Evidence

- [Original frozen report](../../reports/attack_phase14_report.md) (historical wording, usually German).
- [Complete machine-readable phase summary](../../results/phase14_summary.json).
- [Checkpoint and resource accounting](../../checkpoints/phase14_complete.json).
- [All registered outcomes](../../experiment_log.jsonl), [hypotheses](../../hypotheses.json), and [English index](INDEX.md).

Additional original evidence: [section_key_unknown_plan.json](../../experiments/section_key_unknown_plan.json), [section_key_selection.json](../../experiments/section_key_selection.json), [phase14_summary.json](../../results/phase14_summary.json), [phase14_complete.json](../../checkpoints/phase14_complete.json).
