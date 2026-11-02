from datetime import datetime,timezone
import hashlib
from difference_substitution_supervisor import ROOT,load,save,run_job

if __name__=='__main__':
    plan=load('experiments/difference_substitution_unknown_plan.json');assert load(plan['control_validation'])['full_gate_passed']
    outputs=[];pages=[]
    for item in plan['pages']:
        page=item['page'];p,r=run_job(f'E086-page-{page}',['experiments/difference_substitution_unknown.py','page',page,'0'])
        outputs.append(p);pages.append(r);save('checkpoints/phase31_unknown_progress.json',{'outputs':outputs})
    winner=max(pages,key=lambda r:r['result']['top']['score']);score=winner['result']['top']['score']
    sha=lambda p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
    selection={'page':winner['page'],'score':score,'source_outputs':{p:sha(p) for p in outputs},'registered_at':datetime.now(timezone.utc).isoformat()}
    path='experiments/difference_substitution_selection.json'
    if (ROOT/path).exists():assert all(load(path)[k]==v for k,v in selection.items() if k!='registered_at')
    else:save(path,selection)
    nulls=[]
    for k in range(19):
        p,r=run_job(f'E086-null-{winner["page"]}-{k:02}',['experiments/difference_substitution_unknown.py','null',winner['page'],str(k)])
        outputs.append(p);nulls.append(r);save('checkpoints/phase31_unknown_progress.json',{'outputs':outputs})
    exceed=sum(r['result']['top']['score']>=score for r in nulls);p=(1+exceed)/20
    summary={'page':winner['page'],'score':score,'exceedances':exceed,'raw_p':p,'bonferroni46':min(1,46*p),
        'pending_larger_calibration':exceed==0,'selection_sha256':sha(path),'outputs':outputs}
    save('checkpoints/phase31_unknown_complete.json',summary);print({k:v for k,v in summary.items() if k!='outputs'})
