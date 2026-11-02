"""Complete all fixed confirmation batches or retain a resumable budget checkpoint."""
import json
from pathlib import Path
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]

def main():
    tick=time.perf_counter();outputs=[]
    for batch in range(20):
        remaining=350-(time.perf_counter()-tick)
        if remaining<25:raise TimeoutError('confirmation budget; completed batches retained')
        r=subprocess.run([sys.executable,'experiments/affine_feedback_confirmation.py','--batch',str(batch)],
            cwd=ROOT,capture_output=True,text=True,encoding='utf-8',timeout=min(190,remaining))
        print(r.stdout,flush=True)
        if r.returncode:raise RuntimeError(r.stderr)
        output=json.loads(r.stdout.strip().splitlines()[-1])['output'];outputs.append(output)
        (ROOT/'checkpoints/phase5_confirmation.json').write_text(json.dumps({'outputs':outputs,'seconds':time.perf_counter()-tick},indent=2)+'\n',encoding='utf-8')
    total=sum(json.loads((ROOT/p).read_text(encoding='utf-8'))['exceedances'] for p in outputs)
    print(json.dumps({'status':'completed','replicates':4000,'exceedances':total,'raw_p':(1+total)/4001,'seconds':time.perf_counter()-tick}),flush=True)

if __name__=='__main__':main()
