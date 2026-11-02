from datetime import datetime,timezone
import hashlib
from delay_two_supervisor import ROOT,load,save,run_job


if __name__=='__main__':
    plan=load('experiments/delay_two_unknown_plan.json');assert load(plan['control_validation'])['full_gate_passed']
    outputs=[];pages=[]
    for page in plan['section_ids']:
        path,row=run_job(f'E079-page-{page}',['experiments/delay_two_unknown.py','page',page,'0'])
        outputs.append(path);pages.append(row)
        save('checkpoints/phase28_unknown_progress.json',{'outputs':outputs})
    winner=max(pages,key=lambda r:r['result']['top'][0]['score']);score=winner['result']['top'][0]['score']
    sha=lambda p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
    selection={'page':winner['page'],'score':score,'source_outputs':{p:sha(p) for p in outputs},'registered_at':datetime.now(timezone.utc).isoformat()}
    path='experiments/delay_two_selection.json'
    if (ROOT/path).exists():assert all(load(path)[k]==v for k,v in selection.items() if k!='registered_at')
    else:save(path,selection)
    nulls=[]
    for i in range(19):
        output,row=run_job(f'E079-null-{winner["page"]}-{i:02}',['experiments/delay_two_unknown.py','null',winner['page'],str(i)])
        outputs.append(output);nulls.append(row)
        save('checkpoints/phase28_unknown_progress.json',{'outputs':outputs})
    exceed=sum(r['result']['top'][0]['score']>=score for r in nulls);p=(1+exceed)/20
    summary={'page':winner['page'],'score':score,'exceedances':exceed,'raw_p':p,'bonferroni55':min(1,55*p),
        'pending_larger_calibration':exceed==0,'selection_sha256':sha(path),'outputs':outputs}
    save('checkpoints/phase28_unknown_complete.json',summary);print({k:v for k,v in summary.items() if k!='outputs'})
