"""Frozen inputs and compact recording helpers for the second attack phase."""
from collections import Counter
from datetime import datetime,timezone
import hashlib
import itertools
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from liberprimus.alphabet import RUNES,to_indices,to_runes,transliterate,latin_to_indices
from liberprimus.ciphers import primes
from liberprimus.decoding import BackoffModel,replay


def load(path):return json.loads((ROOT/path).read_text(encoding="utf-8"))
def training_fixtures():
    return [f for f in load("known_solutions/fixtures.json") if f.get("eligible_language_training") and f["id"].startswith("LP1-")]
def model_without(exclude=None):
    return BackoffModel([to_indices(f["plaintext_runes"]) for f in training_fixtures() if f["id"]!=exclude],order=3,alpha=0.5,strength=5)
def digest(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def cycle_key(key):
    """Primitive period and lexicographically minimal rotation; all phases searched."""
    key=tuple(key)
    for length in range(1,len(key)+1):
        if len(key)%length==0 and key[:length]*(len(key)//length)==key:
            key=key[:length];break
    return min(key[i:]+key[:i] for i in range(len(key)))


def key_catalog():
    counts=Counter();origins={}
    for fixture in training_fixtures():
        ref=next(ref for ref in fixture["source_refs"] if ref.startswith("relikd:pages/solved_"))
        text=(ROOT/"data/raw/relikd"/ref.split(":",1)[1]).read_text(encoding="utf-8").replace("ᛂ","ᛄ")
        for token in re.findall("["+RUNES+"]+",text):
            if 3<=len(token)<=24:
                value=tuple(to_indices(token));counts[value]+=1;origins.setdefault(value,set()).add(ref)
    for label in ["DIVINITY","FIRFUMFERENFE","CIRCUMFERENCE","LIBERPRIMUS","CICADA","PRIMUS","TOTIENT","PRIMES"]:
        key=tuple(latin_to_indices(label));counts[key]+=1;origins.setdefault(key,set()).add("explicit historical/thematic label: "+label)
    catalog={}
    for key,count in counts.items():
        for reverse in (False,True):
            canonical=cycle_key(key[::-1] if reverse else key)
            row=catalog.setdefault(canonical,{"indices":list(canonical),"evidence":[],"frequency":0})
            row["evidence"].append({"original_runes":to_runes(key),"reversed":reverse,"sources":sorted(origins[key])})
            row["frequency"]+=count
    return [catalog[key] for key in sorted(catalog)]


def stream_catalog(length):
    prime_values=list(itertools.islice(primes(),length))
    phi=list(range(length+1))
    for p in range(2,len(phi)):
        if phi[p]==p:
            for n in range(p,len(phi),p):phi[n]-=phi[n]//p
    return {"prime_totient":[p-1 for p in prime_values],"prime":prime_values,"integer_totient":phi[1:]}


def candidate(decoded,values,key,recipe,repeating):
    actual=replay(values,key,repeating=repeating,start=decoded.start,skip_positions=decoded.skip_positions,
                  cipher_sign=recipe["cipher_sign"],key_sign=recipe["key_sign"])
    if actual!=decoded.plaintext:raise AssertionError("independent forward replay failed")
    return {"score":decoded.score,"plaintext_runes":to_runes(decoded.plaintext),
            "transliteration":transliterate(decoded.plaintext),
            "recipe":{**recipe,"start":decoded.start,"skip_positions":decoded.skip_positions},
            "replay_verified":True,"transitions":decoded.transitions,"max_states":decoded.max_states}


def top_unique(rows,keep=3):
    seen=set();result=[]
    for row in sorted(rows,key=lambda row:row["score"],reverse=True):
        if row["plaintext_runes"] not in seen:
            seen.add(row["plaintext_runes"]);result.append(row)
            if len(result)==keep:break
    return result
