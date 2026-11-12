"""11-08 迭代准则硬约束 1（泛化）的机械检查：提示词模板里不许出现具体作品的内容。
来由：11-08 我自己写的写稿提示词用了船歌珠子里的“小船漂进起雾的水域”“脚下没了支撑”当例子，不走样评委的例子就是 RHL 犯的错；准则只写了“要逐条查”，没有机械拦截，我绕过顾问直接写提示词时就没人查。
用法：from prompt_lint import lint; lint(模板文字, 名字)  —— 只查模板（材料填进去之前），发现就抛错，不许送出。
python prompt_lint.py 模块名.变量名 ...   单独检查，例如 python prompt_lint.py blend.BLEND faithful.FAITH vs2.VS2
"""
import glob, importlib, json, re, sys
from pathlib import Path

ROOTS = [Path(__file__).resolve().parent/'r2', Path('D:/musicclaude/_thread_evo_20261019/works')]


def corpus():
    texts = []
    for p in glob.glob(str(ROOTS[0]/'op6?_src.json')):
        d = json.load(open(p, encoding='utf-8'))
        for s in d['sections']:
            texts += [l['text'] for l in s['lines']] + [b['text'] for b in s['beads']]
    for p in glob.glob(str(ROOTS[1]/'*'/'center*.txt')) + glob.glob(str(ROOTS[1]/'*'/'center*.md')):
        texts.append(Path(p).read_text(encoding='utf-8'))
    return '\n'.join(texts)


CORPUS = None
GENERIC = None
WHITE = {'一个人经', '个人经历', '只剩一个', '怎样一步步', '也像一个人', '是一种尚未', '经历过什么', '个人经历了'}   # 描述“线”本身的通用说法


def generic():
    """通用文字（标准、准则、用户判定）：这些里也有的 4 字片段当作常用说法，不算作品内容。"""
    fs = ['D:/musicclaude/_thread_evo_20261019/标准.md', 'D:/musicclaude/_thread_evo_20261019/迭代准则.md', 'D:/musicclaude/_video_public_20261104/大众版标准.md', 'D:/musicclaude/_video_public_20261104/大众版标准_修订草稿_1108.md']
    fs += glob.glob('D:/musicclaude/_thread_evo_20261019/DAG/prompts/*/模板*')   # DAG 各层提示词模板（按准则不含作品内容）
    return chr(10).join(Path(f).read_text(encoding='utf-8', errors='ignore') for f in fs if Path(f).exists())


def find(tpl, n=5):
    """模板里在作品原文中出现、又不是通用说法的片段：引号里的（≥3 字）和任意连续 n 个汉字。"""
    global CORPUS, GENERIC
    CORPUS = CORPUS or corpus(); GENERIC = GENERIC or generic()
    hits = set()
    for q in re.findall(r'[“"「]([^”"」]{3,40})[”"」]', tpl):
        core = re.sub(r'[，。、；！？…\s]', '', q)
        if len(core) >= 4 and core in re.sub(r'[，。、；！？…\s]', '', CORPUS): hits.add(q)
    han = re.sub(r'[^\u4e00-\u9fff]', '|', tpl)
    for seg in han.split('|'):
        for i in range(len(seg)-n+1):
            w = seg[i:i+n]
            if w in CORPUS and w not in GENERIC and w not in WHITE: hits.add(w)
    return sorted(hits)


def lint(tpl, name=''):
    h = find(tpl)
    if h: raise SystemExit(f'【泛化检查没过】{name} 的提示词里有作品原文：{h[:10]}。准则硬约束 1：提示词、评审、规则里不放具体作品的例子。')
    return True


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8'); sys.path.insert(0, str(Path(__file__).resolve().parent))
    bad = 0
    for a in sys.argv[1:]:
        m, v = a.split('.'); t = getattr(importlib.import_module(m), v)
        h = find(t); bad += bool(h); print(a, '没过' if h else '过', h[:15])
    sys.exit(1 if bad else 0)
