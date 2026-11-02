"""Freeze E073 only after the independently checked E072 control gate."""
from datetime import datetime,timezone
import json
from attack_support import ROOT,load,digest


def main():
    validation=load('results/phase26_controls_validation.json')
    assert validation['full_gate_passed'] and len(validation['controls'])==16
    path=ROOT/'experiments/affine_feedback_unknown_plan.json'
    assert not path.exists()
    plan=load('experiments/bilinear_feedback_unknown_plan.json')
    plan.update(registered_at=datetime.now(timezone.utc).isoformat(),experiment='E073',hypothesis='H049',
        control_validation='results/phase26_controls_validation.json',
        control_validation_sha256=digest('results/phase26_controls_validation.json'),
        required_gate='All16 E072 plaintext/key/a/b/c exact and injected families retained; independent source/queue/retained-family/score checks and full-screen deterministic replay passed.',
        solver='Frozen E072,659344 families,top8 per period,232 full optimizations,12 refinements. a,b1..28,c0..28,m4..32. No skips, no language/key resets within inputs. Same parameters for observed/null.',
        null_seed=3302073,family_seconds=2400,phase_seconds=3600,
        limits='Heuristic top8 screening, not exhaustive key search. E071 independently enumerates27608 family scores; each attack independently checks232 retained families and replays complete screen. No skipped runes or hidden boundaries. Grouping unauthenticated. No community claims.',
        registration_script_sha256=digest('scripts/register_phase26_unknown.py'))
    path.write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
    print({'plan':str(path.relative_to(ROOT)),'inputs':56,'control_gate':True})


if __name__=='__main__':main()
