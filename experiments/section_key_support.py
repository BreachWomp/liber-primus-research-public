"""Explicit page spans and endpoint-conditioned per-page nulls."""
import random
import time
from attack_support import load,to_indices


def join_pages(page_ids):
    catalog={p['id']:p for p in load('transcriptions/pages.json')};values=[];spans=[]
    for ident in page_ids:
        p=catalog[ident];piece=to_indices(p['runes']);begin=len(values);values.extend(piece)
        spans.append({'page_id':ident,'start':begin,'end':len(values),'runes':len(piece),
                      'source_refs':p['source_refs'],'zero_rune_page':not bool(piece)})
    return values,spans


def artificial_spans(lengths,chapter):
    cursor=0;rows=[]
    for i,length in enumerate(lengths):
        rows.append({'page_id':f'external-{chapter}-{i:02}','start':cursor,'end':cursor+length,
                     'runes':length,'zero_rune_page':length==0})
        cursor+=length
    return rows


def page_null(values,spans,seed,deadline):
    doublets=lambda x:sum(a==b for a,b in zip(x,x[1:]))
    output=[];records=[]
    for j,span in enumerate(spans):
        if span['start']!=len(output):raise ValueError('Noncontiguous page spans')
        source=values[span['start']:span['end']];target=doublets(source)
        if len(source)<=2:sample=source[:];proposal=0
        else:
            rng=random.Random(seed+j)
            for proposal in range(1,100001):
                if time.perf_counter()>deadline:raise TimeoutError('Per-page null deadline')
                middle=source[1:-1];rng.shuffle(middle);sample=[source[0]]+middle+[source[-1]]
                if doublets(sample)==target:break
            else:raise RuntimeError('Per-page null rejection limit')
        output.extend(sample);records.append({'page_id':span['page_id'],'seed':seed+j,'proposals':proposal})
    if len(output)!=len(values):raise ValueError('Spans do not cover stream')
    return output,records
