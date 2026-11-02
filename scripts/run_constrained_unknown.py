"""Resume-aware E059 supervisor with frozen group selection and bounded jobs."""
import ctypes
from ctypes import wintypes
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from run_fragment_initialization_phase import Memory
ROOT=Path(__file__).resolve().parents[1]
def load(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))
def save(path,data):(ROOT/path).write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def main():
    plan=load('experiments/constrained_unknown_plan.json')
    assert load(plan['control_validation'])['full_gate_passed']
    started=time.perf_counter();outputs=[]
    events=[json.loads(x) for x in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    prior=sum(e['wall_seconds'] for e in events if e['experiment'].startswith('E059-') and e['status'] in ('completed','failed'))
    controls_seconds=sum(e['wall_seconds'] for e in events if e['experiment'].startswith('E058-') and e['status'] in ('completed','failed'))
    psapi=ctypes.WinDLL('psapi',use_last_error=True)
    psapi.GetProcessMemoryInfo.argtypes=[wintypes.HANDLE,ctypes.POINTER(Memory),wintypes.DWORD]
    psapi.GetProcessMemoryInfo.restype=wintypes.BOOL
    path='results/phase21_unknown_processes.json';processes=load(path) if (ROOT/path).exists() else []
    env=os.environ.copy();env['PYTHONIOENCODING']='utf-8';env['PYTHONPATH']=str(ROOT/'src')+os.pathsep+str(ROOT/'experiments')
    env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
    def call(mode,section,replicate=0):
        if prior+time.perf_counter()-started>plan['family_seconds']-185:raise TimeoutError('Insufficient atomic-run reserve')
        if controls_seconds+prior+time.perf_counter()-started>plan['combined_phase21_seconds']-185:raise TimeoutError('Combined phase21 budget')
        log=f'results/E059-{mode}-{section}-{replicate:02}-process.txt';tick=time.perf_counter();peak=0;reason=None
        with (ROOT/log).open('w',encoding='utf-8') as stream:
            proc=subprocess.Popen([sys.executable,'experiments/constrained_unknown.py','--mode',mode,
                '--section',section,'--replicate',str(replicate)],cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT)
            while proc.poll() is None:
                memory=Memory();memory.cb=ctypes.sizeof(memory)
                if not psapi.GetProcessMemoryInfo(int(proc._handle),ctypes.byref(memory),memory.cb):
                    if proc.poll() is None:reason='memory_monitor_failed'
                else:peak=max(peak,memory.WorkingSetSize,memory.PrivateUsage)
                if peak>plan['memory_ceiling_mib']*1024**2:reason='memory_ceiling'
                if time.perf_counter()-tick>185:reason='process_watchdog'
                if reason:proc.kill();proc.wait();break
                time.sleep(.25)
        record={'mode':mode,'section':section,'replicate':replicate,'exit_code':proc.returncode,'reason':reason,
                'seconds':time.perf_counter()-tick,'peak_sampled_bytes':peak,'log':log}
        processes.append(record);save(path,processes)
        if proc.returncode or reason:raise RuntimeError(record)
        last=json.loads((ROOT/log).read_text(encoding='utf-8').strip().splitlines()[-1]);output=last['output'];outputs.append(output)
        data=load(output);print(json.dumps({'output':output,'score':data['score'],'seconds':record['seconds']}),flush=True)
        save('checkpoints/phase21_unknown_progress.json',{'outputs':outputs,'prior_seconds':prior,'seconds':time.perf_counter()-started})
        return data
    sections=[call('section',s) for s in plan['section_ids']]
    winner=max(sections,key=lambda r:r['score'])
    selection={'selected_section':winner['section'],'observed_score':winner['score'],
               'source_outputs':{p:sha(p) for p in outputs},'replicates':19,'null_seed':plan['null_seed'],
               'registered_at':datetime.now(timezone.utc).isoformat()}
    selected='experiments/constrained_selection.json'
    if (ROOT/selected).exists():assert all(load(selected)[k]==v for k,v in selection.items() if k!='registered_at')
    else:save(selected,selection)
    nulls=[call('null',winner['section'],i) for i in range(19)]
    exceed=sum(r['score']>=winner['score'] for r in nulls);p=(exceed+1)/20
    summary={'selected_section':winner['section'],'observed_score':winner['score'],'exceedances':exceed,
             'raw_p':p,'bonferroni9':min(1,9*p),'pending_larger_calibration':exceed==0,
             'selection_sha256':sha(selected),'outputs':outputs,'prior_seconds':prior,'seconds':time.perf_counter()-started}
    save('checkpoints/phase21_unknown_complete.json',summary)
    print(json.dumps({k:v for k,v in summary.items() if k!='outputs'}),flush=True)


if __name__=='__main__':main()
