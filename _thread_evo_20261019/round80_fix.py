"""11-06 晚：新盲比（六项，含贴 Center、往前走）下的局部修线。
起因：r79f（只修偏离 Center）贴 Center +13，但单独 −31、往前走 −23：评委说它在后半段反复回到“留不住 / 时间会过去 / 舍不得”。
r79d 对 r49b 船歌贴 Center 输在 S06–S14：r49b 保住了“互相需要”的幸福本身，r79d 偏到单方面陪伴、不后悔自己的喜欢。
这一轮：把新盲比里“别版这段更贴 Center”的评委理由（附别版原段）交给修的人，要求贴 Center 的方式每段都是新的、从这一段新发生的事里长出来，
当前稿已有的推进一条都不丢。复用 round65_fix 的 REPAIR 和套用逻辑。
python round80_fix.py TAG SOURCE --others r49b,r79f [--max 8] [--model g6]
"""
import argparse, json, os, sys
from concurrent.futures import ThreadPoolExecutor
import round65_fix as R
import v6fix as V

CSTEP = """
【这一轮只修一件事：让被点到的段更贴 Center，同时不往回走】
这条线本该讲的是：{CENTER}。
下面是评委在正反比较里指出“别版这一段更贴 Center”的地方，附了理由和别版这一段的原文。别版的话只是参考，不要整段搬。
改法：
- 让这一段里，Center 的几样东西以这一段特有的样子缠在一起，从这一段新发生的事里长出来。比如这一段新发现了互相需要：这份互相本身就是幸福，也正因为是互相的，才更怕哪天不再是。
- 每一段贴 Center 的方式都必须是新的。前面段已经说过的“留不住、时间会过去、舍不得、越喜欢越怕”不许再说一遍；评委已经因为这种重复判过别的版本“来回”。
- 当前稿每一段新增的心理事实（评委说它“往前走”的地方）一条都不许丢，也不许改弱。
- 幸福本身要写得实：两个人此刻具体的好，不要只剩“怕失去”。
- 贴 Center 的意思要替换掉这段原来较弱、较泛的说法，不是往上加{NOGROW}
- 下面每条意见来自一次独立的正反比较（评委、座位、对比版本不同就算不同的读者）；同一段被两次以上点到就要动。
硬性要求：不许删除条目（不要输出 delete），不许并条；改后的条目不比原来长出两成；不新编情节，不把珠子的比喻写成真事；没被点到的段逐字不动。
"""


LEAN = """
【这一轮只修一件事：收紧措辞】
这条线本该讲的是：{CENTER}。上一轮把它改得更贴 Center、更往前走了，评委认可；但也说有些段比旧版啰嗦、不如旧版像人话。下面是评委指出旧版更简洁或更像人话的段和理由。
改法：把被点到的条目说得更短、更像平常人讲话：删掉重复交代、多余的修饰和“既……又……”式的堆叠。意思一样不少。
下面“当前稿赢的地方”是评委认定这一版贴 Center、往前走、单独成立更好的理由，那些意思一个都不许丢，也不许改弱。
硬性要求：不许删除条目（不要输出 delete），不许并条；改后的条目不比原来长；不新编情节；没被点到的段逐字不动。
"""


def dim_losses(w, cur, others, dims, lose=True):
    """新盲比（v6b4）里，别版（lose=True）或当前稿（lose=False）在 dims 某项赢的段。"""
    out = []
    for o in others:
        for tag, base, cur_is_new in ((cur, o, True), (o, cur, False)):
            for j in R.F.JUDGES:
                for seat in ('newX', 'newY'):
                    rid = f'v6b4_{w}_{j}_{tag}_vs{base}_{seat}'
                    if not os.path.exists(f'runs/{rid}/output.txt'):
                        continue
                    d = V.parse(rid)
                    if not d:
                        continue
                    new, old = ('X', 'Y') if seat == 'newX' else ('Y', 'X')
                    me, other = (new, old) if cur_is_new else (old, new)
                    for s in d.get('sections', []):
                        for k in dims:
                            if s.get(k) == (other if lose else me):
                                out.append({'别版': o, '评委': f'{j}-{seat}-{o}', '段': s['sec'], '项': k, '理由': R.swap(s.get(k + '_why'), me, other)})
    return out


def center_losses(w, cur, others):
    """新盲比（v6b4）里，别版在 center 一项赢当前稿的段：[{别版, 段, 理由}]。比较对两种顺序都找。"""
    out = []
    for o in others:
        for tag, base, cur_is_new in ((cur, o, True), (o, cur, False)):
            for j in R.F.JUDGES:
                for seat in ('newX', 'newY'):
                    rid = f'v6b4_{w}_{j}_{tag}_vs{base}_{seat}'
                    if not os.path.exists(f'runs/{rid}/output.txt'):
                        continue
                    d = V.parse(rid)
                    if not d:
                        continue
                    new, old = ('X', 'Y') if seat == 'newX' else ('Y', 'X')
                    me, other = (new, old) if cur_is_new else (old, new)
                    for s in d.get('sections', []):
                        if s.get('center') == other:
                            out.append({'别版': o, '评委': f'{j}-{seat}-{o}', '段': s['sec'], '理由': R.swap(s.get('center_why'), me, other)})
    return out


def main():
    p = argparse.ArgumentParser(); p.add_argument('tag'); p.add_argument('source'); p.add_argument('--others', default='r49b,r79f')
    p.add_argument('--max', type=int, default=8); p.add_argument('--model', default='g6'); p.add_argument('--route', default='gpt3s'); p.add_argument('--grow', action='store_true', help='11-07：r80a 卡字数后删了内容；--grow 去掉“字数不增加”，只留每条最多长两成'); p.add_argument('--lean', action='store_true', help='收紧：只修旧版更简洁/更像人话的段，保住贴 Center 和往前走')
    a = p.parse_args(); os.environ['THREAD_ROUTE'] = a.route; R.F.configure(); others = a.others.split(',')

    def one_lean(w):
        L = dim_losses(w, a.source, others, ('lean', 'plain')); G = dim_losses(w, a.source, others, ('center', 'step', 'alone'), lose=False)
        print(w, '旧版更简洁/更像人话', len(L), '票，', sorted({x['段'] for x in L}), flush=True)
        name = {'lean': '更简洁', 'plain': '更像人话', 'center': '贴 Center', 'step': '往前走', 'alone': '单独成立'}
        iss = [{'读者': x['评委'], 'where': x['段'], 'why': f"别版这段{name[x['项']]}——{x['理由']}"} for x in L]
        extra = LEAN.replace('{CENTER}', V.graph_of(w, a.source)['center']) + chr(10) + '【当前稿赢的地方（不许丢）】' + chr(10) + chr(10).join(f"- {x['段']} {name[x['项']]}：{x['理由']}" for x in G) + chr(10)
        msg = R.REPAIR.format(MAX=a.max, LINE=V.view(V.graph_of(w, a.source), ids=True), BEADS=V.beads(w), ISSUES=json.dumps(iss, ensure_ascii=False, indent=0), EXTRA=extra)
        ans = R.pipe.call(f'sc{a.tag}_{w}_F2', msg, a.model, a.tag)
        ans['edits'] = [e for e in ans.get('edits', []) if e.get('op') != 'delete']
        R.apply_answer(w, a.tag, a.source, ans, a.max)

    def one(w):
        if a.lean: return one_lean(w)
        L = center_losses(w, a.source, others)
        secs = sorted({x['段'] for x in L})
        print(w, '别版贴 Center 赢的段', len(L), '票，', secs, flush=True)
        ref = '\n\n'.join(f'——别版 {o} 的这些段——\n' + V.view(V.graph_of(w, o), secs=secs, center=False) for o in others)
        extra = CSTEP.replace('{NOGROW}', '。原有的意思一个都不许删（r80a 就是为了腾字数删了内容才输）。' if a.grow else '；改后这一段的字数不增加。').replace('{NOGROW}', '').replace('{CENTER}', V.graph_of(w, a.source)['center']) + '\n【别版的这些段（参考）】\n' + ref + '\n'
        iss = [{'读者': x['评委'], 'where': x['段'], 'why': f"偏离 Center：别版 {x['别版']} 这段更贴 Center——{x['理由']}"} for x in L]
        msg = R.REPAIR.format(MAX=a.max, LINE=V.view(V.graph_of(w, a.source), ids=True), BEADS=V.beads(w), ISSUES=json.dumps(iss, ensure_ascii=False, indent=0), EXTRA=extra)
        ans = R.pipe.call(f'sc{a.tag}_{w}_F2', msg, a.model, a.tag)
        if any(e.get('op') == 'delete' for e in ans.get('edits', [])):
            ans['edits'] = [e for e in ans['edits'] if e.get('op') != 'delete']; print(w, '去掉了删除操作', flush=True)
        R.apply_answer(w, a.tag, a.source, ans, a.max)
    with ThreadPoolExecutor(2) as ex: list(ex.map(one, R.F.WORKS))
    R.show(a.tag, a.source)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8'); main()
