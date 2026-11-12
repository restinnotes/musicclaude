"""T-entry finders with all 24 T documents (adds the 6 recovered GPT-5.6 T docs). Separate zip; does not touch the 18-doc runs."""
import thr, common
T = thr.load_T(); assert len(T) == 24
Z = thr.zip_of("T_research24", {f"T/{k}.md": v for k, v in T.items()})
TPL = (thr.ROOT / "prompts" / "find_v1.md").read_text(encoding="utf-8")
mat = (f"全曲按 PTNA／朝山冻结的十四段：{common.SEGLIST}。\n\n附件 `T_research24.zip` 的 `T/` 里有 24 份独立的纵向聆听研究（文件名即来源 ID：四个模型，各有不查资料的 int 版与查阅资料的 web 版，各 3 份）。"
       "它们直接讨论这首曲子从头到尾在处理什么、前面怎样改变后面。")
p = TPL.replace("{MATERIALS}", mat).replace("{WEB_NOTE}", "不要联网搜索。")
keys = []
for i in range(1, 6):
    name = f"T24-{i}"
    def fn(name=name):
        return thr.finish_text("find", name, thr.call("find", name, p, [Z]))
    thr.task("find", name, fn, kind="text"); keys.append(("find", name))
if __name__ == "__main__":
    thr.run(keys)
