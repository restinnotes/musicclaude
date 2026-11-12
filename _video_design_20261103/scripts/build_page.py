# 全文页：全部线和珠子逐字；点任意一句跳到音乐的那个位置。只读 r54weave，不改任何主线文件。
import json, re, sys, shutil, html, os
sys.stdout.reconfigure(encoding='utf-8')
RUNS = r'D:\music-experience-pipeline\runs\production'
WORKS = {
    'op60': dict(title='肖邦《船歌》Op.60', player='迪努·利帕蒂', run=RUNS + r'\frederic-chopin-barcarolle-in-f-sharp-major-op-6-b1ce4fc10b1b',
                 audio=r'D:\musicclaude\bead_video\remotion_b\public\audio.m4a', name='船歌'),
    'op61': dict(title='肖邦《幻想波兰舞曲》Op.61', player='斯维亚托斯拉夫·里赫特', run=RUNS + r'\polonaise-fantaisie-op-61-d53d9c49da26',
                 audio=r'D:\archive\classical-op52-legacy-2026-08-29\classical\里赫特 61 布拉格_trimmed.m4a', name='幻想波兰舞曲'),
}
EVO = r'D:\musicclaude\_thread_evo_20261019'
parsed = json.load(open('r54weave_parsed.json', encoding='utf-8'))
TPL = open('scripts/page_tpl.html', encoding='utf-8').read()
os.makedirs('out/全文页', exist_ok=True)
for w, cfg in WORKS.items():
    bars = {int(k): float(v) for k, v in json.load(open(cfg['run'] + r'\music\alignment\measure_alignment.json', encoding='utf-8')).items()}
    g = json.load(open(EVO + f'\\evaluations\\v6fix\\{w}_r54weave.json', encoding='utf-8'))['graph']
    segs = []
    for sec, s in zip(g['segments'], parsed[w]):
        a, b_end = [int(x) for x in re.split('[–-]', s['bars'])]
        t_seg = bars[a]
        out = []
        for li, line in enumerate(s['lines']):
            out.append(dict(k='line', text=line, t=t_seg))
            for x in [x for x in s['beads'] if x['after'] == li]:
                txt = x['text']
                alt = txt.startswith('也可以听成：')
                # 合写脚本加的“也可以听成：”如果后面又是“也可以/还有人”，只去掉脚本加的前缀，珠子本身一字不动
                body = re.sub(r'^也可以听成：(?=也可以|还有人)', '', txt)
                nums = re.findall(r'\d+', x.get('where', '').split('；')[0])
                lo = int(nums[0]) if nums else a
                hi = int(nums[-1]) if nums else b_end
                t = bars.get(lo, t_seg)
                out.append(dict(k='bead', text=body, t=round(t, 2), bars=f'{lo}–{hi}' if lo != hi else f'{lo}', alt=alt))
        # 线的跳转点：取它后面第一颗珠子的时间，没有就取段首
        for i, r in enumerate(out):
            if r['k'] == 'line':
                nb = out[i + 1] if i + 1 < len(out) and out[i + 1]['k'] == 'bead' else None
                r['t'] = nb['t'] if nb else t_seg
        segs.append(dict(bars=s['bars'], rel=s['rel'], t0=t_seg, rows=out))
    fn = cfg['name'] + '_录音.m4a'
    shutil.copyfile(cfg['audio'], 'out/全文页/' + fn)
    page = (TPL.replace('__TITLE__', html.escape(cfg['title'])).replace('__PLAYER__', html.escape(cfg['player']))
            .replace('__AUDIO__', html.escape(fn))
            .replace('__DATA__', json.dumps(segs, ensure_ascii=False).replace('</', '<\\/')))
    open(f"out/全文页/{cfg['name']}_全文页.html", 'w', encoding='utf-8').write(page)
    # 逐字核对
    src_lines = [i['text'] for s in g['segments'] for i in s['items']]
    pg_lines = [r['text'] for s in segs for r in s['rows'] if r['k'] == 'line']
    src_beads = [x['text'] for s in parsed[w] for x in s['beads']]
    pg_beads = [r['text'] for s in segs for r in s['rows'] if r['k'] == 'bead']
    ok = all(any(b in x for x in src_beads) for b in pg_beads) and len(pg_beads) == len(src_beads)
    print(w, '线', len(pg_lines), '珠', len(pg_beads), '线逐字一致', pg_lines == src_lines, '珠全部在且逐字', ok)
