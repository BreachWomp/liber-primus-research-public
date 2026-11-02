"""E070 fixed fresh-null calibration; retains E069 results and parameters."""
import argparse
import numpy as np
from attack_support import load,digest
from bilinear_feedback_unknown import run as base_run, DEPS as BASE_DEPS
from registry import registered
PLAN='experiments/bilinear_feedback_more_null_plan.json'


def run(section,replicate):
    plan=load(PLAN)
    assert section==plan['section'] and replicate in plan['replicates']
    assert digest('experiments/bilinear_feedback_selection.json')==plan['selection_sha256']
    assert digest(plan['original_validation'])==plan['original_validation_sha256']
    row=base_run('null',section,replicate)
    row['experiment']='E070';row['extension_plan']=plan
    return row


DEPS=BASE_DEPS+[PLAN,'experiments/bilinear_feedback_more_nulls.py','scripts/run_bilinear_feedback_more_nulls.py',
    'experiments/bilinear_feedback_unknown.py','experiments/bilinear_feedback_unknown_plan.json',
    'experiments/bilinear_feedback_selection.json','experiments/section_key_support.py','experiments/section_plan.json',
    'transcriptions/pages.json','results/phase25_controls_validation.json','results/phase25_unknown_validation.json',
    'scripts/verify_bilinear_feedback.py','scripts/verify_bilinear_feedback_unknown.py','scripts/register_phase25_more_nulls.py']
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['null']);parser.add_argument('section');parser.add_argument('replicate',type=int);args=parser.parse_args()
    registered(f'E070-null-{args.section}-{args.replicate:03}',load(PLAN)|vars(args)|{'numpy':np.__version__},DEPS,lambda:run(args.section,args.replicate))
