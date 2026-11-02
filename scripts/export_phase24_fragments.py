"""Exact, post-hoc illustrations of language-like substrings; not evidence."""
import json
from pathlib import Path
from attack_support import ROOT,load,digest,to_indices
from liberprimus.alphabet import LATIN,render_like


def main():
    complete=load('checkpoints/phase24_unknown_complete.json')
    pages={p['id']:p for p in load('transcriptions/pages.json')}
    result=[]
    for ident,needles in [('LP2-33',['EAT','BEAR','OUTBATH']),('LP2-02',['INTUNE'])]:
        path=next(p for p in complete['outputs'] if load(p)['mode']=='section' and load(p)['section']==ident)
        row=load(path);top=row['result']['top'][0];values=to_indices(top['plaintext_runes'])
        text=''.join(LATIN[v] for v in values);assert text==top['transliteration']
        boundaries={0:0};cursor=0
        for i,v in enumerate(values):cursor+=len(LATIN[v]);boundaries[cursor]=i+1
        fragments=[]
        for needle in needles:
            a=text.index(needle);b=a+len(needle)
            assert a in boundaries and b in boundaries
            fragments.append({'literal':needle,'latin_range_zero_based_half_open':[a,b],
                'rune_range_zero_based_half_open':[boundaries[a],boundaries[b]],
                'unsegmented_context':text[max(0,a-8):min(len(text),b+8)],
                'rune_tokens':[LATIN[v] for v in values[boundaries[a]:boundaries[b]]]})
        result.append({'page':ident,'output':path,'output_sha256':digest(path),'candidate_rank':1,
            'score':top['score'],'recipe':top['recipe'],'transliteration':text,
            'layout':render_like(pages[ident]['text_with_layout'],values,latin=True),
            'source_refs':pages[ident]['source_refs'],'fragments':fragments})
    artifact={'purpose':'Post-hoc illustrative substring selection requested by user, not a new statistical test or decryption claim.',
        'selection':'Top-ranked E067 candidates for LP2-33 and LP2-02; handpicked substrings after inspecting results.',
        'separator_note':'Source layout retained. Latin digraphs are not silently split or corrected. IN TUNE adds a hypothetical internal word boundary inside OINTUNE.',
        'pages':result,'script_sha256':digest('scripts/export_phase24_fragments.py')}
    (ROOT/'results/phase24_language_fragments.json').write_text(json.dumps(artifact,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    text='''# Sprachähnliche Stücke aus Serie 24

Diese Beispiele wurden nach Sichtung der Ausgaben ausgewählt. Sie sind keine
Entschlüsselung und kein zusätzlicher statistischer Nachweis. Es wurde nichts
umgeschrieben oder in vermeintlich korrektes Englisch verbessert.
`•` kennzeichnet einen Worttrenner der Quelltranskription; Zeilen und weitere
Trennzeichen bleiben erhalten. Die Runengrenzen der zitierten Teilstücke sind geprüft.

| Seite | Originalgetreuer Ausgabekontext | Sprachähnlichkeit und Grenze |
|---|---|---|
| LP2-33 | `CH•EAT•RUSA` | `EAT` steht tatsächlich zwischen zwei Quell-Worttrennern. `CHEAT` würde einen Trenner übergehen. |
| LP2-33 | `BEARRO•RBMNW` | `BEAR` ist nur der Anfang von `BEARRO`. |
| LP2-33 | `IU•AUNGASOUT•BATHA•GICT` | `OUT` und `BATH` stehen in längeren Zeichenfolgen; daraus ergibt sich kein Satz. |
| LP2-02 | `EEISUD•OINTUNE•FISENG` | `IN TUNE` ist eine mögliche künstliche Trennung innerhalb von `OINTUNE`; die Quelle hat dort kein Leerzeichen. |

## Vollständige Kandidatenausgaben mit Quelllayout

'''
    for p in result:
        text+=f"### {p['page']}\n\nScore {p['score']:.9f}; m={len(p['recipe']['key_indices'])}, a={p['recipe']['cipher_sign']}, b={p['recipe']['feedback_sign']}.\n\n```text\n{p['layout']}\n```\n\n[Reproduzierbares Ergebnis](../{p['output']}); SHA-256 `{p['output_sha256']}`.\n\n"
    text+='Die unveränderten Schlüsselrezepte, Rune- und Zeichenpositionen sowie Quellreferenzen stehen in [der maschinenlesbaren Beilage](../results/phase24_language_fragments.json).\n'
    (ROOT/'reports/phase24_language_fragments.md').write_text(text,encoding='utf-8')
    print({'pages':[p['page'] for p in result],'fragments':sum(len(p['fragments']) for p in result)})


if __name__=='__main__':main()
