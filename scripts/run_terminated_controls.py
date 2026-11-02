from terminated_supervisor import run_job,save

if __name__=='__main__':
    outputs=[];controls=[];nulls=[]
    for i in range(9):
        p,r=run_job(f'E081-control-{i}',['experiments/terminated_controls.py','control',str(i),'0'])
        outputs.append(p);controls.append(r)
        save('checkpoints/phase29_controls_progress.json',{'outputs':outputs})
    for k in range(3):
        p,r=run_job(f'E081-null-2-{k}',['experiments/terminated_controls.py','null','2',str(k)])
        outputs.append(p);nulls.append(r)
        save('checkpoints/phase29_controls_progress.json',{'outputs':outputs})
    summary={'outputs':outputs,'full_gate_passed':all(r['exact'] for r in controls),
        'exact_controls':sum(r['exact'] for r in controls),'null_scores':[r['result']['top']['score'] for r in nulls]}
    save('checkpoints/phase29_controls_complete.json',summary)
    print({k:v for k,v in summary.items() if k!='outputs'})
