"""2026-10-25 continuation: fail closed, resume, contextual caching and transactional history repair.
Keeps synth.py as the historical baseline. No source draft or bead is modified.
"""
import copy
import hashlib
import json
import sys
import synth
import evo
import judge_synth_v4 as judge_synth_v3

VERSION = "synth-v2-20261025"


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


class Run(synth.Run):
    def __init__(self, *args):
        super().__init__(*args)
        # V4 GPT-6 passed all eight definitive fixtures. GPT-5.6 did not; keep both authors,
        # but use fresh GPT-6 checks and direct author-independent human-agent review.
        self.b = 'g6'
        self.checkpoints = {}
        self.rejected = []
        self.status = "running"
        self._pending_checks = {}

    def call(self, rid, msg, mdl, meta):
        # A backtrack changes History. Reusing an old answer just because S04_A exists is invalid.
        digest = hashlib.sha256((VERSION + mdl + msg).encode()).hexdigest()[:12]
        runid=f'sy{self.T}_{self.w}_{rid}_{digest}'
        if not evo.done(runid):
            synth.node2b.job(runid,msg,{'stage':'synth_v2','T':self.T,**meta},w=mdl)[1]()
        result=judge_synth_v3.parse(evo.output(runid))
        if 'section_pass' in result:
            result['pass']=result['section_pass'] and all(m.get('usable') for m in result.get('mechanisms',[]))
            sec=meta.get('sec')
            picked=getattr(self,'_pending_checks',{}).get(sec)
            if picked is not None:
                errors=self.validate_check(sec,picked,result)
                if errors:
                    result['pass']=False
                    result['problems']=list(result.get('problems',[]))+errors
        return result

    def validate_check(self, sec, picked, result):
        errors=self.validate_pick(sec,picked)
        expected={b['id'] for b in self.beads if b['sec']==sec and b['role']!='演奏条件'}
        coverage=result.get('coverage',[])
        checks=result.get('mechanisms',[])
        if [m.get('index') for m in checks]!=list(range(1,len(picked.get('chosen',[]))+1)):
            errors.append('检查者没有逐条完整核查所选解释')
        if len(coverage)!=len(expected) or {b.get('id') for b in coverage}!=expected:
            errors.append('检查者没有逐颗完整核查本段听感')
        if any(b.get('status') not in ('explained','compatible','alternative','missing') or not b.get('why') for b in coverage):
            errors.append('听感检查缺少有效判断或理由')
        if any(u.get('id') not in expected or u.get('why') not in ('池子太窄','缺前提','听感存疑') for u in result.get('unexplained',[])):
            errors.append('补缺诊断引用了本段以外的听感或未知原因')
        if result.get('section_pass') is True and (result.get('problems') or any(b.get('status')=='missing' for b in coverage)):
            errors.append('检查者的通过结论与仍有实质问题或缺口矛盾')
        return errors

    def validate_pick(self, sec, pk):
        errors = []
        if not isinstance(pk, dict):
            return ["选择结果不是对象"]
        beads = {b["id"] for b in self.beads if b["sec"] == sec and b["role"] != "演奏条件"}
        prior = {h["id"] for h in self.history(sec)}
        sources = {m["id"] for m in self.mechs(sec)}
        assessed=[m.get('id') for m in pk.get('eval',[])]
        if len(assessed)!=len(sources) or set(assessed)!=sources:
            errors.append('必须逐条判断本段全部候选，不能静默遗漏或重复')
        if set(pk.get("fate", {})) != beads:
            errors.append(f"听感去处必须逐颗完整，缺少={sorted(beads-set(pk.get('fate',{})))}，多出={sorted(set(pk.get('fate',{}))-beads)}")
        for i, chosen in enumerate(pk.get("chosen", []), 1):
            if not chosen.get("text"):
                errors.append(f"第{i}条没有内容")
            if not set(chosen.get("depends", [])) <= prior:
                errors.append(f"第{i}条引用不存在或未来的历史编号")
            if not chosen.get("from") or not set(chosen["from"]) <= sources:
                errors.append(f"第{i}条没有可追溯的池内来源")
            if not set(chosen.get("explains", [])) <= beads:
                errors.append(f"第{i}条引用不属于本段的听感")
        for h in pk.get("new_history", []):
            if not h.get("text") or not h.get("explains") or not set(h["explains"]) <= beads:
                errors.append("新增历史必须写出内容及本段听感依据，不能建立没有依据的前史")
        # Fate indices are checked independently from model prose.
        import re
        for bid, fate in pk.get("fate", {}).items():
            match = re.match(r"第(\d+)条", fate)
            if match:
                pos = int(match[1]) - 1
                if pos < 0 or pos >= len(pk.get("chosen", [])) or bid not in pk["chosen"][pos].get("explains", []):
                    errors.append(f"{bid} 的去处与选中解释不一致")
            elif not fate.startswith(("独立保留", "另一种听法", "没有解释")):
                errors.append(f"{bid} 的去处不是约定的四类")
        return errors

    def check_msg(self, sec, pk):
        if not hasattr(self,'_pending_checks'):
            self._pending_checks={}
        self._pending_checks[sec]=pk
        msg = judge_synth_v3.message(self.w,sec,self.history(sec),pk.get('chosen',[]),self.bead_text(sec),self.mech_text(self.mechs(sec)))
        msg += '\n【作者提出的听感去处与新增历史，也须核查】\n'+json.dumps({'fate':pk.get('fate',{}),'new_history':pk.get('new_history',[])},ensure_ascii=False)
        msg += '\n处境边界：可以采用从头到尾不变的轻处境，例如身旁有一个在意的人；亲近与相伴本身不必判成虚构事件。禁止的是把类比中的具体话语、动作或新发生的外部事件确认为人物的经历，并靠它们推动转折。心理推导可以有珠子之外的信息。'
        # Quality and completeness are different. One reason can genuinely explain several beads.
        msg += ("\n\n核查尺度：不要因为一条解释没有把每颗听感逐字复述，就要求增加心理步骤。"
                "只要已写明得到历史支持的原因与后果，不能因为简短便判作‘只有结果’。"
                "原因必须增加真实的解释信息：把感受换一个抽象名字，或者把‘更强’归因于‘更深’，"
                "没有解释具体经历怎样使这一刻变得不同，不能算机制。"
                "但一种原因没有解释到的重要体验仍须指出。感受本身带着时间、回忆或失去的性质，"
                "不等于编出具体离别事件。problems 只列足以判不合格的实质问题，措辞改进放在 reason；"
                "有实质问题时 pass 必须为 false。"
                "\n\n【本段候选原文，核对有没有擅自增加理由】\n" + self.mech_text(self.mechs(sec)))
        errors = self.validate_pick(sec, pk)
        if errors:
            msg += "\n\n程序已发现的结构问题（修复前不能通过）：\n" + "\n".join(errors)
        dep_ids={d for c in pk.get('chosen',[]) for d in c.get('depends',[])}
        cited={bid for h in self.history(sec) if h['id'] in dep_ids for bid in h.get('explains',[])}
        if cited:
            msg += ("\n\n【所依赖历史的原始听感依据】编号存在并不证明前提成立；"
                    "请核对过去的解释有没有把声音或意象的比喻变成真实事件，或把推测变成了确定事实。\n")
            msg += '\n'.join(f"{b['id']}：{b['text']}" for b in self.beads if b['id'] in cited)
        return msg

    def pick_msg(self, sec, critique=''):
        return (super().pick_msg(sec,critique)+
                '\n边界补充：听感的说话、动作与画面是听者类比，不证明人物身上实际发生了这些事。允许从头到尾不变的轻处境，不能靠新增外部事件推动情绪。开头可确立一个当下起点，也可还说不清，不补写往事；一条心理解释不必能从珠子逐字推出，但必须在这条历史中成立。')

    def segment(self, sec, tag=""):
        pk, ck = super().segment(sec, tag)
        errors = self.validate_check(sec, pk, ck)
        if errors or (ck.get("pass") and ck.get("problems")):
            ck = dict(ck, **{"pass": False, "problems": list(ck.get("problems", [])) + errors})
            self.state[sec]["check"] = ck
            dump(self.dir / f"{sec}.json", self.state[sec])
        return pk, ck

    def save(self):
        dump(self.dir / "run.json", {"version": VERSION, "T": self.T, "work": self.w,
             "pool": self.pool, "a": self.a, "b": self.b, "backs": self.backs,
             "status": self.status, "state": self.state, "checkpoints": self.checkpoints,
             "rejected": self.rejected, "judge_version": judge_synth_v3.VERSION,
             "judge_calibration": "calibration_v4.json:g6:8/8 definitive; all actual sections also reviewed by continuation agent"})

    def restore(self):
        path = self.dir / "run.json"
        if path.exists():
            d = json.loads(path.read_text(encoding="utf-8"))
            if d.get("version") != VERSION or d.get("pool") != self.pool:
                raise ValueError("已有运行与当前版本/候选池不一致，请用新编号")
            self.state = d["state"]
            self.backs = d["backs"]
            self.checkpoints = d["checkpoints"]
            self.rejected = d["rejected"]

    def repair(self, start, end, reason):
        """Try a different earlier interpretation; re-evaluate all later sections and checkpoints atomically."""
        saved = copy.deepcopy(self.state)
        saved_checkpoints = copy.deepcopy(self.checkpoints)
        self.backs += 1
        tag = f"_repair{self.backs}"
        k0, _ = self.seg(start)
        k1, _ = self.seg(end)
        for x in self.segs[k0:]:
            self.state.pop(x["id"], None)
            self.checkpoints.pop(x["id"], None)
        try:
            pk = self.call(start + tag + "_A", self.pick_msg(start, reason), self.a,
                           {"sec": start, "step": "repair-A"})
            ck = self.call(start + tag + "_B", self.check_msg(start, pk), self.b,
                           {"sec": start, "step": "repair-B"})
            if not ck.get("pass") or ck.get("problems") or self.validate_pick(start, pk):
                raise ValueError("回头段未通过")
            self.commit(start, pk, ck)
            if start in synth.CHECK[self.w]:
                g = self.glob_check(start)
                self.checkpoints[start] = g
                if not g.get("ok"):
                    raise ValueError("回头段全局检查未通过")
            for x in self.segs[k0 + 1:k1 + 1]:
                sec = x["id"]
                _, ck = self.segment(sec, tag)
                if not ck.get("pass"):
                    raise ValueError(f"下游 {sec} 未通过")
                if sec in synth.CHECK[self.w]:
                    g = self.glob_check(sec)
                    self.checkpoints[sec] = g
                    if not g.get("ok"):
                        raise ValueError(f"下游 {sec} 全局检查未通过")
        except Exception as exc:
            self.rejected.append({"start": start, "end": end, "why": str(exc), "state": self.state})
            self.state = saved
            self.checkpoints = saved_checkpoints
            for sec, state in saved.items():
                dump(self.dir / f"{sec}.json", state)
            self.save()
            return False
        self.save()
        return True

    def back(self, sec, pk, ck):
        wants = [(c.get("id"), c.get("missing")) for c in pk.get("conditional", [])]
        wants += [(u["id"], u.get("note")) for u in ck.get("unexplained", []) if u.get("why") == "缺前提"]
        if not wants or self.backs >= synth.BACK_MAX:
            return False
        mid, missing = wants[0]
        k, _ = self.seg(sec)
        earlier = "\n\n".join(f"{x['id']}\n当前：{self.state[x['id']]['chosen']}\n候选：{self.mech_text(self.mechs(x['id']))}" for x in self.segs[:k])
        text = next((m["text"] for m in self.mechs(sec) if m["id"] == mid), str(mid))
        r = self.call(f"{sec}_C{self.backs}", synth.BACK.format(K=k+1, TEXT=text, MISSING=missing, EARLIER=earlier), self.b, {"step": "C"})
        start = r.get("sec")
        if start not in self.state or self.seg(start)[0] >= k:
            return False
        return self.repair(start, sec, f"后面{sec}需要前提：{missing}。考虑{r.get('mech')}，理由：{r.get('why')}。不得为后段编造前段经历。")

    def glob_check(self, sec):
        k,_=self.seg(sec)
        selected=[{'sec':s['id'],'bars':[s['start'],s['end']],
                   'chosen':self.state[s['id']]['chosen'],'hist':self.state[s['id']]['hist']}
                  for s in self.segs[:k+1]]
        msg=synth.GLOBAL.format(K=k+1,THREAD=json.dumps(selected,ensure_ascii=False))
        msg+=('\n补充：逐段有原因不代表形成了同一件事。请具体指出哪段先前经历改变了哪段的意义，'
              '有没有把同一个“珍贵所以怕失去”重复贴到每一段，或只用历史编号掩盖实际未建立的前提。'
              '允许延续、允许暂时没在想，不要求每段产生新领悟。检查鲜活、具体、独立可读与理解的积累，'
              '有内容的抽象判断和心理矛盾可以保留。不要在此预设或强迫写出Center。'
              '音乐变化只能用来核对感受，不能把声线、伴奏或强弱变化本身当作心理变化的原因。'
              '历史摘要应保留原选择的具体原因，不能用声音或比喻代替心理经历。'
              'problems只列足以使全局不合格的问题；只要problems非空，ok必须false。'
              '不影响合格的措辞或摘要改进另列suggestions。'
              '\n【此前原始听感，用于核对经历，而非要求逐字复述】\n')
        msg+='\n'.join(self.bead_text(s['id']) for s in self.segs[:k+1])
        if self.w=='op60' and k>=11:
            msg+=('\n远距检查：93–102怎样改变40–61曾经有过的不同快乐的意义？'
                  '不能只说感情更深、情绪更强。须看此前实际建立了哪些不同体验，'
                  '是否在后段真的相遇、发生新关系；不强制照搬某个旧故事。'
                  '同时检查自我退到更大经验之后的感受是否有依据。103–110已写到时，'
                  '检查已经释放与情绪仍不能停下的区别是否被抹平。')
        result=self.call(f'{sec}_G',msg,self.b,{'sec':sec,'step':'G'})
        if result.get('ok') and result.get('problems'):
            result['ok']=False
            result['inconsistent_verdict']=True
        dump(self.dir/f'global_{sec}.json',result)
        print(f'{self.T} {self.w} global@{sec} ok={result.get("ok")}',flush=True)
        return result

    def run(self, last=None):
        self.restore()
        self.status = "running"
        for x in self.segs:
            sec = x["id"]
            if sec in self.state and self.state[sec].get("check", {}).get("pass"):
                pk, ck = self.state[sec]["pick"], self.state[sec]["check"]
            else:
                pk, ck = self.segment(sec)
            if not ck.get("pass"):
                if self.back(sec, pk, ck):
                    pk, ck = self.state[sec]["pick"], self.state[sec]["check"]
                if not ck.get("pass"):
                    self.status = f"needs_revision:{sec}"
                    self.save()
                    return self.status
            if sec in synth.CHECK[self.w]:
                g = self.checkpoints.get(sec) or self.glob_check(sec)
                self.checkpoints[sec] = g
                if not g.get("ok"):
                    problems = g.get("problems", [])
                    start = problems[0].get("sec") if problems else None
                    if not start or start not in self.state or self.backs >= synth.BACK_MAX or not self.repair(start, sec, json.dumps(g, ensure_ascii=False)):
                        self.status = f"needs_global_revision:{sec}"
                        self.save()
                        return self.status
            self.save()
            if sec == last:
                break
        self.status = "complete" if sec == self.segs[-1]["id"] else f"pilot_passed:{sec}"
        self.save()
        return self.status


if __name__ == "__main__":
    print(Run(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]).run(sys.argv[5] if len(sys.argv)>5 else None))
