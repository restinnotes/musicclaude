"""Read only Chromium cache headers; output official public asset URLs only."""
from pathlib import Path
import json
import re
import struct
import time

MAGIC=0xfcfb6d1ba7725c30
PUBLIC=re.compile(r'https://(?:chatgpt\.com|cdn\.oaistatic\.com)/[A-Za-z0-9_./@%+-]*assets/[A-Za-z0-9_.-]+\.js(?=$|[\x00\s])')


def run():
    root=Path('/source-profile')
    started=time.monotonic();found={};scanned=recognized=0;budget=False
    for sub in ('Default/Cache/Cache_Data','Default/Code Cache/js'):
        folder=root/sub
        if not folder.is_dir() or folder.is_symlink():continue
        for file in folder.iterdir():
            if time.monotonic()-started>5 or scanned>=5000:
                budget=True;break
            if not file.is_file() or file.is_symlink():continue
            scanned+=1
            try:
                with file.open('rb') as stream:
                    header=stream.read(24)
                    if len(header)!=24:continue
                    magic,version,length,keyhash,padding=struct.unpack('<QIIII',header)
                    if magic!=MAGIC or not 0<length<=8192:continue
                    raw=stream.read(length)
                if len(raw)!=length:continue
                recognized+=1
                key=raw.decode('utf-8',errors='replace')
                for match in PUBLIC.finditer(key):
                    url=match.group();found[url]=max(found.get(url,0),file.stat().st_mtime)
            except OSError:continue
        if budget:break
    print(json.dumps(dict(public_asset_urls=sorted(found),
        public_asset_cache_mtime={url:found[url] for url in sorted(found)},files_scanned=scanned,
        recognized_simple_cache_headers=recognized,budget_exhausted=budget,
        account_response_bodies_read=False,cache_values_or_nonpublic_keys_logged=False)))


if __name__=='__main__':run()
