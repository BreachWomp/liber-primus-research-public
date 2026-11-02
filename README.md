# Liber Primus: reproducible cryptanalysis under uncertainty

**No previously unknown Liber Primus page has been decrypted by this project.**
This repository publishes the complete research file snapshot from 31 phases of
bounded cryptanalysis: implementations, source provenance, hypotheses, controls,
candidate outputs, null experiments, failed attempts, and validation records.

The engineering question is how to search for a real solution while preventing
plausible-looking output from becoming a false claim of success.

## Start here

- [Research engineering case study](PORTFOLIO.md): three concrete decisions, their evidence, and their limitations.
- [English research index](docs/en/INDEX.md): all 31 phases and supporting documentation.
- [Latest results: differences and general substitution](docs/en/phase31.md).
- [Research protocol](reports/research_protocol.md), [hypotheses](hypotheses.json), and [saved state](research_state.json).
- [Publication and integrity notes](PUBLICATION.md), including what is preserved and what is new.

## What is included

| Measure | Published research snapshot |
|---|---:|
| Catalogued manuscript pages | 75: LP1 has 17, LP2 has 58 |
| Research phases | 31 |
| Completed registered runs | 1,799 |
| Distinct completed experiment groups | 84 |
| Research test cases at the snapshot | 145 |
| Original tracked files preserved | 3,822 |
| Original file content | 2,644,068,564 bytes, about 2.64 GB |
| New confirmed decryptions | **0** |

Counts describe work performed, not independent discoveries. Some runs are
controls, null replications, or validations. In particular, E085 transfers
existing controls algebraically; it does not perform twelve new blind searches.

The latest attack tested a fixed-initial-value difference transform followed by
general substitution on 46 longer unknown LP2 pages. Nine of nineteen matched
null searches scored at least as highly as the selected page: raw Monte Carlo
`p = 0.50`, page-adjusted `p = 1.00`. That is not evidence of decryption.

## Inspect and verify

Python 3.12.14 and NumPy 2.3.5 were used for the saved snapshot. Core code uses
the Python standard library; NumPy is an optional research-runner dependency.
Install the pinned research dependency to exercise the NumPy-backed tests too.

```sh
python -m pip install -r requirements-research.txt
python scripts/verify_public_snapshot.py
```

Run the full suite from the repository root. PowerShell:

```powershell
$env:PYTHONPATH = "src;experiments"
python -m unittest discover -s tests -v
```

POSIX shell:

```sh
PYTHONPATH=src:experiments python -m unittest discover -s tests -v
```

The snapshot verifier is read-only. Historical supervisors and finalizers can
write research state and outputs; inspect their frozen plans before running
them. Several resource supervisors use Windows-specific process monitoring.
This publication does not claim cross-platform validation of every runner.
Completed experiments are keyed by their inputs, parameters, and dependencies
and are skipped when the same fingerprint is resumed.

## Repository map

| Location | Contents |
|---|---|
| `src/` | Alphabet operations, statistics, scoring, ciphers, and search primitives |
| `experiments/` | Frozen plans and bounded research runners |
| `tests/` | Regression, algebraic, statistical, and implementation checks |
| `scripts/` | Acquisition, supervision, independent verification, and checkpoint tools |
| `results/` | Complete machine-readable outputs, including negative results |
| `checkpoints/` | Saved phase state and resource accounting |
| `sources/`, `data/raw/` | Pinned provenance and unmodified source snapshots |
| `transcriptions/`, `known_solutions/` | Page-aware corpus and established solution fixtures |
| `docs/en/` | English editions of the research reports and reviewer navigation |
| `reports/` | Original historical reports, retained byte for byte |
| `experiment_log.jsonl` | Append-only research registration and outcome log |
| `publication/` | Source manifest and publication validation record |

LP1 and LP2 identifiers are kept separate. LP2-50 is a numeric page and remains
in the corpus; exclusion from a rune-only attack is explicit. LP2-56 and LP2-57
are established controls, not new solutions.

## Authorship and limitations

This is human-directed, AI-assisted research developed collaboratively with
**OpenAI Codex**. Code, experiments, and reports were produced in that workflow;
this is not a claim that the repository was entirely hand-written. Publication
is by [BreachWomp](https://github.com/BreachWomp). No affiliation with or
endorsement by Anthropic, OpenAI, or the original puzzle authors is implied.

“Independent verification” in these records means separate implementations
within this project, with shared components disclosed. It does not mean external
peer review. Source mirrors can share ancestry; pinned bytes establish
reproducibility, not original Cicada authenticity. Search heuristics, English
language models, small null samples, and repeated exploratory use of the corpus
limit what can be concluded. Language-like fragments are recorded candidates,
not plaintext discoveries.

All new reader-facing publication material is in English. Original historical
reports and source material retain their original languages and exact bytes;
English editions provide the reading path without rewriting research evidence.
See [third-party provenance and rights](THIRD_PARTY.md).
