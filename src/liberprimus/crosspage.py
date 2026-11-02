"""Cross-page comparisons with explicit alignments and denominators."""

from collections.abc import Iterable, Mapping
from .alphabet import MODULUS, validate_indices
from .stats import ngram_counts


def aligned_differences(left: Iterable[int], right: Iterable[int], *, shift: int = 0) -> dict:
    """Compare left[i] to right[i+shift], reporting histogram of left-right."""
    if type(shift) is not int:
        raise ValueError("shift must be an integer")
    a, b = validate_indices(left), validate_indices(right)
    start, stop = max(0, -shift), min(len(a), len(b) - shift)
    differences = [(a[i] - b[i + shift]) % MODULUS for i in range(start, stop)]
    histogram = [0] * MODULUS
    for difference in differences:
        histogram[difference] += 1
    return {"shift": shift, "overlap": len(differences), "difference_counts": histogram,
            "equality_rate": histogram[0] / len(differences) if differences else None}


def shared_ngrams(pages: Mapping[str, Iterable[int]], n: int = 3) -> dict[tuple[int, ...], dict[str, int]]:
    """Only ngrams occurring on at least two pages; never join page boundaries."""
    ngram_counts([], n)
    occurrences = {}
    for page, values in pages.items():
        for gram, count in ngram_counts(values, n).items():
            occurrences.setdefault(gram, {})[page] = count
    return {gram: counts for gram, counts in occurrences.items() if len(counts) > 1}
