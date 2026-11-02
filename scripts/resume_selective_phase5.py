"""Resume-aware bounded orchestration with control gates and per-batch outputs."""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]


def main(family,budget):
    tick=time.perf_counter();script="long_autokey_attack.py" if family=="autokey" else "external_selective_attack.py"
    records=[]
    last_compute_seconds=0.0
    def call(mode,first=0,last=55):
        nonlocal last_compute_seconds
        remaining=budget-(time.perf_counter()-tick)
        if remaining<=0:raise TimeoutError("phase total budget")
        # A completed fingerprint may still be skipped by the registry. Reserve
        # enough time for a new batch so avoidable mid-batch kills are uncommon.
        if mode=="pages" and remaining<last_compute_seconds+5:
            raise TimeoutError("checkpoint retained: insufficient budget for another estimated batch")
        command=[sys.executable,"experiments/"+script,"--mode",mode,"--first",str(first),"--last",str(last)]
        started=time.perf_counter()
        try:
            result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,encoding="utf-8",timeout=min(190,remaining))
        except subprocess.TimeoutExpired:
            # subprocess.run has killed and waited for the child at this point.
            log=ROOT/"experiment_log.jsonl"
            events=[json.loads(s) for s in log.read_text(encoding="utf-8").splitlines()]
            latest_by_fp={e["fingerprint"]:e for e in events}
            terminal={fp for fp,e in latest_by_fp.items() if e.get("status") in ("completed","failed","aborted")}
            prefix="E017" if family=="autokey" else "E018"
            pending=[e for e in latest_by_fp.values() if e.get("status")=="started" and e["fingerprint"] not in terminal and e["experiment"].startswith(prefix)]
            if len(pending)==1:
                event={**pending[0],"status":"aborted","finished_at":datetime.now(timezone.utc).isoformat(),
                       "reason":"orchestrator subprocess timeout; child terminated; no scientific output committed",
                       "subprocess_wall_seconds":time.perf_counter()-started}
                with log.open("a",encoding="utf-8") as f:f.write(json.dumps(event,sort_keys=True)+"\n")
            raise
        print(result.stdout,flush=True)
        if result.returncode:raise RuntimeError(result.stderr)
        path=json.loads(result.stdout.strip().splitlines()[-1])["output"]
        records.append(path)
        elapsed=time.perf_counter()-started
        if '"status": "skipped_completed"' not in result.stdout:last_compute_seconds=elapsed
        (ROOT/f"checkpoints/phase5_{family}.json").write_text(json.dumps({"outputs":records,"seconds":time.perf_counter()-tick},indent=2)+"\n",encoding="utf-8")
        return json.loads((ROOT/path).read_text(encoding="utf-8"))
    control=call("controls")
    if not control["gate_passed"]:raise RuntimeError("control gate failed; unknown search not launched")
    rows=[]
    for first in range(0,56,5):
        data=call("pages",first,min(first+4,55));rows+=data["pages"]
    chosen=max(rows,key=lambda r:r["top"][0]["score"])["page"]
    number=int(chosen.split("-")[1]);calibration=call("null",number,number)
    print(json.dumps({"family":family,"status":"completed","pages":len(rows),"selected":chosen,
                      "p":calibration["null_calibration"]["monte_carlo_p"],"seconds":time.perf_counter()-tick}),flush=True)


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--family",choices=["autokey","selective"],required=True)
    p.add_argument("--budget-seconds",type=float,default=650.0);args=p.parse_args();main(args.family,args.budget_seconds)
