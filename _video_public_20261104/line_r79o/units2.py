"""11-10 午 覆盖测法第二版的分层（两位顾问 GPT-6、GPT-5.6 独立问诊印证，见 judge_check/unitstier_*）。
旧分层（units.py）：船歌 225 单元 = 核心 149 + 重要 76 + 补充 0，幻想 134 + 119 + 0；“两位不一致取更重”一路上抬；核心覆盖这个硬检查实际等于“全放进去”。
两位共同的改法：
  1. 分层只判语义重要性（删掉后观众具体会误解什么、不知道什么），不看屏幕容量，也不因为独特、生动就算核心；核心必须写出删除后果。
  2. 重要性、类型、位置分开标：音乐观察可以是核心（放旁注照样算留住），不退出分层。
  3. 两位独立分层，不一致不取更重：两位都判核心 = 确认核心（硬检查）；只有一位判核心 = 争议核心（单独报告，不进硬检查，也不许因此删）。
     （顾问建议第三位盲审；这里没有第三个可用的独立模型，改为单独报告争议层。）
  4. 只是同一体验换个说法的单元，两位都指出才并（并后屏幕留住其中一个就算留住）。
  5. 另设“大块必读”清单（只看原稿定、冻结），单独测“只看大块拿不拿得到”，和整屏核心覆盖分开报。
单元本身沿用 units.py 冻结的 r3/s24/units_{作品}.json，逐单元的整屏判定（cov3_*）不用重测，只重新计分。
python units2.py tier                 两位独立分层，结果 r3/s24/tier2_{作品}_{g6|g56}.json，合并 r3/s24/units2_{作品}.json
python units2.py score TAG...         用已有 cov3 重新计分
python units2.py big TAG...           只看大块的必读覆盖（新调用），结果 r3/s24/big2_{作品}_{评委}_{TAG}.json
python units2.py lost TAG             列出确认核心里过半判没有的单元
"""
import os, sys
os.environ.setdefault('PUB_BC_ALL', '1')
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import prompt_lint
from pub24 import S, rd, wr, call, parse, WORKS, JUDGES
from units import texts, src_text

NL = chr(10)
TIER = """下面是一首钢琴曲每一段的原稿：线（一个人经历的事）和珠子（几位听众在这一刻写下的感受，已按句拆成要点，每条有编号）；后面是已经从原稿里拆好的“意思单元”，每个单元附了它对应的原稿说法。这份原稿以后要做成观众边听边扫的视频屏幕（大块是必看的，小块是补充，对着具体声音的细节放在动画旁边的旁注里）。现在不看任何屏幕稿，只根据原稿给每个单元做四个判断。

一、重要性（只判内容本身，不看屏幕放不放得下，不看它将来放在哪个区域）
对每个单元做删除测试：假设这个单元从这一段完全消失，别的单元都还在，观众会失去什么？
- 核心：删掉它，观众对这一段的主要理解会实质改变——不知道此刻主要发生了什么、人物处在什么状态；不明白重要的原因、关系或转折；对主要情绪或它怎么变的理解错了；不明白这一段在整首曲子往前走里起的作用；或者失去构成这一刻关键听感、从别的单元推不出来的体验。判核心必须写出具体的删除后果（观众会误解什么、不知道什么、把什么关系弄错）。只能说出“会少一个独特的画面”“会少一个生动的比喻”“体验没那么丰富”的，不是核心。
- 重要：删掉它，主要的经历、感受、原因、转折照样看得懂，但会少一样有独立价值、别的单元替代不了的具体东西（一个画面、身体感觉、有辨识度的比喻、心里话、主要情绪之外的细微层次、有价值的音乐观察）。
- 补充：删掉它，主要理解基本不受影响，损失的东西边际价值低（对已有体验的轻微展开、增量很小的细节、重复强调、次要的联想）。有独立信息的也可以是补充。
纪律：不预设每段有几个核心；不因为内容多、时间短把真正的核心降层；不因为独特、生动、只有一位听众写到就升层或降层；不要求每段都有补充。讲音乐本身的单元同样按删除测试分层，可以是任何一层。

二、类型（选一个）：人物经历 / 原因转折 / 情绪 / 画面身体感觉 / 音乐观察 / 其他
“音乐观察”指这个单元讲的是声音本身（旋律、和弦、节奏、左右手、音色、调、哪几小节怎么样），而不是它带出的感受。

三、大块必读（是 / 否）
是 = 一个只看大块、不看小块和旁注的观众，也必须拿到（或能从大块准确推断出）这个单元的意思，否则这一段主要在讲什么就拼不起来。大块必读只能从核心里选，但核心不一定都是大块必读（比如放在旁注里的核心音乐体验）。

四、重复（可空）
如果这个单元和同一段里另一个单元其实是同一个具体体验、只是换了个说法，没有多出可分辨的画面、身体感觉、情绪层次或别的信息，在 dup_of 里写那个单元的编号；不同的理解、不同的画面、不同层的体验不算重复，不要写。

只输出 JSON，逐个单元给全：{"units":[{"uid":"S01-u1","tier":"核心|重要|补充","why":"核心写删除后果；其余一句话","type":"人物经历|原因转折|情绪|画面身体感觉|音乐观察|其他","main":"是|否","dup_of":""}]}

【原稿】
{SOURCE}

【意思单元】
{UNITS}
"""

BIG = """下面是一首钢琴曲视频的两份文字。“必读单元”是从原稿（线和听众的感受）里理出来、观众至少要拿到的内容，每个单元附了原稿里的说法。“大块”是视频每一段屏幕上放大的、扫一眼就会看到的那几块字，按出现顺序列出；屏幕上别的小字和旁注这里没有给，就当观众没看。

逐个单元判断：一个只看大块的观众，在同一段里拿不拿得到这个单元的意思：
- 留住：大块里说到了，或能从大块准确推断出来；说法可以不同、可以更短。
- 部分：只剩大意或情绪，原因、转折或那个具体的东西没了；或者要靠猜。
- 没有：只看大块拿不到。

只输出 JSON：{"items":[{"uid":"S01-u1","verdict":"留住|部分|没有"}]}，逐个给全。

【大块】
{SCREEN}

【必读单元】
{UNITS}
"""
for t, n in ((TIER, 'TIER'), (BIG, 'BIG')): prompt_lint.lint(t, 'units2.py ' + n)
TIERS = ('核心', '重要', '补充')


def utext(us, tx):
    return NL.join(f"[{u['uid']}] {u['what']}" + NL + NL.join(f"    原稿：{tx[i]}" for i in u['ids'] if i in tx) for u in us)


def tier_one(a):
    w, j = a; p = S/f'tier2_{w}_{j}.json'
    if p.exists(): return rd(p)
    us = rd(S/f'units_{w}.json'); tx = texts(w); ids = {u['uid'] for u in us}
    msg = TIER.replace('{SOURCE}', src_text(w)).replace('{UNITS}', utext(us, tx))
    for k in range(3):
        try:
            it = [x for x in parse(call(f'pub24UT_{w}_{j}' + ('' if not k else f'_r{k}'), msg, JUDGES[j], 'gpt3s', 'public24-tier2'))['units'] if x.get('uid') in ids and x.get('tier') in TIERS]
            assert len(it) >= 0.95*len(ids), len(it); wr(p, {'units': it}); return {'units': it}
        except Exception as ex: print('不合格', w, j, repr(ex)[:150], flush=True)


def merge(w):
    us = rd(S/f'units_{w}.json'); js = list(JUDGES)
    t = {j: {x['uid']: x for x in rd(S/f'tier2_{w}_{j}.json')['units']} for j in js}
    out = []
    for u in us:
        v = [t[j].get(u['uid']) or {} for j in js]; ts = [x.get('tier') for x in v]
        if all(x == '核心' for x in ts): tier = '核心'
        elif '核心' in ts: tier = '争议核心'
        elif '重要' in ts: tier = '重要' if all(x == '重要' for x in ts) else '重要或补充'
        else: tier = '补充'
        dups = [x.get('dup_of') or '' for x in v]
        out.append({'uid': u['uid'], 'sec': u['sec'], 'what': u['what'], 'ids': u['ids'], 'tier': tier, 'tiers': ts,
                    'music': all(x.get('type') == '音乐观察' for x in v), 'music_any': any(x.get('type') == '音乐观察' for x in v),
                    'main': tier == '核心' and all(x.get('main') == '是' for x in v) and not any(x.get('type') == '音乐观察' for x in v),   # 11-10：讲音乐本身的按标准放旁注，不能要求进大块（船歌结尾两个对着小节的单元每版都判丢）
                    'dup_of': dups[0] if dups[0] and len(set(dups)) == 1 else '',
                    'why': [x.get('why') for x in v]})
    wr(S/f'units2_{w}.json', out)
    c = Counter(u['tier'] for u in out)
    print(w, '单元', len(out), dict(c), '大块必读', sum(u['main'] for u in out), '两位都判音乐', sum(u['music'] for u in out),
          '核心里的音乐', sum(u['music'] and u['tier'] == '核心' for u in out), '两位都指的重复', sum(bool(u['dup_of']) for u in out), flush=True)
    sec = Counter(u['sec'] for u in out if u['tier'] == '核心'); print('   每段确认核心', dict(sorted(sec.items())), flush=True)
    return out


def groups(us):
    """两位都指出的重复并成一组：组里留住一个就都算留住。"""
    root = {u['uid']: u['uid'] for u in us}
    def find(x):
        while root[x] != x: x = root[x]
        return x
    for u in us:
        if u['dup_of'] in root: root[find(u['uid'])] = find(u['dup_of'])
    return {u: find(u) for u in root}


def score(w, t):
    us = rd(S/f'units2_{w}.json'); g = groups(us); js = [j for j in JUDGES if (S/f'cov3_{w}_{j}_{t}.json').exists()]
    rank = {'留住': 2, '部分': 1, '没有': 0, None: 0}; per = {}; votes = {}
    for j in js:
        v = {x['uid']: x.get('verdict') for x in rd(S/f'cov3_{w}_{j}_{t}.json')['items']}
        best = {}
        for u in g: best[g[u]] = max(best.get(g[u], 0), rank.get(v.get(u), 0))
        for u in us: votes.setdefault(u['uid'], []).append(best[g[u['uid']]])
    def rate(sel):
        uu = [u['uid'] for u in us if sel(u)]
        if not uu or not js: return None, len(uu)
        return round(sum(sum(x == 2 for x in votes[u])/len(js) for u in uu)/len(uu), 3), len(uu)
    r = {'核心': rate(lambda u: u['tier'] == '核心'), '争议核心': rate(lambda u: u['tier'] == '争议核心'),
         '重要': rate(lambda u: u['tier'] in ('重要', '重要或补充')), '补充': rate(lambda u: u['tier'] == '补充'),
         '音乐': rate(lambda u: u['music']), '核心非音乐': rate(lambda u: u['tier'] == '核心' and not u['music_any'])}
    lost = [u['uid'] for u in us if u['tier'] == '核心' and sum(x == 0 for x in votes[u['uid']]) > len(js)/2]
    part = [u['uid'] for u in us if u['tier'] == '核心' and u['uid'] not in lost and sum(x != 2 for x in votes[u['uid']]) > len(js)/2]
    return r, lost, part, len(js)


def big_text(w, tag):
    return NL.join(NL + '### ' + s['sec'] + NL + NL.join(x['text'] for x in s['rows'] if x['kind'] == 'line') for s in rd(S/f'screen_{w}_{tag}.json')['sections'])


def big_one(a):
    w, j, t = a; p = S/f'big2_{w}_{j}_{t}.json'
    if p.exists(): return rd(p)
    us = [u for u in rd(S/f'units2_{w}.json') if u['main']]; tx = texts(w); ids = {u['uid'] for u in us}
    msg = BIG.replace('{SCREEN}', big_text(w, t)).replace('{UNITS}', utext(us, tx))
    for k in range(3):
        try:
            it = [x for x in parse(call(f'pub24UB_{w}_{j}_{t}' + ('' if not k else f'_r{k}'), msg, JUDGES[j], 'gpt3s', 'public24-big2'))['items'] if x.get('uid') in ids]
            assert len(it) >= 0.9*len(ids); wr(p, {'items': it}); return it
        except Exception as ex: print('不合格', w, j, t, repr(ex)[:150], flush=True)


def big_score(w, t):
    us = [u for u in rd(S/f'units2_{w}.json') if u['main']]; js = [j for j in JUDGES if (S/f'big2_{w}_{j}_{t}.json').exists()]
    if not js: return None, [], 0
    vs = [{x['uid']: x.get('verdict') for x in rd(S/f'big2_{w}_{j}_{t}.json')['items']} for j in js]
    rate = round(sum(sum(v.get(u['uid']) == '留住' for v in vs)/len(js) for u in us)/max(1, len(us)), 3)
    lost = [u['uid'] for u in us if sum(v.get(u['uid']) == '没有' for v in vs) > len(js)/2]
    return rate, lost, len(us)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    cmd, tags = sys.argv[1], sys.argv[2:]
    if cmd == 'tier':
        with ThreadPoolExecutor(4) as ex: list(ex.map(tier_one, [(w, j) for w in WORKS for j in JUDGES]))
        for w in WORKS: merge(w)
    elif cmd == 'merge':
        for w in WORKS: merge(w)
    elif cmd == 'big':
        jobs = [(w, j, t) for t in tags for w in WORKS for j in JUDGES]
        with ThreadPoolExecutor(min(16, len(jobs))) as ex: list(ex.map(big_one, jobs))
    if cmd in ('score', 'big'):
        for t in tags:
            for w in WORKS:
                r, lost, part, nj = score(w, t); b, bl, bn = big_score(w, t) if not t.startswith('w') else (None, [], 0)
                print(f"{t} {w}（{nj} 位）：确认核心 {r['核心'][0]}（{r['核心'][1]} 个）、争议核心 {r['争议核心'][0]}（{r['争议核心'][1]}）、重要 {r['重要'][0]}（{r['重要'][1]}）、补充 {r['补充'][0]}（{r['补充'][1]}）、音乐 {r['音乐'][0]}（{r['音乐'][1]}）；"
                      f"确认核心丢失 {len(lost)} {lost[:8]}；过半判不全 {len(part)}；只看大块必读 {b}（{bn} 个）丢 {len(bl)} {bl[:8]}", flush=True)
    elif cmd == 'lost':
        for w in WORKS:
            us = {u['uid']: u for u in rd(S/f'units2_{w}.json')}; r, lost, part, nj = score(w, tags[0]); b, bl, bn = big_score(w, tags[0])
            print('==', tags[0], w, '整屏确认核心丢失')
            for u in lost: print('  ', u, '音乐' if us[u]['music_any'] else '', us[u]['what'])
            print('== 只看大块丢的必读')
            for u in bl: print('  ', u, us[u]['what'])
