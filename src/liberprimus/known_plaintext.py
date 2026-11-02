"""Crib compatibility is an algebraic filter, not evidence that the crib is true."""

from collections.abc import Iterable
from .alphabet import MODULUS, validate_indices


def derive_keystream(ciphertext: Iterable[int], plaintext: Iterable[int]) -> list[int]:
    cipher, plain = validate_indices(ciphertext), validate_indices(plaintext)
    if len(cipher) != len(plain):
        raise ValueError("aligned texts must have the same length")
    return [(c - p) % MODULUS for c, p in zip(cipher, plain)]


def periodic_key_constraints(ciphertext: Iterable[int], crib: Iterable[int], period: int,
                             *, offset: int = 0, phase: int = 0) -> tuple[int | None, ...] | None:
    """Return key residues, or None on contradiction. No interrupted schedule.

    offset is the crib start within ciphertext. At ciphertext index i the key
    slot is (i+phase)%period. Unobserved slots remain None, not guessed zero.
    """
    cipher, plain = validate_indices(ciphertext), validate_indices(crib)
    if type(period) is not int or period < 1:
        raise ValueError("period must be a positive integer")
    if type(offset) is not int or offset < 0 or offset + len(plain) > len(cipher):
        raise ValueError("crib must fit within ciphertext")
    if type(phase) is not int:
        raise ValueError("phase must be an integer")
    key = [None] * period
    for j, p in enumerate(plain):
        slot, residue = (offset + j + phase) % period, (cipher[offset + j] - p) % MODULUS
        if key[slot] is not None and key[slot] != residue:
            return None
        key[slot] = residue
    return tuple(key)


def crib_drag(ciphertext: Iterable[int], crib: Iterable[int], period: int) -> list[dict]:
    cipher, plain = validate_indices(ciphertext), validate_indices(crib)
    if not plain:
        raise ValueError("crib cannot be empty")
    # Validate period even if the crib is too long to have any alignments.
    if type(period) is not int or period < 1:
        raise ValueError("period must be a positive integer")
    result = []
    for offset in range(len(cipher) - len(plain) + 1):
        key = periodic_key_constraints(cipher, plain, period, offset=offset)
        if key is not None:
            result.append({"offset": offset, "key": key})
    return result


def substitution_constraints(ciphertext: Iterable[int], plaintext: Iterable[int]) -> dict[int, int] | None:
    """Partial cipher->plain bijection, or None when equality patterns conflict."""
    cipher, plain = validate_indices(ciphertext), validate_indices(plaintext)
    if len(cipher) != len(plain):
        raise ValueError("aligned texts must have the same length")
    forward, reverse = {}, {}
    for c, p in zip(cipher, plain):
        if (c in forward and forward[c] != p) or (p in reverse and reverse[p] != c):
            return None
        forward[c], reverse[p] = p, c
    return forward
