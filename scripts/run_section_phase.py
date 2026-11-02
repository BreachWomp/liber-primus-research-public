"""Run registered section tasks sequentially within one total wall budget."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]


def main(budget):
    tick=time.perf_counter();plan=json.loads((ROOT/"experiments/section_plan.json").read_text(encoding="utf-8"));records=[]
    def execute(section,replicates=0):
        remaining=budget-(time.perf_counter()-tick)
        if remaining<1:raise TimeoutError("section phase total budget exhausted")
        command=[sys.executable,"experiments/section_stream_attack.py","--section",section,
                 "--replicates",str(replicates),"--seconds","180","--seed","3301012"]
        result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,encoding="utf-8",timeout=min(190,remaining))
        print(result.stdout,flush=True)
        if result.returncode:raise RuntimeError(result.stderr)
        last=json.loads(result.stdout.strip().splitlines()[-1]);path=last["output"]
        records.append(path)
        (ROOT/"checkpoints/phase3_sections.json").write_text(json.dumps({"outputs":records,"seconds":time.perf_counter()-tick},indent=2)+"\n",encoding="utf-8")
        return json.loads((ROOT/path).read_text(encoding="utf-8"))
    execute("control")
    results=[execute(section["id"]) for section in plan["sections"]]
    selected=max(results,key=lambda r:r["top"][0]["score"])["section"]["id"]
    execute(selected,plan["null"]["replicates"])
    print(json.dumps({"status":"completed","selected_for_null":selected,"seconds":time.perf_counter()-tick}),flush=True)


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--budget-seconds",type=float,default=420)
    args=p.parse_args();main(args.budget_seconds)
