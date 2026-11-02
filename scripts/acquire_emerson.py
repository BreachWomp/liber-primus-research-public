"""Retrieve one public-domain candidate key text; preserve original bytes."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
URL="https://www.gutenberg.org/cache/epub/2944/pg2944.txt"
dest=ROOT/"data/raw/gutenberg/pg2944.txt"
manifest=ROOT/"sources/emerson_manifest.json"
if manifest.exists():
    row=json.loads(manifest.read_text(encoding="utf-8"))
    if hashlib.sha256(dest.read_bytes()).hexdigest()!=row["sha256"]:raise RuntimeError("changed cached source")
else:
    request=urllib.request.Request(URL,headers={"User-Agent":"LiberPrimusResearch/0.1"})
    with urllib.request.urlopen(request,timeout=30) as response:
        data=response.read(2000001);resolved=response.url
    if len(data)>2000000:raise RuntimeError("source exceeds2MB cap")
    dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
    row={"title":"Essays — First Series","author":"Ralph Waldo Emerson","ebook_id":2944,
         "metadata_url":"https://www.gutenberg.org/ebooks/2944","requested_url":URL,"resolved_url":resolved,
         "retrieved_at_utc":datetime.now(timezone.utc).isoformat(),"sha256":hashlib.sha256(data).hexdigest(),
         "bytes":len(data),"local_path":dest.relative_to(ROOT).as_posix(),"source_class":"Project Gutenberg primary publication of this digital edition",
         "copyright_metadata":"Public domain in the USA, per official ebook page. Full supplied header/footer retained.",
         "use":"Speculative candidate running key, not an established Cicada key; no upstream code executed."}
    manifest.write_text(json.dumps(row,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(row,ensure_ascii=False))
