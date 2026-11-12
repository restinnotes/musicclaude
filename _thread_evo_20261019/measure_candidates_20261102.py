"""Compatibility entry: staged blind -> coverage -> alone; no unconditional diagnostics."""
import argparse
import json
import screen_flow as F


def measure(tag, base='qurefs', repeat=False):
    F.configure()
    quick = F.screen(tag, base)
    if repeat and quick['status'] == 'quick_pass':
        return F.screen(tag, base, acceptance=True)
    return quick


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('tag')
    parser.add_argument('--base', default='qurefs')
    parser.add_argument('--repeat', action='store_true')
    args = parser.parse_args()
    result = measure(args.tag, args.base, args.repeat)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result['status'] in ('pending', 'invalid'):
        raise SystemExit(2)
