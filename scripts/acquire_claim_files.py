"""Retrieve two explicitly named text files at the recorded public commit."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import time
import urllib.parse
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'sources/claim_repository_2026-10-20'


def main():
    target=FOLDER/'files_manifest.json'
    if target.exists():
        for item in json.loads(target.read_text(encoding='utf-8'))['files']:
            assert hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256']
        print('Pinned files already preserved; skipped');return
    commit=json.loads((FOLDER/'manifest.json').read_text(encoding='utf-8'))['pinned_commit']
    tree=json.loads((FOLDER/'tree-1.raw').read_bytes());files=[];tick=time.perf_counter()
    for source,local in [('README.md','README.raw'),('public/index.html','index.raw')]:
        assert source in {item['path'] for item in tree}
        url='https://gitlab.com/api/v4/projects/21skibidiserb37%2Fxyzsolving333/repository/files/'+urllib.parse.quote(source,safe='')+'/raw?ref='+commit
        now=datetime.now(timezone.utc).isoformat()
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'LiberPrimusResearch/1.0'}),timeout=12) as response:
            data=response.read(2000001)
            assert len(data)<=2000000
            path=FOLDER/local;path.write_bytes(data)
            blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
            assert blob==next(item['id'] for item in tree if item['path']==source)
            files.append({'url':url,'source_path':source,'commit':commit,'status':response.code,
                          'path':path.relative_to(ROOT).as_posix(),'retrieved_at_utc':now,'bytes':len(data),
                          'sha256':hashlib.sha256(data).hexdigest(),'git_blob_sha1':blob})
    target.write_text(json.dumps({'files':files,'seconds':time.perf_counter()-tick,
                      'remote_code_executed':False,'limits':{'requests':2,'timeout_per_request':12,'bytes_per_file':2000000}},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'files':[(r['source_path'],r['bytes']) for r in files]}))


if __name__=='__main__':main()
