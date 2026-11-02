# LP1 control-source discrepancy

Exact control tests discovered two differences in the pinned LP1 koan source.
This is a data-quality finding, not a new decryption or a claim of first discovery.

The iddqd master (used for LP1 page records) has 778 runes across LP1-06..09.
The relikd `0_koan_1.txt` control has 780. At concatenated zero-based offsets
142 and 278, iddqd has `ᛠ`; relikd instead has `ᚹᛋ`. Under the established
P=(2-C) mod 29 transform these correspond to O versus AT, changing WHO to WHAT.
The local offsets are LP1-06:142 and LP1-07:69.

The pinned scream314 images `06.jpg` and `07.jpg` were inspected on 2026-10-18.
The three-glyph WHO groups in the relevant lines appear consistent with iddqd:
LP1-06 text line 8 (including the header line), and LP1-07 text line 4.
This is targeted visual evidence, not an exhaustive independent transcription.
Image sources, retrieval times, and hashes are in `sources/manifest.json`.

No source bytes were changed. Both variants are preserved in
`transcriptions/LP1_discrepancies.json`; the disputed published control still
reproduces exactly from its own cited ciphertext. The language model excludes
that entire fixture. Eight other fixtures match the canonical corpus exactly.

This matters because a readable, exactly reproducible solution can still be
based on a different transcription. Both correctness checks are required.
