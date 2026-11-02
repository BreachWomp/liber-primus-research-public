"""Invertible progressive substitution over the 29-rune field."""
from .alphabet import validate_indices


def coefficients(a,b,c,d):
    if type(a) is not int or not 1<=a<29:raise ValueError('Nonzero multiplier required')
    if any(type(x) is not int or not 0<=x<29 for x in (b,c,d)):
        raise ValueError('Coefficients must be residues')


def decrypt(values,a,b,c,d):
    coefficients(a,b,c,d)
    return [(a*x+b*i*i+c*i+d)%29 for i,x in enumerate(validate_indices(values))]


def encrypt(values,a,b,c,d):
    coefficients(a,b,c,d);inv=pow(a,-1,29)
    return [(inv*(x-b*i*i-c*i-d))%29 for i,x in enumerate(validate_indices(values))]
