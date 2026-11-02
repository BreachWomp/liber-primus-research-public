"""Independent language data from the pinned Emerson volume, excluding essay II."""
from collections import Counter
import hashlib
import re
import unicodedata
from attack_support import ROOT,load
from liberprimus.alphabet import latin_to_indices
from liberprimus.decoding import BackoffModel


def paragraphs():
    raw=(ROOT/"data/raw/gutenberg/pg2944.txt").read_bytes()
    if hashlib.sha256(raw).hexdigest()!=load("sources/emerson_manifest.json")["sha256"]:
        raise ValueError("external language source changed")
    text=raw.decode("utf-8-sig")
    starts=list(re.finditer(r"(?m)^([IVX]+)\.\r?\n([A-Z][A-Z -]+)\r?$",text))
    end=text.index("*** END OF THE PROJECT GUTENBERG EBOOK")
    if len(starts)!=12:raise ValueError("expected12chapters")
    sequences=[];word_counts=Counter();sections=[];non_ascii=Counter()
    for i,match in enumerate(starts):
        finish=starts[i+1].start() if i+1<len(starts) else end
        if match[1]=="II":continue
        body=text[match.end():finish]
        non_ascii.update(c for c in body if c.isalpha() and not c.isascii())
        normalized=body.replace("æ","ae").replace("Æ","AE").replace("œ","oe").replace("Œ","OE")
        normalized=unicodedata.normalize("NFKD",normalized)
        normalized="".join(c for c in normalized if not unicodedata.combining(c))
        n_before=sum(map(len,sequences))
        for paragraph in re.split(r"\r?\n\s*\r?\n",normalized):
            sequence=[]
            for word in re.findall(r"[A-Za-z]+",paragraph):
                word=word.upper().replace("QU","CW").replace("Q","C")
                runes=latin_to_indices(word);sequence+=runes;word_counts[tuple(runes)]+=1
            if sequence:sequences.append(sequence)
        sections.append({"roman":match[1],"title":match[2],"source_character_range":[match.end(),finish],
                         "runes":sum(map(len,sequences))-n_before})
    return sequences,word_counts,{"source_sha256":hashlib.sha256(raw).hexdigest(),"excluded_chapter":"II.Self-Reliance",
        "sections":sections,"paragraphs":len(sequences),"runes":sum(map(len,sequences)),"word_tokens":sum(word_counts.values()),
        "distinct_rune_words":len(word_counts),"non_ascii_letters":dict(non_ascii),
        "normalization":"Explicit ae/oe ligature expansion; NFKD and combining-mark removal; ASCII words; QU->CW, remainingQ->C; greedyGP within words; no ngrams across paragraphs.",
        "training_data":"No Liber Primus plaintext or ciphertext, and no Self-Reliance text is used."}


def external_model(order=3):
    sequences,_,_=paragraphs()
    return BackoffModel(sequences,order=order,alpha=0.5,strength=5.0)
