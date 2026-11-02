# Phase 1: Corpus, known controls, and statistical foundations

**No new decryption confirmed.** Historical report date: 2026-10-18T19:52:03.178045+00:00.

English editorial edition; the original report and raw results are preserved
unchanged. This edition consolidates repeated wording and navigation.

The initial corpus contains 75 pages: 17 in LP1 and 58 in LP2. LP2-50 is a
numeric-grid page and remains included. Two mirrors agree on all 58 LP2 rune
streams after the declared alias mapping: 13,136 runes overall, 12,956 on
LP2-00–55. Agreement does not establish independent transcription ancestry.
Nine known-solution fixtures reproduce exactly; eight match the canonical
corpus. The remaining LP1 fixture differs at two WHO/WHAT positions and is
excluded from language training. Original Cicada signatures were not verified.

| Experiment | Result | Interpretation |
|---|---|---|
| E001, adjacent equality | 86 observed pairs versus 439.166 expected; 9,999 permutations; raw p=0.0001, Holm59=0.0059 | Replication of a known repeat deficit, not cipher identification |
| E002, held-out Markov diagnostic | Lags 2–16, maxT p=0.6465 | No rejection of this limited plug-in model |
| E003, bounded cipher screen | 113,448 variants, 110,432 on unknown pages | No new plaintext; correct LP2-56 output ranks second |
| E004, sampler counterexample | Twelve states, exact total-variation distance 5/21 | Counting accepted swaps can bias a purportedly uniform sampler |
| E005, periods 2–32 | 434 page/period combinations, 9,999 simulations, maxT p=0.3012 | No detected signal; injected period-eight control succeeds |

Repeat deficits also occur within words (60 versus 328.067 expected) and lines
(82 versus 420.815). Jointly adjusted E002/E005 values are 0.6465 and 0.6024.
Non-rejection does not prove randomness or impossibility of decryption.
The initial language model has only 2,019 training runes. Its wrong LP2-56
selection skips F at position 51 instead of 56, exposing a scoring failure.
Six successful experiment processes, including one documented rerun after a
code change, used 30.905 seconds. The finite affine/prime-totient search does not cover arbitrary F subsets or
cross-page keys. The sampler result applies established Markov-chain theory to
a frozen code path; it is not claimed as a new theorem. **36 tests passed.**

## Evidence

- [Original frozen report](../../reports/research_report.md) (historical wording, usually German).
- [All registered outcomes](../../experiment_log.jsonl), [hypotheses](../../hypotheses.json), and [English index](INDEX.md).

Additional original evidence: [E001-adjacency-dca9ed9aa460.json](../../results/E001-adjacency-dca9ed9aa460.json), [E002-markov-heldout-7e729f4fda7a.json](../../results/E002-markov-heldout-7e729f4fda7a.json), [E003-bounded-cipher-screen-c2e41025a0eb.json](../../results/E003-bounded-cipher-screen-c2e41025a0eb.json), [E004-sampler-audit-7c4a6a3fc016.json](../../results/E004-sampler-audit-7c4a6a3fc016.json), [E005-heldout-period-scan-4dcfc95b826f.json](../../results/E005-heldout-period-scan-4dcfc95b826f.json), [research_checkpoint_2026-10-18.json](../../checkpoints/research_checkpoint_2026-10-18.json).
