"""DAG node N04 (10-31, user: "先把这个 center 先试试"; the old N04b fed per-piece history candidates and an example
sentence, banned body/scene words, and Op.61's Center came out as a near copy of the example: "向外行动与旧梦…", specificity 47%).
Three steps, piece-agnostic, no examples, no history:
  write : from the A-draft consensus clusters (N04a, reused: evaluations/centers/A_<w>.json) write the minimal complete
          relation sentence that NAMES ITS DOMAIN (what the matter is about) — keep the concrete objects the drafts name.
          ids cdw_<w> (GPT-6).
  spec  : specificity, the Center sentence alone, all candidates of both works shuffled together; probability on the right
          piece among 10 (centersel.SPEC). ids cds_<judge>_<s>.
  fit   : explanatory power + room to develop per segment (centersel.FIT). ids cdf_<w>_<judge>.
  report: evaluations/center_dag/<w>.md, candidates = new + the current Center (OLD).
usage: python center_dag.py write | spec | fit | report"""
import argparse, json, random, sys
import work_meta
from collections import defaultdict
from statistics import mean
import centers, centersel, evo, seg

OUT = evo.ROOT / "evaluations" / "center_dag"
WORK = {w: work_meta.name(work_meta.load(w, work_meta.ROOT / "works")) for w in ("op60", "op61")}
OLD = {w: work_meta.load(w, work_meta.ROOT / "works")["old_center"] for w in ("op60", "op61")}

WRITE = """任务：为{WORK}确定 Center。Center 是一条“线”所围绕的那件人的事：什么对这个人重要，又是什么使它难以安顿。它是读者听完全曲回头看时，把各段组织起来的那件事。

写成一句“最小完整关系句”：
- 主语：一个或几个对象，用名词短语直接说出它们是什么。
- 要点出领域：读者单看这句话，就要知道这件事是关于什么的、落在哪种关系或处境里。下面材料里说出的具体对象，尽量保留它们本来的名字，不要换成更空的上位词；不能只剩形式上的词（只说“做事”“想念”“内心”“向外”，却不说是关于什么的）。
- 谓语：说清这几个对象之间的一个关系，这个关系从曲子较早处就成立，一直到结尾都成立。不要为了戏剧性默认冲突；材料里是冲突就写明。
- 不写人称和心理动词（他、我、想、怕……）；不写后来才出现的变化、认识、解决或结局；不用比喻和画面；不写问句；不超过 30 个汉字。

依据：下面是 24 份独立文章对这首曲子中心理解的聚类结果（括号里是支持的份数）。贴着支持最多的那一类写，不要换成新奇角度。如果另一类也有很广的独立支持，而且确实是另一件事，可以另写一个；同一件事换个说法只算一个。
{CLUSTERS}

每个 Center 先给 3 种写法，再选一种，并用一句话说出它点出的领域是什么。
只输出一个 ```json 代码块：{{"centers": [{{"options": ["…", "…", "…"], "center": "选中的一句", "domain": "这句话点出的领域", "basis": "依据哪一类、几份"}}]}}"""


# v2 (10-31, user on "失去后的自尊与行动力始终受回忆和脆弱牵制": 失去啥了 / 为什么是受…牵制而不是平等 / 牵制就是最精确的吗):
# feed the 24 per-draft cores (cluster summaries had already dropped the objects), make the model count objects and the
# drafts' own relation verbs first, keep the predicate true for the whole piece incl. the ending, no default verbs.
WRITE2 = """任务：为{WORK}确定 Center。Center 是一条“线”所围绕的那件人的事：什么对这个人重要，又是什么使它难以安顿。它是读者听完全曲回头看时，把各段组织起来的那件事。

材料：24 篇独立文章，每篇对这首曲子中心理解的一句话概括（文章来自不同的人，彼此没有商量）：
{CORES}

请按下面的步骤做，前三步是给你自己理清材料用的，也要写出来：
1. 对象：列出材料里反复出现的“对象”——这个人在意、失去、守住、渴望或抗拒的东西。每个写出几篇提到，并说明材料对它的叫法是否一致（例如有的说出了具体是什么，有的只说“某种东西”）。
2. 关系动词：列出材料用来描述这些对象之间关系的动词或说法（原词），每个写出几篇用到。
3. 从头到尾：这几个对象之间，有没有一个从曲子较早处一直到结尾都成立的关系？特别看结尾：到结尾时，各方是什么状态（被战胜、被接纳、合在一起、仍在拉扯……）？只算多数材料都支持的。
4. 写 Center：一句“最小完整关系句”，不超过 30 个汉字。
   - 名词：说得出它究竟是什么。材料里叫法一致的，用材料的叫法；不一致的，用支持最多、多数材料都能接受的说法，并在 why 里写明几篇支持；不能留下没有对象的空词（单说“失去”“牵挂”“过去”“某种东西”而不说是什么的）。
   - 谓语：必须对全曲成立，包括结尾；各方的地位按材料来——不要把一方定成另一方的障碍或附属，除非多数材料从头到尾都这样写；动词从第 2 步的材料用词里选，或者贴近它们，并在 why 里说明它为什么比其他候选动词更准确。“牵制”“张力”“并存”“交织”这类放在哪首曲子上都说得通的词，除非你能说明它比材料用词更准确，否则不用。
   - 不写人称和心理动词（他、我、想、怕……）；不写后来才出现的变化、认识或结局；不用比喻和画面；不写问句。
5. 自检：一个没读过这些材料的人，单看这句话，能不能说出这件事是关于什么的？把它放到另一首{COMPOSER}作品上是否也成立？如果也成立，就改得更贴这首曲子。

如果材料里另有一种理解也有很广的独立支持，而且确实是另一件事，可以另写一个；同一件事换个说法只算一个。每个 Center 给 3 种写法，再选一种。
只输出一个 ```json 代码块：
{{"objects": [{{"object": "…", "n": 0, "naming": "叫法是否一致"}}], "verbs": [{{"verb": "…", "n": 0}}], "whole": "从头到尾成立的关系，以及结尾时各方的状态",
  "centers": [{{"options": ["…", "…", "…"], "center": "选中的一句", "domain": "这句话点出的领域", "why": "名词和谓语为什么这样选（几篇支持、为什么这个动词最准确）", "selfcheck": "第 5 步的结果"}}]}}"""


def cores(w):
    A = json.loads((evo.ROOT / "evaluations" / "centers" / f"A_{w}.json").read_text(encoding="utf-8"))
    return "\n".join(f"{k}. {x['core']}" for k, x in enumerate(A["per_draft"], 1))


def clusters(w):
    A = json.loads((evo.ROOT / "evaluations" / "centers" / f"A_{w}.json").read_text(encoding="utf-8"))
    return "\n".join(f"- （{c['n']} 份）{c['summary']}" for c in A["clusters"])


V = __import__("os").environ.get("CDV", "")
WID = lambda w: f"cdw{V}_{w}"


def pool(w):
    j = evo.parse_json(evo.output(WID(w)) or "{}") or {}
    return [{"id": f"N{k}", "center": c["center"], "domain": c.get("domain", ""), "src": "新流程"} for k, c in enumerate(j.get("centers") or [], 1)] \
        + ([{"id": "OLD", "center": work_meta.load(w)["old_center"], "domain": "", "src": "现在的 Center"}] if work_meta.load(w).get("old_center") else [])


def render_write(w, version=None, material=None):
    version = V if version is None else version
    T = globals().get(f"WRITE{version}") or WRITE
    if material is None:
        material = json.loads((evo.ROOT / "evaluations" / "centers" / f"A_{w}.json").read_text(encoding="utf-8"))
    d = work_meta.load(w)
    return T.format(WORK=work_meta.name(d), COMPOSER=d["composer"],
                    CLUSTERS="\n".join(f"- （{c['n']} 份）{c['summary']}" for c in material["clusters"]),
                    CORES="\n".join(f"{k}. {x['core']}" for k, x in enumerate(material["per_draft"], 1)))


def spec_template(works):
    ds = [work_meta.load(w) for w in works]
    if any((d["composer"], d["specificity_candidates"]) != (ds[0]["composer"], ds[0]["specificity_candidates"]) for d in ds):
        raise ValueError("joint specificity requires identical composer and candidate lists; run --work separately")
    return centersel.spec_for(works[0])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("phase", choices=["write", "spec", "fit", "report", "render"])
    ap.add_argument("--work")
    ap.add_argument("--render-dir")
    ap.add_argument("--a-json", help="offline render: material JSON with per_draft and clusters")
    ap.add_argument("--candidates-json", help="offline render: candidate JSON list with id and center")
    ap.add_argument("--raw", action="store_true", help="offline render: omit the existing transport NO_WEB suffix")
    a = ap.parse_args(); ph = a.phase
    works = work_meta.selected(work=a.work)
    if ph == "render":
        if not a.render_dir:
            raise ValueError("render requires --render-dir")
        material = json.loads(open(a.a_json, encoding="utf-8").read()) if a.a_json else None
        prompts = {}; pools = {}
        transport = lambda msg: msg if a.raw or evo.NO_WEB.strip() in msg[-60:] else msg + evo.NO_WEB
        for w in works:
            pp = json.loads(open(a.candidates_json, encoding="utf-8").read()) if a.candidates_json else pool(w)
            pools[w] = pp
            prompts[f"N04b.{w}.txt"] = transport(render_write(w, material=material))
            for jn in ("gpt6", "gpt56"):
                shuffled = pp[:]; random.Random(f"cdf{w}{jn}").shuffle(shuffled)
                prompts[f"N04d.{w}.{jn}.txt"] = transport(centersel.fit_for(w) + "\n".join(f"{x['id']}：{x['center']}" for x in shuffled))
        items = [{"id": f"{w}:{x['id']}", "center": x["center"]} for w in works for x in pools[w]]
        for jn in ("gpt6", "gpt56"):
            for sample in (1, 2):
                shuffled = items[:]; random.Random(f"cds{jn}{sample}").shuffle(shuffled)
                prompts[f"N04c.{jn}.{sample}.txt"] = transport(spec_template(works) + "\n".join(f"C{i+1}：{x['center']}" for i, x in enumerate(shuffled)))
        work_meta.write_prompts(a.render_dir, prompts)
        raise SystemExit(0)
    OUT.mkdir(parents=True, exist_ok=True)
    # New-work specificity calls need separate ids/keys from the historical joint test.
    scope = "" if works == ["op60", "op61"] else "_" + "_".join(works)
    if ph == "write":
        T = globals().get(f"WRITE{V}") or WRITE
        msg = lambda w: render_write(w)
        evo.run_parallel([(w, (lambda w=w: evo.call(WID(w), msg(w), prompt_text=T, model=evo.G6, meta={"stage": f"center_dag_write{V}"}))) for w in works], 2)
        for w in works:
            j = evo.parse_json(evo.output(WID(w)) or "{}") or {}
            print(w, "对象", [(o.get("object"), o.get("n")) for o in j.get("objects") or []])
            print(w, "动词", [(o.get("verb"), o.get("n")) for o in j.get("verbs") or []])
            print(w, "从头到尾", j.get("whole"))
            for c in j.get("centers") or []:
                print(w, "候选", c.get("options"), "→", c.get("center")); print("   why:", c.get("why")); print("   自检:", c.get("selfcheck"))
        for w in works:
            for c in pool(w):
                print(w, c["id"], c["center"], "|", c["domain"])
    elif ph == "spec":
        items = [{"id": f"{w}:{c['id']}", "center": c["center"]} for w in works for c in pool(w)]
        jobs = []
        for jn, model in (("gpt6", evo.G6), ("gpt56", evo.G56)):
            for s in (1, 2):
                it = items[:]; random.Random(f"cds{jn}{s}").shuffle(it)
                key = {f"C{i + 1}": x["id"] for i, x in enumerate(it)}
                (OUT / f"spec_key{V}{scope}_{jn}_{s}.json").write_text(json.dumps(key, ensure_ascii=False), encoding="utf-8")
                S = spec_template(works)
                msg = S + "\n".join(f"C{i + 1}：{x['center']}" for i, x in enumerate(it))
                rid = f"cds{V}{scope}_{jn}_{s}"
                jobs.append((rid, (lambda rid=rid, msg=msg, model=model: evo.call(rid, msg, prompt_text=S, model=model, meta={"stage": "center_dag_spec"}))))
        evo.run_parallel(jobs, 4)
    elif ph == "fit":
        jobs = []
        for w in works:
            p = pool(w)
            for jn, model in (("gpt6", evo.G6), ("gpt56", evo.G56)):
                pp = p[:]; random.Random(f"cdf{w}{jn}").shuffle(pp)
                msg = centersel.fit_for(w) + "\n".join(f"{c['id']}：{c['center']}" for c in pp)
                rid = f"cdf{V}_{w}_{jn}"
                jobs.append((rid, (lambda rid=rid, msg=msg, model=model: evo.call(rid, msg, prompt_text=centersel.FIT, model=model, meta={"stage": "center_dag_fit"}))))
        evo.run_parallel(jobs, 4)
    elif ph == "report":
        spec = defaultdict(list)
        for jn in ("gpt6", "gpt56"):
            for s in (1, 2):
                r = evo.output(f"cds{V}{scope}_{jn}_{s}")
                if not r:
                    continue
                key = json.loads((OUT / f"spec_key{V}{scope}_{jn}_{s}.json").read_text(encoding="utf-8"))
                for it in evo.parse_json(r)["items"]:
                    cid = key.get(it["id"])
                    if cid:
                        w = cid.split(":")[0]; tot = sum(float(v) for v in it["probs"].values()) or 1
                        spec[cid].append(100 * float(it["probs"].get(work_meta.load(w)["specificity_right"], 0)) / tot)
        for w in works:
            fit = defaultdict(list)
            for jn in ("gpt6", "gpt56"):
                r = evo.output(f"cdf{V}_{w}_{jn}")
                if r:
                    for c in evo.parse_json(r)["candidates"]:
                        bs = c.get("by_segment") or []
                        fit[c["id"]].append({"nat": bs.count("自然") / max(1, len(bs)), "no": bs.count("不能"), "dev": float(c.get("development", 0)),
                                             "ov": float(c.get("overall", 0)), "note": c.get("note", "")})
            m = lambda xs: mean(xs) if xs else float("nan")
            md = [f"# {w}｜Center（DAG N04 新流程）", "", "| 候选 | 来源 | 专属性 | 解释力（自然段比例） | 不能解释的段 | 展开空间 | 说服力 | Center | 点出的领域 |", "|---|---|---|---|---|---|---|---|---|"]
            for c in pool(w):
                f = fit.get(c["id"], []); sp = spec.get(f"{w}:{c['id']}", [])
                md.append(f"| {c['id']} | {c['src']} | {m(sp):.0f}% | {100 * m([x['nat'] for x in f]):.0f}% | {m([x['no'] for x in f]):.1f} | "
                          f"{m([x['dev'] for x in f]):.1f} | {m([x['ov'] for x in f]):.1f} | {c['center']} | {c['domain']} |")
            md += ["", "评委一句话："] + [f"- {cid}（{'gpt-6' if k == 0 else '5.6'}）：{x['note']}" for cid, xs in fit.items() for k, x in enumerate(xs)]
            (OUT / f"{w}{V}.md").write_text("\n".join(md), encoding="utf-8"); print("\n".join(md)); print()
