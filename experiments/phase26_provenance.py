"""Resolve exact E072 input bytes archived after a historical filename collision."""
from attack_support import ROOT,digest


def verify_dependency(path, expected):
    if digest(path)==expected:
        return path
    archived='checkpoints/phase26_input_snapshot/'+path
    allowed={'experiments/affine_feedback_plan.json','experiments/affine_feedback_controls.py',
        'scripts/run_affine_feedback_controls.py'}
    assert path in allowed and (ROOT/archived).is_file(),path
    assert digest(archived)==expected,path
    return archived
