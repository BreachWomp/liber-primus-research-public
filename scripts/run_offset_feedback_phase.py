"""Bounded resume-aware E034 queue, frozen selection and full-grid nulls."""
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
    history=[json.loads(line) for line in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    prior={r['fingerprint']:r for r in history if r['experiment'].startswith('E034-') and r['status']=='completed'}
    spent=sum(r['wall_seconds'] for r in prior.values())
    def call(mode,page='LP2-00',replicate=0):
        if 750-spent-(time.perf_counter()-tick)<183:
            raise TimeoutError('Saved progress; insufficient reserve for next atomic experiment')
        proc=subprocess.run([sys.executable,'experiments/offset_feedback_attack.py','--mode',mode,
            '--page',page,'--replicate',str(replicate)],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=182)
        print(proc.stdout,flush=True)
        if proc.returncode:raise RuntimeError(proc.stderr)
        path=json.loads(proc.stdout.strip().splitlines()[-1])['output'];outputs.append(path)
        save('checkpoints/phase10_offset_progress.json',{'outputs':outputs,'prior_seconds':spent,'seconds':time.perf_counter()-tick})
        return load(path)
    controls=call('controls')
    if not controls['gate_passed']:raise RuntimeError('Control gate failed; no unknown scan')
    pages=[call('page',f'LP2-{n:02}') for n in range(56) if n!=50]
    winner=max(pages,key=lambda row:row['score'])
    selection={'selected_page':winner['page'],'observed_score':winner['score'],
        'source_outputs':{p:sha(p) for p in outputs},'seed':3301034,'replicates':19,
        'registered_at':datetime.now(timezone.utc).isoformat()}
    path='experiments/offset_feedback_selection.json'
    if (ROOT/path).exists():
        old=load(path);assert all(old[k]==v for k,v in selection.items() if k!='registered_at')
    else:save(path,selection)
    nulls=[call('null',winner['page'],i) for i in range(19)]
    exceed=sum(row['score']>=winner['score'] for row in nulls)
    summary={'selected_page':winner['page'],'raw_p':(exceed+1)/20,'bonferroni55':min(1,55*(exceed+1)/20),
        'exceedances':exceed,'outputs':outputs,'selection_sha256':sha(path),'prior_seconds':spent,
        'seconds':time.perf_counter()-tick,'pending_larger_calibration':exceed==0}
    save('checkpoints/phase10_offset_complete.json',summary)
    print(json.dumps({k:v for k,v in summary.items() if k!='outputs'}),flush=True)


if __name__=='__main__':main()
