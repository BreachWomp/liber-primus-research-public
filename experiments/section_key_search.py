"""Long-input adapter preserving the frozen joint key/schedule objective."""
from attack_support import cycle_key,to_runes,top_unique
from periodic_key_search import search as fixed_search
from joint_skip_search import search as short_search,seed_ranges,fixed_schedule_key,optimize_schedule
from liberprimus.periodic_key import decrypt,encrypt
from liberprimus.alphabet import transliterate


def search(values,model,lookup,deadline,seed=3303040):
    if not 1<=len(values)<=4096:raise ValueError('Section length outside bound')
    if len(values)<=1024:return short_search(values,model,lookup,deadline,seed)
    sources=[('prefix',0,1024,None),('suffix',len(values)-1024,len(values),None)]
    sources += [('non_F_run',a,b,[]) for a,b in seed_ranges(values)]
    unique={};source_stats=[]
    for label,a,b,skips in sources:
        found=fixed_search(values[a:b],lookup,deadline,seed=seed,oracle_skips=skips)
        source_stats.append({'kind':label,'range':[a,b],'families':len(found['families']),
                             'coordinate_evaluations':found['coordinate_evaluations']})
        for row in found['families']:
            canonical=cycle_key(row['key']);index=(row['sign'],canonical)
            candidate={'key':list(canonical),'sign':row['sign'],'seed_score':row['score'],
                'source_kind':label,'source_range':[a,b],'source_key':row['key'],
                'source_policy':row['policy'],'nominal_period':row['nominal_period']}
            if index not in unique or row['score']>unique[index]['seed_score']:unique[index]=candidate
    seeds=sorted(unique.values(),key=lambda r:r['seed_score'],reverse=True)[:12]
    top=[];restarts=[]
    for index,initial in enumerate(seeds):
        state=optimize_schedule(values,initial['key'],initial['sign'],model,deadline);trace=[state]
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
        restarts.append({'initial':initial,'trace':trace,'final':row});top=top_unique(top+[row],keep=3)
    return {'top':top,'restarts':restarts,'source_stats':source_stats,'unique_seed_keys':len(unique)}
