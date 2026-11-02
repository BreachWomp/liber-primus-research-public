"""Exact small-state audit of accepted-move versus proposal-count sampling.

No upstream program is imported or executed. Transition matrices are derived
independently and evaluated with exact rational arithmetic.
"""
from __future__ import annotations
import argparse
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import time


def doublets(state):
    return sum(a==b for a,b in zip(state,state[1:]))


def multiply(distribution,matrix):
    return [sum(distribution[i]*matrix[i][j] for i in range(len(distribution))) for j in range(len(distribution))]


def build(multiset=(0,0,1,1,2),target=1):
    states=sorted(s for s in set(itertools.permutations(multiset)) if doublets(s)==target)
    index={state:i for i,state in enumerate(states)}
    adjacency=[]
    n=len(multiset)
    for state in states:
        neighbors=[]
        for i,j in itertools.combinations(range(n),2):
            if state[i]==state[j]:
                continue
            new=list(state);new[i],new[j]=new[j],new[i]
            if doublets(new)==target:
                neighbors.append(index[tuple(new)])
        adjacency.append(neighbors)
    size=len(states)
    jump=[[Fraction(0) for _ in states] for _ in states]
    proposal=[[Fraction(0) for _ in states] for _ in states]
    for i,neighbors in enumerate(adjacency):
        if not neighbors:
            raise ValueError("Accepted-move chain can stall forever at a state with zero admissible moves")
        for j in neighbors:
            jump[i][j]+=Fraction(1,len(neighbors))
            proposal[i][j]+=Fraction(2,n*n)  # two ordered proposals out of n^2
        proposal[i][i]=1-sum(proposal[i])
    components=[]
    unseen=set(range(size))
    while unseen:
        stack=[unseen.pop()];seen=set(stack)
        while stack:
            for neighbor in adjacency[stack.pop()]:
                if neighbor not in seen:
                    seen.add(neighbor);unseen.discard(neighbor);stack.append(neighbor)
        components.append(sorted(seen))
    return states,adjacency,jump,proposal,components


def run(root):
    start=time.perf_counter()
    states,adjacency,jump,proposal,components=build()
    uniform=[Fraction(1,len(states))]*len(states)
    degrees=[len(x) for x in adjacency]
    degree_stationary=[Fraction(d,sum(degrees)) for d in degrees]
    after_jump=multiply(uniform,jump)
    after_proposal=multiply(uniform,proposal)
    assert multiply(degree_stationary,jump)==degree_stationary
    assert after_proposal==uniform
    assert after_jump!=uniform
    source=root/"data/raw/prior_art/r5_doublet_anatomy.py"
    return {"experiment":"E004-sampler-audit","claim":"Fixed accepted-swap steps do not generally sample the uniform fixed-count/fixed-doublet ensemble.",
        "method":"Exhaustive state enumeration and exact Fraction transition matrices; upstream not executed",
        "parameters":{"multiset":[0,0,1,1,2],"doublets":1,"proposal":"ordered uniform i,j from 0..4 including equality"},
        "state_count":len(states),"degrees":degrees,"components":components,
        "states":[{"sequence":list(s),"degree":degrees[i],"uniform":str(uniform[i]),
                   "after_one_accepted_step_from_uniform":str(after_jump[i]),
                   "jump_chain_stationary":str(degree_stationary[i])} for i,s in enumerate(states)],
        "accepted_transition_matrix":[[str(v) for v in row] for row in jump],
        "proposal_transition_matrix":[[str(v) for v in row] for row in proposal],
        "uniform_stationary_for_accepted_chain":False,"degree_stationary_exactly_verified":True,
        "uniform_stationary_for_proposal_chain":True,
        "total_variation_after_one_accepted_step":str(sum(abs(a-b) for a,b in zip(after_jump,uniform))/2),
        "total_variation_degree_stationary_from_uniform":str(sum(abs(a-b) for a,b in zip(degree_stationary,uniform))/2),
        "source_audited":{"path":str(source.relative_to(root)).replace("\\","/"),"sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
            "url":"https://github.com/Dukotah/cicada3301/blob/f08b20b632d91209ddbaa747e8e2f23df0c78ba1/liber-primus/analysis/r5_doublet_anatomy.py#L300-L315"},
        "limitations":["A small counterexample disproves a general uniformity guarantee, not every numerical conclusion from the full LP corpus.",
            "Fixed proposal count repairs the stationary target only; it does not prove finite-time mixing or global connectivity on full pages.",
            "The general jump-chain principle is established mathematics; novelty of this application is not claimed.",
            "This test does not execute or benchmark the original large-corpus sampler."],
        "wall_seconds":time.perf_counter()-start,"new_decryptions":[]}


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    result=run(args.root)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:result[k] for k in ["experiment","state_count","degrees","components","total_variation_degree_stationary_from_uniform","wall_seconds"]}))

