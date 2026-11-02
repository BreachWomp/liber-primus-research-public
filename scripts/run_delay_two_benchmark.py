from delay_two_supervisor import run_job,save

if __name__=='__main__':
    path,data=run_job('E077-benchmark',['experiments/delay_two_benchmark.py'])
    save('checkpoints/phase28_benchmark_complete.json',{'output':path,'gate_passed':data['gate_passed']})
    print({k:data[k] for k in ('literal_prefix_comparisons','max_absolute_error','benchmark_seconds','gate_passed')})
