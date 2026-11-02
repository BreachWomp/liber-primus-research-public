"""Bounded public GitLab metadata retrieval, never execute retrieved content."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'sources/claim_repository_2026-10-20'
API='https://gitlab.com/api/v4/projects/21skibidiserb37%2Fxyzsolving333'


def main():
    manifest_path=FOLDER/'manifest.json'
    if manifest_path.exists():
        prior=json.loads(manifest_path.read_text(encoding='utf-8'))
        for row in prior['requests']:
            if 'path' in row:
                assert hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256']
        print('Preserved retrieval already exists; skipped')
        return
    FOLDER.mkdir(exist_ok=True);tick=time.perf_counter()
    manifest={'notice':'Public HTTPS only. Exact HTTP bodies retained; no downloaded code executed. A current repository does not authenticate a historical onion-server drop.',
              'limits':{'seconds':120,'requests':8,'bytes_per_response':2000000,'tree_pages':4},
              'requests':[],'tree_complete':False,'candidate_paths':[]}
    def fetch(url,label):
        if time.perf_counter()-tick>100 or len(manifest['requests'])>=8:raise TimeoutError('Retrieval budget')
        record={'url':url,'retrieved_at_utc':datetime.now(timezone.utc).isoformat()}
        manifest['requests'].append(record)
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'LiberPrimusResearch/1.0'})
            try:response=urllib.request.urlopen(req,timeout=12)
            except urllib.error.HTTPError as exc:response=exc
            with response:
                data=response.read(2000001)
                record.update(status=response.code,final_url=response.url)
                if len(data)>2000000:raise ValueError('Response size limit exceeded')
                path=FOLDER/(label+'.raw')
                path.write_bytes(data)
                record.update(path=path.relative_to(ROOT).as_posix(),bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
                if response.code!=200:return None,{}
                return json.loads(data),dict(response.headers)
        except (OSError,ValueError) as exc:
            record['error']=str(exc)
            return None,{}
    try:
        commits,_=fetch(API+'/repository/commits?per_page=1','head')
        if not isinstance(commits,list) or not commits:return
        commit=commits[0]['id']
        if len(commit)!=40 or any(c not in '0123456789abcdef' for c in commit):raise ValueError('Invalid commit')
        manifest['pinned_commit']=commit;tree=[]
        for page in range(1,5):
            data,headers=fetch(API+f'/repository/tree?ref={commit}&recursive=true&per_page=100&page={page}',f'tree-{page}')
            if not isinstance(data,list):break
            tree.extend(data)
            if not headers.get('x-next-page',headers.get('X-Next-Page','')):
                manifest['tree_complete']=True;break
        manifest['tree_entries']=len(tree)
        manifest['candidate_paths']=[r['path'] for r in tree if r.get('type')=='blob' and
            any(s in r['path'].lower() for s in ('sexagesimal','onion','stage11','provenance'))]
        print(json.dumps({'commit':commit,'tree_entries':len(tree),'tree_complete':manifest['tree_complete'],
                          'candidate_paths':manifest['candidate_paths']}),flush=True)
    finally:
        manifest['seconds']=time.perf_counter()-tick
        manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({'manifest':manifest_path.relative_to(ROOT).as_posix(),'seconds':manifest['seconds']}))


if __name__=='__main__':main()
