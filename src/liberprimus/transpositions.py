"""Reversible permutations. Ragged final rows never introduce padding runes."""

from collections.abc import Iterable
from .alphabet import validate_indices


def _permutation(order: Iterable[int], length: int) -> list[int]:
    result = list(order)
    if any(type(i) is not int for i in result) or sorted(result) != list(range(length)):
        raise ValueError(f"order must be a permutation of 0..{length - 1}")
    return result


def permute(values: Iterable[int], order: Iterable[int], *, inverse: bool = False) -> list[int]:
    """Forward output[i] = input[order[i]], with exact inverse available."""
    data = validate_indices(values)
    permutation = _permutation(order, len(data))
    if not inverse:
        return [data[i] for i in permutation]
    result = [0] * len(data)
    for i, position in enumerate(permutation):
        result[position] = data[i]
    return result


def columnar(values: Iterable[int], order: Iterable[int], *, decrypt: bool = True) -> list[int]:
    """Write plaintext rowwise; read columns in the specified order to encrypt.

    Example: order=(2,0,1) reads column 2, then 0, then 1. This avoids
    ambiguous alphabetical key ordering and defines ragged columns exactly.
    """
    data, columns = validate_indices(values), list(order)
    if not columns:
        raise ValueError("column order cannot be empty")
    columns = _permutation(columns, len(columns))
    permutation = [i for column in columns for i in range(column, len(data), len(columns))]
    return permute(data, permutation, inverse=decrypt)


def rail_fence(values: Iterable[int], rails: int, *, decrypt: bool = True) -> list[int]:
    if type(rails) is not int or rails < 2:
        raise ValueError("rail fence requires at least two rails")
    data = validate_indices(values)
    period = 2 * (rails - 1)
    tracks = [[] for _ in range(rails)]
    for i in range(len(data)):
        position = i % period
        tracks[min(position, period - position)].append(i)
    permutation = [i for track in tracks for i in track]
    return permute(data, permutation, inverse=decrypt)
