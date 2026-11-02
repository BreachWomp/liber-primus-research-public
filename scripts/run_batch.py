"""Run a bounded research batch, preserving fingerprints and append-only history."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"src"))
from liberprimus.alphabet import to_indices
from liberprimus.stats import summary, lag_coincidences, periodic_ic, ngram_counts


def utc():
    return datetime.now(timezone.utc).isoformat()


def write_json(path, obj):
    temporary=path.with_suffix(path.suffix+".tmp")
    temporary.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    temporary.replace(path)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fingerprint(script, parameters):
    dependencies=sorted((ROOT/"src").rglob("*.py"))+[ROOT/script, ROOT/"transcriptions/pages.json", ROOT/"known_solutions/fixtures.json"]
    if "sampler_audit" in script:
        dependencies.append(ROOT/"data/raw/prior_art/r5_doublet_anatomy.py")
    if "period_scan" in script:
        dependencies.append(ROOT/"experiments/markov_followup.py")
    manifest={str(p.relative_to(ROOT)).replace("\\","/"):digest(p) for p in dependencies}
    value={"dependencies":manifest,"parameters":parameters}
    return hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest(),manifest


def append_log(record):
    with (ROOT/"experiment_log.jsonl").open("a",encoding="utf-8") as handle:
        handle.write(json.dumps(record,ensure_ascii=False,sort_keys=True)+"\n")


def baseline():
    source=ROOT/"transcriptions/pages.json"
    pages=json.loads(source.read_text(encoding="utf-8"))
    result=[]
    for page in pages:
        values=to_indices(page["runes"])
        result.append({"id":page["id"],"status":page["status"],**summary(values),
            "lag_coincidences":lag_coincidences(values,max_lag=32),
            "periodic_ic":periodic_ic(values,max_period=32),
            "most_common_bigrams":[{"indices":list(k),"count":v} for k,v in ngram_counts(values,2).most_common(10)]})
    return {"experiment":"E000-descriptive-baseline","created_at":utc(),"input_sha256":digest(source),
            "interpretation":"Descriptive estimates only. No p-values for period selection; no cross-page concatenation.","pages":result}


def run(budget_seconds):
    started=time.perf_counter()
    environment=dict(os.environ,PYTHONUTF8="1",OPENBLAS_NUM_THREADS="1",OMP_NUM_THREADS="1")
    (ROOT/"results").mkdir(exist_ok=True)
    (ROOT/"checkpoints").mkdir(exist_ok=True)
    tests=subprocess.run([sys.executable,"-m","unittest","discover","-s","tests","-v"],cwd=ROOT,env=environment,
                         text=True,encoding="utf-8",capture_output=True,timeout=min(60,budget_seconds))
    (ROOT/"results/validation.txt").write_text(tests.stdout+tests.stderr,encoding="utf-8")
    if tests.returncode:
        raise RuntimeError("Validation failed; inspect results/validation.txt. No experiments launched.")
    if not (ROOT/"tests/test_known_solutions.py").exists():
        raise RuntimeError("Known-solution gate is not installed yet")
    print("Known-solution and engine validation passed",flush=True)
    baseline_path=ROOT/"results/baseline.json"
    write_json(baseline_path,baseline())
    commands=[
        ("E001-adjacency","experiments/adjacency.py",["--replicates","9999","--seed","330120261018","--timeout-seconds","120"],130),
        ("E002-markov-heldout","experiments/markov_followup.py",["--replicates","9999","--seed","3301003","--timeout-seconds","120"],130),
        ("E003-bounded-cipher-screen","experiments/cipher_screen.py",["--seed","3301003","--timeout-seconds","180"],190),
        ("E004-sampler-audit","experiments/sampler_audit.py",[],30),
        ("E005-heldout-period-scan","experiments/period_scan.py",["--replicates","9999","--seed","3301005","--timeout-seconds","180"],190),
    ]
    records=[]
    history=[]
    logfile=ROOT/"experiment_log.jsonl"
    if logfile.exists():
        history=[json.loads(line) for line in logfile.read_text(encoding="utf-8").splitlines() if line.strip()]
    for experiment,script,parameters,limit in commands:
        fp,dependencies=fingerprint(script,parameters)
        previous=next((row for row in reversed(history) if row.get("fingerprint")==fp and row.get("status")=="completed"),None)
        if previous and (ROOT/previous["output"]).exists() and digest(ROOT/previous["output"])==previous["output_sha256"]:
            records.append(previous)
            print(f"{experiment}: resume skip, identical fingerprint and output checksum",flush=True)
            continue
        remaining=budget_seconds-(time.perf_counter()-started)
        if remaining < 1:
            print("Batch budget exhausted; remaining experiments stay queued",flush=True)
            break
        output=Path("results")/f"{experiment}-{fp[:12]}.json"
        command=[sys.executable,script,"--root",str(ROOT),*parameters,"--output",str(ROOT/output)]
        record={"experiment":experiment,"fingerprint":fp,"input_dependencies":dependencies,"parameters":parameters,
                "started_at":utc(),"command":["python",*command[1:]],"output":output.as_posix(),
                "python_version":platform.python_version(),"status":"started"}
        append_log(record)
        tick=time.perf_counter()
        try:
            child=subprocess.run(command,cwd=ROOT,env=environment,text=True,encoding="utf-8",capture_output=True,
                                 timeout=min(limit,remaining))
            record.update(status="completed" if child.returncode==0 else "failed",returncode=child.returncode)
            logpath=output.with_suffix(".log")
            (ROOT/logpath).write_text(child.stdout+child.stderr,encoding="utf-8")
            record["console_log"]=logpath.as_posix()
            if child.returncode==0:
                record["output_sha256"]=digest(ROOT/output)
            print(child.stdout.strip() or f"{experiment}: {record['status']}",flush=True)
            if child.returncode:
                print(child.stderr,flush=True)
        except subprocess.TimeoutExpired:
            record["status"]="timeout"
        record.update(finished_at=utc(),wall_seconds=time.perf_counter()-tick)
        append_log(record)
        records.append(record)
        checkpoint={"created_at":utc(),"records":records,"batch_wall_seconds":time.perf_counter()-started,
                    "new_decryptions":[],"status":"partial_batch"}
        write_json(ROOT/"checkpoints/latest_batch.json",checkpoint)
    checkpoint={"created_at":utc(),"records":records,"batch_wall_seconds":time.perf_counter()-started,
                "budget_seconds":budget_seconds,"new_decryptions":[],"status":"batch_finished_review_required"}
    write_json(ROOT/"checkpoints/latest_batch.json",checkpoint)
    print(json.dumps({"checkpoint":"checkpoints/latest_batch.json","seconds":checkpoint["batch_wall_seconds"],
                      "statuses":{r["experiment"]:r["status"] for r in records}}),flush=True)
    if any(r["status"]!="completed" for r in records):
        return 1
    return 0


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--budget-seconds",type=float,default=900)
    args=parser.parse_args()
    if args.budget_seconds <= 0:
        parser.error("--budget-seconds must be positive")
    raise SystemExit(run(args.budget_seconds))
