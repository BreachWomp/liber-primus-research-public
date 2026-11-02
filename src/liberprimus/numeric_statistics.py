"""Prespecified diagnostics for a source-aligned 32 by 8 byte table."""
from collections import Counter
import math

NAMES = ('collision_deviation', 'adjacent_repeat_deviation', 'max_bit_imbalance', 'column_sum_dispersion')

def statistics(values):
    if len(values) != 256 or any(not isinstance(x,int) or not 0 <= x <= 255 for x in values):
        raise ValueError('Expected exactly 256 bytes')
    counts = Counter(values)
    pairs = sum(n*(n-1)//2 for n in counts.values())
    adjacent = sum(a == b for a,b in zip(values, values[1:]))
    bit_counts = [sum((v >> bit) & 1 for v in values) for bit in range(8)]
    columns = [sum(values[c::8]) for c in range(8)]
    total = sum(columns)
    return dict(zip(NAMES, [abs(2*pairs-255), abs(256*adjacent-255),
        max(abs(2*n-256) for n in bit_counts), sum((8*n-total)**2 for n in columns)]))

def descriptive(values):
    counts = Counter(values)
    return {'length':len(values),'distinct_values':len(counts),
        'equal_unordered_pairs':sum(n*(n-1)//2 for n in counts.values()),
        'adjacent_equal_pairs':sum(a == b for a,b in zip(values,values[1:])),
        'empirical_entropy_bits':-sum((n/len(values))*math.log2(n/len(values)) for n in counts.values()),
        'entropy_note':'Finite-sample descriptive plug-in estimate; not a test of cryptographic randomness.',
        'bit_one_counts_lsb_first':[sum((v>>b)&1 for v in values) for b in range(8)],
        'column_sums':[sum(values[c::8]) for c in range(8)]}
