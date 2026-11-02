"""Control-gated, resume-aware 900-second reading-order experiment."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]

def main():
    tick=time.perf_counter();outputs=[]
    def call(mode,page='LP2-00',batch=0):
        remaining=900-(time.perf_counter()-tick)
        if remaining<190:raise TimeoutError('checkpoint saved; insufficient reserve for next experiment')
        r=subprocess.run([sys.executable,'experiments/reading_order_attack.py','--mode',mode,'--page',page,'--batch',str(batch)],cwd=ROOT,
            capture_output=True,text=True,encoding='utf-8',timeout=190)
        print(r.stdout,flush=True)
        if r.returncode:raise RuntimeError(r.stderr)
        path=json.loads(r.stdout.strip().splitlines()[-1])['output'];outputs.append(path)
        (ROOT/'checkpoints/phase6_routes.json').write_text(json.dumps({'outputs':outputs,'seconds':time.perf_counter()-tick},indent=2)+'\n',encoding='utf-8')
        return json.loads((ROOT/path).read_text(encoding='utf-8'))
    control=call('controls')
    if not control['gate_passed']:print('CONTROL GATE FAILED; no unknown scan');return
    rows=[call('page',p) for p in ['LP2-00','LP2-49','LP2-51','LP2-55']]
    chosen=max(rows,key=lambda r:r['top'][0]['score'])
    path=ROOT/'experiments/reading_order_null_plan.json'
    if not path.exists():
        path.write_text(json.dumps({'registered_at':datetime.now(timezone.utc).isoformat(),'selected_page':chosen['page'],
            'observed_score':chosen['top'][0]['score'],'source_outputs':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in outputs},
            'replicates':19,'seed':3301021,'selection_correction':55,'optimizer':'Full frozen route+cipher grid, no reranking changes','total_family_budget_seconds':900},indent=2)+'\n',encoding='utf-8')
    else:assert json.loads(path.read_text(encoding='utf-8'))['selected_page']==chosen['page']
    null=[call('null',chosen['page'],i) for i in range(19)]
    p=(1+sum(n['score']>=chosen['top'][0]['score'] for n in null))/20
    print(json.dumps({'status':'completed','selected':chosen['page'],'p':p,'seconds':time.perf_counter()-tick}),flush=True)

if __name__=='__main__':main()
