"""Preregister fresh second-stage calibration, without pooling adaptive p-values."""
from datetime import datetime,timezone
import json
from attack_support import ROOT,load,digest


def main():
    old=load('results/phase25_unknown_validation.json')
    assert old['pending_larger_calibration'] and old['exceedances']==0 and len(old['nulls'])==19
    selection=load('experiments/bilinear_feedback_selection.json')
    assert selection['section']==old['selected_section'] and selection['score']==old['score']
    path=ROOT/'experiments/bilinear_feedback_more_null_plan.json';assert not path.exists()
    plan={'registered_at':datetime.now(timezone.utc).isoformat(),'experiment':'E070','hypothesis':'H048',
        'section':selection['section'],'observed_score':selection['score'],
        'selection_sha256':digest('experiments/bilinear_feedback_selection.json'),
        'original_validation':'results/phase25_unknown_validation.json',
        'original_validation_sha256':digest('results/phase25_unknown_validation.json'),
        'replicates':list(range(19,118)),'fresh_null_count':99,'seed':'3302069+100*replicate+page_index',
        'algorithm':'Frozen E068 solver and E069 per-page matched null sampler; no new tuning, candidate selection, or altered initializers. Each null repeats all22736-family screening and232-family search.',
        'inference':'Fresh99 only: plus-one p=(1+fresh exceedances)/100, Bonferroni56. Original19 are descriptive, never pooled into an adaptively stopped pvalue. No early stopping or promotion before all99 and independent audit. Minimum corrected p0.56, no significance claim; zero fresh exceedances leaves larger calibration pending.',
        'process_seconds':180,'watchdog_seconds':185,'family_seconds':1500,'phase_seconds':3600,'memory_ceiling_mib':768,'workers':1,
        'limits':'Follow-up was triggered by the original0/19 screen. This finite follow-up may reject an apparent lead but cannot establish corrected significance at0.05. Source/algorithm and selection remain immutable.'}
    path.write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
    print({'experiment':'E070','fresh_nulls':99,'section':plan['section'],'original_exceedances':0})


if __name__=='__main__':main()
