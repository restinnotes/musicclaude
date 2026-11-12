"""Record manually read phase outputs and mechanical shape; never edit outputs."""
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
for work in ('op60','op61'):
    folder = root / 'runs' / f'scr26t3_{work}_A4'
    parsed = json.loads((folder / 'parsed.json').read_text(encoding='utf-8'))
    segments = parsed['segments']
    items = [item for seg in segments for item in seg['items']]
    shape = all(2 <= len(seg['items']) <= 4 for seg in segments)
    sentences = all(len(re.findall('[。！？]', item['text'])) == 1 for item in items)
    assert shape and sentences
    record = {'read_complete': True, 'segments': len(segments), 'items': len(items),
        'characters': sum(len(item['text']) for item in items), 'items_per_segment_2_to_4': shape,
        'one_sentence_per_item': sentences,
        'judgment': 'Proceed to blind comparison against qu; not accepted as mainline',
        'risks': ['psychological outline voice', 'late repetition', 'coverage and causality need actual blind review']}
    (folder / 'inspection.json').write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
    print(work, record['segments'], record['items'], record['characters'])
    folder = root / 'runs' / f'scr27p2_{work}_A1'
    parsed = json.loads((folder / 'parsed.json').read_text(encoding='utf-8'))
    assert len(parsed['routes']) == 3
    record = {'read_complete': True, 'routes': 3,
        'new_external_events_or_other_person_response_found': False,
        'judgment': 'Allow A2 selection, which may reject every route; no A4 before reading selected output',
        'risks': ['abstract internal distinctions', 'phase development may be thin',
                  'plans must not become completed events']}
    (folder / 'inspection.json').write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
