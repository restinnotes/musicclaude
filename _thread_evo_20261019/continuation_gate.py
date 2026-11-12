"""Check existing paired evidence before spending on the next continuation stage."""
import argparse
import json
import continue_r80 as C
import continuation_evidence as E
import screen_flow as F


def require(tag, base, stage, anchor='r49b'):
    quick = json.loads((C.BATCH / f'{tag}_vs{base}_quick_audit.json').read_text(encoding='utf-8'))
    assert quick['total']['pass'] and not quick['missing'], 'Quick screening has not passed'
    E.fair(tag, base)  # Every completed original must have a full-read receipt.
    for kind in (('coverage',) if stage == 'alone' else ('coverage', 'alone')):
        E.floor(tag, base, kind)
        for comparison in dict.fromkeys((base, anchor)):
            state = F.floor_state(tag, comparison, kind)
            assert state['status'] == 'pass', (tag, comparison, kind, state)
    print('NEXT_STAGE_EVIDENCE_READY', tag, stage)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('tag')
    p.add_argument('stage', choices=('alone', 'finish'))
    p.add_argument('--base', default='r78a')
    p.add_argument('--anchor', default='r49b')
    a = p.parse_args()
    require(a.tag, a.base, a.stage, a.anchor)
