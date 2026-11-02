"""A fixed, bounded descriptive screen; language scores are not p-values."""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from liberprimus.alphabet import to_indices, to_runes, transliterate
from liberprimus.ciphers import primes
from liberprimus.scoring import NGramModel


def recipes(values):
    """P=a*C+b, then explicit prime-totient shifts; skip consumes no key."""
    n = len(values)
    affine_meta = [{"family": "affine", "a": a, "b": b} for a in range(1, 29) for b in range(29)]
    affine = np.array([(a * values + b) % 29 for a in range(1, 29) for b in range(29)], dtype=np.int16)
    yield affine, affine_meta
    f_positions = np.flatnonzero(values == 0).tolist()
    masks = [[], f_positions] + [[i] for i in f_positions]
    unique_masks = sorted(set(tuple(mask) for mask in masks))
    stream = np.array([p-1 for p in itertools.islice(primes(), n+29)], dtype=np.int32)
    for mask in unique_masks:
        active = np.ones(n, dtype=bool)
        active[list(mask)] = False
        rows, metadata = [], []
        for offset in range(29):
            key = stream[offset:offset+int(active.sum())]
            for cipher_sign in (1, -1):
                for key_sign in (-1, 1):
                    plain = values.copy()
                    plain[active] = (cipher_sign * values[active] + key_sign * key) % 29
                    rows.append(plain)
                    metadata.append({"family": "prime_totient", "prime_offset": offset,
                                     "cipher_sign": cipher_sign, "key_sign": key_sign,
                                     "skip_positions": list(mask), "skip_semantics": "copy rune; consume no key"})
        yield np.array(rows, dtype=np.int16), metadata


def model_table(model):
    table = np.full((29,)*3, math.log(model.alpha/(model.total+model.alpha*29**3)))
    for gram, count in model.counts.items():
        table[gram] = math.log((count+model.alpha)/(model.total+model.alpha*29**3))
    return table


def score_rows(rows, table):
    return table[rows[:, :-2], rows[:, 1:-1], rows[:, 2:]].mean(axis=1)


def run(root, timeout_seconds=180, seed=3301003):
    started = time.perf_counter()
    data_bytes = (root/"transcriptions/pages.json").read_bytes()
    fixture_bytes = (root/"known_solutions/fixtures.json").read_bytes()
    pages, fixtures = json.loads(data_bytes), json.loads(fixture_bytes)
    training = [f for f in fixtures if f.get("eligible_language_training", False) and all(p.startswith("LP1-") for p in f["page_ids"])]
    model = NGramModel.train([to_indices(f["plaintext_runes"]) for f in training], order=3, alpha=0.1)
    table = model_table(model)
    controls = {f["page_ids"][0]: f for f in fixtures if len(f["page_ids"]) == 1 and f["page_ids"][0].startswith("LP2-")}
    rows, all_trials, rng = [], 0, np.random.default_rng(seed)
    for page in sorted((p for p in pages if p["edition"] == "LP2"), key=lambda p:p["page"]):
        values = np.array(to_indices(page["runes"]), dtype=np.int16)
        if len(values) < 3:
            rows.append({"id": page["id"], "status": "excluded_no_rune_trigrams", "variants": 0})
            continue
        candidates, trials, best_exact, unique, all_scores = [], 0, None, set(), []
        expected = np.array(to_indices(controls[page["id"]]["plaintext_runes"]), dtype=np.int16) if page["id"] in controls else None
        for outputs, metadata in recipes(values):
            if time.perf_counter()-started > timeout_seconds:
                raise TimeoutError("Cipher screen exceeded wall-time budget")
            scores = score_rows(outputs, table)
            all_scores.extend(float(s) for s in scores)
            trials += len(outputs)
            for plain, recipe, score in zip(outputs, metadata, scores):
                if expected is not None and np.array_equal(plain, expected):
                    best_exact = {"recipe": recipe, "score": float(score)}
            batch_unique = set()
            for index in np.argsort(scores)[::-1]:
                key = outputs[index].tobytes()
                if key in batch_unique:
                    continue
                batch_unique.add(key)
                if key in unique:
                    if len(batch_unique) >= 3:
                        break
                    continue
                unique.add(key)
                candidates.append((float(scores[index]), metadata[index], outputs[index].tolist()))
                if len(batch_unique) >= 3:
                    break
            candidates.sort(key=lambda c:c[0], reverse=True)
            candidates = candidates[:3]
        all_trials += trials
        output = {"id": page["id"], "status": "known_control" if expected is not None else "unverified_screen",
                  "runes": len(values), "variants": trials,
                  "top": [{"score": s, "recipe": r, "plaintext_runes": to_runes(p), "transliteration": transliterate(p)} for s,r,p in candidates]}
        if expected is not None:
            if best_exact is None:
                raise AssertionError(f"Positive control not in enumerated family: {page['id']}")
            output["positive_control"] = {**best_exact, "exact_recovery": True,
                "rank_among_recipes": 1 + sum(s > best_exact["score"] for s in all_scores),
                "top_is_exact": candidates[0][2] == expected.tolist()}
        # One shuffled negative control is descriptive only; it supplies no p-value.
        shuffled = rng.permutation(values)
        shuffle_best = -math.inf
        for outputs, _ in recipes(shuffled):
            if time.perf_counter()-started > timeout_seconds:
                raise TimeoutError("Cipher screen exceeded wall-time budget")
            shuffle_best = max(shuffle_best, float(score_rows(outputs, table).max()))
        output["one_shuffled_negative_control_best"] = shuffle_best
        rows.append(output)
    threshold = min(row["positive_control"]["score"] for row in rows if "positive_control" in row)
    for row in rows:
        if row["status"] == "unverified_screen":
            row["above_minimum_known_control_score"] = row["top"][0]["score"] >= threshold
    return {"experiment": "E003-bounded-cipher-screen", "created_at": datetime.now(timezone.utc).isoformat(),
            "input_sha256": hashlib.sha256(data_bytes).hexdigest(),
            "fixtures_sha256": hashlib.sha256(fixture_bytes).hexdigest(),
            "parameters": {"seed": seed, "timeout_seconds": timeout_seconds, "model_order":3, "alpha":0.1,
                "training_ids": [f["id"] for f in training], "training_runes":sum(len(f["plaintext_runes"]) for f in training),
                "affine_grid":"a=1..28,b=0..28,P=aC+b mod29",
                "prime_grid":"phi(p) offsets 0..28,cipher_sign +/-1,key_sign +/-1",
                "skip_masks":"none, all ciphertext F, each single ciphertext F; duplicate masks removed",
                "negative_control_replicates":1, "top_saved_per_page":3},
            "variants_total":all_trials, "descriptive_control_score_threshold":threshold,
            "limitations":["Screening scores are not calibrated significance or decryption probabilities.",
                "No corrected p-value: adaptive maximum over this large family prevents inferential use of raw scores.",
                "One shuffle per page is a pipeline sanity check, not a statistical test.",
                "A score below known controls does not reject a cipher family or a different language/register.",
                "Exact positive controls use previously published transformations; no novelty.",
                "Skipped-F subsets of size 2..n-1, global section keys, and larger prime offsets are outside scope."],
            "scoring_gate": {"all_known_controls_rank_first":all(p["positive_control"]["top_is_exact"] for p in rows if "positive_control" in p),
                             "policy":"Failure blocks any automatic decryption claim or broad negative inference from language-score ranks."},
            "new_decryptions":[], "pages":rows, "wall_seconds":time.perf_counter()-started}


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",type=Path,default=ROOT)
    parser.add_argument("--timeout-seconds",type=float,default=180)
    parser.add_argument("--seed",type=int,default=3301003)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    result=run(args.root,args.timeout_seconds,args.seed)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"output":str(args.output),"variants_total":result["variants_total"],"seconds":result["wall_seconds"],
        "controls":[{"id":p["id"],**p["positive_control"]} for p in result["pages"] if "positive_control" in p],
        "screen_hits":[p["id"] for p in result["pages"] if p.get("above_minimum_known_control_score")]}))
