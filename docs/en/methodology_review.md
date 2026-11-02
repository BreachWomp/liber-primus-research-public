# Adversarial methodological review

## Source and control gates

All nine declared known-solution fixtures reproduce exactly. Eight also match
the canonical page corpus. One published LP1 fixture differs at two places and
is explicitly excluded from language training. Targeted image inspection
supports the retained iddqd reading; an exhaustive image transcription remains
unfinished. LP2 rune streams agree across two mirrors, which may share ancestry.

## E001: exchangeability test

For N symbols with counts n_a, the expected number of adjacent matches under a
uniform count-preserving permutation is sum(n_a(n_a-1))/N. A fixed subset of m
edges instead has expectation m*sum(n_a(n_a-1))/(N*(N-1)). The implemented test
uses these exact expectations and independent per-page shuffles. It never adds
cross-page edges. Word/line masks are fixed from the declared source layout.

The test has a predeclared lower tail, plus-one Monte Carlo correction, and a
59-test Holm family. A rejection is evidence against this exchangeable null.
It does not identify intentional suppression, a stream cipher, OTP, or an
external key. The deficit is prior art. Page images have not all been audited.

## E002 and E005: model-dependent diagnostics

The symmetric Markov null uses Taa=q, Tab=(1-q)/28. For lag k, its equality
probability is 1/29+(28/29)*((29*q-1)/28)^k. Independent transition-matrix tests
check the formula. Training and evaluation pages follow a fixed modulo split.
MaxT statistics center and scale all B+1 observed/simulated rows symmetrically.

These are plug-in diagnostics: uncertainty in fitted q is not propagated, and
page-specific symbol counts are not fixed. The holdout is computational; the
material is public and has prior analyses. E005 followed inspection of E002 and
reuses its split, so it is exploratory. Its 434 page/period comparisons are
adjusted jointly; the two experiment-global p-values also need joint correction
if interpreted as a family. Neither rejects, before or after that correction.
The injected period-eight control checks sensitivity to a strong unskipped
case, not to every actual cipher construction.

## E003: scoring is not validation

The exact LP2-56 solution ranks second. The first-ranked candidate uses the same
prime stream but skips F at position 51 rather than 56, corrupting a short region
while retaining much of the known message. Thus exact inclusion/recovery of a
control is weaker than correct selection. The scoring gate is recorded as
failed, and automatic decryption claims are disabled.

The language model has only 2,019 training runes after excluding the discrepant
fixture. Its scores are descriptive; no calibrated significance follows from
the 113,448 recipe evaluations. One shuffled input per page is a sanity check,
not a null distribution. Low scores cannot exclude cipher families, other
languages, key offsets outside the grid, or larger interrupter subsets.

## E004: exact sampler counterexample

For the multiset 00112 with exactly one adjacent equality, there are 12 states
in one connected component. An admissible swap graph has degrees 1, 2, or 4.
The accepted-move transition from state x to a neighbor is 1/degree(x).
Its stationary measure is proportional to degree, not uniform. Exact rational
arithmetic verifies detailed balance/stationarity. The total variation distance
between the degree-weighted and uniform measures is 5/21.

Counting every proposal, including rejections, restores a uniform stationary
target because off-diagonal transitions are symmetric. This alone does not
establish practical mixing on long pages. The small counterexample invalidates
a general uniformity guarantee, not every numerical result in the cited project.
This is established Markov-chain mathematics applied to a specific code path;
historical novelty is not claimed. No external issue or message was posted.

## Next gates

1. Audit every observed adjacent double against the images and an independent
   transcription; preserve uncertainty instead of silently correcting text.
2. Validate a richer language scorer on leave-one-section-out LP1 controls and
   new synthetic near-miss cases. LP2-56 is now a seen regression test, not an
   untouched holdout for further tuning.
3. Before conditional-null inference, verify stationary weights and mixing on
   exactly enumerable toy cases and use proposal-count chains with diagnostics.
4. Expand selective-F or transposition searches only after benchmark gates pass.
