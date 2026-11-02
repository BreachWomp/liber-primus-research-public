"""Predeclared held-out first-order null; no decryption or fitted key search.

Fit diagonal transition probability on LP2 pages with page % 4 != 0.
Inspect aggregate lag 2..16 on remaining pages, never crossing page boundaries.
Monte Carlo p-values are conditional on a plug-in q and uniform stationary
marginals. They are approximate model diagnostics, not exact permutation tests.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import time
from pathlib import Path

import numpy as np

ALPHABET = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
ALIASES = {"ᛂ": "ᛄ", "ᛋ": "ᛋ"}
LAGS = tuple(range(2, 17))


def rune_indices(text: str) -> np.ndarray:
    normalized = "".join(ALIASES.get(c, c) for c in text)
    unknown = set(normalized) - set(ALPHABET)
    if unknown:
        raise ValueError(f"Unknown symbols in rune-only input: {sorted(unknown)}")
    return np.array([ALPHABET.index(c) for c in normalized], dtype=np.int16)


def match_probability(q: float, lag: int, alphabet_size: int = 29) -> float:
    """Diagonal of T**lag for T_aa=q and T_ab=(1-q)/(m-1)."""
    if not 0 <= q <= 1 or lag < 0 or alphabet_size < 2:
        raise ValueError("Invalid Markov parameters")
    m = alphabet_size
    eigenvalue = (m * q - 1) / (m - 1)
    return 1 / m + (m - 1) / m * eigenvalue**lag


def simulate_pages(length: int, replicates: int, q: float,
                   rng: np.random.Generator, alphabet_size: int = 29) -> np.ndarray:
    """Independent stationary Markov chains using uniform nonzero increments."""
    if length < 0 or replicates < 1 or not 0 <= q <= 1:
        raise ValueError("Invalid simulation parameters")
    if length == 0:
        return np.empty((replicates, 0), dtype=np.int16)
    steps = rng.integers(1, alphabet_size, size=(replicates, length), dtype=np.int16)
    steps[:, 0] = rng.integers(0, alphabet_size, size=replicates)
    if length > 1:
        same = rng.random((replicates, length - 1)) < q
        steps[:, 1:][same] = 0
    return (np.cumsum(steps, axis=1, dtype=np.int64) % alphabet_size).astype(np.int16)


def symmetric_max_t(observed: np.ndarray, simulated: np.ndarray) -> dict:
    """All B+1 rows share centering/scaling, preserving exchangeability."""
    rows = np.vstack((observed, simulated)).astype(float)
    mean = rows.mean(axis=0)
    sd = rows.std(axis=0, ddof=0)
    active = sd > 0
    z = np.zeros_like(rows)
    z[:, active] = np.abs((rows[:, active] - mean[active]) / sd[active])
    maxima = z.max(axis=1) if active.any() else np.zeros(len(rows))
    # Include the observed row (equivalent to plus-one Monte Carlo correction).
    global_p = float(np.mean(maxima >= maxima[0]))
    adjusted = [float(np.mean(maxima >= v)) if a else 1.0
                for v, a in zip(z[0], active)]
    raw = [float(np.mean(z[:, j] >= z[0, j])) if active[j] else 1.0
           for j in range(rows.shape[1])]
    return {"global_p_plugin": global_p, "observed_max_abs_z": float(maxima[0]),
            "adjusted_p_plugin": adjusted, "raw_p_plugin": raw,
            "observed_abs_z": z[0].tolist(), "null_mean_symmetric": mean.tolist(),
            "null_sd_symmetric": sd.tolist(), "active": active.tolist()}


def wilson(successes: int, trials: int, z: float = 1.959963984540054) -> list[float]:
    if trials == 0:
        return [0.0, 1.0]
    q = successes / trials
    denominator = 1 + z*z/trials
    center = (q + z*z/(2*trials)) / denominator
    half = z * math.sqrt(q*(1-q)/trials + z*z/(4*trials*trials)) / denominator
    return [center-half, center+half]


def run(root: Path, replicates: int, seed: int, timeout_seconds: float) -> dict:
    started = time.monotonic()
    source = root / "transcriptions" / "pages.json"
    raw = source.read_bytes()
    records = json.loads(raw)
    eligible = [r for r in records if r["edition"] == "LP2" and
                r["status"] == "unsolved" and 0 <= int(r["page"]) <= 55 and r["runes"]]
    eligible.sort(key=lambda r: int(r["page"]))
    if len({r["id"] for r in eligible}) != len(eligible):
        raise ValueError("Duplicate page identifiers")
    train = [(r, rune_indices(r["runes"])) for r in eligible if int(r["page"]) % 4 != 0]
    held = [(r, rune_indices(r["runes"])) for r in eligible if int(r["page"]) % 4 == 0]
    train_edges = sum(max(len(x)-1, 0) for _, x in train)
    train_equal = sum(int(np.sum(x[1:] == x[:-1])) for _, x in train)
    if not train_edges or not held:
        raise ValueError("Empty training or held-out set")
    q = train_equal / train_edges
    lag_values = (1,) + LAGS
    observed = np.zeros(len(lag_values), dtype=np.int64)
    pair_totals = np.zeros(len(lag_values), dtype=np.int64)
    simulated = np.zeros((replicates, len(lag_values)), dtype=np.int64)
    rng = np.random.default_rng(seed)
    for record, x in held:
        for j, lag in enumerate(lag_values):
            pair_totals[j] += max(len(x)-lag, 0)
            if len(x) > lag:
                observed[j] += int(np.sum(x[lag:] == x[:-lag]))
        for start in range(0, replicates, 512):
            if time.monotonic() - started > timeout_seconds:
                raise TimeoutError("Markov diagnostic exceeded declared budget; no partial result accepted")
            stop = min(start+512, replicates)
            chains = simulate_pages(len(x), stop-start, q, rng)
            for j, lag in enumerate(lag_values):
                if len(x) > lag:
                    simulated[start:stop, j] += np.sum(chains[:, lag:] == chains[:, :-lag], axis=1)
    test = symmetric_max_t(observed[1:], simulated[:, 1:])
    calibration = symmetric_max_t(observed[:1], simulated[:, :1])
    theoretical = [float(n * match_probability(q, lag)) for n, lag in zip(pair_totals, lag_values)]
    return {
        "experiment_id": "E002-markov-heldout",
        "status": "completed", "decryption_claim": False,
        "source": {"path": "transcriptions/pages.json", "sha256": hashlib.sha256(raw).hexdigest()},
        "parameters": {"replicates": replicates, "seed": seed, "timeout_seconds": timeout_seconds,
                       "alphabet_size": 29, "lags": list(LAGS), "split": "heldout page % 4 == 0",
                       "training_page_ids": [r["id"] for r, _ in train],
                       "heldout_page_ids": [r["id"] for r, _ in held],
                       "null": "stationary symmetric first-order Markov; Taa=q; Tab=(1-q)/28"},
        "training": {"adjacent_equal": train_equal, "adjacent_edges": train_edges,
                     "q_mle": q, "q_wilson95_under_model": wilson(train_equal, train_edges)},
        "heldout_adjacent_calibration": {"observed_count": int(observed[0]),
                    "edge_count": int(pair_totals[0]), "expected_count": theoretical[0],
                    "p_two_sided_plugin": calibration["global_p_plugin"],
                    "note": "Separate descriptive calibration; outside the lag2..16 maxT family."},
        "lag_family": {"lags": list(LAGS), "observed_equal_counts": observed[1:].tolist(),
                    "pair_counts": pair_totals[1:].tolist(), "theoretical_expected_counts": theoretical[1:],
                    **test},
        "limits": ["Plugin q estimated only on declared training pages; estimation uncertainty is not propagated.",
                   "Uniform stationary marginals are assumed, not conditioned to observed page rune counts.",
                   "MaxT adjusts the 15 held-out aggregate lags only; it does not correct other experiments.",
                   "Page split is a computational holdout, not a historically unseen source; general prior-art knowledge exists.",
                   "Rejection identifies model mismatch, not a cipher; non-rejection does not validate the model or prove randomness."],
        "elapsed_seconds": time.monotonic() - started,
        "numpy_version": np.__version__, "rng": "numpy.default_rng/PCG64"
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--replicates", type=int, default=9999)
    parser.add_argument("--seed", type=int, default=3301003)
    parser.add_argument("--timeout-seconds", type=float, default=120)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.replicates < 99 or args.timeout_seconds <= 0:
        parser.error("At least 99 replicates and a positive timeout are required")
    result = run(args.root, args.replicates, args.seed, args.timeout_seconds)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"experiment_id": result["experiment_id"], "status": result["status"],
                      "global_p_plugin": result["lag_family"]["global_p_plugin"],
                      "elapsed_seconds": result["elapsed_seconds"]}))


if __name__ == "__main__":
    main()
