"""Small independent checks of published claims; remote content is never executed."""
from html.parser import HTMLParser
import re
import time
from attack_support import ROOT,load,digest
from registry import registered

FOLDER='sources/community_claim_2026-10-20'
class PlainText(HTMLParser):
    def __init__(self):super().__init__();self.parts=[];self.hidden=0
    def handle_starttag(self,tag,attrs):
        if tag in ('script','style'):self.hidden+=1
    def handle_endtag(self,tag):
        if tag in ('script','style'):self.hidden=max(0,self.hidden-1)
    def handle_data(self,data):
        if not self.hidden and data.strip():self.parts.append(data.strip())

def run():
    tick=time.perf_counter();manifest=load(FOLDER+'/manifest.json')
    for source in manifest['requests']:
        if 'path' in source:assert digest(source['path'])==source['sha256']
    parser=PlainText();parser.feed((ROOT/FOLDER/'project.html').read_text(encoding='utf-8'))
    content='\n'.join(parser.parts)
    prior=load('results/E023-glyph-audit-8315f5c684bb.json');bytehash=prior['byte_sha256']
    alternate='8db2a93497bc02bbf0ab07ac3cf96edd227fec630232c04ea35493d3a7d7b65e'
    assert bytehash in content and alternate in content
    powers=[pow(11,k,29) for k in range(1,29)];order=next(k for k,value in enumerate(powers,1) if value==1)
    a,b=0,1;states=[]
    for k in range(1,1001):
        a,b=b,(a+b)%29;states.append([a,b])
        if (a,b)==(0,1):period=k;break
    else:raise AssertionError('Period not found within fixed bound')
    assert order==28 and period==14
    fixtures={f['id']:f for f in load('known_solutions/fixtures.json')}
    assert fixtures['LP2-56_totient_primes']['skip_positions']==[56]
    assert fixtures['LP2-57_direct']['cipher']=='direct'
    assert time.perf_counter()-tick<30
    return {'experiment':'E029-community-claim-triage','status':'completed',
        'project_url':'https://21skibidiserb37.gitlab.io/xyzsolving333/',
        'post_url':'https://www.reddit.com/r/mystery/comments/1x0432x/proof_5_new_liber_primus_pages_solved/',
        'published_digest_matches_E023':bytehash,'alternate_claimed_authoritative_digest':alternate,
        'digest_interpretation':'E023 reproduces a byte sequence already reported by this source; no novelty claim. Alternate digest provenance has not been established.',
        'order_11_mod29':order,'powers_11_mod29':powers,'pisano_29':period,'fibonacci_states_until_return':states,
        'mathematical_limit':'These two arithmetic facts alone do not imply a particular cipher or yield unknown plaintext.',
        'known_solution_classification':'LP2-56 and LP2-57 are existing source-anchored controls, not previously unknown solutions.',
        'unverified':['Historical provenance of claimed sexagesimal.bin','RSA identification from256-byte length',
                      'Any new plaintext arising from claimed matrix inversion','Entire project correctness outside the scoped checks'],
        'remote_code_executed':False,'wall_seconds':time.perf_counter()-tick,'new_decryptions':[]}

if __name__=='__main__':
    registered('E029-community-claim-triage',{'seconds':30,'seed':None},[
        'experiments/community_claim_triage.py','experiments/community_claim_plan.json',
        'experiments/attack_support.py',FOLDER+'/manifest.json',FOLDER+'/project.html',FOLDER+'/mirror.html',FOLDER+'/reddit.html',
        'results/E023-glyph-audit-8315f5c684bb.json','known_solutions/fixtures.json'],run)
