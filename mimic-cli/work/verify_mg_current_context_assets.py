"""Verify fetched public code against hashes observed in the actual MG trial."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import PurePosixPath
import re
from urllib.parse import urlsplit,urlunsplit
from urllib.request import Request,urlopen
from build_mg_storage_pair import OUT


def main():
    rows=json.loads((OUT/'observer-native_identity-221442.json').read_text())
    observed={r['basename']:(r.get('body_sha256') if r.get('observation_complete') else None) for r in rows
        if r.get('event')=='forensic_frontend_asset'}
    cache=json.loads((OUT/'cached-public-frontend-223309/cache-key-evidence.json').read_text())
    stamp=datetime.now(timezone.utc).strftime('%H%M%S')
    directory=OUT/('verified-current-context-'+stamp);directory.mkdir(exist_ok=False)
    result=[]
    for prefix in ('7078','646436'):
        candidates=[name for name in observed if name.startswith(prefix+'.')]
        assert len(candidates)==1
        name=candidates[0]
        previous=next(url for url in cache['public_asset_urls'] if urlsplit(url).path.rsplit('/',1)[-1].startswith(prefix+'.'))
        parsed=urlsplit(previous)
        target_path=str(PurePosixPath(parsed.path).parent/name)
        # The public asset directory is evidenced by the source cache header;
        # the current basename and body hash are evidenced by actual CDP trial.
        url=urlunsplit((parsed.scheme,parsed.netloc,target_path,'',''))
        record=dict(basename=name,public_url=url,expected_observed_sha256=observed[name],
            source_cached_directory=True,current_basename_observed=True,account_cookies_sent=False)
        try:
            with urlopen(Request(url,headers={'Accept-Encoding':'identity','Accept':'application/javascript'}),timeout=15) as response:
                assert urlsplit(response.url).hostname==parsed.hostname
                data=response.read(2*1024*1024+1)
            if len(data)>2*1024*1024:raise ValueError('Bounded public body exceeded')
            sha=hashlib.sha256(data).hexdigest()
            record.update(actual_sha256=sha,bytes=len(data),
                matches_actual_trial_body=(sha==observed[name]) if observed[name] else None,
                actual_trial_body_hash_available=observed[name] is not None)
            text=data.decode('utf-8');(directory/name).write_bytes(data)
            patterns=('browser_context','browserContext?.instanceId','browserContext.instanceId')
            record['code_matches']={needle:[text[max(0,m.start()-180):m.end()+250]
                for m in list(re.finditer(re.escape(needle),text))[:3]] for needle in patterns
                if needle in text}
        except Exception as error:record['error_class']=type(error).__name__
        result.append(record)
    report=dict(utc=datetime.now(timezone.utc).isoformat(),model_sent=False,browser_started=False,
        source_profile_unmodified=True,assets=result)
    file=directory/'report.json';file.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(dict(file=str(file),assets=result)),flush=True)


if __name__=='__main__':main()
