import json,urllib.request,urllib.error
from src.config import Config
payload={'model':'gpt-5.6-sol','reasoning_effort':'xhigh','messages':[{'role':'user','content':'Reply with exactly TEST_OK. No other text.'}],'stream':False}
req=urllib.request.Request('http://127.0.0.1:8000/v1/chat/completions',data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+Config.API_TOKEN,'Content-Type':'application/json','X-MimicGate-Mode':'temporary-unpersonalized'})
try:
    with urllib.request.urlopen(req,timeout=1100) as response: result={'http_status':response.status,'body':json.loads(response.read())}
except urllib.error.HTTPError as error:
    result={'http_status':error.code,'body':json.loads(error.read())}
print(json.dumps(result,ensure_ascii=False))
