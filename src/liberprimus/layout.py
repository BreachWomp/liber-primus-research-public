"""Explicit, reversible permutations of ragged rune rows; no padding or glyph changes."""
from .alphabet import RUNES

def rune_rows(text):
    rows=[]
    for line in text.splitlines():
        unknown=[c for c in line if 0x16a0<=ord(c)<=0x16ff and c not in RUNES and c not in '᛫᛬᛭']
        if unknown:raise ValueError('Unreviewed rune glyph: '+repr(unknown))
        row=''.join(c for c in line if c in RUNES)
        if row:rows.append(row)
    return rows

def row_permutations(lengths):
    if not lengths or any(n<=0 for n in lengths):raise ValueError('Need nonempty positive row lengths')
    rows=[];offset=0
    for n in lengths:rows.append(list(range(offset,offset+n)));offset+=n
    out=[];seen=set()
    for bottom in (False,True):
        sequence=list(reversed(rows)) if bottom else rows
        for mode in ('left','right','snake_left','snake_right'):
            order=[]
            for j,row in enumerate(sequence):
                reverse=mode=='right' or (mode=='snake_left' and j%2==1) or (mode=='snake_right' and j%2==0)
                order.extend(reversed(row) if reverse else row)
            if tuple(order) in seen:continue
            seen.add(tuple(order));out.append({'name':('bottom_' if bottom else 'top_')+mode,'indices':order})
    return out

def permute(values,indices):
    if sorted(indices)!=list(range(len(values))):raise ValueError('Not a bijective permutation')
    return [values[i] for i in indices]

def scatter(values,indices):
    if sorted(indices)!=list(range(len(values))):raise ValueError('Not a bijective permutation')
    out=[None]*len(values)
    for j,i in enumerate(indices):out[i]=values[j]
    return out
