# Source audit

The corpus is reproducible from pinned community repositories. Original Cicada release authenticity and cryptographic signatures have **not** been verified.

## Numbering

LP1 uses complete-image numbers 00–16 (17 pages); pages 00 and 02 are Latin title pages. LP2 uses 0–57 (58 pages), corresponding to complete-image numbers 17–74. LP2 page 50 is retained as a numeric-grid page with zero runes. LP2 pages 56 and 57 are known solved controls; pages 0–55 remain research targets.

## Acquired sources

- [relikd/LiberPrayground](https://github.com/relikd/LiberPrayground/tree/719380ebee0523ad7f2fbf389c6f960d51bea5a4), commit `719380ebee0523ad7f2fbf389c6f960d51bea5a4`.
- [cicada-solvers/iddqd](https://github.com/cicada-solvers/iddqd/tree/0e3789ad2949c62ea7fb9e3e00ded93df3b3ce07), commit `0e3789ad2949c62ea7fb9e3e00ded93df3b3ce07`.
- [scream314/cicada3301](https://github.com/scream314/cicada3301/tree/10733feb487bb8beb9966d534727ee5897aa54fc), commit `10733feb487bb8beb9966d534727ee5897aa54fc`.

Every acquired file has a pinned URL, UTC retrieval timestamp, byte count and SHA-256 in `sources/manifest.json`. Acquisition does not execute upstream programs. Raw bytes remain in `data/raw/`.

`krisyotam/cicada3301` returned HTTP 404 from the GitHub API; the corpus instead compares the relikd and cicada-solvers/iddqd repositories. Agreement is **not evidence of independent transcription**: these repositories may share ancestry.

## Comparison

58/58 LP2 rune streams agree exactly after the single declared alias mapping ᛂ → ᛄ. LP2 contains 13,136 runes; the pages 0–55 subset contains 12,956. Detailed comparisons are in `transcriptions/comparison.json`.

7/7 sampled image pairs are SHA-256 byte-identical across relikd and scream314. This establishes mirror consistency only. Complete-image page samples: 1, 3, 14, 17, 67, 73, 74. The primary images were not exhaustively compared glyph by glyph.

## Normalization and limitations

- `transcriptions/pages.json` is a JSON list with one record per page. `runes` contains only canonical Gematria Primus glyphs. `text_with_layout` preserves punctuation, line breaks and numeric material.
- LP2 layout uses relikd's bullets and Unicode punctuation verbatim. Multi-page source sections are split on their source page breaks. In p40–53, separate numeric paragraphs are explicitly attached to pages 49, 50 and 51 using iddqd's page markers; blank lines are not universally page boundaries.
- LP1 layout preserves iddqd's literal scheme: `-` word, `/` line, `%` page, `&` paragraph, `$` segment and `§` chapter. The delimiter header is excluded. The original file remains unchanged.
- Rune agreement does not establish punctuation agreement. Statistical work sensitive to word or line boundaries should retain the declared layout scheme and test sensitivity to source choices.
- Numeric-grid spellings are transcription data, not decoded values; their interpretation is unverified.
- Reproducing known plaintext is a correctness gate, never evidence of a new solution. Fixtures include exact ciphertext and expected rune indices, explicit key direction, and exact interrupter positions.
- Third-party material remains attributed to its source. A repository-level code license does not relicense the manuscript or upstream files. Upstream licensing must be reviewed before redistribution beyond the research corpus.

## LP1 disagreement discovered by exact-control tests

The LP1-06_09 fixture in relikd differs from the iddqd canonical corpus at two places (780 versus 778 runes). Both sources are preserved; this fixture is excluded from language-model training. See `transcriptions/LP1_discrepancies.json` and `reports/transcription_discrepancy.md`. Reproducing that fixture proves the published algorithm on its declared source, not its equality to the canonical page stream.
