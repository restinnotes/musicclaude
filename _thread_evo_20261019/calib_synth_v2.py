"""Separate local mechanism validity from whole-section completeness in calibration.
The original fixture tested short excerpts with missing fate/dependency fields as if they were complete sections.
Known-good local excerpts need not explain the whole section. Content and completeness now have separate verdicts.
"""
import json
import calib_synth as old
import evo
import node2b
import synth

PROMPT='''请检查下面这一条局部 Thread 解释本身是否成立。此处在校准“内容判断”，不是验收整段成品。
valid 只回答：已建立的历史和当前听感能否支持这条解释，它有没有真正提供原因。
不是要求这一个短例子解释整段全部听感；coverage_gaps 单独列其未解释的重要听感。
不要因缺少本次未提供的机器编号或去处字段而判内容失败。
内容失败包括编造人物前史/习惯/外部事件，把听感比喻当真实剧情，只宣布结果没有原因，
抽象词替代无法说明的推导，或者解释依赖当前历史并没有建立的前提。
内容成立不要求永远不能用于别处：同一种心理机制可以在不同音乐里发生，需判断它在此处是否有具体历史和听感依据。
一个已说明原因与后果的简短解释可以成立，不必追加一串自我劝说、决定和心理步骤。
感受本身有时间、回忆、失去的性质，不等于编造具体事件；S03 的漂浮、急切、暗流可以并存。

【历史】
{HISTORY}
【本段听感】
{BEADS}
【待评局部解释】
{TEXT}

只输出 JSON：{{"valid":true,"why":"指出具体依据或问题，不只给分", "coverage_gaps":["编号及尚未解释的感受"]}}
'''


def msg(key):
    sec,hist,text,want,why=old.CASES[key]
    r=synth.Run('calib2','op60','g6','none')
    # Controlled fixture correction, NOT a reconstruction of the original 60d history.
    # The original synthetic H2 said only "possible closeness" whereas the excerpt assumes enjoyment.
    # Test that mechanism with its premise explicitly supplied; retain the original raw fixture in calib_synth.py.
    if key=='60d_S04':
        hist=[dict(h) for h in hist]
        hist[1]['text']='他真实享受到亲近带来的快乐；亲近越显珍贵，他越不忍它转瞬即逝，期待也渐渐成了盼这份亲近长久。'
    return PROMPT.format(HISTORY=r.hist_text(hist),BEADS=r.bead_text(sec),TEXT=text)


if __name__=='__main__':
    jobs=[node2b.job(f'cs2_{key}_{judge}',msg(key),{'stage':'calib_synth_v2','case':key},w=judge)
          for key in old.CASES for judge in ('g6','g56') if not evo.done(f'cs2_{key}_{judge}')]
    evo.run_parallel(jobs,len(jobs) or 1)
    report=[]
    for key,(_,_,_,want,_) in old.CASES.items():
        for judge in ('g6','g56'):
            try:
                result=evo.parse_json(evo.output(f'cs2_{key}_{judge}'))
                report.append({'case':key,'judge':judge,'expected':want,'correct':result.get('valid') is want,'result':result})
            except Exception as exc:
                report.append({'case':key,'judge':judge,'error':str(exc),'correct':False})
    out=evo.ROOT/'evaluations'/'synth'/'calibration_v2.json'
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    print(sum(r['correct'] for r in report),'/',len(report),'correct')
