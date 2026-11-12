"""Read gateway admission state through its authenticated local endpoint."""
import json
import urllib.request
from src.config import Config

opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
request=urllib.request.Request('http://127.0.0.1:8000/v1/tabs',headers={'Authorization':'Bearer '+Config.API_TOKEN})
with opener.open(request,timeout=10) as response:
    state=json.load(response)
tabs=state.get('tabs',[])
busy=[row.get('index') for row in tabs if row.get('is_busy')]
print(json.dumps({'busy_tabs':busy,'concurrency':state.get('concurrency'),'tab_count':len(tabs)}))
assert 'tabs' in state and not busy, 'Cannot deploy while a request owns a tab'
