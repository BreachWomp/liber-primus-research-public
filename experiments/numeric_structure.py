"""Bounded streaming calibration of four byte-table diagnostics."""
import hashlib
import random
import time
from attack_support import load
from registry import registered
from liberprimus.numeric_statistics import statistics, descriptive, NAMES

def run():
    tick = time.perf_counter(); plan = load('experiments/numeric_structure_plan.json')
    source = load(plan['input']); observed = bytes.fromhex(source['byte_hex'])
    assert hashlib.sha256(observed).hexdigest() == source['byte_sha256']
    assert observed == bytes(c['value'] for c in source['cells'])
    controls = {'constant_zero': bytes(256), 'column_stripes': bytes(range(0,256,32))*32}
    targets = {'observed': observed, **controls}
    scores = {label:statistics(data) for label,data in targets.items()}
    exceed = {label:{name:0 for name in NAMES} for label in targets}
    rng = random.Random(plan['seed'])
    for i in range(plan['replicates']):
        simulated = statistics(rng.randbytes(256))
        for label,target in scores.items():
            for name in NAMES:
                exceed[label][name] += simulated[name] >= target[name]
        if i % 128 == 0 and time.perf_counter()-tick > plan['max_seconds']:
            raise TimeoutError('Numeric diagnostic budget exhausted')
    calibration = {label:{name:{'statistic':score,'exceedances':exceed[label][name],
        'raw_p':(1+exceed[label][name])/(1+plan['replicates']),
        'adjusted_p':min(1,4*(1+exceed[label][name])/(1+plan['replicates']))}
        for name,score in target.items()} for label,target in scores.items()}
    for name in NAMES[:3]: assert calibration['constant_zero'][name]['adjusted_p'] < .01
    assert calibration['column_stripes']['column_sum_dispersion']['adjusted_p'] < .01
    return {'experiment':'E024-numeric-structure','status':'completed','plan':plan,
        'input_byte_sha256':source['byte_sha256'],'descriptive':descriptive(observed),
        'calibration':calibration,'controls_passed':4,
        'rejected_at_familywise_005':[name for name,row in calibration['observed'].items() if row['adjusted_p'] <= .05],
        'wall_seconds':time.perf_counter()-tick,'new_decryptions':[]}

if __name__ == '__main__':
    plan = load('experiments/numeric_structure_plan.json')
    registered('E024-numeric-structure', plan, ['experiments/numeric_structure.py',
        'experiments/numeric_structure_plan.json','src/liberprimus/numeric_statistics.py',
        'experiments/attack_support.py',plan['input']], run)
