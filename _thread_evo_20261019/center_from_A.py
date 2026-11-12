"""Typical Centers from the 24 A drafts (user 10-21: A-int/A-web drafts already carry typical whole-piece readings;
keep only the few most convincing Centers, no padding with fringe ones). One GPT-6 call per work, drafts attached.
ids: cA_<work> -> evaluations/centers/A_<work>.json"""
import argparse, json, glob
import work_meta
import centers, evo

SRC = {w: str(work_meta.source_dir(work_meta.load(w, work_meta.ROOT / "works"))) for w in ("op60", "op61")}
P = ("附件是 24 份关于{WORK}的文章，由不同模型（gflash = Gemini Flash，luna = Luna，gpt56w = GPT-5.6，gpt6w = GPT-6）按两种提示词写成"
     "（int = 凭自己理解，web = 先查资料），每份都讲了这首曲子表达了怎样的情绪和精神状态。\n"
     "请做三件事：\n"
     "1. per_draft：逐份用一句话说出它对整首曲子的中心理解（它认为这首曲子从头到尾在处理一个人的什么事），标明文件名。\n"
     "2. clusters：把意思相同或相近的中心理解归为一类，写出每类的概括、支持它的文件名和份数。\n"
     "3. centers：只从最有说服力的类里，给出 2–4 个 Center——优先是多份稿子、多个模型都独立得出的理解；只有一两份提到的偏门读法不要，"
     "除非它确实特别贴合这首曲子。每个 Center 按这个定义写：说清楚共同的困扰——什么对这个人重要（matters），又是什么使它难以安顿（hard）；"
     "不预告发展的路线和最后的回答（不要写他最后怎样了）。用贴近这些稿子原本说法的人话，不要改写成新奇的角度。\n"
     "只输出一个 ```json 代码块：{\"per_draft\": [{\"file\": \"…\", \"core\": \"…\"}], \"clusters\": [{\"summary\": \"…\", \"files\": [\"…\"], \"n\": 0}], "
     "\"centers\": [{\"center\": \"一句话\", \"matters\": \"…\", \"hard\": \"…\", \"support\": 0, \"models\": [\"…\"], \"why_convincing\": \"…\"}]}")

def render(w):
    return P.replace("{WORK}", work_meta.name(work_meta.load(w))).replace("附件是 24 份", "附件（一个文件，内含 24 份，以“########## 文件：…”分隔）是 24 份")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", help="one work or comma-separated works; default WORK or legacy op60,op61")
    ap.add_argument("--render-dir")
    a = ap.parse_args()
    works = work_meta.selected(work=a.work)
    if a.render_dir:
        work_meta.write_prompts(a.render_dir, {f"N04a.{w}.txt": render(w) for w in works})
        raise SystemExit(0)
    jobs = []
    for w in works:
        d = str(work_meta.source_dir(work_meta.load(w)))
        files = sorted(glob.glob(f"{d}/SRC-*.md"))
        assert len(files) == 24, (w, len(files))
        merged = evo.RUNS / f"A_drafts_{w}.md"   # 24 attachments -> HTTP 422; one merged file instead
        merged.write_text("\n\n".join(f"########## 文件：{f.replace(chr(92), '/').split('/')[-1]} ##########\n\n" + open(f, encoding="utf-8").read()
                                      for f in files), encoding="utf-8")
        files = [str(merged)]
        msg = render(w)
        jobs.append((f"cA_{w}", (lambda w=w, msg=msg, files=files: evo.call(f"cA_{w}", msg, prompt_text=P, attach=files, meta={"stage": "center_from_A", "work": w}))))
    evo.run_parallel(jobs, 2)
    for w in works:
        r = evo.output(f"cA_{w}")
        if r:
            j = evo.parse_json(r)
            (evo.ROOT / "evaluations" / "centers" / f"A_{w}.json").write_text(json.dumps(j, ensure_ascii=False, indent=1), encoding="utf-8")
            print("==", w)
            for c in j["clusters"]:
                print(f"  [{c['n']}] {c['summary']}")
            for k, c in enumerate(j["centers"], 1):
                print(f"  CENTER {k} (support {c.get('support')}, {','.join(c.get('models', []))}): {c['center']}")
