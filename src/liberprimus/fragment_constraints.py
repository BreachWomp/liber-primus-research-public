"""Exact phase-chain optimization from ciphertext-only cursor bounds."""
import time


def build_chains(values, page_spans, ranges):
    """Connect successive selected F-free fragments within each source page."""
    if not ranges or len(ranges) > 12:
        raise ValueError('Require 1..12 fragments')
    assigned = set()
    chains = []
    for page in page_spans:
        indices = sorted((i for i, (a, b) in enumerate(ranges)
                          if page['start'] <= a < b <= page['end']), key=lambda i: ranges[i][0])
        if not indices:
            continue
        links = []
        for i in indices:
            a, b = ranges[i]
            if i in assigned or a < 0 or b > len(values) or 0 in values[a:b]:
                raise ValueError('Invalid, overlapping-page, or non-F-free fragment')
            assigned.add(i)
        for left, right in zip(indices, indices[1:]):
            a, end = ranges[left]
            b = ranges[right][0]
            if end > b:
                raise ValueError('Overlapping fragments')
            links.append({'left': left, 'right': right, 'distance': b-a,
                          'f_count': values[a:b].count(0)})
        chains.append({'indices': indices, 'links': links})
    if assigned != set(range(len(ranges))):
        raise ValueError('Every fragment must belong to exactly one page')
    return chains


def feasible(phases, chains, period):
    return all(any((phases[e['right']]-phases[e['left']]-e['distance']+s) % period == 0
                   for s in range(min(e['f_count']+1, period)))
               for chain in chains for e in chain['links'])


def seed_phases(chains, period, start, rng):
    phases = [0] * sum(len(c['indices']) for c in chains)
    for chain in chains:
        phases[chain['indices'][0]] = 0 if start < 3 else rng.randrange(period)
        for e in chain['links']:
            count = e['f_count']
            skipped = (0, count, count//2)[start] if start < 3 else rng.randrange(count+1)
            phases[e['right']] = (phases[e['left']] + e['distance'] - skipped) % period
    return phases


def maximize(costs, chains, deadline):
    """Maximum over all admissible fragment phases, with deterministic ties."""
    if not costs or not 1 <= len(costs[0]) <= 32:
        raise ValueError('Require nonempty costs and period <=32')
    period = len(costs[0])
    if len(costs) > 12 or any(len(row) != period for row in costs):
        raise ValueError('Invalid cost dimensions')
    phases = [0] * len(costs)
    total = 0.
    for chain in chains:
        first = chain['indices'][0]
        scores = list(costs[first])
        backs = []
        for e in chain['links']:
            if time.perf_counter() > deadline:
                raise TimeoutError('Fragment-chain deadline')
            following = [-float('inf')] * period
            back = [-1] * period
            shifts = sorted({(e['distance']-s) % period for s in range(min(e['f_count']+1, period))})
            for previous, score in enumerate(scores):
                for shift in shifts:
                    phase = (previous+shift) % period
                    value = score + costs[e['right']][phase]
                    if value > following[phase]:
                        following[phase] = value
                        back[phase] = previous
            scores = following
            backs.append(back)
        phase = max(range(period), key=scores.__getitem__)
        total += scores[phase]
        phases[chain['indices'][-1]] = phase
        for e, back in reversed(list(zip(chain['links'], backs))):
            phase = back[phase]
            phases[e['left']] = phase
    if time.perf_counter() > deadline:
        raise TimeoutError('Fragment-chain deadline')
    return total, phases
