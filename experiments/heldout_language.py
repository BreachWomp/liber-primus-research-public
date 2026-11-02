"""Chapter-level training exclusion with explicit apostrophe representations."""
from collections import Counter
import re
import unicodedata
from attack_support import ROOT, load, digest
from liberprimus.alphabet import latin_to_indices
from liberprimus.decoding import BackoffModel
from liberprimus.word_model import WordModel

PLAN='experiments/fragment_benchmark_plan.json'


def tokenize(text):
    normalized=text.replace('æ','ae').replace('Æ','AE').replace('œ','oe').replace('Œ','OE')
    normalized=unicodedata.normalize('NFKD',normalized)
    normalized=''.join(c for c in normalized if not unicodedata.combining(c))
    tokens=list(re.finditer('[A-Za-z]+',normalized))
    words=[];joined=[];joins=[];cursor=0
    for i,m in enumerate(tokens):
        word=tuple(latin_to_indices(m[0].upper().replace('QU','CW').replace('Q','C')))
        if i and normalized[tokens[i-1].end():m.start()] in ("'",'’'):
            joined[-1]+=word;joins.append(cursor)
        else:joined.append(word)
        words.append(word);cursor+=len(word)
    return words,joined,joins


def corpus():
    plan=load(PLAN);path='data/raw/gutenberg/pg2944.txt'
    raw=(ROOT/path).read_bytes();assert len(raw)<=plan['max_source_bytes']
    assert digest(path)==load('sources/emerson_manifest.json')['sha256']
    text=raw.decode('utf-8-sig')
    starts=list(re.finditer(r'(?m)^([IVX]+)\.\r?\n([A-Z][A-Z -]+)\r?$',text))
    assert len(starts)==12
    stop=text.index('*** END OF THE PROJECT GUTENBERG EBOOK')
    rows=[]
    for i,m in enumerate(starts):
        if m[1] in plan['excluded_chapters']:continue
        end=starts[i+1].start() if i+1<len(starts) else stop
        body=text[m.end():end]
        # Spans refer to original decoded source, before normalization.
        boundaries=[0]+[x.end() for x in re.finditer(r'\r?\n\s*\r?\n',body)]+[len(body)]
        for j,(a,b) in enumerate(zip(boundaries,boundaries[1:])):
            words,joined,joins=tokenize(body[a:b])
            if not words:continue
            assert sum(map(len,words))<=plan['max_paragraph_runes']
            rows.append({'chapter':m[1],'paragraph':j,'source_character_range':[m.end()+a,m.end()+b],
                         'words':words,'joined':joined,'apostrophe_offsets':joins})
    return rows


def make_models(rows):
    plan=load(PLAN);train=[r for r in rows if r['chapter'] in plan['training_chapters']]
    assert set(plan['training_chapters']).isdisjoint(plan['heldout_chapters'])
    sequences=[[x for w in r['words'] for x in w] for r in train]
    counts=Counter(w for r in train for w in r['words'])
    joined=Counter(w for r in train for w in r['joined'])
    assert max(len(counts),len(joined))<=plan['max_word_types']
    char=BackoffModel(sequences,**plan['character_model'])
    return (WordModel(counts,char,tau=plan['word_tau']),WordModel(joined,char,tau=plan['word_tau']),
            {'training_chapters':plan['training_chapters'],'heldout_chapters':plan['heldout_chapters'],
             'training_paragraphs':len(train),'training_runes':sum(map(len,sequences)),
             'split_word_tokens':sum(counts.values()),'joined_word_tokens':sum(joined.values()),
             'split_word_types':len(counts),'joined_word_types':len(joined),
             'training_source_ranges':[r['source_character_range'] for r in train],
             'source_sha256':digest('data/raw/gutenberg/pg2944.txt')})
