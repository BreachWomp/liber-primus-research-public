# Research engineering case study

## Outcome and role

The objective was to decrypt unknown Liber Primus pages. **That objective has
not been achieved.** The delivered artifact is an inspectable research system
and a record of bounded experiments that did not support a new decryption.
This case study is intended to make the engineering and judgment behind that
negative outcome easy to evaluate.

The repository owner set the research objective, required evidence before any
solution claim, and directed the focus toward unknown pages. OpenAI Codex
assisted with implementation, analysis, experiments, and writing. The case study
attributes the work to that collaborative workflow rather than claiming entirely
unaided authorship.

## 1. A plausible scoring improvement still failed its gate

An earlier model selected `TUNNELEA` instead of `TUNNELNG` in the known LP2-57
control. Phase 29 introduced explicit beginning-of-word and end-of-word events
in a fixed backoff model, trained on pinned Emerson chapters rather than LP
plaintext. It corrected that known error and improved fresh one-rune mutation
rankings from 355/360 to 358/360.

The stronger test was recovery from nine fresh random substitutions. Eight
controls were exact, but a 67-rune control recovered 65/67 symbols and preferred
`TRAPS / YANS` to the true `TRAYS / PANS`. The word `TRAPS` occurred once in the
training data; the other three did not. The gain of about 7.636 log units for
one change outweighed the penalty of about 0.934 for the other.

This was an objective-function failure: searching longer could not make the
truth the global optimum under that score. The preregistered 9/9 criterion was
not relaxed. The planned unknown-page experiment E082 was never registered or
run. A later phase explicitly changed scope to longer texts and required twelve
new successful controls before testing unknown pages. It did not relabel the
short-text failure as a success.

Evidence: [English phase 29 report](docs/en/phase29.md),
[English control comparison](docs/en/phase29_candidates.md),
[separate validation](results/phase29_controls_validation.json),
[phase 30](docs/en/phase30.md).

## 2. An attractive score disappeared under matched optimization

Phase 5 searched 1,244,100 affine plaintext-feedback variants on 55 unknown rune
pages. Initially, none of nineteen matched null texts reached the selected
LP2-55 score. A raw plus-one p-value of 0.05 was not evidence after selecting
the best of 55 pages.

The declared escalation rule froze the candidate and search procedure, then
ran 4,000 fresh null searches in twenty fixed batches with no early stopping.
Each null repeated the full optimization instead of evaluating only the chosen
key. Of those searches, 115 matched or exceeded the selected score. The fresh
raw p-value was approximately 0.028993; the page-adjusted value was 1.

The full candidate and reversible rule remain available. The readable-looking
parts were not edited into a message, and a low raw p-value was not presented
as a discovery.

Evidence: [English phase 5 report](docs/en/phase05.md),
[saved phase summary](results/phase5_summary.json),
[append-only log](experiment_log.jsonl).

## 3. Validation distinguished new work from reused evidence

Phase 31 tested the reversible family

```text
C[-1] = 0
D[i] = (C[i] - C[i-1]) mod 29
P[i] = S(D[i])

C[i] = (C[i-1] + inverse(S)(P[i])) mod 29
```

Here `S` is a permutation of the 29 rune symbols. Integrating the twelve
already-passed phase-30 substitution controls gives synthetic examples of this
family. Taking differences returns exactly the previous optimizer inputs.
Those controls were transported, not searched again or counted as new blind
successes. Checks across all 29 initial values were algebraic tests; the
unknown-page attack remained limited to initial value zero.

On 46 pages with at least 200 runes, the selected page was LP2-02. Nine of
nineteen matched null searches reached its score. A separate checker recomputed
1,320 candidate scores, 535,920 final-neighbor scores, and 1,320 cumulative
re-encryptions to the original ciphertext. These checks validate the reported
rules and scores, not the linguistic authenticity of the output.

The validator did not independently reproduce all optimization trajectories,
and it shares GP tokenization. The bounded heuristic does not exhaust 29!
permutations. The nineteen-null screen cannot attain significance after a
46-page correction even with zero exceedances.

Evidence: [English phase 31 report](docs/en/phase31.md),
[frozen attack plan](experiments/difference_substitution_unknown_plan.json),
[saved summary](results/phase31_summary.json).

## Infrastructure worth inspecting

- **Data lineage:** page IDs, upstream commits, retrieval timestamps, SHA-256,
  and unmodified source bytes. A two-rune LP1 source disagreement is retained,
  and the affected fixture is excluded from language training.
- **Reproducible execution:** fixed seeds, declared finite grids, input and
  dependency fingerprints, append-only outcomes, and resume checks.
- **Resource control:** bounded arrays and caches; recent phases use one worker,
  a 768 MiB process-memory ceiling, and explicit per-process and phase budgets.
- **Failure preservation:** aborted work, control failures, null-generator
  deviations, and historical duplicate runs remain visible.
- **Separate checking:** scalar rescoring, source-window reconstruction,
  invertibility, and re-encryption tests alongside optimized research runners.

An early exact sampler check is another useful small artifact: for the multiset
`00112` conditioned on one adjacent equality, counting only accepted swaps gives
a degree-weighted stationary distribution over twelve states, not a uniform
one. Exact arithmetic gives total-variation distance `5/21`. This applies known
Markov-chain mathematics; historical novelty is not claimed. See the
[methodology review](reports/methodology_review.md).

## What this does and does not demonstrate

The evidence supports reproducible implementation and explicit handling of
false positives within the tested settings. It does not demonstrate a solved
puzzle, a new cryptographic theorem, external peer review, a globally exhaustive
search, or a globally validated language scorer. The practical next step is a
predeclared test of the unresolved initial-value ambiguity, with fresh controls
and separate score validation, rather than increasing claims about existing
fragments.
