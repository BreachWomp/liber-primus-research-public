"""E056 calibration supervisor with wall and resident/private memory ceilings."""
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]


class Memory(ctypes.Structure):
    _fields_=[('cb',wintypes.DWORD),('PageFaultCount',wintypes.DWORD)]+[(name,ctypes.c_size_t) for name in
        ('PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage',
         'QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage','PrivateUsage')]


def main():
    if os.name!='nt':raise RuntimeError('Windows memory supervisor required')
    psapi=ctypes.WinDLL('psapi',use_last_error=True)
    psapi.GetProcessMemoryInfo.argtypes=[wintypes.HANDLE,ctypes.POINTER(Memory),wintypes.DWORD]
    psapi.GetProcessMemoryInfo.restype=wintypes.BOOL
    started=time.perf_counter();records=[]
    jobs=[('calibration',0)]
    env=os.environ.copy();env['PYTHONIOENCODING']='utf-8'
    env['PYTHONPATH']=str(ROOT/'src')+os.pathsep+str(ROOT/'experiments')
    env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
    for kind,index in jobs:
        if time.perf_counter()-started>180:raise TimeoutError('Phase budget exhausted')
        path=ROOT/'results/E056-process.txt'; tick=time.perf_counter(); peak=0; reason=None
        with path.open('w',encoding='utf-8') as stream:
            process=subprocess.Popen([sys.executable,'experiments/context_phase_controls.py'],
                                     cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT)
            while process.poll() is None:
                memory=Memory();memory.cb=ctypes.sizeof(memory)
                if not psapi.GetProcessMemoryInfo(int(process._handle),ctypes.byref(memory),memory.cb):
                    if process.poll() is None:reason='memory_monitor_failed'
                else:peak=max(peak,memory.WorkingSetSize,memory.PrivateUsage)
                if peak>768*1024**2:reason='memory_ceiling'
                if time.perf_counter()-tick>185:reason='process_watchdog'
                if time.perf_counter()-started>180:reason='phase_watchdog'
                if reason:process.kill();process.wait();break
                time.sleep(.25)
        record={'kind':kind,'index':index,'exit_code':process.returncode,'reason':reason,
                'seconds':time.perf_counter()-tick,'peak_sampled_bytes':peak,'log':str(path.relative_to(ROOT))}
        records.append(record);print(json.dumps(record),flush=True)
        (ROOT/'results/phase20_context_processes.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')
        if process.returncode or reason:raise RuntimeError(record)


if __name__=='__main__':main()
