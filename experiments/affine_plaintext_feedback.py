"""One-rune affine plaintext feedback, excluding the four old sign pairs."""
import argparse
import random
import time
import numpy as np
from attack_support import load,to_indices,to_runes,top_unique
from liberprimus.alphabet import transliterate
from external_language import external_model
from ngram_arrays import dense_tables,array_scores
from conditional_attack_null import conditional_shuffle
from registry import registered


def encrypt(plain,a,b,key):
    inverse=pow(a,-1,29);out=[];previous=key
    for p in plain:
        out.append((inverse*(p-b*previous))%29);previous=p
    return out


def decrypt(cipher,a,b,key):
    out=[];previous=key
    for c in cipher:
        previous=(a*c+b*previous)%29;out.append(previous)
    return out


def parameters():
    return [(a,b) for b in range(1,29) for a in range(1,29) if (a,b) not in ((1,1),(1,28),(28,1),(28,28))]


def search(values,lookup,deadline,keep=3):
    top=[];best=-float('inf');recipes=0;n=len(values)
    initial=np.arange(29,dtype=np.int16)[None,:,None]
    for b in range(1,29):
        if time.perf_counter()>deadline:raise TimeoutError('affine plaintext-feedback deadline')
        aa=np.array([a for a in range(1,29) if not (a in (1,28) and b in (1,28))],dtype=np.int16)
        base=np.zeros(n,dtype=np.int16);power=np.ones(n,dtype=np.int16)
        for i in range(1,n):
            base[i]=(int(values[i])+b*int(base[i-1]))%29
            power[i]=(b*int(power[i-1]))%29
        plain=(aa[:,None,None]*base[None,None,:]+initial*power[None,None,:])%29
        plain=plain.reshape(-1,n);scores=array_scores(plain,lookup);recipes+=len(plain)
        best=max(best,float(scores.max()))
        if keep:
            for idx in np.argsort(scores,kind='stable')[-keep:]:
                a=int(aa[int(idx)//29]);p0=int(idx)%29
                key=((p0-a*values[0])*pow(b,-1,29))%29;p=plain[idx].tolist()
                assert encrypt(p,a,b,key)==list(values)
                row={'score':float(scores[idx]),'plaintext_runes':to_runes(p),'transliteration':transliterate(p),
                     'recipe':{'a':a,'b':b,'initial_key':int(key),'initial_plaintext':p0,'F_policy':'none'},
                     'reencryption_verified':True}
                top=top_unique(top+[row],keep=keep)
    return best,top,recipes


def run(mode,first,last,seconds,replicates,seed):
    tick=time.perf_counter();deadline=tick+seconds;lookup=dense_tables(external_model(4))
    result={'experiment':'E019-affine-plaintext-feedback-'+mode,'status':'completed','new_decryptions':[],
        'parameters':{'mode':mode,'first':first,'last':last,'seconds':seconds,'replicates':replicates,'seed':seed,
            'recurrence':'P_i=a*C_i+b*P_(i-1) mod29, P_(-1)=initial_key',
            'coefficient_pairs':parameters(),'keys':list(range(29)),'F_policy':'none','page_reset':True,
            'language':'fixed external4gram','memory':'one b at a time, at most 812 plaintext rows; dense29^4 language table'}}
    if mode=='controls':
        fixtures={f['id']:f for f in load('known_solutions/fixtures.json')};rng=random.Random(seed);rows=[]
        for ident,a,b in [('LP1-03_04_divinity',5,11),('LP1-14_15_circumference',13,7),('LP2-57_direct',28,3)]:
            key=rng.randrange(29);expected=fixtures[ident]['plaintext_runes']
            cipher=encrypt(to_indices(expected),a,b,key);_,top,recipes=search(cipher,lookup,deadline)
            rows.append({'fixture':ident,'a':a,'b':b,'initial_key':key,'ciphertext_indices':cipher,
                         'exact':top[0]['plaintext_runes']==expected,'top':top,'recipes':recipes})
            print({'control':ident,'exact':rows[-1]['exact'],'seconds':time.perf_counter()-tick},flush=True)
        result.update(controls=rows,gate_passed=all(r['exact'] for r in rows))
    else:
        rows=[]
        for page in load('transcriptions/pages.json'):
            if page['edition']!='LP2' or not first<=page['page']<=min(last,55) or not page['runes']:continue
            best,top,recipes=search(to_indices(page['runes']),lookup,deadline)
            rows.append({'page':page['id'],'ciphertext_runes':page['runes'],'top':top,'recipes':recipes})
            print({'page':page['id'],'score':best,'seconds':time.perf_counter()-tick},flush=True)
        result['pages']=rows;result['evaluated_recipes']=sum(r['recipes'] for r in rows)
        if mode=='null':
            assert len(rows)==1
            values=to_indices(rows[0]['ciphertext_runes']);rng=random.Random(seed);null=[]
            for i in range(replicates):
                sample,proposals=conditional_shuffle(values,rng,deadline=deadline)
                best,_,recipes=search(sample,lookup,deadline,keep=0)
                null.append({'score':best,'ciphertext_indices':sample,'proposals':proposals,'recipes':recipes})
            p=(1+sum(r['score']>=rows[0]['top'][0]['score'] for r in null))/(replicates+1)
            result['null_calibration']={'runs':null,'monte_carlo_p':p,'bonferroni_55_pages':min(1,55*p),
                'selection':'Same full coefficient/key grid on every exact count/doublet shuffle; Bonferroni55 for best page.'}
    result['limits']=['One-rune feedback only; no additive constant, interruptions, permutations or continuation across pages.',
        'Four sign pairs already covered by E014/E017 are explicitly excluded; this is a family extension, not independent replication.',
        'Synthetic controls are previously inspected LP texts excluded from training, not fresh blind historical validation.',
        'B19 cannot resolve corrected significance; zero exceedances require a separately registered larger follow-up.']
    result['wall_seconds']=time.perf_counter()-tick
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--mode',choices=['controls','pages','null'],required=True)
    parser.add_argument('--first',type=int,default=0);parser.add_argument('--last',type=int,default=55)
    parser.add_argument('--seconds',type=float,default=180.0);parser.add_argument('--replicates',type=int,default=19)
    parser.add_argument('--seed',type=int,default=3301019);args=parser.parse_args()
    deps=['experiments/affine_plaintext_feedback.py','experiments/affine_feedback_plan.json','experiments/external_language.py',
        'experiments/external_model_plan.json','experiments/ngram_arrays.py','experiments/attack_support.py',
        'experiments/conditional_attack_null.py','src/liberprimus/alphabet.py','src/liberprimus/ciphers.py',
        'src/liberprimus/decoding.py','known_solutions/fixtures.json','transcriptions/pages.json',
        'sources/emerson_manifest.json','data/raw/gutenberg/pg2944.txt']
    ident='E019-'+args.mode+(f'-LP2-{args.first:02}_{args.last:02}' if args.mode!='controls' else '')
    registered(ident,{**vars(args),'numpy':np.__version__},deps,lambda:run(args.mode,args.first,args.last,args.seconds,args.replicates,args.seed))
