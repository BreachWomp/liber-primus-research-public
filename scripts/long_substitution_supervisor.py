"""Shared single-worker Windows supervisor; immutable registered runs are reused."""
import ctypes
from ctypes import wintypes
from datetime import datetime,timezone
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


def run_job(ident,arguments):
    import hashlib
    def sha(path):return hashlib.sha256((ROOT/path).read_bytes()).hexdigest()
    events=[json.loads(x) for x in (ROOT/'experiment_log.jsonl').read_text(encoding='utf-8').splitlines()]
    old=next((e for e in reversed(events) if e['experiment']==ident and e['status']=='completed'),None)
    if old:
        assert sha(old['output'])==old['output_sha256']
        for path,digest in old['input_dependencies'].items():assert sha(path)==digest,path
        return old['output'],load(old['output'])
    records_path='results/phase30_processes.json'
    prior=load(records_path) if (ROOT/records_path).exists() else []
    spent=sum(r['seconds'] for r in prior)
    if spent>1800-185:raise TimeoutError('Phase30 atomic reserve exhausted')
    psapi=ctypes.WinDLL('psapi',use_last_error=True)
    psapi.GetProcessMemoryInfo.argtypes=[wintypes.HANDLE,ctypes.POINTER(Memory),wintypes.DWORD]
    psapi.GetProcessMemoryInfo.restype=wintypes.BOOL
    env=os.environ.copy();env.update(PYTHONIOENCODING='utf-8',PYTHONPATH=str(ROOT/'src')+os.pathsep+str(ROOT/'experiments'),
        OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
    attempt=1+sum(r['experiment']==ident for r in prior)
    suffix='' if attempt==1 else f'-attempt{attempt:02}'
    log=f'results/{ident}{suffix}-process.txt';tick=time.perf_counter();peak=0;reason=None
    with (ROOT/log).open('x',encoding='utf-8') as stream:
        proc=subprocess.Popen([sys.executable]+arguments,cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT)
        while proc.poll() is None:
            mem=Memory();mem.cb=ctypes.sizeof(mem)
            if psapi.GetProcessMemoryInfo(int(proc._handle),ctypes.byref(mem),mem.cb):peak=max(peak,mem.WorkingSetSize,mem.PrivateUsage)
            elif proc.poll() is None:reason='memory_monitor_failed'
            if peak>768*1024**2:reason='memory_ceiling'
            if time.perf_counter()-tick>185:reason='process_watchdog'
            if reason:proc.kill();proc.wait();break
            time.sleep(.25)
    record={'experiment':ident,'exit_code':proc.returncode,'reason':reason,'seconds':time.perf_counter()-tick,'peak_sampled_bytes':peak,'log':log}
    path='results/phase30_processes.json';records=load(path) if (ROOT/path).exists() else []
    records.append(record);save(path,records)
    if proc.returncode or reason:raise RuntimeError(record)
    output=json.loads((ROOT/log).read_text(encoding='utf-8').strip().splitlines()[-1])['output']
    data=load(output)
    print({'experiment':ident,'seconds':record['seconds'],'output':output,'exact':data.get('exact')},flush=True)
    return output,data
