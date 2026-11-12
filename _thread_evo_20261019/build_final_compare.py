"""由脚本生成“最终版本 vs 固定起点”的逐段对比，正文和指标都从文件读，不手写。
usage: python build_final_compare.py TAG BASE OUTPUT TAG2 [TAG3 ...]（TAG2 起为要列出直接比较结果的其他基准）"""
import json, os, sys
os.environ.setdefault('JV', '2')
import round37_fair as FAIR, screen_flow as F, v6fix as V

NAMES = {'op60': '《船歌》Op.60', 'op61': '《幻想波兰舞曲》Op.61'}
DIM = {'alone': '单独成立', 'lean': '不啰嗦', 'plain': '人话', 'cover': '接得上珠子'}


def rows(tag, base):
    return [r for r in (FAIR.read(w, j, tag, base, s) for w in F.WORKS for j in F.JUDGES for s in ('newX', 'newY')) if r]


def table(tag, bases):
    out = ['| 比较基准 | 范围 | 票数 | 选新版 | 判不退步 | 单独成立 | 不啰嗦 | 人话 | 接得上珠子 |', '|---|---|---:|---:|---:|---:|---:|---:|---:|']
    for b in bases:
        got = rows(tag, b)
        for scope, x in (('两首', got), *((w, [r for r in got if r['w'] == w]) for w in F.WORKS)):
            nets = [sum(r['net'][k] for r in x) for k in DIM]
            out.append(f"| `{b}` | {NAMES.get(scope, scope)} | {len(x)} | {sum(r['new_win'] for r in x)} | {sum(r['no_regress'] for r in x)} | " + ' | '.join(f'{n:+d}' for n in nets) + ' |')
    return out


def main(tag, base, output, *others):
    md = [f'<!-- 由 build_final_compare.py 生成，不手改 -->', f'# 最终版本 `{tag}` 对比 `{base}`', '',
          '净胜 = 新版赢的段数 − 旧版赢的段数，所有票合计。门槛：8 票至少 6 票选新、至少 6 票不退步、前三项净胜不为负，覆盖和单独读两道底线过。', '']
    md += table(tag, [base, *others]) + ['']
    for w in F.WORKS:
        a, b = V.graph_of(w, base), V.graph_of(w, tag)
        chars = [sum(len(i['text']) for s in g['segments'] for i in s['items']) for g in (a, b)]
        md += [f'## {NAMES[w]}', '', f'`{base}` {chars[0]} 字，`{tag}` {chars[1]} 字。Center：{b["center"]}', '']
        for sa, sb in zip(a['segments'], b['segments']):
            ta, tb = [i['text'] for i in sa['items']], [i['text'] for i in sb['items']]
            md += [f"### {sb['sec']}｜{sb['bars']} 小节（{sa.get('relation')} → {sb.get('relation')}）" if sa.get('relation') != sb.get('relation') else f"### {sb['sec']}｜{sb['bars']} 小节（{sb.get('relation')}）", '']
            if ta == tb:
                md += ['两版相同：', ''] + [f'- {x}' for x in tb] + ['']
            else:
                md += [f'**`{base}`**', ''] + [f'- {x}' for x in ta] + ['', f'**`{tag}`**', ''] + [f'- {x}' for x in tb] + ['']
    open(output, 'w', encoding='utf-8').write('\n'.join(md))
    print('已写', output, len(md))


if __name__ == '__main__':
    main(*sys.argv[1:])
