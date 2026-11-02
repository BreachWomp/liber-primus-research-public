"""Plaintext feedback over Z/29Z; no omitted symbols or implicit resets."""


def validate(period, cipher_sign, feedback):
    if period < 1 or cipher_sign not in (-1, 1) or feedback not in range(1, 29):
        raise ValueError('Invalid feedback family')


def affine_chain(cipher, period, cipher_sign, feedback):
    """P[i] = base[i] + coefficient[i] * P[i % period] (mod 29)."""
    validate(period, cipher_sign, feedback)
    if len(cipher) < period:
        raise ValueError('Cipher shorter than prefix')
    base = [0] * period
    coefficient = [1] * period
    for i in range(period, len(cipher)):
        base.append((cipher_sign * cipher[i] + feedback * base[i-period]) % 29)
        coefficient.append(feedback * coefficient[i-period] % 29)
    return base, coefficient


def decode_prefix(cipher, prefix, cipher_sign, feedback):
    validate(len(prefix), cipher_sign, feedback)
    if len(cipher) < len(prefix):
        raise ValueError('Cipher shorter than prefix')
    plain = list(prefix)
    for i in range(len(prefix), len(cipher)):
        plain.append((cipher_sign*cipher[i] + feedback*plain[i-len(prefix)]) % 29)
    inverse = pow(feedback, -1, 29)
    key = [(p-cipher_sign*c)*inverse % 29 for p, c in zip(prefix, cipher)]
    return plain, key


def encrypt(plain, key, cipher_sign, feedback):
    validate(len(key), cipher_sign, feedback)
    return [cipher_sign*(p-feedback*(key[i] if i < len(key) else plain[i-len(key)])) % 29
            for i, p in enumerate(plain)]
