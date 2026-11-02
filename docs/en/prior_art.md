# Prior art and evidence classification

The adjacent-repeat deficit was already described in
[Dukotah's findings](https://github.com/Dukotah/cicada3301/blob/f08b20b632d91209ddbaa747e8e2f23df0c78ba1/liber-primus/docs/FINDINGS.md).
E001 is an independent replication, not a discovery. That document also reports
interrupter-scoring ambiguity. We independently encounter it in E003.
Its broad cipher-family exclusions do not follow from the limited statistical
summaries or finite searches; we do not adopt them.

[The research ledger](https://github.com/Dukotah/cicada3301/blob/f08b20b632d91209ddbaa747e8e2f23df0c78ba1/research/LEDGER.md)
records earlier doublet-related and coordinate-period tests. It establishes that
these topics have substantial prior work, not that every reported inference is
valid. Our work preserves page boundaries and declares each tested family.

The primary source of the sampler audit is
[r5_doublet_anatomy.py, lines 300–315](https://github.com/Dukotah/cicada3301/blob/f08b20b632d91209ddbaa747e8e2f23df0c78ba1/liber-primus/analysis/r5_doublet_anatomy.py#L300-L315).
Its mixing counter advances after accepted count-preserving swaps only. E004
tests the resulting sampling rule mathematically without executing upstream code.
Raw source snapshots and SHA-256 hashes are in `sources/prior_art_manifest.json`.

Original material is represented by pinned community mirrors and transcriptions
in `sources/manifest.json`. Known methods and fixtures are drawn from relikd and
scream314; iddqd supplies the comparison corpus. Agreement between mirrors does
not establish independent historical provenance or authentic Cicada signatures.

Claims of new solutions found during web reconnaissance were not used as
ground truth. No exhaustive novelty review or new-decryption claim is made.
