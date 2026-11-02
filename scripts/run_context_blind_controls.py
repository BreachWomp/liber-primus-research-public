"""Staged resume-aware E057 supervisor, no unknown search on failed gates."""
import ctypes
from ctypes import wintypes
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


def main():
    assert load('results/phase20_context_validation.json')['oracle_gate_passed']
    started=time.perf_counter();outputs=[]
    events=[json.loads(x) for x in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    prior=sum(e['wall_seconds'] for e in events if e['experiment'].startswith('E057-') and e['status'] in ('completed','failed'))
    logpath='results/phase20_blind_processes.json';processes=load(logpath) if (ROOT/logpath).exists() else []
    psapi=ctypes.WinDLL('psapi',use_last_error=True);psapi.GetProcessMemoryInfo.argtypes=[wintypes.HANDLE,ctypes.POINTER(Memory),wintypes.DWORD];psapi.GetProcessMemoryInfo.restype=wintypes.BOOL
    env=os.environ.copy();env['PYTHONIOENCODING']='utf-8';env['PYTHONPATH']=str(ROOT/'src')+os.pathsep+str(ROOT/'experiments')
    env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
    def call(kind,index):
        if prior+time.perf_counter()-started>1400-185:raise TimeoutError('Insufficient atomic-run reserve')
        tick=time.perf_counter();log=f'results/E057-{kind}-{index}-process.txt';peak=0;reason=None
        with (ROOT/log).open('w',encoding='utf-8') as stream:
            p=subprocess.Popen([sys.executable,'experiments/context_blind_controls.py',kind,str(index)],cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT)
            while p.poll() is None:
                m=Memory();m.cb=ctypes.sizeof(m)
                if not psapi.GetProcessMemoryInfo(int(p._handle),ctypes.byref(m),m.cb):
                    if p.poll() is None:reason='memory_monitor_failed'
                else:peak=max(peak,m.WorkingSetSize,m.PrivateUsage)
                if peak>768*1024**2:reason='memory_ceiling'
                if time.perf_counter()-tick>185:reason='process_watchdog'
                if reason:p.kill();p.wait();break
                time.sleep(.25)
        row={'kind':kind,'index':index,'exit_code':p.returncode,'reason':reason,'seconds':time.perf_counter()-tick,'peak_sampled_bytes':peak,'log':log}
        processes.append(row);save(logpath,processes)
        if p.returncode or reason:raise RuntimeError(row)
        last=json.loads((ROOT/log).read_text(encoding='utf-8').strip().splitlines()[-1]);path=last['output'];outputs.append(path);data=load(path)
        print(json.dumps({'output':path,'exact':data.get('exact'),'correct_runes':data.get('correct_runes'),'seconds':row['seconds']}),flush=True)
        save('checkpoints/phase20_blind_progress.json',{'outputs':outputs,'prior_seconds':prior,'seconds':time.perf_counter()-started})
        return data
    a=[call('regression',2)]+[call('fresh',i) for i in range(3)];null=call('null',2)
    stage_a=all(r['exact'] for r in a);b=[]
    if stage_a:
        b=[call('regression',i) for i in range(12) if i!=2]+[call('stress',i) for i in range(3)]
    summary={'stage_A_passed':stage_a,'stage_B_executed':stage_a,'full_gate_passed':stage_a and all(r['exact'] for r in b),
        'controls_completed':len(a)+len(b),'exact_controls':sum(r['exact'] for r in a+b),
        'null_score':null['result']['top'][0]['score'],'outputs':outputs,'prior_seconds':prior,'seconds':time.perf_counter()-started,
        'unknown_sections_searched':0,'new_decryptions':[]}
    save('checkpoints/phase20_blind_complete.json',summary)
    print(json.dumps({k:v for k,v in summary.items() if k!='outputs'}),flush=True)


if __name__=='__main__':main()
