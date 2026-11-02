"""Create E069 preregistration only after independently verified E068 gate."""
from datetime import datetime,timezone
import json
from pathlib import Path
from attack_support import ROOT,load,digest


def main():
    validation=load('results/phase25_controls_validation.json')
    assert validation['full_gate_passed'] and len(validation['controls'])==16
    path=ROOT/'experiments/bilinear_feedback_unknown_plan.json'
    assert not path.exists()
    plan=load('experiments/general_feedback_unknown_plan.json')
    assert len(plan['groups'])==56 and len(plan['section_ids'])==56
    plan.update(registered_at=datetime.now(timezone.utc).isoformat(),experiment='E069',hypothesis='H048',
        control_validation='results/phase25_controls_validation.json',
        control_validation_sha256=digest('results/phase25_controls_validation.json'),
        required_gate='All16 E068 exact plaintext/key/a/b, retained true families and independent literal verification passed.',
        solver='Frozen E068 screen22736 families,top8per period,232 full optimizations,12 refinements. a,b1..28,m4..32,no skips. Histogram objective checked by direct symbol evaluation. No key/language reset within an input. Same parameters for observed/null.',
        null_seed=3302069,family_seconds=2400,phase_seconds=3600,
        limits='Heuristic top8 screening; control success does not prove exhaustiveness. No additive constant, skipped runes or hidden resets. Source grouping not authenticated. No community claims.',
        registration_script_sha256=digest('scripts/register_phase25_unknown.py'))
    path.write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
    print({'plan':str(path.relative_to(ROOT)),'inputs':56,'control_gate':True})


if __name__=='__main__':main()
