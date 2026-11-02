"""Explicitly trained rune ngram likelihoods, with add-alpha smoothing.

Train and evaluate on separate documents/pages. Fixed-order likelihoods are
ranking features, not calibrated probabilities that a decryption is correct.
Scores from different models or orders must not be compared directly.
"""

from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from math import isfinite, log
from .alphabet import MODULUS, validate_indices
from .stats import ngram_counts


@dataclass(frozen=True)
class NGramModel:
    order: int
    counts: dict[tuple[int, ...], int]
    total: int
    alpha: float

    def __post_init__(self):
        if type(self.order) is not int or self.order < 1:
            raise ValueError("order must be a positive integer")
        if not isfinite(self.alpha) or self.alpha <= 0:
            raise ValueError("alpha must be finite and positive")
        if type(self.total) is not int or self.total <= 0 or self.total != sum(self.counts.values()):
            raise ValueError("model needs a positive, consistent training count")
        for gram, count in self.counts.items():
            if len(gram) != self.order or type(count) is not int or count < 1:
                raise ValueError("invalid ngram or count")
            validate_indices(gram)

    @classmethod
    def train(cls, sequences: Iterable[Iterable[int]], *, order: int = 3, alpha: float = 0.1):
        counts = Counter()
        ngram_counts([], order)
        for sequence in sequences:
            counts.update(ngram_counts(sequence, order))
        return cls(order, dict(counts), sum(counts.values()), alpha)

    def score(self, values: Iterable[int]) -> float:
        """Mean natural-log likelihood per ngram; -inf when no ngram fits."""
        grams = ngram_counts(validate_indices(values), self.order)
        size = sum(grams.values())
        if not size:
            return float("-inf")
        denominator = self.total + self.alpha * MODULUS ** self.order
        return sum(count * log((self.counts.get(gram, 0) + self.alpha) / denominator)
                   for gram, count in grams.items()) / size
