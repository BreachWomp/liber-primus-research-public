# Phase 8: Source word boundaries and an external word score

**No new decryption confirmed.** Historical report date: 2026-10-19T22:49:29.345701+00:00.

English editorial edition; the original report and raw results are preserved
unchanged. This edition consolidates repeated wording and navigation.

E026 records all 75 pages with original layout, offsets, aliases, and non-rune
content. Lines and whitespace do not automatically create word boundaries.
Across suitable control pages, words continue unless an explicit separator is
present. Fifty-four of 55 unknown rune pages agree between sources on interior
segment boundaries. On LP2-35 at rune offset 80, an image supports relikd's
raised mark in `ᛈᛖ'ᛏ` against iddqd's `ᛈᛖᛏ`. Both readings and the separate
decision are retained; the image was inspected by one reader.
Apostrophes split lexical segments (for example DON T), not necessarily printed
words. Page-edge fragments are scored as complete segments, an explicit limit.

E027 trains a fixed word model on eleven Emerson essays excluding chapter II:
64,574 word tokens and 8,182 distinct rune words. For length L,
`P(w|L)=(count(w)+20*Q(w))/(N_L+20)`, with the fourgram backoff reset at each
segment. The model is normalized for fixed length and gives unseen words
positive probability. On the same 1,600 correlated mutations it favors truth
1,582 times versus 1,568 for the character score. Three known-key interruption
controls are exact. Selective-F dynamic programming keeps the complete partial
word and cursor until the segment is scored, then merges equal cursors; small
enumerations check its exactness within the specified search.

E028 tests all 55 pages using 812 affine maps, 381 word-key cycles, three number
streams, starts 0–255, four signs, and all F subsets. Four controls pass in the
combined grid. Selected LP2-55 scores -5.696945; 3/19 fully optimized nulls
reach it, raw p=0.20 and Bonferroni55=1. Nulls preserve segment endpoints,
counts, and adjacent matches. This retests known families with a changed score.

E029 is a historical limited check of a public solution claim. A published
byte digest agrees with E023; order(11 mod29)=28 and the Fibonacci-pair period
mod29 is 14. These facts do not decrypt a page. A claimed alternate binary
has unverified provenance; 256-byte length does not identify RSA. Source HTML
and hashes are archived, and downloaded code was not executed. The claim is
not endorsed, and later work stops this side investigation at the user's request.

**77 tests passed; 180 candidates were independently checked.** The image crop
matches its source region exactly. Seventy-eight tasks took 674.770 seconds;
E028 used 673.000 within 850 seconds, phase limit 900.

## Preserved candidate outputs

These blocks are copied verbatim from the historical report, in its order.
They are search outputs, **not confirmed plaintext**. Their rules, selection
context, and full records are in the linked evidence.

```text
I GNDI UG AN EASNGEOEOS PUIGSL LW OBFAFORLTHEJRS CRRBYF LDUS THTH THREATRME RROENGSNGU LO AEOPCDA PAR OWL
```

## Evidence

- [Original frozen report](../../reports/attack_phase8_report.md) (historical wording, usually German).
- [Complete machine-readable phase summary](../../results/phase8_summary.json).
- [Checkpoint and resource accounting](../../checkpoints/phase8_complete.json).
- [All registered outcomes](../../experiment_log.jsonl), [hypotheses](../../hypotheses.json), and [English index](INDEX.md).

Additional original evidence: [LP2-35-boundary-crop.png](../../sources/LP2-35-boundary-crop.png), [boundary_image_manifest.json](../../sources/boundary_image_manifest.json), [boundary_layout_decisions.json](../../sources/boundary_layout_decisions.json), [manifest.json](../../sources/community_claim_2026-10-20/manifest.json), [phase8_complete.json](../../checkpoints/phase8_complete.json), [phase8_summary.json](../../results/phase8_summary.json).
