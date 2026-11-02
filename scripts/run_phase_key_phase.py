"""Bounded resume-aware E048 queue, frozen selection and full-optimizer nulls."""
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
    tick=time.perf_counter();plan=load('experiments/phase_key_unknown_plan.json')
    outputs=[plan['control_output']];assert load(outputs[0])['gate_passed']
    history=[json.loads(line) for line in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    prior=[r for r in history if r['experiment'].startswith('E048-') and r['status'] in ('completed','failed')]
    # Conservative overhead reserve on resume, beyond logged successful/failed subprocess time.
    spent=sum(r['wall_seconds'] for r in prior)+(60 if prior else 0)
    def call(mode,page,replicate=0):
        if (ROOT/'checkpoints/phase16_stop_requested').exists():
            raise RuntimeError('Stopped at atomic boundary; completed fingerprints retained')
        if plan['family_seconds']-spent-(time.perf_counter()-tick)<183:
            raise TimeoutError('Insufficient reserve for next atomic experiment; progress saved')
        proc=subprocess.run([sys.executable,'experiments/phase_key_unknown.py','--mode',mode,
            '--section',page,'--replicate',str(replicate)],cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=182)
        print(proc.stdout,flush=True)
        if proc.returncode:raise RuntimeError(proc.stderr)
        path=json.loads(proc.stdout.strip().splitlines()[-1])['output'];outputs.append(path)
        save('checkpoints/phase16_phases_progress.json',{'outputs':outputs,'prior_seconds':spent,
                                                         'seconds':time.perf_counter()-tick})
        return load(path)
    pages=[call('section',s['id']) for s in load('experiments/section_plan.json')['sections']]
    winner=max(pages,key=lambda row:row['score'])
    selection={'selected_section':winner['section'],'observed_score':winner['score'],
        'source_outputs':{p:sha(p) for p in outputs},'null_seed':plan['null_seed'],
        'search_seed':plan['search_seed'],'replicates':plan['replicates'],
        'registered_at':datetime.now(timezone.utc).isoformat()}
    path='experiments/phase_key_selection.json'
    if (ROOT/path).exists():
        old=load(path);assert all(old[k]==v for k,v in selection.items() if k!='registered_at')
    else:save(path,selection)
    nulls=[call('null',winner['section'],i) for i in range(plan['replicates'])]
    exceed=sum(row['score']>=winner['score'] for row in nulls);p=(exceed+1)/(len(nulls)+1)
    summary={'selected_section':winner['section'],'raw_p':p,'bonferroni10':min(1,10*p),
        'exceedances':exceed,'outputs':outputs,'selection_sha256':sha(path),'prior_seconds':spent,
        'seconds':time.perf_counter()-tick,'pending_larger_calibration':exceed==0}
    save('checkpoints/phase16_phases_complete.json',summary)
    print(json.dumps({k:v for k,v in summary.items() if k!='outputs'}),flush=True)


if __name__=='__main__':main()
