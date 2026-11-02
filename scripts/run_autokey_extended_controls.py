"""Bounded Windows E062 supervisor; immutable completed runs are reused."""
import ctypes
from ctypes import wintypes
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
    started=time.perf_counter();outputs=[]
    events=[json.loads(x) for x in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    prior=sum(e['wall_seconds'] for e in events if e['experiment'].startswith('E062-') and e['status'] in ('completed','failed'))
    logpath='results/phase22_controls_processes.json';processes=load(logpath) if (ROOT/logpath).exists() else []
    psapi=ctypes.WinDLL('psapi',use_last_error=True);psapi.GetProcessMemoryInfo.argtypes=[wintypes.HANDLE,ctypes.POINTER(Memory),wintypes.DWORD];psapi.GetProcessMemoryInfo.restype=wintypes.BOOL
    env=os.environ.copy();env['PYTHONIOENCODING']='utf-8';env['PYTHONPATH']=str(ROOT/'src')+os.pathsep+str(ROOT/'experiments')
    env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
    def call(kind,index):
        ident=f'E062-{kind}-{index}'
        old=next((e for e in reversed(events) if e['experiment']==ident and e['status']=='completed'),None)
        if old:
            assert sha(old['output'])==old['output_sha256']
            for path,digest in old['input_dependencies'].items():assert sha(path)==digest,path
            outputs.append(old['output']);return load(old['output'])
        if prior+time.perf_counter()-started>1800-185:raise TimeoutError('Insufficient atomic reserve')
        tick=time.perf_counter();log=f'results/{ident}-process.txt';peak=0;reason=None
        with (ROOT/log).open('x',encoding='utf-8') as stream:
            proc=subprocess.Popen([sys.executable,'experiments/autokey_extended_controls.py',kind,str(index)],cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT)
            while proc.poll() is None:
                memory=Memory();memory.cb=ctypes.sizeof(memory)
                if not psapi.GetProcessMemoryInfo(int(proc._handle),ctypes.byref(memory),memory.cb):
                    if proc.poll() is None:reason='memory_monitor_failed'
                else:peak=max(peak,memory.WorkingSetSize,memory.PrivateUsage)
                if peak>768*1024**2:reason='memory_ceiling'
                if time.perf_counter()-tick>185:reason='process_watchdog'
                if reason:proc.kill();proc.wait();break
                time.sleep(.25)
        row={'kind':kind,'index':index,'exit_code':proc.returncode,'reason':reason,'seconds':time.perf_counter()-tick,'peak_sampled_bytes':peak,'log':log}
        processes.append(row);save(logpath,processes)
        if proc.returncode or reason:raise RuntimeError(row)
        output=json.loads((ROOT/log).read_text(encoding='utf-8').strip().splitlines()[-1])['output'];outputs.append(output);data=load(output)
        print(json.dumps({'output':output,'exact':data.get('exact'),'correct_runes':data.get('correct_runes'),'seconds':row['seconds']}),flush=True)
        save('checkpoints/phase22_controls_progress.json',{'outputs':outputs,'prior_seconds':prior,'seconds':time.perf_counter()-started})
        return data
    a=[call('control',i) for i in range(6)];null=call('null',2)
    stage_a=all(r['exact'] for r in a);b=[call('control',i) for i in range(6,12)] if stage_a else []
    summary={'stage_A_passed':stage_a,'stage_B_executed':stage_a,'full_gate_passed':stage_a and all(r['exact'] for r in b),
        'controls_completed':len(a)+len(b),'exact_controls':sum(r['exact'] for r in a+b),
        'null_score':null['result']['top'][0]['score'],'outputs':outputs,'prior_seconds':prior,'seconds':time.perf_counter()-started,
        'unknown_pages_searched':0,'new_decryptions':[]}
    save('checkpoints/phase22_controls_complete.json',summary);print(json.dumps(summary),flush=True)


if __name__=='__main__':main()
