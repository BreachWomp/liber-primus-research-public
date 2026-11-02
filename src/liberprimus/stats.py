"""Descriptive rune statistics; no significance claim is implicit in a peak."""

from collections import Counter, defaultdict
from collections.abc import Iterable, Sequence
from math import log2
from .alphabet import MODULUS, validate_indices


def frequencies(values: Iterable[int]) -> list[int]:
    counts = Counter(validate_indices(values))
    return [counts[i] for i in range(MODULUS)]


def index_of_coincidence(values: Iterable[int]) -> float | None:
    data = validate_indices(values)
    n = len(data)
    return sum(c * (c - 1) for c in Counter(data).values()) / (n * (n - 1)) if n > 1 else None


def entropy(values: Iterable[int]) -> float:
    """Plugin Shannon entropy in bits per rune (downward biased at small n)."""
    data = validate_indices(values)
    n = len(data)
    return -sum((c / n) * log2(c / n) for c in Counter(data).values()) if n else 0.0


def summary(values: Iterable[int]) -> dict:
    data = validate_indices(values)
    return {"length": len(data), "frequencies": frequencies(data),
            "ic": index_of_coincidence(data), "entropy": entropy(data)}


def ngram_counts(values: Iterable[int], n: int = 2) -> Counter:
    if type(n) is not int or n < 1:
        raise ValueError("ngram order must be a positive integer")
    data = validate_indices(values)
    return Counter(tuple(data[i:i + n]) for i in range(len(data) - n + 1))


def repeated_ngrams(values: Iterable[int], n: int = 3) -> dict[tuple[int, ...], list[int]]:
    """Return overlapping positions of repeated ngrams, suitable for Kasiski tests."""
    data = validate_indices(values)
    ngram_counts([], n)  # shared validation
    positions = defaultdict(list)
    for i in range(len(data) - n + 1):
        positions[tuple(data[i:i + n])].append(i)
    return {gram: offsets for gram, offsets in positions.items() if len(offsets) > 1}


def lag_coincidences(values: Iterable[int], max_lag: int = 30) -> list[dict]:
    """Non-circular equality autocorrelation. Pairs and rates accompany counts."""
    if type(max_lag) is not int or max_lag < 1:
        raise ValueError("max_lag must be a positive integer")
    data = validate_indices(values)
    result = []
    for lag in range(1, min(max_lag + 1, len(data))):
        pairs = len(data) - lag
        matches = sum(a == b for a, b in zip(data, data[lag:]))
        result.append({"lag": lag, "pairs": pairs, "matches": matches, "rate": matches / pairs})
    return result


def periodic_ic(values: Iterable[int], max_period: int = 30) -> list[dict]:
    """Pooled within-column IC, weighted by comparable pairs, not column count."""
    if type(max_period) is not int or max_period < 1:
        raise ValueError("max_period must be a positive integer")
    data = validate_indices(values)
    result = []
    for period in range(1, max_period + 1):
        numerator = denominator = 0
        for offset in range(period):
            column = data[offset::period]
            numerator += sum(c * (c - 1) for c in Counter(column).values())
            denominator += len(column) * (len(column) - 1)
        result.append({"period": period, "ordered_pairs": denominator,
                       "ic": numerator / denominator if denominator else None})
    return result


def chi_squared(values: Iterable[int], expected: Sequence[float]) -> float:
    """Descriptive Pearson statistic against an explicit 29-rune distribution."""
    from math import isfinite
    if len(expected) != MODULUS or any(not isfinite(p) or p <= 0 for p in expected):
        raise ValueError("expected must contain 29 positive finite weights")
    data = validate_indices(values)
    if not data:
        raise ValueError("chi-squared needs a nonempty sample")
    total = sum(expected)
    return sum((count - len(data) * p / total) ** 2 / (len(data) * p / total)
               for count, p in zip(frequencies(data), expected))
