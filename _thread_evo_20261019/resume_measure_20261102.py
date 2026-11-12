"""Legacy batch entry: use sequential gates, not unconditional diagnostics."""
import argparse
import json
from measure_candidates_20261102 import measure


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('tags', nargs='+', help='explicit current candidate tags; no retired default batch')
    p.add_argument('--base', default='qurefs')
    args = p.parse_args()
    result = {tag: measure(tag, args.base) for tag in args.tags}
    print(json.dumps(result, ensure_ascii=False, indent=2))
