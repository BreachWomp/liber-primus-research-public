"""Append-only experiment registration shared by new research runners."""
from datetime import datetime,timezone
import hashlib
import json
import platform
import time
from attack_support import ROOT,digest


def registered(ident,parameters,dependencies,compute):
    dependencies=sorted(set(dependencies+["experiments/registry.py"]))
    hashes={p:digest(p) for p in dependencies}
    fingerprint=hashlib.sha256(json.dumps({"dependencies":hashes,"parameters":parameters,
        "python":platform.python_version()},sort_keys=True).encode()).hexdigest()
    output=f"results/{ident}-{fingerprint[:12]}.json"
    history=[json.loads(line) for line in (ROOT/"experiment_log.jsonl").read_text(encoding="utf-8").splitlines()]
    old=next((e for e in reversed(history) if e.get("fingerprint")==fingerprint and e.get("status")=="completed"),None)
    if old and (ROOT/old["output"]).exists() and digest(old["output"])==old["output_sha256"]:
        print(json.dumps({"status":"skipped_completed","output":old["output"]}),flush=True)
        return json.loads((ROOT/old["output"]).read_text(encoding="utf-8"))
    row={"experiment":ident,"fingerprint":fingerprint,"input_dependencies":hashes,"parameters":parameters,
         "status":"started","started_at":datetime.now(timezone.utc).isoformat(),"output":output}
    def append():
        with (ROOT/"experiment_log.jsonl").open("a",encoding="utf-8") as f:f.write(json.dumps(row,sort_keys=True)+"\n")
    append();tick=time.perf_counter()
    try:
        result=compute()
        (ROOT/output).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        row.update(status="completed",output_sha256=digest(output))
        print(json.dumps({"status":"completed","output":output,"seconds":time.perf_counter()-tick}),flush=True)
        return result
    except Exception as exc:row.update(status="failed",error=repr(exc));raise
    finally:
        row.update(finished_at=datetime.now(timezone.utc).isoformat(),wall_seconds=time.perf_counter()-tick);append()
