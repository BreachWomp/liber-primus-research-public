"""Constant-aware family screening; full scores are hashed, retained rows stored."""
import hashlib
import time
import numpy as np
from liberprimus.bilinear_feedback import affine_chain as zero_chain
from liberprimus.affine_feedback import affine_chain


def period_scores(values, m, unigram, deadline):
    # Output order is a,b,c. For b!=1, P=a*(base1+power*t)+d,
    # d=c/(1-b). This is a reparameterization, NOT a score invariance.
    symbols29 = np.arange(29)
    units = np.arange(1, 29)
    weights = unigram[(symbols29[:, None, None]*units[None, :, None]+symbols29[None, None, :]) % 29]
    weights = weights.reshape(29, 28*29)
    offset = (np.arange(len(values)) % m)[None, :]*841+symbols29[:, None]*29
    scores = np.empty((28, 28, 29))
    for b in range(1, 29):
        if time.perf_counter() > deadline:
            raise TimeoutError('Affine screening deadline')
        base, power = map(np.array, zero_chain(values, m, 1, b))
        if b == 1:
            # c/a spans the same 29 values, but c must be restored per a.
            block = np.arange(len(values)) // m
            scale_weights = unigram[(symbols29[:, None]*units[None, :]) % 29]
            for normalized_c in range(29):
                symbols = (base[None, :]+symbols29[:, None]+normalized_c*block[None, :]) % 29
                hist = np.bincount((offset+symbols).ravel(), minlength=m*841).reshape(m, 29, 29)
                scores[np.arange(28), 0, units*normalized_c % 29] = (hist@scale_weights).max(axis=1).sum(axis=0)
        else:
            symbols = (base[None, :]+symbols29[:, None]*power[None, :]) % 29
            hist = np.bincount((offset+symbols).ravel(), minlength=m*841).reshape(m, 29, 29)
            by_shift = (hist@weights).max(axis=1).sum(axis=0).reshape(28, 29)
            scores[:, b-1, :] = by_shift[:, symbols29*pow(1-b, -1, 29) % 29]
    return scores


def screen(values, unigram, deadline, probe=None):
    selected, audit = [], []
    for m in range(4, 33):
        scores = period_scores(values, m, unigram, deadline)
        rounded = np.round(scores.ravel(), 9)
        order = np.argsort(-rounded, kind='stable')
        rows = []
        for rank, flat in enumerate(order[:8], 1):
            a, b, c = np.unravel_index(flat, scores.shape)
            rows.append({'period':m, 'cipher_sign':int(a)+1, 'feedback_sign':int(b)+1,
                'constant':int(c), 'unigram_max_total':float(scores[a,b,c]),
                'selection_score':float(rounded[flat]), 'rank':rank})
        record = {'period':m, 'families':22736,
            'score_sha256':hashlib.sha256(scores.astype('<f8').tobytes()).hexdigest(),
            'rounded_score_sha256':hashlib.sha256(rounded.astype('<f8').tobytes()).hexdigest()}
        if probe and probe[0] == m:
            _, a, b, c = probe
            flat = np.ravel_multi_index((a-1,b-1,c), scores.shape)
            record['probe'] = {'family':probe, 'rank':int(np.flatnonzero(order == flat)[0])+1,
                'score':float(scores[a-1,b-1,c])}
        selected.extend(rows);audit.append(record)
    return selected, audit


def factor_tables(values, period, cs, ks, constant, lookup):
    base, coeff = map(np.array, affine_chain(values, period, cs, ks, constant))
    grids = [np.arange(29).reshape(s) for s in ((29,1,1),(1,29,1),(1,1,29))]
    factors = np.zeros((period,29,29,29))
    for end in range(len(values)):
        start = max(0,end-2)
        symbols = [(coeff[j]*grids[j-start]+base[j]) % 29 for j in range(start,end+1)]
        factors[start % period] += lookup[end-start][tuple(symbols)]
    return factors, 0.0, list(range(len(values))), base, coeff
