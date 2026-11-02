"""Exact modular transforms. Default direction is decryption, P=C-K mod 29.

An interrupter is an explicitly selected zero-based rune position: its value
is copied unchanged and it consumes neither a key item nor an autokey item.
No rune, including F, is implicitly an interrupter. Positions are in the
sequence passed to the function, excluding formatting. Dropped nulls should
be removed explicitly by a separate, recorded preprocessing hypothesis.
"""

from collections.abc import Iterable
from itertools import cycle
from .alphabet import MODULUS, validate_indices


def _integer(value: int, name: str) -> int:
    if type(value) is not int:
        raise ValueError(f"{name} must be an integer")
    return value


def _skips(skip_positions: Iterable[int], length: int) -> set[int]:
    positions = list(skip_positions)
    if any(type(i) is not int or not 0 <= i < length for i in positions):
        raise ValueError("skip positions must be zero-based indices within the input")
    if len(set(positions)) != len(positions):
        raise ValueError("duplicate skip positions")
    return set(positions)


def atbash(values: Iterable[int]) -> list[int]:
    return [MODULUS - 1 - value for value in validate_indices(values)]


def affine(values: Iterable[int], a: int, b: int, *, decrypt: bool = True) -> list[int]:
    """Encryption C=aP+b; a must be invertible modulo 29."""
    a, b = _integer(a, "a") % MODULUS, _integer(b, "b") % MODULUS
    if a == 0:
        raise ValueError("a must be invertible modulo 29")
    data = validate_indices(values)
    if decrypt:
        inverse = pow(a, -1, MODULUS)
        return [(inverse * (value - b)) % MODULUS for value in data]
    return [(a * value + b) % MODULUS for value in data]


def substitution(values: Iterable[int], mapping: Iterable[int], *, decrypt: bool = True) -> list[int]:
    """mapping[p] is ciphertext. A full permutation is mandatory."""
    key = validate_indices(mapping)
    if sorted(key) != list(range(MODULUS)):
        raise ValueError("substitution key must be a permutation of 0..28")
    if decrypt:
        inverse = [0] * MODULUS
        for plaintext, ciphertext in enumerate(key):
            inverse[ciphertext] = plaintext
        key = inverse
    return [key[value] for value in validate_indices(values)]


def keystream(values: Iterable[int], key: Iterable[int], *, decrypt: bool = True,
              skip_positions: Iterable[int] = ()) -> list[int]:
    """Consume exactly one integer key item per active rune; reduce key mod 29.

    Infinite generators are permitted; only needed items are consumed.
    Exhaustion is an error; excess key material is intentionally not consumed.
    """
    data = validate_indices(values)
    skips, stream, result = _skips(skip_positions, len(data)), iter(key), []
    direction = -1 if decrypt else 1
    for position, value in enumerate(data):
        if position in skips:
            result.append(value)
            continue
        try:
            shift = _integer(next(stream), "keystream item")
        except StopIteration as exc:
            raise ValueError("keystream exhausted before all active runes") from exc
        result.append((value + direction * shift) % MODULUS)
    return result


def vigenere(values: Iterable[int], key: Iterable[int], *, decrypt: bool = True,
             skip_positions: Iterable[int] = ()) -> list[int]:
    material = validate_indices(key)
    if not material:
        raise ValueError("Vigenere key cannot be empty")
    return keystream(values, cycle(material), decrypt=decrypt, skip_positions=skip_positions)


def autokey(values: Iterable[int], key: Iterable[int], *, decrypt: bool = True,
            feedback: str = "plaintext", skip_positions: Iterable[int] = ()) -> list[int]:
    """Append recovered/original plaintext, or ciphertext, after the seed key."""
    if feedback not in {"plaintext", "ciphertext"}:
        raise ValueError("feedback must be plaintext or ciphertext")
    data, stream = validate_indices(values), validate_indices(key)
    if not stream:
        raise ValueError("autokey seed cannot be empty")
    skips, result, cursor = _skips(skip_positions, len(data)), [], 0
    direction = -1 if decrypt else 1
    for position, value in enumerate(data):
        if position in skips:
            result.append(value)
            continue
        output = (value + direction * stream[cursor]) % MODULUS
        plain, cipher = (output, value) if decrypt else (value, output)
        stream.append(plain if feedback == "plaintext" else cipher)
        result.append(output)
        cursor += 1
    return result


def primes() -> Iterable[int]:
    """Incremental trial-division prime generator, suitable for page-sized keys."""
    found, candidate = [], 2
    while True:
        is_prime = True
        for prime in found:
            if prime * prime > candidate:
                break
            if candidate % prime == 0:
                is_prime = False
                break
        if is_prime:
            found.append(candidate)
            yield candidate
        candidate += 1 if candidate == 2 else 2


def prime_totients() -> Iterable[int]:
    """phi(p)=p-1 for consecutive primes, starting with p=2."""
    for prime in primes():
        yield prime - 1
