"""Compare preserved alphanumeric grids without choosing ambiguous glyphs."""
import re
import time
from attack_support import load,ROOT,digest
from registry import registered

ALPHABET='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwx'

def value(token):
    if len(token)!=2 or any(c not in ALPHABET for c in token):raise ValueError('Invalid base60 pair')
    return 60*ALPHABET.index(token[0])+ALPHABET.index(token[1])

def token_rows(text,hyphens=False):
    rows=[]
    for line in text.splitlines():
        clean=line.strip().rstrip('/')
        cells=clean.split('-') if hyphens else clean.split()
        if len(cells)==8 and all(re.fullmatch(r'[0-4][0-9A-Za-x]',c) for c in cells):rows.append(cells)
    return rows

def run():
    tick=time.perf_counter();pages={p['id']:p for p in load('transcriptions/pages.json')}
    master=(ROOT/'data/raw/iddqd/liber-primus__transcription--master/liber-primus__transcription--master.txt').read_text(encoding='utf-8').split('\n\n',1)[1].split('%')
    mirror=(ROOT/'data/raw/scream314/liber_primus.md').read_text(encoding='utf-8');records=[];mismatches=[];decimal_errors=[]
    assert [value(x) for x in ['00','0x','10','4F']]==[0,59,60,255]
    for number,expected in [(49,10),(50,13),(51,9)]:
        ident=f'LP2-{number:02}';heading=f'## {number+17}.jpg - {number}.jpg'
        section=mirror.split(heading,1)[1].split('\n## ',1)[0]
        source_block=section.split('base60',1)[1].split('dec',1)[0]
        grids={'relikd_canonical':token_rows(pages[ident]['text_with_layout']),
               'iddqd':token_rows(master[15+number],hyphens=True),'scream314':token_rows(source_block)}
        assert all(len(rows)==expected for rows in grids.values())
        numbers=[list(map(int,line.split())) for line in section.split('dec',1)[1].splitlines() if re.fullmatch(r'\s*(?:\d+\s+){7}\d+\s*',line)]
        assert len(numbers)==expected
        decoded={name:[[value(c) for c in row] for row in grid] for name,grid in grids.items()}
        assert all(0<=v<=255 for grid in decoded.values() for row in grid for v in row)
        for i in range(expected):
            for j in range(8):
                cells={name:grid[i][j] for name,grid in grids.items()}
                if len(set(cells.values()))>1:mismatches.append({'page_id':ident,'row_1based':i+1,'column_1based':j+1,'tokens':cells,'values':{name:decoded[name][i][j] for name in grids},'resolution':'unresolved; preserve alternatives, image-level glyph audit required'})
                if decoded['scream314'][i][j]!=numbers[i][j]:decimal_errors.append({'page_id':ident,'row_1based':i+1,'column_1based':j+1,'token':grids['scream314'][i][j],'computed':decoded['scream314'][i][j],'published_decimal':numbers[i][j]})
        records.append({'page_id':ident,'rows':expected,'columns':8,'tokens_by_source':grids,'values_by_source':decoded,'published_decimal':numbers})
    result={'experiment':'E022-numeric-source-audit','status':'completed','alphabet':ALPHABET,'total_cells_per_source':256,
        'pages':records,'source_disagreements':mismatches,'published_decimal_inconsistencies':decimal_errors,
        'positive_controls':['00=0','0x=59','10=60','4F=255'],'null_model':'Not applicable: exact source comparison and deterministic arithmetic, no significance or cipher claim.',
        'limits':['Base60 interpretation is prior art in pinned source, not new decryption.','All256values fit bytes, but this does not establish a cipher, file type, or key.','No uncertain glyph normalized and no existing canonical data changed.','No full independent glyph-by-glyph image transcription performed.'],
        'wall_seconds':time.perf_counter()-tick,'new_decryptions':[]}
    assert result['wall_seconds']<30
    return result

if __name__=='__main__':
    deps=['experiments/numeric_source_audit.py','experiments/numeric_audit_plan.json','experiments/attack_support.py',
        'src/liberprimus/alphabet.py','src/liberprimus/ciphers.py','src/liberprimus/decoding.py','transcriptions/pages.json',
        'data/raw/iddqd/liber-primus__transcription--master/liber-primus__transcription--master.txt',
        'data/raw/scream314/liber_primus.md','data/raw/relikd/pages/p40-53.txt','sources/manifest.json','sources/layout_images_manifest.json']
    registered('E022-numeric-source-audit',{'seconds':30,'alphabet':ALPHABET,'seed':None},deps,run)
