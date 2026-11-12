import json
from pathlib import Path

root = Path(__file__).parent
d = json.loads((root / 'failure_215805.json').read_text(encoding='utf-8'))
s = d['snapshot']
print(json.dumps({k:s[k] for k in ['assistantTurns', 'latestAssistant', 'assistantCount', 'copyButtonCount', 'hasStopButton', 'stats']}, ensure_ascii=False, indent=2))
h = d['html_sample']['mainHtml']
i = h.find('data-message-author-role="assistant"')
print('assistant html', h[max(0,i-400):i+6500] if i >= 0 else h[-9000:])
