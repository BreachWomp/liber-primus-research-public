"""Restore historical files without rewriting any completed experiment record."""
import hashlib
import json
from pathlib import Path
import subprocess
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]


def main():
    assert (ROOT/'checkpoints/phase26_controls_complete.json').exists()
    target=ROOT/'experiments/delayed_affine_feedback_plan.json'
    assert not target.exists()
    paths=('experiments/affine_feedback_plan.json','experiments/affine_feedback_controls.py','scripts/run_affine_feedback_controls.py')
    aliases={}
    for path in paths:
        archive='checkpoints/phase26_input_snapshot/'+path
        assert (ROOT/path).read_bytes()==(ROOT/archive).read_bytes()
        aliases[path]={'archive':archive,'sha256':hashlib.sha256((ROOT/archive).read_bytes()).hexdigest()}
    target.write_bytes((ROOT/paths[0]).read_bytes())
    (ROOT/paths[0]).write_bytes(subprocess.check_output(['git','show','HEAD:'+paths[0]],cwd=ROOT))
    for path in ('experiments/affine_feedback_controls.py','scripts/verify_affine_feedback.py'):
        p=ROOT/path;s=p.read_text(encoding='utf-8')
        s=s.replace('experiments/affine_feedback_plan.json','experiments/delayed_affine_feedback_plan.json')
        if path.startswith('scripts/'):
            s=s.replace('from affine_feedback_factors import', 'from phase26_provenance import verify_dependency\nfrom affine_feedback_factors import')
            s=s.replace('for dep,digest in event[\'input_dependencies\'].items():assert sha(dep)==digest,dep',
                        'for dep,digest in event[\'input_dependencies\'].items():verify_dependency(dep,digest)')
        else:
            s=s.replace('DEPS=OLD_DEPS+[PLAN,', "DEPS=OLD_DEPS+[PLAN,'experiments/phase26_provenance.py',")
        p.write_text(s,encoding='utf-8')
    p=ROOT/'scripts/run_affine_feedback_controls.py';s=p.read_text(encoding='utf-8')
    s=s.replace('from run_context_calibration import Memory','from run_context_calibration import Memory\nfrom phase26_provenance import verify_dependency')
    s=s.replace("for path,digest in old['input_dependencies'].items():assert sha(path)==digest,path", "for path,digest in old['input_dependencies'].items():verify_dependency(path,digest)")
    p.write_text(s,encoding='utf-8')
    record={'created_at':datetime.now(timezone.utc).isoformat(),'base_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'reason':'E072 plan and new test filename collided with historical E019 files. Tests restored before E072 completion; historical plan restored after the active batch finished. No E072 output or log entry rewritten.',
        'archived_inputs':aliases,'current_plan':'experiments/delayed_affine_feedback_plan.json',
        'current_tests':'tests/test_delayed_affine_feedback.py',
        'reproduction':'For the original fingerprints reconstruct an isolated checkout at base_commit, add the new unchanged dependencies from this checkpoint, and overlay each archive at its original relative path. Never overlay historical files in the research working tree. Current runner uses the uniquely named identical plan; supervisor skips completed E072 tasks by verifying archived bytes.',
        'new_decryptions':[]}
    (ROOT/'checkpoints/phase26_path_migration.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    print('Historical paths restored; completed-run dependency snapshots recorded.')


if __name__=='__main__':main()
