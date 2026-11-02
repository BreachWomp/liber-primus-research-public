"""One-worker bounded driver; registered completed inputs are reused on resume."""
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
    tick=time.perf_counter();paths=[]
    def call(mode,first=0,last=55,replicate=0):
        remaining=650-(time.perf_counter()-tick)
        if remaining<183: raise TimeoutError('Family budget: insufficient reserve for next atomic experiment; resume saved inputs later')
        command=[sys.executable,'experiments/periodic_feedback.py','--mode',mode,
                 '--first',str(first),'--last',str(last),'--replicate',str(replicate)]
        proc=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=182)
        print(proc.stdout,flush=True)
        if proc.returncode: raise RuntimeError(proc.stderr)
        path=json.loads(proc.stdout.strip().splitlines()[-1])['output'];paths.append(path)
        save('checkpoints/phase7_feedback_progress.json',{'outputs':paths,'seconds':time.perf_counter()-tick})
        return load(path)
    controls=call('controls')
    if not controls['gate_passed']: raise RuntimeError('Control gate failed; no unknown search')
    pages=[];page_paths=[]
    for number in range(56):
        if number==50:continue
        pages.extend(call('pages',number,number)['pages']);page_paths.append(paths[-1])
    selected=max(pages,key=lambda p:p['top'][0]['score']);number=int(selected['page'].split('-')[1])
    selection={'experiment':'E025-selection','selected_page':selected['page'],
        'observed_score':selected['top'][0]['score'],'page_outputs':{p:sha(p) for p in page_paths},
        'null_seed_base':3301025,'replicates':19,'frozen_at':datetime.now(timezone.utc).isoformat()}
    frozen=ROOT/'experiments/periodic_feedback_selection.json'
    if frozen.exists():
        old=load('experiments/periodic_feedback_selection.json')
        assert all(old[k]==v for k,v in selection.items() if k!='frozen_at')
    else:save('experiments/periodic_feedback_selection.json',selection)
    nulls=[call('null',number,number,i)['pages'][0] for i in range(19)]
    exceed=sum(row['score']>=selected['top'][0]['score'] for row in nulls)
    summary={'selected':selected['page'],'raw_p':(1+exceed)/20,'exceedances':exceed,
        'outputs':paths,'seconds':time.perf_counter()-tick,'selection_sha256':sha('experiments/periodic_feedback_selection.json')}
    save('checkpoints/phase7_feedback_complete.json',summary)
    print(json.dumps(summary),flush=True)

if __name__=='__main__':main()
