from long_substitution_supervisor import run_job,save

if __name__=='__main__':
    outputs=[];controls=[];nulls=[]
    for i in range(12):
        p,r=run_job(f'E083-control-{i}',['experiments/long_substitution_controls.py','control',str(i),'0'])
        outputs.append(p);controls.append(r)
        save('checkpoints/phase30_controls_progress.json',{'outputs':outputs})
    for k in range(3):
        p,r=run_job(f'E083-null-0-{k}',['experiments/long_substitution_controls.py','null','0',str(k)])
        outputs.append(p);nulls.append(r)
        save('checkpoints/phase30_controls_progress.json',{'outputs':outputs})
    summary={'outputs':outputs,'full_gate_passed':all(r['exact'] for r in controls),
        'exact_controls':sum(r['exact'] for r in controls),'null_scores':[r['result']['top']['score'] for r in nulls]}
    save('checkpoints/phase30_controls_complete.json',summary)
    print({k:v for k,v in summary.items() if k!='outputs'})
