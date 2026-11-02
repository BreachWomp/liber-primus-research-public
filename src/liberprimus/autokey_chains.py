"""Scalar plaintext-autokey residue chains, with no omitted ciphertext symbols."""


def decode_prefix(cipher, prefix, cipher_sign, feedback_sign):
    if not prefix or len(prefix) > len(cipher):
        raise ValueError('Invalid prefix length')
    if cipher_sign not in (-1, 1) or feedback_sign not in (-1, 1):
        raise ValueError('Signs must be units +1 or -1')
    if any(not 0 <= x < 29 for x in list(cipher)+list(prefix)):
        raise ValueError('Symbols must be in 0..28')
    plain = list(prefix)
    period = len(prefix)
    for i in range(period, len(cipher)):
        plain.append((cipher_sign*cipher[i]+feedback_sign*plain[i-period]) % 29)
    key = [(feedback_sign*(p-cipher_sign*c)) % 29
           for p,c in zip(prefix,cipher)]
    return plain, key
