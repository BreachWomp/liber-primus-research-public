"""Serial bounded E065 scan and immutable pre-null selection."""
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
from run_context_calibration import Memory
ROOT=Path(__file__).resolve().parents[1]
def load(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))
def save(path,data):(ROOT/path).write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()


def main():
    plan=load('experiments/autokey_section_unknown_plan.json');assert load(plan['control_validation'])['full_gate_passed']
    started=time.perf_counter();outputs=[]
    events=[json.loads(x) for x in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    prior=sum(e['wall_seconds'] for e in events if e['experiment'].startswith('E065-') and e['status'] in ('completed','failed'))
    control_seconds=sum(e['wall_seconds'] for e in events if e['experiment'].startswith('E064-') and e['status'] in ('completed','failed'))
    logpath='results/phase23_unknown_processes.json';processes=load(logpath) if (ROOT/logpath).exists() else []
    psapi=ctypes.WinDLL('psapi',use_last_error=True);psapi.GetProcessMemoryInfo.argtypes=[wintypes.HANDLE,ctypes.POINTER(Memory),wintypes.DWORD];psapi.GetProcessMemoryInfo.restype=wintypes.BOOL
    env=os.environ.copy();env['PYTHONIOENCODING']='utf-8';env['PYTHONPATH']=str(ROOT/'src')+os.pathsep+str(ROOT/'experiments')
    env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
    def call(mode,page,replicate=0):
        ident=f'E065-{mode}-{page}'+(f'-{replicate:02}' if mode=='null' else '')
        old=next((e for e in reversed(events) if e['experiment']==ident and e['status']=='completed'),None)
        if old:
            assert sha(old['output'])==old['output_sha256']
            for path,digest in old['input_dependencies'].items():assert sha(path)==digest,path
            outputs.append(old['output']);return load(old['output'])
        elapsed=prior+time.perf_counter()-started
        if elapsed>plan['family_seconds']-185 or control_seconds+elapsed>plan['phase_seconds']-185:raise TimeoutError('Insufficient atomic reserve')
        tick=time.perf_counter();log=f'results/{ident}-process.txt';peak=0;reason=None
        with (ROOT/log).open('x',encoding='utf-8') as stream:
            proc=subprocess.Popen([sys.executable,'experiments/autokey_section_unknown.py',mode,page,str(replicate)],cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT)
            while proc.poll() is None:
                memory=Memory();memory.cb=ctypes.sizeof(memory)
                if not psapi.GetProcessMemoryInfo(int(proc._handle),ctypes.byref(memory),memory.cb):
                    if proc.poll() is None:reason='memory_monitor_failed'
                else:peak=max(peak,memory.WorkingSetSize,memory.PrivateUsage)
                if peak>768*1024**2:reason='memory_ceiling'
                if time.perf_counter()-tick>185:reason='process_watchdog'
                if reason:proc.kill();proc.wait();break
                time.sleep(.25)
        row={'mode':mode,'section':page,'replicate':replicate,'exit_code':proc.returncode,'reason':reason,'seconds':time.perf_counter()-tick,'peak_sampled_bytes':peak,'log':log}
        processes.append(row);save(logpath,processes)
        if proc.returncode or reason:raise RuntimeError(row)
        output=json.loads((ROOT/log).read_text(encoding='utf-8').strip().splitlines()[-1])['output'];outputs.append(output);data=load(output)
        print(json.dumps({'output':output,'score':data['result']['top'][0]['score'],'seconds':row['seconds']}),flush=True)
        save('checkpoints/phase23_unknown_progress.json',{'outputs':outputs,'prior_seconds':prior,'seconds':time.perf_counter()-started})
        return data
    pages=[call('section',p) for p in plan['section_ids']]
    winner=max(pages,key=lambda r:r['result']['top'][0]['score']);score=winner['result']['top'][0]['score']
    selection={'section':winner['section'],'score':score,'source_outputs':{p:sha(p) for p in outputs},'registered_at':datetime.now(timezone.utc).isoformat()}
    path='experiments/autokey_section_selection.json'
    if (ROOT/path).exists():assert all(load(path)[k]==v for k,v in selection.items() if k!='registered_at')
    else:save(path,selection)
    nulls=[call('null',winner['section'],i) for i in range(19)]
    exceed=sum(r['result']['top'][0]['score']>=score for r in nulls);p=(1+exceed)/20
    summary={'section':winner['section'],'score':score,'exceedances':exceed,'raw_p':p,'bonferroni10':min(1,10*p),
        'pending_larger_calibration':exceed==0,'outputs':outputs,'selection_sha256':sha(path),'prior_seconds':prior,'seconds':time.perf_counter()-started}
    save('checkpoints/phase23_unknown_complete.json',summary);print(json.dumps({k:v for k,v in summary.items() if k!='outputs'}),flush=True)


if __name__=='__main__':main()
