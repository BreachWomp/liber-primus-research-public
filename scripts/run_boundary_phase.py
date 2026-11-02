"""Resume-aware bounded E028 driver with frozen selected-page null calibration."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
def load(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))
def save(path,data):(ROOT/path).write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()

def main():
    tick=time.perf_counter();outputs=[]
    def call(mode,page='LP2-00',replicate=0):
        if 850-(time.perf_counter()-tick)<183:
            raise TimeoutError('Saved progress: insufficient family reserve for next atomic experiment')
        proc=subprocess.run([sys.executable,'experiments/boundary_selective_attack.py','--mode',mode,
             '--page',page,'--replicate',str(replicate)],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=182)
        print(proc.stdout,flush=True)
        if proc.returncode:raise RuntimeError(proc.stderr)
        path=json.loads(proc.stdout.strip().splitlines()[-1])['output'];outputs.append(path)
        save('checkpoints/phase8_boundary_progress.json',{'outputs':outputs,'seconds':time.perf_counter()-tick})
        return load(path)
    controls=call('controls')
    if not controls['gate_passed']:raise RuntimeError('Full-union control gate failed; no unknown scan')
    rows=[]
    for number in range(56):
        if number!=50:rows.append(call('page',f'LP2-{number:02}'))
    selected=max(rows,key=lambda r:r['top'][0]['score'])
    frozen={'selected_page':selected['page'],'observed_score':selected['top'][0]['score'],
        'source_outputs':{p:sha(p) for p in outputs},'seed':3301028,'replicates':19,
        'segment_ends':selected['segment_ends'],'registered_at':datetime.now(timezone.utc).isoformat()}
    path='experiments/boundary_attack_selection.json'
    if (ROOT/path).exists():
        old=load(path);assert all(old[k]==v for k,v in frozen.items() if k!='registered_at')
    else:save(path,frozen)
    null=[call('null',selected['page'],i) for i in range(19)]
    exceed=sum(n['score']>=selected['top'][0]['score'] for n in null)
    summary={'selected_page':selected['page'],'raw_p':(1+exceed)/20,'exceedances':exceed,
        'selection_sha256':sha(path),'outputs':outputs,'seconds':time.perf_counter()-tick}
    save('checkpoints/phase8_boundary_complete.json',summary)
    print(json.dumps({k:v for k,v in summary.items() if k!='outputs'}),flush=True)

if __name__=='__main__':main()
