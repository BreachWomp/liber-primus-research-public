"""Reversible affine plaintext feedback with an explicit positive delay."""
def decrypt(cipher, a, b, initial):
    if not initial or not 1 <= a < 29 or not 1 <= b < 29:
        raise ValueError('Nonzero coefficients and a nonempty seed required')
    state = list(initial); delay = len(state); out = []
    for i,c in enumerate(cipher):
        p = (a*c+b*state[i % delay]) % 29
        out.append(p); state[i % delay] = p
    return out

def encrypt(plain, a, b, initial):
    if not initial or not 1 <= a < 29 or not 1 <= b < 29:
        raise ValueError('Nonzero coefficients and a nonempty seed required')
    state = list(initial); delay = len(state); inverse = pow(a,-1,29); out = []
    for i,p in enumerate(plain):
        out.append((inverse*(p-b*state[i % delay])) % 29)
        state[i % delay] = p
    return out

def basis(cipher, b, delay):
    if delay < 1 or len(cipher) < delay:
        raise ValueError('Need at least delay ciphertext symbols')
    base = [0]*len(cipher); powers = [1]*len(cipher)
    for i in range(delay,len(cipher)):
        base[i] = (cipher[i]+b*base[i-delay]) % 29
        powers[i] = b*powers[i-delay] % 29
    return base,powers
