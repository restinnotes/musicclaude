"""Compare independent demand observations, preserving disagreement and metric bases."""
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
observations = {}
for replicate in 'ABC':
    job = 'W1-' + replicate
    path = HERE / 'jobs' / job / 'evidence.json'
    if not path.exists() and job == 'W1-C':
        path = HERE / 'jobs' / 'W1-C-continuation01' / 'evidence.json'
    if not path.exists(): continue
    data = json.loads(path.read_text(encoding='utf-8'))
    for category in data.get('categories', []):
        if isinstance(category, dict) and category.get('category_id'):
            observations.setdefault(category['category_id'], {})[job] = category

rows = []
for number in range(1, 19):
    identifier = 'C' + str(number).zfill(2)
    reports = observations.get(identifier, {})
    row = {'category_id': identifier, 'status': 'PRELIMINARY_NOT_ADJUDICATED',
        'reports_available': list(reports), 'demand_weight': None,
        'warning': 'Do not average different years, definitions, forecasts, shipments, spending or retailer-industry sales'}
    for job, category in reports.items():
        row[job] = category
    rows.append(row)
(HERE / 'demand-comparison-preliminary.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8')
fields = ['category_id', 'status', 'reports_available', 'demand_weight', 'W1-A', 'W1-B', 'W1-C', 'warning']
with (HERE / 'demand-comparison-preliminary.csv').open('w', encoding='utf-8-sig', newline='') as handle:
    writer = csv.DictWriter(handle, fieldnames=fields)
    writer.writeheader()
    for row in rows:
        writer.writerow({key: json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else value
                         for key, value in row.items()})
print(json.dumps({'categories':18, 'available_reports':sorted({job for reports in observations.values() for job in reports}),
    'weights_assigned':False, 'adjudicated':False}))
