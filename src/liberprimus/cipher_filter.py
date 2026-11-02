"""Invertible two-lag ciphertext feedback; the first two cipher runes are IV."""
from .alphabet import validate_indices


def coefficients(a,b,c,d):
    if any(type(x) is not int or not 0<=x<29 for x in (a,b,c,d)) or a==0:
        raise ValueError('Coefficients in Z29 and nonzero a required')


def decrypt_suffix(cipher,a,b,c,d):
    coefficients(a,b,c,d);cipher=validate_indices(cipher)
    if len(cipher)<3:raise ValueError('Two IV runes and nonempty payload required')
    return [(a*cipher[i]+b*cipher[i-1]+c*cipher[i-2]+d)%29 for i in range(2,len(cipher))]


def encrypt_suffix(plain,a,b,c,d,iv):
    coefficients(a,b,c,d);plain=validate_indices(plain);out=validate_indices(iv)
    if len(out)!=2:raise ValueError('Two IV runes required')
    inverse=pow(a,-1,29)
    for p in plain:out.append(inverse*(p-b*out[-1]-c*out[-2]-d)%29)
    return out
