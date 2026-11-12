"""Verify mg demand figures against Census's explicitly linked public downloadable table."""
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import urllib.request
import zipfile

HERE = Path(__file__).resolve().parent
DEST = HERE / 'source-artifacts'
DEST.mkdir(exist_ok=True)
URL = 'https://www2.census.gov/programs-surveys/aies/data/2024/AIES44BASIC.zip'
path = DEST / 'AIES44BASIC.zip'
if not path.exists():
    with urllib.request.urlopen(URL, timeout=30) as response, path.open('wb') as out:
        total = 0
        while True:
            chunk = response.read(65536)
            if not chunk: break
            total += len(chunk)
            if total > 100 * 1024 * 1024:
                raise RuntimeError('Unexpected table archive size; extraction cancelled')
            out.write(chunk)
matches = []
names = []
headers = []
with zipfile.ZipFile(path) as archive:
    for name in archive.namelist():
        names.append(name)
        if not name.lower().endswith(('.csv', '.dat')): continue
        with archive.open(name) as raw:
            reader = csv.DictReader(io.TextIOWrapper(raw, encoding='utf-8-sig'),
                delimiter='|' if name.lower().endswith('.dat') else ',')
            headers = reader.fieldnames
            for row in reader:
                label = str(row.get('NAICS2017_LABEL', ''))
                geography = str(row.get('GEO_ID', ''))
                if ('UNITED STATES' not in str(row.get('NAME', '')).upper()
                        and geography and geography != '0100000US'):
                    continue
                if any(term in label.lower() for term in ['clothing', 'shoe stores', 'luggage', 'sporting goods',
                    'hobby, toy', 'outdoor power', 'automotive parts']):
                    matches.append(row)
record = {'url':URL, 'retrieved_at':datetime.now(timezone.utc).isoformat(),
    'sha256':hashlib.sha256(path.read_bytes()).hexdigest(), 'archive_members':names,
    'headers':headers, 'filtered_rows':matches,
    'interpretation':'Retailer-industry employer firm revenue, not product-line all-channel GMV. No category sum accepted until rows and taxonomy checked.'}
(DEST / 'census-retail-selected-rows.json').write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'archive_bytes':path.stat().st_size, 'members':names, 'headers':headers,
    'selected_rows':len(matches), 'sample':matches[:4]}, ensure_ascii=False))
