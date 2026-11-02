"""Control-gated E019 driver, with one worker and a 400 second family bound."""
import json
from pathlib import Path
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]

def main():
    tick=time.perf_counter();outputs=[]
    def call(mode,first=0,last=55):
        remaining=400-(time.perf_counter()-tick)
        if remaining<190:raise TimeoutError('not enough reserved time for next atomic experiment')
        command=[sys.executable,'experiments/affine_plaintext_feedback.py','--mode',mode,'--first',str(first),'--last',str(last)]
        result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=190)
        print(result.stdout,flush=True)
        if result.returncode:raise RuntimeError(result.stderr)
        path=json.loads(result.stdout.strip().splitlines()[-1])['output'];outputs.append(path)
        (ROOT/'checkpoints/phase5_feedback.json').write_text(json.dumps({'outputs':outputs,'seconds':time.perf_counter()-tick},indent=2)+'\n',encoding='utf-8')
        return json.loads((ROOT/path).read_text(encoding='utf-8'))
    controls=call('controls')
    if not controls['gate_passed']:
        print(json.dumps({'status':'control_gate_failed','unknown_scan_launched':False}));return
    pages=call('pages')['pages'];chosen=max(pages,key=lambda p:p['top'][0]['score'])['page']
    number=int(chosen.split('-')[1]);result=call('null',number,number)
    print(json.dumps({'status':'completed','selected':chosen,'p':result['null_calibration']['monte_carlo_p'],'seconds':time.perf_counter()-tick}),flush=True)

if __name__=='__main__':main()
