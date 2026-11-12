"""11-10 午 DAG 层的小改：只修“意思读不清”的线（DAG 标准的底线：每句话意思读得清，DAG2 不会照着读歪的意思去写）。
起因（端到端证据）：船歌结尾一条线几乎每一版屏幕稿都被写走样（K26a、K26c2、K26b 等，两位评委同报），原句本身绕。
评委对全曲的判断（K25a、K26c2、K26a3 共 12 份绝对验收）：两首的事都在往前走、不是打转；所以这次不动骨架，只修读不清的句子。
做法：两位各自独立挑出容易读歪的句子并给改法；两位都挑中的才改，用 GPT-6 的改法；其余原样。产物 line_r79o/{NEW}/（珠子、对应、分段照抄 r2c）。
之后用 PUB_SRC={NEW} 和 PUB_SRC=r2c 走同一份 DAG2 提示词，比走样和问题数（端到端），好了才收。
python r3/dagclear.py NEW
"""
import json, os, sys, copy, shutil
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(HERE))
os.environ.setdefault('PUB_SRC', 'r2c')
import prompt_lint
from pub24 import R2, rd, call, parse, G6, G56, WORKS
sys.stdout.reconfigure(encoding='utf-8')
NL = chr(10)

CLEAR = """下面是一首钢琴曲的“线”：一个人经历的一件事，分段、分条写成，每条有编号。这份线以后会交给另一位写手压缩成视频屏幕上的短块；写手只看字面，读歪了就会照着歪的意思写。

请只做一件事：挑出字面上容易被读歪的句子。读歪指的是——谁对谁做什么、谁希望谁怎样会被弄反；否定套否定或“不想再……自己……”这类结构让人分不清到底要不要；一句里层层转折，压短以后主次会颠倒；指代不清（“这样”“那样”“这些”指什么要往前翻好几条）。
不要挑：只是啰嗦、不够口语、不够生动的句子；意思清楚、只是长的句子。宁可少挑。

每挑一句，给一个改法：意思完全不变，不加新的事、原因或感受，不删原有的意思；只把“谁、想不想、做什么”说到字面上不会读错；长度和原句差不多。

只输出 JSON：{"fix":[{"id":"S01-1","risk":"会被读成什么","text":"改后的整句"}]}。没有就输出 {"fix":[]}。

【线】
{LINE}
"""
prompt_lint.lint(CLEAR, 'dagclear.CLEAR')


def ask(a):
    w, j, model = a
    src = rd(R2/f'{w}_src.json')
    line = NL.join(f"{l['id']}：{l['text']}" for s in src['sections'] for l in s['lines'])
    for k in range(3):
        try: return w, j, parse(call(f'dagclear_{w}_{j}' + ('' if not k else f'_r{k}'), CLEAR.replace('{LINE}', line), model, 'gpt3s', 'dag-clear'))['fix']
        except Exception as ex: print('不合格', w, j, repr(ex)[:150], flush=True)
    return w, j, []


if __name__ == '__main__':
    new = sys.argv[1]; out = R2.parent/new; out.mkdir(exist_ok=True)
    with ThreadPoolExecutor(4) as ex: res = list(ex.map(ask, [(w, j, m) for w in WORKS for j, m in (('g6', G6), ('g56', G56))]))
    for w in WORKS:
        f = {j: {x['id']: x for x in fx if x.get('id') and x.get('text')} for ww, j, fx in res if ww == w}
        src = copy.deepcopy(rd(R2/f'{w}_src.json')); both = set(f['g6']) & set(f['g56']); n = 0
        print('==', w, 'GPT-6 挑', sorted(f['g6']), 'GPT-5.6 挑', sorted(f['g56']), '都挑中', sorted(both))
        for s in src['sections']:
            for l in s['lines']:
                if l['id'] in both:
                    print('  ', l['id'], '原：', l['text']); print('      改：', f['g6'][l['id']]['text'], '｜风险：', f['g6'][l['id']].get('risk')); print('      另一位的改法：', f['g56'][l['id']]['text'])
                    l['text'] = f['g6'][l['id']]['text']; n += 1
        (out/f'{w}_src.json').write_text(json.dumps(src, ensure_ascii=False, indent=1), encoding='utf-8')
        (out/f'dagclear_{w}.json').write_text(json.dumps(f, ensure_ascii=False, indent=1), encoding='utf-8')
        print('  改了', n, '条')
    for p in R2.glob('*'):
        if p.is_file() and not (out/p.name).exists() and p.suffix != '.md': shutil.copy(p, out/p.name)
