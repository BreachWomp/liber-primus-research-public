"""Explicit source-layout parsing; physical line breaks do not split words."""
from .alphabet import RUNES,RUNE_ALIASES

LEXICAL_SEPARATORS=frozenset('-.,:;!?\"\'()[]{}•⁘⁙⁚⁛⁜⁖&$§|_—–…')
LAYOUT_SEPARATORS=frozenset('/%\\')

def parse_layout(text):
    runes=[];offsets=[];events=[];aliases=[];nonrune=[];unknown=[];cuts=set()
    for position,symbol in enumerate(text):
        normalized=RUNE_ALIASES.get(symbol,symbol)
        if normalized in RUNES:
            if symbol!=normalized:aliases.append({'character_offset':position,'source':symbol,'canonical':normalized})
            runes.append(normalized);offsets.append(position)
        elif symbol in LEXICAL_SEPARATORS:
            cuts.add(len(runes));events.append({'character_offset':position,'rune_offset':len(runes),'symbol':symbol,'kind':'lexical_separator'})
        elif symbol.isspace() or symbol in LAYOUT_SEPARATORS:
            continue
        elif symbol.isascii() and symbol.isalnum():
            cuts.add(len(runes));nonrune.append({'character_offset':position,'symbol':symbol,'rune_offset':len(runes)})
        else:unknown.append({'character_offset':position,'symbol':symbol})
    if unknown:raise ValueError(f'Unreviewed layout symbols: {unknown[:10]}')
    ends=sorted(p for p in cuts if 0<p<len(runes))+([len(runes)] if runes else [])
    return {'runes':''.join(runes),'rune_character_offsets':offsets,'segment_ends':ends,
            'events':events,'aliases':aliases,'nonrune_characters':nonrune,'raw_text':text}

def segments(values,ends):
    if not values:
        if ends:raise ValueError('Boundaries on empty sequence')
        return []
    if not ends or ends[-1]!=len(values) or any(type(x) is not int for x in ends):
        raise ValueError('Segment endpoints must end at sequence length')
    start=0;out=[]
    for end in ends:
        if not start<end<=len(values):raise ValueError('Endpoints must strictly increase')
        out.append(values[start:end]);start=end
    return out
