"""Exact 29^2 prefix enumeration within 128 unigram-screened affine families."""
import hashlib
import time
import numpy as np
from affine_feedback_factors import period_scores
from liberprimus.affine_feedback import affine_chain,decode_prefix
from attack_support import to_runes,top_unique
from liberprimus.alphabet import transliterate

PREFIXES=np.indices((29,29),dtype=np.int16).reshape(2,-1).T


def prefix_scores(cipher,a,b,c,lookup,deadline):
    base,power=affine_chain(cipher,2,a,b,c)
    total=np.zeros(29**2);history=[]
    for i in range(len(cipher)):
        if i%22==0 and time.perf_counter()>deadline:raise TimeoutError('Exact prefix deadline')
        symbols=(base[i]+power[i]*PREFIXES[:,i%2])%29
        history.append(symbols)
        if len(history)>4:history.pop(0)
        total+=lookup[len(history)-1][tuple(history)]
    return total/len(cipher)


def search(cipher,lookup,deadline,probe=None):
    scores=period_scores(cipher,2,lookup[0],deadline)
    order=np.argsort(-np.round(scores.ravel(),9),kind='stable')
    audit={'families':22736,'retained':128,
        'score_sha256':hashlib.sha256(scores.astype('<f8').tobytes()).hexdigest()}
    if probe:
        a,b,c=probe;flat=np.ravel_multi_index((a-1,b-1,c),scores.shape)
        audit['probe']={'family':probe,'rank':int(np.flatnonzero(order==flat)[0])+1,'score':float(scores[a-1,b-1,c])}
    families=[];top=[]
    for rank,flat in enumerate(order[:128],1):
        ai,bi,ci=np.unravel_index(flat,scores.shape);a,b,c=int(ai)+1,int(bi)+1,int(ci)
        exact=prefix_scores(cipher,a,b,c,lookup,deadline)
        take=np.argsort(-exact,kind='stable')[:3]
        row={'a':a,'b':b,'c':c,'rank':rank,'unigram_max_total':float(scores[ai,bi,ci]),
            'prefix_scores_sha256':hashlib.sha256(exact.astype('<f8').tobytes()).hexdigest(),'top_prefixes':[]}
        for k in take:
            prefix=PREFIXES[k].tolist();plain,key=decode_prefix(cipher,prefix,a,b,c)
            row['top_prefixes'].append({'prefix':prefix,'score':float(exact[k])})
            top=top_unique(top+[{'score':float(exact[k]),'plaintext_runes':to_runes(plain),
                'transliteration':transliterate(plain),'recipe':{'key_indices':key,'cipher_sign':a,
                'feedback_sign':b,'constant':c,'skip_positions':[],'skip_policy':'none'}}],keep=3)
        families.append(row)
    return {'screen_audit':audit,'families':families,'top':top,
        'prefixes_per_retained_family':29**2,'total_prefix_evaluations':128*29**2}
