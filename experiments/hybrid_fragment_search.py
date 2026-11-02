"""Fixed union of complementary blind searches; exact prior runs may be reused."""
from attack_support import top_unique
from context_phase_search import alternatives
from constrained_fragment_search import search as constrained
from context_blind_search import search as independent


def search(values,spans,model,lookup,deadline,cached=None):
    cached=cached or {};branches={};candidates=[]
    for name,solver in (('constrained',constrained),('independent',independent)):
        if name in cached:
            result=cached[name]['result']
            branches[name]={'cached_output':cached[name]['output'],'cached_sha256':cached[name]['sha256']}
        else:
            result=solver(values,spans,model,lookup,deadline)
            branches[name]={'result':result}
        candidates+=result['top']
    top=top_unique(candidates,keep=3)
    return {'branches':branches,'top':top,'alternatives':alternatives(values,spans,top[0],model)}
