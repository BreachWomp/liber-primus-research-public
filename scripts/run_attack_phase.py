"""Resume-aware, bounded second phase; one result per page prevents lost work."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def utc():return datetime.now(timezone.utc).isoformat()
def save(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def append(obj):
    with (ROOT/"experiment_log.jsonl").open("a",encoding="utf-8") as f:f.write(json.dumps(obj,sort_keys=True)+"\n")


def run(mode,budget):
    started=time.perf_counter();env=dict(os.environ,PYTHONUTF8="1",OMP_NUM_THREADS="1",OPENBLAS_NUM_THREADS="1")
    gate=subprocess.run([sys.executable,"-m","unittest","discover","-s","tests","-v"],cwd=ROOT,env=env,
                        capture_output=True,text=True,encoding="utf-8",timeout=60)
    (ROOT/"results/validation_phase2.txt").write_text(gate.stdout+gate.stderr,encoding="utf-8")
    if gate.returncode:raise RuntimeError("tests failed; see validation_phase2.txt")
    dependency_paths=["experiments/selective_attack.py","experiments/attack_support.py","experiments/phase2_plan.json",
                      "src/liberprimus/decoding.py","src/liberprimus/alphabet.py","src/liberprimus/ciphers.py",
                      "known_solutions/fixtures.json","transcriptions/pages.json"]
    dependency_paths+=sorted(str(p.relative_to(ROOT)).replace("\\","/") for p in (ROOT/"data/raw/relikd/pages").glob("solved_*.txt"))
    dependencies={p:sha(ROOT/p) for p in dependency_paths}
    history=[json.loads(line) for line in (ROOT/"experiment_log.jsonl").read_text(encoding="utf-8").splitlines()]
    pages=[p for p in json.loads((ROOT/"transcriptions/pages.json").read_text(encoding="utf-8")) if p["edition"]=="LP2" and p["page"]<=55 and p["runes"]]
    tasks=[]
    if mode in ("controls","all"):tasks.append(("E006-selective-control-benchmark",["--mode","controls"]))
    for family in ("dictionary","streams"):
        if mode in (family,"all"):
            prefix="E007" if family=="dictionary" else "E008"
            for page in pages:
                tasks.append((f"{prefix}-{family}-{page['id']}",["--mode",family,"--first",str(page["page"]),"--last",str(page["page"]),"--max-offset","255"]))
    records=[]
    for ident,params in tasks:
        fingerprint=hashlib.sha256(json.dumps({"dependencies":dependencies,"parameters":params,"timeout":180,"python":platform.python_version()},sort_keys=True).encode()).hexdigest()
        previous=next((r for r in reversed(history) if r.get("fingerprint")==fingerprint and r.get("status")=="completed"),None)
        if previous and (ROOT/previous["output"]).exists() and sha(ROOT/previous["output"])==previous["output_sha256"]:
            records.append(previous);continue
        remaining=budget-(time.perf_counter()-started)
        if remaining<1:break
        path=Path("results")/f"{ident}-{fingerprint[:12]}.json"
        command=[sys.executable,"experiments/selective_attack.py",*params,"--timeout-seconds","180","--output",str(ROOT/path)]
        row={"experiment":ident,"fingerprint":fingerprint,"input_dependencies":dependencies,"parameters":params,
             "started_at":utc(),"status":"started","output":path.as_posix(),"command":["python",*command[1:]]}
        append(row);tick=time.perf_counter()
        try:
            result=subprocess.run(command,cwd=ROOT,env=env,capture_output=True,text=True,encoding="utf-8",timeout=min(190,remaining))
            log=path.with_suffix(".log");(ROOT/log).write_text(result.stdout+result.stderr,encoding="utf-8")
            row.update(status="completed" if result.returncode==0 else "failed",returncode=result.returncode,console_log=log.as_posix())
            if result.returncode==0:row["output_sha256"]=sha(ROOT/path)
            print(json.dumps({"id":ident,"status":row["status"],"seconds":time.perf_counter()-tick}),flush=True)
            if result.returncode:print(result.stderr[-2000:],flush=True)
        except subprocess.TimeoutExpired:row["status"]="timeout"
        row.update(finished_at=utc(),wall_seconds=time.perf_counter()-tick);append(row);records.append(row)
        save(ROOT/f"checkpoints/phase2_{mode}.json",{"created_at":utc(),"records":records,"wall_seconds":time.perf_counter()-started})
        if row["status"]!="completed":break
    save(ROOT/f"checkpoints/phase2_{mode}.json",{"created_at":utc(),"records":records,"wall_seconds":time.perf_counter()-started,
        "requested_tasks":len(tasks),"completed_tasks":sum(r["status"]=="completed" for r in records),"budget_seconds":budget})
    print(json.dumps({"mode":mode,"requested":len(tasks),"completed":sum(r["status"]=="completed" for r in records),"seconds":time.perf_counter()-started}),flush=True)


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mode",choices=["controls","dictionary","streams","all"],required=True)
    p.add_argument("--budget-seconds",type=float,default=900)
    args=p.parse_args()
    if args.budget_seconds<=0:p.error("positive budget required")
    run(args.mode,args.budget_seconds)
