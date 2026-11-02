"""Replay fixed initialization seeds from independent scalar queue decodings."""
import json
import random
import time
import numpy as np
from verify_bilinear_feedback import BilinearVerifier,ROOT,load,sha


def main():
    tick=time.perf_counter();v=BilinearVerifier();families=starts=0;outputs={}
    paths=load('checkpoints/phase25_controls_complete.json')['outputs']+load('checkpoints/phase25_unknown_complete.json')['outputs']+load('checkpoints/phase25_more_nulls_complete.json')['outputs']
    assert len(paths)==191
    for path in paths:
        assert time.perf_counter()-tick<300
        row=load(path);cipher=row['source']['ciphertext_indices'] if 'source' in row else row['ciphertext_indices']
        for family in row['result']['families']:
            m,a,b=family['period'],family['cipher_sign'],family['feedback_sign']
            zero,_=v.decode(cipher,[0]*m,a,b);one,_=v.decode(cipher,[1]*m,a,b)
            delta=(np.array(one)-np.array(zero))%29
            variants=(np.array(zero)[None,:]+np.arange(29)[:,None]*delta)%29
            unary=np.array([v.lookup[0][variants[:,r::m]].sum(axis=1) for r in range(m)])
            ranks=np.argsort(-unary,axis=1,kind='stable');rng=random.Random(3303068+784*m+28*(a-1)+b-1)
            assert len(family['starts'])==8
            for j,record in enumerate(family['starts']):
                expected=[int(ranks[r,j if j<3 else rng.randrange(5)]) for r in range(m)]
                assert record['initial']==expected
                starts+=1
            families+=1
        outputs[path]=sha(path)
    summary={'families_checked':families,'seeded_initializers_checked':starts,'outputs':outputs,
        'seconds':time.perf_counter()-tick,'script_sha256':sha('scripts/audit_bilinear_feedback_seeds.py')}
    (ROOT/'results/phase25_seed_audit.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    print({k:v for k,v in summary.items() if k!='outputs'})


if __name__=='__main__':main()
