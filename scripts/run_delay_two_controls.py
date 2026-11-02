from delay_two_supervisor import run_job,save


if __name__=='__main__':
    outputs=[];controls=[]
    for i in range(16):
        path,row=run_job(f'E078-control-{i}',['experiments/delay_two_controls.py','control',str(i)])
        outputs.append(path);controls.append(row)
        save('checkpoints/phase28_controls_progress.json',{'outputs':outputs})
    path,null=run_job('E078-null-5',['experiments/delay_two_controls.py','null','5']);outputs.append(path)
    summary={'outputs':outputs,'full_gate_passed':all(r['exact'] and r['injected_recipe_exact'] and r['injected_family_retained'] for r in controls),
        'exact_controls':sum(r['exact'] for r in controls),'null_score':null['result']['top'][0]['score']}
    save('checkpoints/phase28_controls_complete.json',summary)
    print({k:v for k,v in summary.items() if k!='outputs'})
