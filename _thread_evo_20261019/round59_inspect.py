"""Local input/schema binding after the executor has read each returned answer."""
import argparse
import json
import re
import hashlib
import experiment_batch as B
import round50_measure as M
import round54_candidates as R
import v6cov
import v6alone


def exact(rid, message):
    folder = B.evo.RUNS / rid
    for name in ('prepared_input.txt', 'prompt.txt'):
        # Floor collector has no separate prepared_input file.
        if name != 'prepared_input.txt' or (folder / name).exists():
            assert (folder / name).read_text(encoding='utf-8') == message, (rid, name)
    actual = (folder / 'input.txt').read_text(encoding='utf-8')
    proof = {'rid': rid, 'input_sha256': B.digest(message), 'output_sha256': B.digest(B.evo.output(rid))}
    if actual != message:
        log = json.loads((folder / 'call.log').read_text(encoding='utf-8'))
        assert log['completed'] and log['route'] == 'gpt3-serial' and len(message)>60000
        assert actual == ('这次的任务全文太长，放在附件 full_prompt.txt 里。请把附件从头到尾完整读完（不要只检索片段），'
                          '然后严格按附件里的要求作答，只输出附件要求的格式。')
        assert log['message_sha256'] == B.digest(actual)
        attachment = folder / 'full_prompt.txt'
        assert attachment.read_text(encoding='utf-8') == message
        entries = json.loads((B.ROOT / log['job_directory'] / 'attachment-manifest.json').read_text(encoding='utf-8'))
        sha = hashlib.sha256(attachment.read_bytes()).hexdigest()
        assert entries == [{'name':'full_prompt.txt','size':attachment.stat().st_size,'sha256':sha}]
        proof['attachment_bytes_sha256'] = sha
    return proof


def bind_blind(rid, message, base):
    proof = exact(rid, message)
    work = 'op60' if '_op60_' in rid else 'op61'
    data = B.V.parse(rid)
    expected = {s['sec'] for s in B.V.graph_of(work, base)['segments']}
    assert len(data['sections']) == len(expected)
    assert {s['sec'] for s in data['sections']} == expected
    assert data['better'] in ('X', 'Y', '差不多')
    assert all(s[k] in ('X', 'Y', '差不多') for s in data['sections'] for k in B.F.DIMENSIONS)
    assert all(data[k] in ('是', '否') for k in ('X_replacing_Y_regress', 'Y_replacing_X_regress'))
    B.record_review(rid, True, '全部段落四维理由、双向损失及整体判断全文读；实际三个输入文件逐字、集合枚举核对；原票和分歧保留。' + B.json_text(proof))
    return proof


def blind(tag, base, batch):
    for rid, message, judge in M.jobs('fair', tag, base):
        seat = 'newX' if ('_op60_g6_' in rid or '_op61_g56_' in rid) else 'newY'
        if not rid.endswith('_' + seat):
            continue
        bind_blind(rid, message, base)
    R.BASE, R.ROOT = base, B.ROOT / 'runs/_batches' / batch
    result = R.quick_state(tag)
    print(B.json_text(result))
    return result


def floor(rid):
    kind, work, judge, tag = rid.split('_', 3)
    graph = B.V.graph_of(work, tag)
    if kind == 'cov2':
        message = v6cov.COV2.format(NAME=B.V.covjudge.NAME[work], WHAT=B.V.WHAT2, LINE=B.V.view(graph), BEADS=B.V.beads(work))
        d = B.V.parse(rid)
        expected = {(b['sec'], b['id'].split('-')[-1]) for b in B.V.covjudge.beads(work) if b['role'] != '演奏条件'}
        got = {(b['sec'], b['bead']) for b in d['beads']}
        assert len(d['beads']) == len(expected) and got == expected, (len(got), len(expected), got ^ expected)
        assert all(b['status'] in ('说清', '偏弱', '相反', '没有') for b in d['beads'])
    else:
        assert kind == 'al2'
        message = v6alone.ALONE2.format(NAME=B.V.covjudge.NAME[work], LINE=v6alone.line_ids(graph))
        d = B.V.parse(rid)
        expected = {s['sec'] for s in graph['segments']}
        assert len(d['sections']) == len(expected) and {s['sec'] for s in d['sections']} == expected
        assert all(s['self'] in ('成立', '勉强', '不成立') for s in d['sections'])
    proof = exact(rid, message)
    B.record_review(rid, True, '全部逐颗/逐段及理由、引文、整体意见全文读；实际输入逐字及完整ID集合枚举核对；保留评委分歧，不改原票。' + B.json_text(proof))
    print(B.json_text(proof))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('action', choices=('blind', 'floor'))
    p.add_argument('tag')
    p.add_argument('--base', default='qu')
    p.add_argument('--batch')
    a = p.parse_args()
    if a.action == 'blind':
        blind(a.tag, a.base, a.batch)
    else:
        floor(a.tag)
