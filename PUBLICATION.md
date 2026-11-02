# Publication record

This public repository is a complete file snapshot of the research workspace at
source commit `211378e8fbc8486222e97299bdeb70f791793cec`, published on 2026-11-02.
It starts a clean public Git history. Private repository history, local caches,
credentials, ignored files, and account email addresses are not part of the
publication. The historical experiment log and all tracked results are included.

## Preservation contract

The [source manifest](publication/source_manifest.json) records the path, byte
count, SHA-256, and published location of every one of the 3,822 source files.
All original files remain byte-identical. The original German root README is
preserved at `publication/original/README.md`; the root README is a new English
entry point. The original relative links in that archived README refer to the
source repository root and are retained verbatim as evidence.

The English research editions under `docs/en/` explain each phase in English.
They are editorial editions for reading, not replacements for the frozen
reports, machine-readable results, or preregistrations. They consolidate
repeated caveats and navigation; use linked original evidence for the complete
historical wording and every recorded candidate. No source quotation,
ciphertext, key, or candidate is translated into invented plaintext.

Historical fields that identify the original private repository remain
unchanged, including repository visibility and older paths in saved state.
They describe the research environment at the time, not the current public
repository. Absolute local paths in research records are provenance, not setup
instructions. No private repository access is needed to inspect this snapshot.

The append-only log contains 1,799 completed records; `research_state.json`
contains 1,797 completed entries. Two historical omissions from the state list
are preserved rather than silently rewriting history. The log is the source
for the publication's completed-run count.

## Verification

```sh
python scripts/verify_public_snapshot.py
```

The standard-library verifier reads every manifest-listed file, checks sizes
and SHA-256 values, and checks the recorded output hashes for completed log
events. It does not rerun cryptanalysis or mutate research artifacts.
The publication validation record reports the actual checks run on this copy.

English publication documents and the verifier are additions after the source
commit, so they are intentionally outside the original-file manifest. Public
Git commits track those additions. This is a transparent file snapshot, not a
claim that its new public commit hash is the private source hash.
