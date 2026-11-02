from difference_substitution_supervisor import run_job,save

if __name__=='__main__':
    p,r=run_job('E085-reversible-bridge',['experiments/difference_substitution_bridge.py'])
    save('checkpoints/phase31_bridge_complete.json',{'output':p,'gate_passed':r['gate_passed']})
    print({k:r[k] for k in ('gate_passed','reused_searches','new_optimizer_searches','iv_identity_checks','reencryptions')})
