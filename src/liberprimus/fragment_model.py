"""Fixed edge fallback diagnostic, preserving all interior word scores."""
from .alphabet import validate_indices
from .boundaries import segments


def fragment_score(model, values, ends, *, edge_backoff=False):
    values = validate_indices(values)
    if not values:
        raise ValueError('Empty sequence')
    words = segments(values, ends)
    total = 0.0
    for i, word in enumerate(words):
        if edge_backoff and i in (0, len(words)-1):
            total += len(word)*model.character_model.score(word)
        else:
            total += model.logword(tuple(word))
    return total/len(values)


def clip_edges(values, ends, left, right):
    """Remove positive outer fragments, never an entire edge segment."""
    words = segments(values, ends)
    if len(words)<2 or not 0<left<len(words[0]) or not 0<right<len(words[-1]):
        raise ValueError('Clips must leave both distinct edge segments nonempty')
    return values[left:len(values)-right], [e-left for e in ends[:-1]]+[len(values)-left-right]
