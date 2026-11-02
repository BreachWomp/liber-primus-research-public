"""Fixed paired language diagnostic; never reads unknown-page candidates."""
from collections import defaultdict
import random
import time
from attack_support import load,to_indices
from registry import registered
from heldout_language import corpus,make_models,PLAN
from liberprimus.fragment_model import fragment_score,clip_edges

AUDIT='results/E026-boundary-audit-314198a84563.json'


def flatten(words):
    values=[];ends=[]
    for w in words:values.extend(w);ends.append(len(values))
    return values,ends


def aggregate(rows):
    totals=defaultdict(lambda:{'comparisons':0,'wins':[0,0],'ties':[0,0]})
    for row in rows:
        for m in row['mutations']:
            keys=[(row['origin'],row['condition'],m['region'],'all'),
                  (row['origin'],row['condition'],m['region'],row['chapter'])]
            for key in keys:
                item=totals[key];item['comparisons']+=1
                for k in range(2):
                    delta=row['truth_scores'][k]-m['scores'][k]
                    item['wins'][k]+=int(delta>1e-12);item['ties'][k]+=int(abs(delta)<=1e-12)
    return [{'origin':k[0],'condition':k[1],'region':k[2],'chapter':k[3],**v,
             'win_rates':[n/v['comparisons'] for n in v['wins']]} for k,v in sorted(totals.items())]


def run():
    tick=time.perf_counter();plan=load(PLAN);deadline=tick+plan['seconds'];rng=random.Random(plan['seed'])
    source=corpus();split,joined,metadata=make_models(source);rows=[]
    def evaluate(origin,chapter,anchor,condition,values,ends,other_ends,regions,clip=None):
        if time.perf_counter()>deadline:raise TimeoutError('E030 deadline')
        def scores(v):
            if condition=='apostrophe':return [split.score(v,ends),joined.score(v,other_ends)]
            return [fragment_score(split,v,ends),fragment_score(split,v,ends,edge_backoff=True)]
        truth=scores(values);mutations=[];nulls=[]
        for name,positions in regions.items():
            if not positions:continue
            for _ in range(20):
                pos=rng.choice(positions);new=(values[pos]+rng.randrange(1,29))%29
                changed=values[:];changed[pos]=new
                mutations.append({'region':name,'position':pos,'replacement':new,'scores':scores(changed)})
        for _ in range(19):
            shuffled=values[:];rng.shuffle(shuffled)
            nulls.append({'values':shuffled,'scores':scores(shuffled)})
        rows.append({'origin':origin,'chapter':chapter,'anchor':anchor,'condition':condition,
                     'values':values,'segment_ends':ends,'alternate_ends':other_ends,'clip':clip,
                     'truth_scores':truth,'mutations':mutations,'nulls':nulls,
                     'null_strict_wins':[sum(truth[k]>n['scores'][k]+1e-12 for n in nulls) for k in range(2)]})
    def edge_pair(origin,chapter,anchor,values,ends):
        for condition in ('intact','clipped'):
            left=right=0
            if condition=='clipped':
                if len(ends)<2 or min(ends[0],ends[-1]-ends[-2])<2:continue
                left=rng.randrange(1,ends[0]);right=rng.randrange(1,ends[-1]-ends[-2])
                data,bounds=clip_edges(values,ends,left,right)
            else:data,bounds=values,ends
            edge=list(range(bounds[0]))+list(range(bounds[-2],bounds[-1]))
            inner=list(range(bounds[0],bounds[-2]))
            evaluate(origin,chapter,anchor,condition,data,bounds,bounds,{'edge':edge,'interior':inner},[left,right])
    selection=[]
    for chapter in plan['heldout_chapters']:
        used=0
        for row in [r for r in source if r['chapter']==chapter]:
            words=row['words'];starts=[i for i in range(len(words)-19) if min(len(words[i]),len(words[i+19]))>=2]
            if not starts:continue
            start=rng.choice(starts);values,ends=flatten(words[start:start+20])
            anchor={k:row[k] for k in ('paragraph','source_character_range')};anchor['word_start']=start
            edge_pair('heldout',chapter,anchor,values,ends);used+=1
            if used==24:break
        selection.append({'chapter':chapter,'edge_paragraphs':used})
        used=0
        for row in [r for r in source if r['chapter']==chapter and r['apostrophe_offsets']]:
            values,ends=flatten(row['words']);joined_values,joined_ends=flatten(row['joined']);assert values==joined_values
            near=[];begin=0
            for end in joined_ends:
                if any(begin<a<end for a in row['apostrophe_offsets']):near.extend(range(begin,end))
                begin=end
            near_set=set(near);other=[i for i in range(len(values)) if i not in near_set]
            anchor={k:row[k] for k in ('paragraph','source_character_range','apostrophe_offsets')}
            evaluate('heldout',chapter,anchor,'apostrophe',values,ends,joined_ends,{'apostrophe_word':near,'other':other})
            used+=1
            if used==24:break
        selection[-1]['apostrophe_paragraphs']=used
        print({'chapter':chapter,'selection':selection[-1],'seconds':time.perf_counter()-tick},flush=True)
    layouts={r['fixture']:r['segment_ends'] for r in load(AUDIT)['controls']}
    for f in load('known_solutions/fixtures.json'):
        if f['canonical_pages_match']:
            edge_pair('known_control',f['id'],{'fixture':f['id']},to_indices(f['plaintext_runes']),layouts[f['id']])
    stats=aggregate(rows)
    def rate(condition,region):
        return next(r['win_rates'] for r in stats if (r['origin'],r['condition'],r['region'],r['chapter'])==('heldout',condition,region,'all'))
    gain=lambda c,r:rate(c,r)[1]-rate(c,r)[0]
    known=[r for r in stats if r['origin']=='known_control' and r['chapter']=='all']
    known_rate=sum(r['wins'][1] for r in known)/sum(r['comparisons'] for r in known)
    checks={'clipped_edge_gain_at_least_002':gain('clipped','edge')>=.02,
            'intact_edge_loss_at_most_001':gain('intact','edge')>=-.01,
            'both_interior_losses_at_most_001':min(gain(c,'interior') for c in ('intact','clipped'))>=-.01,
            'known_control_rate_at_least_095':known_rate>=.95}
    assert time.perf_counter()<deadline
    return {'experiment':'E030-fragment-benchmark','parameters':plan,'training':metadata,'selection':selection,
            'rows':rows,'aggregate':stats,'edge_gate_checks':checks,'edge_gate_passed':all(checks.values()),
            'known_control_alternative_win_rate':known_rate,'wall_seconds':time.perf_counter()-tick,
            'new_decryptions':[],'unknown_pages_searched':0}


DEPS=['experiments/fragment_benchmark.py','experiments/heldout_language.py',PLAN,
      'src/liberprimus/fragment_model.py','src/liberprimus/word_model.py','src/liberprimus/boundaries.py',
      'src/liberprimus/decoding.py','src/liberprimus/alphabet.py','experiments/attack_support.py',
      'src/liberprimus/ciphers.py','known_solutions/fixtures.json',AUDIT,
      'data/raw/gutenberg/pg2944.txt','sources/emerson_manifest.json']

if __name__=='__main__':registered('E030-fragment-benchmark',load(PLAN),DEPS,run)
