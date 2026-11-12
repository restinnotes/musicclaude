import json
from pathlib import Path
import sys
import urllib.request
root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / 'cli'))
import mg
mg.configure_profile(sys.argv[1])
token = mg.read_auth()
_, state = mg.http_json('/v1/tabs', token)
active = [tab for tab in state['tabs'] if tab['is_busy'] and not tab['is_control']]
if len(active) == 1:
    tab = active[0]
    request = urllib.request.Request(mg.API + '/v1/tabs/' + str(tab['index']) + '/screenshot',
        headers={'Authorization': 'Bearer ' + token})
    with urllib.request.urlopen(request, timeout=10) as response:
        data = response.read()
    path = Path(__file__).parent / (sys.argv[1] + '-progress.jpg')
    path.write_bytes(data)
    print(json.dumps({'active_tab': tab['index'], 'screenshot': str(path), 'in_flight': state['concurrency']['in_flight']}))
else:
    print(json.dumps({'active_tabs': len(active)}))
