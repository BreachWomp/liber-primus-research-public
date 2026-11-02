"""Count-preserving permutation test of adjacent rune equality.

All page permutations retain page length, rune counts and the original edge
masks. No cross-page edge is created. The inferential family is the three
aggregate masks plus one stream statistic per unsolved page (including empties).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from liberprimus.alphabet import RUNES


def holm(pvalues):
    """Holm step-down adjusted p-values, valid under arbitrary dependence."""
    order = sorted(range(len(pvalues)), key=lambda i: pvalues[i])
    out = [1.0] * len(pvalues)
    largest = 0.0
    for rank, index in enumerate(order):
        largest = max(largest, (len(order) - rank) * pvalues[index])
        out[index] = min(1.0, largest)
    return out


def page_arrays(page):
    text = page["text_with_layout"].replace("ᛂ", "ᛄ")
    positions = [i for i, char in enumerate(text) if char in RUNES]
    values = np.array([RUNES.index(text[i]) for i in positions], dtype=np.int16)
    expected = page["runes"].replace("ᛂ", "ᛄ")
    if "".join(RUNES[int(x)] for x in values) != expected:
        raise ValueError(f"Layout/rune mismatch on {page['id']}")
    gaps = [text[a+1:b] for a, b in zip(positions, positions[1:])]
    masks = {
        "stream": np.ones(max(0, len(values)-1), dtype=bool),
        "within_word": np.array([gap == "" for gap in gaps], dtype=bool),
        "within_line": np.array(["\n" not in gap and "\r" not in gap for gap in gaps], dtype=bool),
    }
    return values, masks


def describe(observed, draws, expectation, edges):
    return {
        "observed": int(observed), "edges": int(edges),
        "rate": float(observed / edges) if edges else None,
        "null_expectation_exact": float(expectation),
        "null_mean_simulated": float(np.mean(draws)),
        "null_sd": float(np.std(draws, ddof=1)),
        "null_interval_95": [float(x) for x in np.quantile(draws, [0.025, 0.975])],
        "p_lower": float((1 + np.count_nonzero(draws <= observed)) / (1 + len(draws))),
    }


def run(root, replicates=9999, seed=330120261018, timeout_seconds=120):
    if replicates < 2 or timeout_seconds <= 0:
        raise ValueError("replicates >= 2 and positive timeout required")
    started = time.perf_counter()
    path = root / "transcriptions/pages.json"
    source_bytes = path.read_bytes()
    pages = [p for p in json.loads(source_bytes) if p["edition"] == "LP2" and 0 <= p["page"] <= 55]
    pages.sort(key=lambda p: p["page"])
    if [p["page"] for p in pages] != list(range(56)):
        raise ValueError("Require all 56 unsolved LP2 pages, including non-rune pages")
    rng = np.random.default_rng(seed)
    names = ("stream", "within_word", "within_line")
    totals = {name: np.zeros(replicates, dtype=np.int64) for name in names}
    observed_total = dict.fromkeys(names, 0)
    expectation_total = dict.fromkeys(names, 0.0)
    edges_total = dict.fromkeys(names, 0)
    rows = []
    for page in pages:
        values, masks = page_arrays(page)
        n = len(values)
        observed = values[1:] == values[:-1]
        counts = np.bincount(values, minlength=29)
        pair_probability = float(sum(counts * (counts - 1)) / (n * (n - 1))) if n >= 2 else 0.0
        draws = {name: np.zeros(replicates, dtype=np.int64) for name in names}
        for first in range(0, replicates, 256):
            if time.perf_counter() - started > timeout_seconds:
                raise TimeoutError("Adjacency experiment exceeded its wall-time budget")
            last = min(first + 256, replicates)
            shuffled = rng.permuted(np.broadcast_to(values, (last-first, n)), axis=1)
            same = shuffled[:, 1:] == shuffled[:, :-1]
            for name in names:
                draws[name][first:last] = same[:, masks[name]].sum(axis=1)
        row = {"id": page["id"], "runes": n, "statistics": {}}
        for name in names:
            edges = int(masks[name].sum())
            value = int(observed[masks[name]].sum())
            expectation = edges * pair_probability
            row["statistics"][name] = describe(value, draws[name], expectation, edges)
            totals[name] += draws[name]
            observed_total[name] += value
            expectation_total[name] += expectation
            edges_total[name] += edges
        rows.append(row)
    aggregate = {name: describe(observed_total[name], totals[name], expectation_total[name], edges_total[name]) for name in names}
    tests = [aggregate[name] for name in names] + [row["statistics"]["stream"] for row in rows]
    adjusted = holm([test["p_lower"] for test in tests])
    for test, value in zip(tests, adjusted):
        test["p_holm_59"] = value
    return {
        "experiment": "E001-adjacency", "created_at": datetime.now(timezone.utc).isoformat(),
        "input_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "parameters": {"replicates": replicates, "seed": seed, "timeout_seconds": timeout_seconds,
                       "batch_size": 256, "page_ids": [p["id"] for p in pages]},
        "software": {"python": platform.python_version(), "numpy": np.__version__,
                     "rng": "numpy.default_rng/PCG64"},
        "null": "Independent uniform count-preserving permutations within each page; fixed layout masks",
        "tail": "lower", "multiple_testing": "Holm over 3 aggregate masks and 56 page-stream tests (59 total)",
        "limitations": ["Known prior-art signal; this is a replication.",
                       "A rejection concerns this exchangeable null, not all cipher families.",
                       "Transcription agreement does not establish independent historical provenance.",
                       "Within-word edges require no intervening non-rune character; within-line edges exclude LF/CR.",
                       "Finite Monte Carlo p-value resolution is 1/(replicates+1)."],
        "aggregate": aggregate, "pages": rows,
        "wall_seconds": time.perf_counter() - started,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--replicates", type=int, default=9999)
    parser.add_argument("--seed", type=int, default=330120261018)
    parser.add_argument("--timeout-seconds", type=float, default=120)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.root, args.replicates, args.seed, args.timeout_seconds)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "aggregate": result["aggregate"], "seconds": result["wall_seconds"]}))

