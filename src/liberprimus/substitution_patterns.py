"""Equality-pattern constraints and deterministic completion of partial bijections."""
from .alphabet import validate_indices


def equality_pattern(values):
    values=validate_indices(values);seen={}
    return tuple(seen.setdefault(v,len(seen)) for v in values)


def complete_mapping(partial,cipher_counts,plain_counts):
    if any(type(k) is not int or type(v) is not int or not 0<=k<29 or not 0<=v<29 for k,v in partial.items()):
        raise ValueError('Mapping symbols must belong to Z29')
    if len(set(partial.values()))!=len(partial):raise ValueError('Non-bijective partial mapping')
    remaining_cipher=sorted((i for i in range(29) if i not in partial),key=lambda i:(-cipher_counts.get(i,0),i))
    used=set(partial.values())
    remaining_plain=sorted((i for i in range(29) if i not in used),key=lambda i:(-plain_counts.get(i,0),i))
    result=dict(partial);result.update(zip(remaining_cipher,remaining_plain))
    return tuple(result[i] for i in range(29))
