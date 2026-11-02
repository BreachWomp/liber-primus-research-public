"""Delayed affine plaintext feedback in Z/29Z, including the initial queue."""
from .bilinear_feedback import validate


def affine_chain(cipher, period, a, b, c):
    validate(period, a, b)
    if c not in range(29) or len(cipher) < period:
        raise ValueError('Invalid constant or short ciphertext')
    base, coefficient = [0] * period, [1] * period
    for i in range(period, len(cipher)):
        base.append((a*cipher[i] + b*base[i-period] + c) % 29)
        coefficient.append(b*coefficient[i-period] % 29)
    return base, coefficient


def decode_prefix(cipher, prefix, a, b, c):
    base, coefficient = affine_chain(cipher, len(prefix), a, b, c)
    plain = [(base[i]+coefficient[i]*prefix[i % len(prefix)]) % 29 for i in range(len(cipher))]
    key = [(p-a*x-c)*pow(b, -1, 29) % 29 for p, x in zip(prefix, cipher)]
    return plain, key


def encrypt(plain, key, a, b, c):
    validate(len(key), a, b)
    if c not in range(29):
        raise ValueError('Invalid constant')
    return [((p-b*(key[i] if i < len(key) else plain[i-len(key)])-c)*pow(a, -1, 29)) % 29
            for i, p in enumerate(plain)]


def reduced_symbol(base_one, power, block, prefix_scaled, a, b, c):
    """Equivalent family parameterization; prefix_scaled runs over all 29 values."""
    if b == 1:
        return (a*(base_one+prefix_scaled)+block*c) % 29
    shift = c*pow(1-b, -1, 29) % 29
    return (a*(base_one+power*prefix_scaled)+shift) % 29
