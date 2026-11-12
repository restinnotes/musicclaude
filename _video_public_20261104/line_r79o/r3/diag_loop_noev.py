"""11-12 晚 用户定死“不加事件”（“绝对不能加……意思都完全不是一个意思了”）。I02 诊断（新问法）：不加事件的前提下，打转能减到什么程度、怎么验证。
材料：主线 g68CTRLsk2F 两首（成片形式）、它的开放评审里关于打转的原话、试验记录里不加事件的所有尝试和结果。
python r3/diag_loop_noev.py → r3/s24/diag_loop_noev_{g6|g56}.json"""
import json, os, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('PUB_SRC', 'r2e')
from pub24 import S, rd, call, parse, G6, G56, view_text
sys.stdout.reconfigure(encoding='utf-8')
TPL = (Path(__file__).parent/'i02_诊断提问模板.txt').read_text(encoding='utf-8')
TRIALS = Path('D:/musicclaude/_thread_evo_20261019/试验记录.md').read_text(encoding='utf-8')
TRIALS = TRIALS[TRIALS.find('## 11-11 写线层治打转'):]

def loops():
    out = []
    for w in ('op60', 'op61'):
        for j in ('g6', 'g56', 'argon'):
            p = S/f'openF3_{w}_{j}_g68CTRLsk2F.json'
            if p.exists():
                for x in rd(p)['issues']:
                    if any(k in x['problem'] for k in ('打转', '重复', '循环', '反复', '又', '失忆')):
                        out.append(f"- {w} {j} {x.get('sec','')}：{x['problem'][:400]}")
    return '\n'.join(out)

ASK = f"""你是顾问。【问题】一首钢琴曲“边听边看”的屏幕稿（两首：船歌、幻想波兰舞曲），开放评审在 30 多个版本里都把“原地打转”排第一：同一个认识、决定、担心隔几屏又被当成新的说一遍，人物在几种心理状态之间来回。

【现在的设定（谁定的）】
- 线不编外加的事件、前史、对白、物件（用户定，11-12 晚刚确认：试过在转折处加几件真实的事，打转消失，但用户看了说“完全收不住了……意思看起来都完全不是一个意思了”，绝对不能加）。允许一个从头到尾不变的轻处境和小动作。
- 大字用线的原话，只切不改（用户定）；线可以改（在写线那一层改，或者在写好的线上局部改）。
- 两首同一套提示词，提示词里不放具体作品内容。
- 音乐分段 13–14 段不变；每屏至少要有大字（空屏会被读成主线断档，两次证实）。

【这个问题这次要的不是“去掉”，是“减轻到不算大问题”】请判断在上面设定下能减到什么程度，以及怎么做、怎么验证。

{TPL[TPL.index('请回答：'):]}
另外请单独回答：5. 你建议先试的一个最小改法（只改被评审点名的那几处、不动别处的局部修改，还是别的），以及用什么数字判断它算不算把打转减轻到“不算大问题”（例如：开放评审三位里有几位还把它排进前三、点名的重复处还剩几处）。回答时请不要进行联网搜索。

【已经试过的（试验记录原文，11-11 以后）】
{TRIALS[:30000]}

【主线开放评审里关于打转的原话】
{loops()}

【主线屏幕稿（成片形式）】
=== 船歌
{view_text('op60', 'g68CTRLsk2F')}
=== 幻想波兰舞曲
{view_text('op61', 'g68CTRLsk2F')}
"""

def one(jm):
    j, m = jm; p = S/f'diag_loop_noev_{j}.json'
    if not p.exists():
        r = parse(call(f'diagloopnoev_{j}', ASK, m, 'gpt3s', 'dag-advisor')); p.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding='utf-8')
    r = rd(p); print('====', j, '最怀疑：', str(r.get('most_suspect'))[:500])
    for h in r.get('hypotheses') or []: print('  -', h.get('cause', '')[:120], '｜验证：', h.get('cheapest_test', '')[:200])
    print('  其余：', json.dumps({k: v for k, v in r.items() if k not in ('hypotheses', 'most_suspect')}, ensure_ascii=False)[:1200])

if __name__ == '__main__':
    print('材料', len(ASK), '字', flush=True)
    with ThreadPoolExecutor(2) as ex: list(ex.map(one, [('g6', G6), ('g56', G56)]))
