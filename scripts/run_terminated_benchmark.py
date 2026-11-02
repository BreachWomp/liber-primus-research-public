from terminated_supervisor import run_job,save

if __name__=='__main__':
    path,data=run_job('E080-terminated-benchmark',['experiments/terminated_benchmark.py'])
    save('checkpoints/phase29_benchmark_complete.json',{'output':path,'gate_passed':data['gate_passed']})
    print({k:data[k] for k in ('gates','new_old_strict_wins','maximum_absolute_error','wall_seconds')})
