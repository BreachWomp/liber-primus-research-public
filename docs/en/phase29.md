# Phase 29: Explicit word endings reveal another scoring failure

**No new decryption confirmed.** Historical report date: 2026-11-01T17:52:27.224779+00:00.

English editorial edition; the original report and raw results are preserved
unchanged. This edition consolidates repeated wording and navigation.

E080 responds to the previously seen LP2-57 error TUNNELEA rather than TUNNELNG.
The fixed new model uses three BOS markers, 29 runes, an EOS event, fourgram
backoff (alpha=0.5,strength=5), and
`P(w)=(count(w)+20*Q(w))/(N+20)`, with EOS in Q. Q permits empty emission;
observed segments remain nonempty. Training uses only pinned Emerson
I,III–IX, excluding II and X–XII from fitting. No LP words, spelling rules,
or case-specific bonuses are added. This is established modeling, designed
after seeing the old error rather than blind to it.

Truth beats every genuinely changing single-symbol swap for three known
controls. Fresh single-rune mutations rank correctly in 358/360 cases versus
355/360 for the old word model. Both models rank all 342 frequency shuffles
below their source texts. These dependent diagnostics have no discovery
p-values. A separate implementation reconstructs 1,944 scores from source
events, maximum discrepancy 5.33e-15, with shared GP tokenization disclosed.

E081 uses nine fresh random substitutions: three LP regressions and six
windows from X–XII. Search gets ciphertext and boundaries, not the true key or
plaintext. At most 24 unchanged starts receive forty 406-swap character sweeps
and forty word-score sweeps. No restarts are added after observing failures.
The known LP2-57 case is now exact (95/95), but overall **8/9** pass. A 67-rune
control gives 65/67: true **TRAYS/PANS** becomes **TRAPS/YANS**. TRAPS appears
once in training; the other three words are absent. A gain of about 7.636 log
units outweighs a penalty of about 0.934. The wrong mapping has a higher total
score; more optimization cannot make truth its global optimum.

Three optimized control nulls score -6.019000, -5.845713, -5.579128, as
capability diagnostics only. Separate checks cover 235 candidate/truth scores,
91,756 final-neighbor scores, and 226 re-encryptions, including bijections,
source windows, seeds, selection, and final local optima. Intermediate search
trajectories and initialization are not independently reimplemented. Symbols
absent from a control cannot have their mappings identified.

The required 9/9 gate is **not relaxed: E082 is never registered or run**.
There is no new unknown-page substitution scan in this phase. Five controls
of at least 200 runes being exact motivates a separate prospective longer-text
test, not a retroactive pass for E081. **142 tests passed; thirteen tasks used
28.111 seconds within 1,800; sampled peak 167.0 MiB against 768.** The English
candidate appendix shows the known control's correct and incorrect outputs.

## Recorded result tables

Values are preserved from the original report; headings and outcome labels
are rendered in English. These tables describe controls or search scores,
not independent discoveries.

| Control | Runes | Correct positions | True score | Recovered score |
|---|---:|---:|---:|---:|
| 0 | 515 | 515/515 | -1.861097 | -1.861097 |
| 1 | 319 | 319/319 | -1.994198 | -1.994198 |
| 2 | 95 | 95/95 | -2.303467 | -2.303467 |
| 3 | 69 | 69/69 | -1.391832 | -1.391832 |
| 4 | 69 | 69/69 | -1.577202 | -1.577202 |
| 5 | 67 | 65/67 | -2.421091 | -2.321066 |
| 6 | 301 | 301/301 | -1.883484 | -1.883484 |
| 7 | 301 | 301/301 | -1.709405 | -1.709405 |
| 8 | 300 | 300/300 | -1.721807 | -1.721807 |

## Evidence

- [Original frozen report](../../reports/attack_phase29_report.md) (historical wording, usually German).
- [Complete machine-readable phase summary](../../results/phase29_summary.json).
- [Checkpoint and resource accounting](../../checkpoints/phase29_complete.json).
- [All registered outcomes](../../experiment_log.jsonl), [hypotheses](../../hypotheses.json), and [English index](INDEX.md).

Additional original evidence: [terminated_substitution_plan.json](../../experiments/terminated_substitution_plan.json), [terminated_controls_plan.json](../../experiments/terminated_controls_plan.json), [phase29_summary.json](../../results/phase29_summary.json).

[English candidate appendix](phase29_candidates.md).
