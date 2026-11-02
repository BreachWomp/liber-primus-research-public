"""Acquire pinned public evidence; rebuild normalized corpus without running upstream code.

Default uses the local cache; --refresh downloads pinned bytes again. Sources are
community mirrors, not authenticated original releases. Python standard library only.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import difflib
import json
from pathlib import Path
import re
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
RUNES = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
ALIASES = {"ᛂ": "ᛄ"}
PINS = {
    "relikd": ("relikd/LiberPrayground", "719380ebee0523ad7f2fbf389c6f960d51bea5a4"),
    "iddqd": ("cicada-solvers/iddqd", "0e3789ad2949c62ea7fb9e3e00ded93df3b3ce07"),
    "scream314": ("scream314/cicada3301", "10733feb487bb8beb9966d534727ee5897aa54fc"),
}
GROUPS = [
    ("p0-2", 0, 2), ("p3-7", 3, 7), ("p8-14", 8, 14),
    ("p15-22", 15, 22), ("p23-26", 23, 26), ("p27-32", 27, 32),
    ("p33-39", 33, 39), ("p40-53", 40, 53), ("p54-55", 54, 55),
    ("p56_an_end", 56, 56), ("p57_parable", 57, 57),
]
CONTROLS = ["0_warning", "0_welcome", "0_wisdom", "0_koan_1", "0_loss_of_divinity", "jpg107-167", "jpg229", "p56_an_end", "p57_parable"]
MASTER = "liber-primus__transcription--master/liber-primus__transcription--master.txt"
IMAGE_SAMPLES = [("0_warning", 1), ("0_welcome_1", 3), ("jpg107-167_1", 14), ("p0", 17), ("p50", 67), ("p56_an_end", 73), ("p57_parable", 74)]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: str, obj) -> None:
    out = ROOT / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def url(label: str, path: str) -> str:
    repo, commit = PINS[label]
    return f"https://raw.githubusercontent.com/{repo}/{commit}/{path}"


def raw(label: str, path: str) -> str:
    return (ROOT / "data/raw" / label / path).read_text(encoding="utf-8")


def rune_text(text: str) -> str:
    unknown = {c for c in text if 0x16A0 <= ord(c) <= 0x16FF and c not in RUNES and c not in ALIASES and c not in "᛫᛬᛭"}
    if unknown:
        raise ValueError(f"Unrecognized runic glyphs require explicit review: {sorted(unknown)}")
    return "".join(ALIASES.get(c, c) for c in text if ALIASES.get(c, c) in RUNES)


def acquire(refresh: bool) -> list[dict]:
    tasks = set()
    for name, _, _ in GROUPS:
        tasks.add(("relikd", f"pages/{name}.txt"))
    for name in CONTROLS:
        tasks.add(("relikd", f"pages/{name}.txt"))
        tasks.add(("relikd", f"pages/solved_{name}.txt"))
    for path in ["solver.py", "LP/Alphabet.py", "LP/Rune.py", "LP/RuneText.py", "LP/RuneSolver.py"]:
        tasks.add(("relikd", path))
    for path in [MASTER, "liber-primus__keys/liber-primus__keys.txt", "liber-primus__index/liber-primus__index.txt"]:
        tasks.add(("iddqd", path))
    tasks.add(("scream314", "liber_primus.md"))
    tasks.add(("scream314", "assets/2014/stage11/56.runes"))
    for complete in (6, 7):
        tasks.add(("scream314", f"assets/2014/liber-primus-complete/{complete:02}.jpg"))
    for name, complete in IMAGE_SAMPLES:
        tasks.add(("relikd", f"pages/{name}.jpg"))
        tasks.add(("scream314", f"assets/2014/liber-primus-complete/{complete:02}.jpg"))
    manifest_path = ROOT / "sources/manifest.json"
    previous = {}
    if manifest_path.exists():
        previous = {x["id"]: x for x in json.loads(manifest_path.read_text(encoding="utf-8"))["files"]}

    def fetch(item):
        label, path = item
        ident = f"{label}:{path}"
        dest = ROOT / "data/raw" / label / path
        if refresh or not dest.exists() or ident not in previous:
            req = urllib.request.Request(url(label, path), headers={"User-Agent": "LiberPrimusResearch/0.1"})
            with urllib.request.urlopen(req, timeout=30) as response:
                data = response.read(8_000_001)
            if len(data) > 8_000_000:
                raise ValueError(f"Source unexpectedly exceeds 8 MB: {ident}")
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            retrieved = datetime.now(timezone.utc).isoformat()
        else:
            data = dest.read_bytes()
            retrieved = previous[ident]["retrieved_at_utc"]
            if sha256(data) != previous[ident]["sha256"]:
                raise ValueError(f"Cached source hash mismatch: {ident}; inspect before --refresh")
        return {
            "id": ident, "repository": PINS[label][0], "commit": PINS[label][1],
            "source_path": path, "url": url(label, path), "local_path": dest.relative_to(ROOT).as_posix(),
            "sha256": sha256(data), "bytes": len(data), "retrieved_at_utc": retrieved,
            "evidence_class": "community_mirror" if path.endswith(".jpg") else "community_transcription_or_documentation",
            "original_authenticity_verified": False,
        }
    with ThreadPoolExecutor(max_workers=6) as pool:
        records = list(pool.map(fetch, sorted(tasks)))
    write_json("sources/manifest.json", {
        "schema_version": 1,
        "warning": "Pinned bytes prove reproducibility, not original Cicada authorship or independent transcription lineage.",
        "repositories": {k: {"repository": v[0], "commit": v[1]} for k, v in PINS.items()},
        "unavailable_sources": [{"repository": "krisyotam/cicada3301", "result": "GitHub API HTTP 404 during initial acquisition; no inference whether deleted or private."}],
        "files": records,
    })
    return records


def iddqd_pages() -> list[str]:
    text = raw("iddqd", MASTER).split("\n\n", 1)[1]
    parts = text.split("%")
    assert len(parts) == 74 and not rune_text(parts[-1]), "Unexpected iddqd page delimiters"
    return parts[:-1]


def relikd_lp2() -> dict[int, tuple[str, str]]:
    result = {}
    for name, start, end in GROUPS:
        text = raw("relikd", f"pages/{name}.txt")
        if start == end:
            pieces = [text]
        else:
            pieces = text.split("\n\n")
        if name == "p3-7":
            assert len(pieces) == 7
            pieces = ["\n\n".join(pieces[:2])] + pieces[2:5] + ["\n\n".join(pieces[5:])]
        if name == "p15-22":
            assert len(pieces) == 9
            pieces = ["\n\n".join(pieces[:2])] + pieces[2:]
        if name == "p33-39":
            assert len(pieces) == 9
            pieces = ["\n\n".join(pieces[:2])] + pieces[2:7] + ["\n\n".join(pieces[7:])]
        if name == "p40-53":
            # The grids belong to 49, 50, 51. Blank lines are paragraph boundaries
            # here, not new pages. Checked against iddqd explicit % boundaries.
            assert len(pieces) == 16
            pieces = pieces[:9] + [pieces[9] + "\n\n" + pieces[10], pieces[11], pieces[12] + "\n\n" + pieces[13]] + pieces[14:]
        assert len(pieces) == end - start + 1, (name, len(pieces))
        for n, piece in zip(range(start, end + 1), pieces):
            result[n] = (piece, f"relikd:pages/{name}.txt")
    return result


def build_pages() -> tuple[list[dict], list[dict]]:
    secondary = iddqd_pages()
    primary = relikd_lp2()
    pages, comparison = [], []
    lp1_numbers = [1] + list(range(3, 17))
    lp1_by_number = dict(zip(lp1_numbers, secondary[:15]))
    for n in range(17):
        text = lp1_by_number.get(n, "Liber Primus" if n == 0 else "Intus")
        # Keep literal delimiter scheme as source metadata; / + LF represent one
        # line boundary, &/$/section sign are non-rune structural markers.
        record = {"id": f"LP1-{n:02}", "edition": "LP1", "page": n, "complete_page": n,
                  "runes": rune_text(text), "text_with_layout": text,
                  "layout_scheme": "iddqd_literal" if n in lp1_by_number else "latin_title",
                  "source_refs": [f"iddqd:{MASTER}"] if n in lp1_by_number else ["scream314:liber_primus.md"],
                  "status": "solved_control" if n in lp1_by_number else "non_rune",
                  "image_ref": url("scream314", f"assets/2014/liber-primus-complete/{n:02}.jpg")}
        pages.append(record)
    for n in range(58):
        text, source = primary[n]
        rs, other = rune_text(text), rune_text(secondary[15+n])
        mismatches = [{"offset": i, "primary": a, "secondary": b} for i, (a,b) in enumerate(zip(rs, other)) if a != b]
        comparison.append({"id": f"LP2-{n:02}", "primary_rune_count": len(rs), "secondary_rune_count": len(other),
                           "runes_equal": rs == other, "mismatches": mismatches,
                           "primary": source, "secondary": f"iddqd:{MASTER}"})
        record = {"id": f"LP2-{n:02}", "edition": "LP2", "page": n, "complete_page": n + 17,
                  "runes": rs, "text_with_layout": text, "layout_scheme": "relikd_literal",
                  "source_refs": [source, f"iddqd:{MASTER}"],
                  "status": "solved_control" if n >= 56 else "non_rune" if not rs else "unsolved",
                  "image_ref": url("scream314", f"assets/2014/liber-primus-complete/{n+17:02}.jpg"),
                  "transcription_agreement": rs == other}
        pages.append(record)
    for page in pages:
        page["rune_count"] = len(page["runes"])
        page["runes_sha256"] = sha256(page["runes"].encode("utf-8"))
    write_json("transcriptions/pages.json", pages)
    write_json("transcriptions/comparison.json", {"scope": "LP2 rune sequences only; punctuation/layout not asserted identical", "pages": comparison})
    return pages, comparison


def make_fixtures() -> list[dict]:
    canonical_pages = {p["id"]: p for p in json.loads((ROOT/"transcriptions/pages.json").read_text(encoding="utf-8"))}
    specs = [
        ("LP1-01_atbash", "0_warning", "atbash", [], [], ["LP1-01"]),
        ("LP1-03_04_divinity", "0_welcome", "vigenere", [23,10,1,10,9,10,16,26], [4,5,6,7,10,11,14,18,20,21,25], ["LP1-03", "LP1-04"]),
        ("LP1-05_direct", "0_wisdom", "direct", [], [], ["LP1-05"]),
        ("LP1-06_09_atbash_shift", "0_koan_1", "affine_plaintext_formula_2_minus_c", [], [], [f"LP1-{n:02}" for n in range(6,10)]),
        ("LP1-10_13_direct", "0_loss_of_divinity", "direct", [], [], [f"LP1-{n:02}" for n in range(10,14)]),
        ("LP1-14_15_circumference", "jpg107-167", "vigenere", [0,10,4,0,1,19,0,18,4,18,9,0,18], [2,3], ["LP1-14", "LP1-15"]),
        ("LP1-16_direct", "jpg229", "direct", [], [], ["LP1-16"]),
        ("LP2-56_totient_primes", "p56_an_end", "prime_minus_one", [], [4], ["LP2-56"]),
        ("LP2-57_direct", "p57_parable", "direct", [], [], ["LP2-57"]),
    ]
    fixtures = []
    for ident, name, method, key, ordinals, ids in specs:
        ciphertext = rune_text(raw("relikd", f"pages/{name}.txt"))
        expected = rune_text(raw("relikd", f"pages/solved_{name}.txt"))
        fs = [i for i, c in enumerate(ciphertext) if c == RUNES[0]]
        fixtures.append({"id": ident, "page_ids": ids, "cipher": method, "key_indices": key,
                         "skip_positions": [fs[n-1] for n in ordinals], "skip_semantics": "copy unchanged, consume no keystream; absolute zero-based rune offsets",
                         "ciphertext_runes": ciphertext, "expected_runes": expected, "plaintext_runes": expected,
                         "expected_indices": [RUNES.index(c) for c in expected],
                         "source_refs": [f"relikd:pages/{name}.txt", f"relikd:pages/solved_{name}.txt", "relikd:solver.py", "scream314:liber_primus.md"],
                         "evidence_limit": "Community known-solution transcription and algorithm; tests verify exact rune reproduction, not historical independent discovery."})
    differences = []
    for fixture in fixtures:
        canonical = "".join(canonical_pages[p]["runes"] for p in fixture["page_ids"])
        mirrored = fixture["ciphertext_runes"]
        fixture["canonical_pages_match"] = canonical == mirrored
        fixture["eligible_language_training"] = canonical == mirrored
        if canonical != mirrored:
            changes = []
            for op, a, b, c, d in difflib.SequenceMatcher(None, canonical, mirrored, autojunk=False).get_opcodes():
                if op != "equal":
                    changes.append({"operation": op, "canonical_range": [a,b], "fixture_range": [c,d],
                                    "canonical_runes": canonical[a:b], "fixture_runes": mirrored[c:d]})
            differences.append({"fixture_id": fixture["id"], "page_ids": fixture["page_ids"],
                                "canonical_length": len(canonical), "fixture_length": len(mirrored), "changes": changes,
                                "policy": "Retain both sources; exclude disputed fixture from language-model training. See reports/transcription_discrepancy.md."})
    write_json("transcriptions/LP1_discrepancies.json", differences)
    write_json("known_solutions/fixtures.json", fixtures)
    return fixtures


def report(records, pages, comparison, fixtures):
    by_id = {r["id"]: r for r in records}
    images = []
    for name, number in IMAGE_SAMPLES:
        a = by_id[f"relikd:pages/{name}.jpg"]
        b = by_id[f"scream314:assets/2014/liber-primus-complete/{number:02}.jpg"]
        images.append({"complete_page": number, "sources": [a["id"], b["id"]], "bytes_sha256_equal": a["sha256"] == b["sha256"]})
    write_json("sources/image_comparison.json", images)
    failures = [p for p in comparison if not p["runes_equal"]]
    counts = {"pages": len(pages), "LP2_pages": 58, "LP2_runes": sum(p["rune_count"] for p in pages if p["edition"] == "LP2"),
              "LP2_unsolved_runes": sum(p["rune_count"] for p in pages if p["edition"] == "LP2" and p["page"] <= 55),
              "LP2_comparisons_equal": 58-len(failures), "known_solution_fixtures": len(fixtures)}
    write_json("sources/corpus_summary.json", counts)
    lines = ["# Source audit", "", "The corpus is reproducible from pinned community repositories. Original Cicada release authenticity and cryptographic signatures have **not** been verified.", "", "## Numbering", "", "LP1 uses complete-image numbers 00–16 (17 pages); pages 00 and 02 are Latin title pages. LP2 uses 0–57 (58 pages), corresponding to complete-image numbers 17–74. LP2 page 50 is retained as a numeric-grid page with zero runes. LP2 pages 56 and 57 are known solved controls; pages 0–55 remain research targets.", "", "## Acquired sources", ""]
    for label, (repo, commit) in PINS.items():
        lines.append(f"- [{repo}](https://github.com/{repo}/tree/{commit}), commit `{commit}`.")
    lines += ["", "Every acquired file has a pinned URL, UTC retrieval timestamp, byte count and SHA-256 in `sources/manifest.json`. Acquisition does not execute upstream programs. Raw bytes remain in `data/raw/`.", "", "`krisyotam/cicada3301` returned HTTP 404 from the GitHub API; the corpus instead compares the relikd and cicada-solvers/iddqd repositories. Agreement is **not evidence of independent transcription**: these repositories may share ancestry.", "", "## Comparison", "", f"{58-len(failures)}/58 LP2 rune streams agree exactly after the single declared alias mapping ᛂ → ᛄ. LP2 contains {counts['LP2_runes']:,} runes; the pages 0–55 subset contains {counts['LP2_unsolved_runes']:,}. Detailed comparisons are in `transcriptions/comparison.json`.", "", f"{sum(x['bytes_sha256_equal'] for x in images)}/{len(images)} sampled image pairs are SHA-256 byte-identical across relikd and scream314. This establishes mirror consistency only. Complete-image page samples: {', '.join(str(x['complete_page']) for x in images)}. The primary images were not exhaustively compared glyph by glyph.", "", "## Normalization and limitations", "", "- `transcriptions/pages.json` is a JSON list with one record per page. `runes` contains only canonical Gematria Primus glyphs. `text_with_layout` preserves punctuation, line breaks and numeric material.", "- LP2 layout uses relikd's bullets and Unicode punctuation verbatim. Multi-page source sections are split on their source page breaks. In p40–53, separate numeric paragraphs are explicitly attached to pages 49, 50 and 51 using iddqd's page markers; blank lines are not universally page boundaries.", "- LP1 layout preserves iddqd's literal scheme: `-` word, `/` line, `%` page, `&` paragraph, `$` segment and `§` chapter. The delimiter header is excluded. The original file remains unchanged.", "- Rune agreement does not establish punctuation agreement. Statistical work sensitive to word or line boundaries should retain the declared layout scheme and test sensitivity to source choices.", "- Numeric-grid spellings are transcription data, not decoded values; their interpretation is unverified.", "- Reproducing known plaintext is a correctness gate, never evidence of a new solution. Fixtures include exact ciphertext and expected rune indices, explicit key direction, and exact interrupter positions.", "- Third-party material remains attributed to its source. A repository-level code license does not relicense the manuscript or upstream files. Upstream licensing must be reviewed before redistribution beyond the research corpus.", ""]
    if failures:
        lines += ["## Disagreements", ""] + [f"- {f['id']}: {len(f['mismatches'])} overlapping substitutions, counts {f['primary_rune_count']}/{f['secondary_rune_count']}." for f in failures]
    lines += ["## LP1 disagreement discovered by exact-control tests", "", "The LP1-06_09 fixture in relikd differs from the iddqd canonical corpus at two places (780 versus 778 runes). Both sources are preserved; this fixture is excluded from language-model training. See `transcriptions/LP1_discrepancies.json` and `reports/transcription_discrepancy.md`. Reproducing that fixture proves the published algorithm on its declared source, not its equality to the canonical page stream.", ""]
    (ROOT / "reports/source_audit.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(counts))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true", help="Download pinned sources even when cached")
    args = parser.parse_args()
    records = acquire(args.refresh)
    pages, comparison = build_pages()
    fixtures = make_fixtures()
    report(records, pages, comparison, fixtures)


if __name__ == "__main__":
    main()
