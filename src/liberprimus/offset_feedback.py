"""Affine plaintext feedback with a constant term over Z29."""
from .alphabet import validate_indices


def validate(a,b,d,key):
    if any(type(x) is not int or not 0<=x<29 for x in (a,b,d,key)) or a==0 or b==0:
        raise ValueError('Nonzero a,b and d,key in Z29 required')


def decrypt(cipher,a,b,d,key):
    validate(a,b,d,key);cipher=validate_indices(cipher);out=[]
    previous=key
    for symbol in cipher:
        previous=(a*symbol+b*previous+d)%29;out.append(previous)
    return out


def encrypt(plain,a,b,d,key):
    validate(a,b,d,key);plain=validate_indices(plain);out=[]
    inverse=pow(a,-1,29);previous=key
    for symbol in plain:
        out.append(inverse*(symbol-b*previous-d)%29);previous=symbol
    return out


def basis(cipher,b):
    cipher=validate_indices(cipher)
    if not cipher or type(b) is not int or not 1<=b<29:raise ValueError('Nonempty cipher and nonzero b required')
    base=[0]*len(cipher);power=[1]*len(cipher);offset=[0]*len(cipher)
    for i in range(1,len(cipher)):
        base[i]=(cipher[i]+b*base[i-1])%29
        power[i]=b*power[i-1]%29
        offset[i]=(1+b*offset[i-1])%29
    return base,power,offset
