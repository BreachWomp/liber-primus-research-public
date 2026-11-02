"""Reversible first differences followed by a rune permutation, with explicit IV."""
from .alphabet import validate_indices


def checked_iv(iv):
    if type(iv) is not int or not 0<=iv<29:raise ValueError('IV must be a rune index')
    return iv


def checked_mapping(mapping):
    mapping=validate_indices(mapping)
    if sorted(mapping)!=list(range(29)):raise ValueError('A permutation of0..28 is required')
    return mapping


def differences(cipher,iv=0):
    values=validate_indices(cipher);previous=checked_iv(iv);out=[]
    for value in values:out.append((value-previous)%29);previous=value
    return out


def integrate(values,iv=0):
    values=validate_indices(values);previous=checked_iv(iv);out=[]
    for value in values:previous=(previous+value)%29;out.append(previous)
    return out


def decode(cipher,mapping,iv=0):
    mapping=checked_mapping(mapping)
    return [mapping[x] for x in differences(cipher,iv)]


def encode(plain,mapping,iv=0):
    mapping=checked_mapping(mapping);inverse=[mapping.index(i) for i in range(29)]
    return integrate([inverse[x] for x in validate_indices(plain)],iv)
