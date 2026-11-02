"""Bounded nominal periods17..32 with joint F-schedule inference."""
from attack_support import cycle_key,to_runes,top_unique
from periodic_key_search import search as fixed_search
from joint_skip_search import fixed_schedule_key,optimize_schedule
from liberprimus.periodic_key import decrypt,encrypt
from liberprimus.alphabet import transliterate
from phase_key_search import optimize as pool_optimize,coordinate_key as pool_coordinates


from long_key_search import source_windows


def pooled_fragments(values):
    runs=[];begin=0
    for i,x in enumerate(list(values)+[0]):
        if x==0:
            if i-begin>=16:runs.append((begin,i))
            begin=i+1
    runs.sort(key=lambda ab:(-(ab[1]-ab[0]),ab[0]));ranges=[(a,min(b,a+256)) for a,b in runs[:12]]
    joined=[];spans=[]
    for j,(a,b) in enumerate(ranges):
        start=len(joined);joined+=values[a:b]
        spans.append({'page_id':f'fragment-{j:02}','start':start,'end':len(joined),'runes':b-a,'zero_rune_page':False})
    return joined,spans,ranges


def search(values,model,lookup,deadline,seed=3303049):
    if not 512<=len(values)<=4096:raise ValueError('Long-key stream bound512..4096')
    sources=source_windows(values)
    unique={};source_stats=[]
    for label,a,b,skips in sources:
        found=fixed_search(values[a:b],lookup,deadline,seed=seed,oracle_skips=skips,periods=range(17,33))
        source_stats.append({'kind':label,'range':[a,b],'families':len(found['families']),
                             'coordinate_evaluations':found['coordinate_evaluations']})
        for row in found['families']:
            canonical=cycle_key(row['key']);index=(row['sign'],canonical)
            candidate={'key':list(canonical),'sign':row['sign'],'seed_score':row['score'],
                'source_kind':label,'source_range':[a,b],'source_key':row['key'],
                'source_policy':row['policy'],'nominal_period':row['nominal_period']}
            if index not in unique or row['score']>unique[index]['seed_score']:unique[index]=candidate
    seeds=sorted(unique.values(),key=lambda r:r['seed_score'],reverse=True)[:12]
    pool,spans,ranges=pooled_fragments(values)
    if not pool:raise ValueError("No pooled fragment available")
    top=[];restarts=[]
    for index,initial in enumerate(seeds):
        pooled=pool_optimize(pool,spans,initial['key'],initial['sign'],model,deadline);pool_trace=[pooled]
        for _ in range(2):
            key,changes=pool_coordinates(pool,spans,pooled['key'],pooled['sign'],[],pooled['page_phases'],lookup,deadline)
            following=pool_optimize(pool,spans,key,pooled['sign'],model,deadline);following['coordinate_changes']=changes
            assert following['score']>=pooled['score']-1e-9
            pool_trace.append(following);pooled=following
        state=optimize_schedule(values,pooled['key'],initial['sign'],model,deadline);trace=[state]
        for _ in range(3):
            key,changes=fixed_schedule_key(values,state['key'],state['sign'],state['skip_positions'],lookup,deadline)
            following=optimize_schedule(values,key,state['sign'],model,deadline);following['coordinate_changes']=changes
            assert following['score']>=state['score']-1e-9
            trace.append(following)
            unchanged=following['key']==state['key'] and following['skip_positions']==state['skip_positions']
            state=following
            if unchanged:break
        plain=decrypt(values,state['key'],state['sign'],state['skip_positions'])
        assert encrypt(plain,state['key'],state['sign'],state['skip_positions'])==list(values)
        row=state|{'seed_index':index,'plaintext_runes':to_runes(plain),'transliteration':transliterate(plain)}
        restarts.append({'initial':initial,'pool_trace':pool_trace,'trace':trace,'final':row});top=top_unique(top+[row],keep=3)
    return {'top':top,'restarts':restarts,'source_stats':source_stats,'unique_seed_keys':len(unique),'pool_ciphertext':pool,'pool_spans':spans,'pool_source_ranges':[list(r) for r in ranges]}
