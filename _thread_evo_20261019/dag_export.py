"""10-31: snapshot every prompt of the current DAG (new work -> final beads + line) into DAG/prompts/, so DAG.md can
point at real files. Two kinds per node: the template as it sits in the script (or prompt file), and one prompt that was
actually sent (Op.61 run). Re-run after any prompt change.  usage: python dag_export.py"""
import importlib, shutil
from pathlib import Path
import evo

ROOT = evo.ROOT; OUT = ROOT / "DAG" / "prompts"; BEAD = ROOT.parent / "_bead_op61_20261020"
OUT.mkdir(parents=True, exist_ok=True)

# node -> [(file name, source)] ; source = ("var", module, NAME) | ("file", path) | ("run", run_id) | ("beadrun", stage)
SPEC = {
    "N05g_成品修补回路": [("局部修订模板.txt", ("file", ROOT / "runs/_batches/continue_r80/templates/repair_scope.txt")),
                      ("回补模板.txt", ("file", ROOT / "runs/_batches/continue_r80/templates/restore.txt")),
                      ("局部修订实发_op61.txt", ("run", "scr84a_op61_F2")),
                      ("回补实发_op61.txt", ("run", "scr86b_op61_F1"))],
    "N05f_全篇重组": [("模板.txt", ("file", ROOT / "runs/_batches/round54_broader/prompts/r54weave_P1.txt")), ("实发_op61.txt", ("run", "scr54weave_op61_P1"))],
    "N05e_写后修订": [("模板.txt", ("var", "round50_continue", "PROMPT")), ("回补模板.txt", ("var", "round50_restore", "PROMPT")), ("实发_op61.txt", ("run", "scr50progress1rr_op61_A5"))],
    "N01_分段": [("模板.txt", ("file", ROOT / "prompts" / "seg_published_v1.txt")), ("实发_op61.txt", ("run", "seg_op61_v1"))],
    "N02_A稿": [("模板_int.txt", ("file", BEAD / "gen_A" / "A_int_v1.op61.txt")), ("模板_web.txt", ("file", BEAD / "gen_A" / "A_web_v2.op61.txt"))],
    "N03a_珠子_pool": [("模板.md", ("file", BEAD / "prompts" / "pool_v2.md")), ("实发_S01.txt", ("beadrun", "pool_v2/pool"))],
    "N03b_珠子_gen": [("模板.md", ("file", BEAD / "prompts" / "gen_v1.md")), ("实发_S01.txt", ("beadrun", "gen_b"))],
    "N03c_珠子_rev1": [("模板.md", ("file", BEAD / "prompts" / "rev1_v1.md")), ("实发_S01.txt", ("beadrun", "rev1_b"))],
    "N03d_珠子_rev2": [("模板.md", ("file", BEAD / "prompts" / "rev2_v1.md")), ("实发_S01.txt", ("beadrun", "rev2_b"))],
    "N03e_珠子_final": [("模板.md", ("file", BEAD / "prompts" / "final_v2.md")), ("实发_S01.txt", ("beadrun", "final_b"))],
    "N03f_珠子_piece": [("模板.md", ("file", BEAD / "prompts" / "piece_v1.md"))],
    "N03g_珠子_fix": [("模板.md", ("file", BEAD / "prompts" / "fix_v1.md"))],
    "N03h_珠子_去编辑句": [("模板.txt", ("var", "bead_clean", "P")), ("实发_op61.txt", ("run", "bc_op61"))],
    "N03_珠子_结构规范": [("模板.md", ("file", BEAD / "prompts" / "struct_spec_v1.md"))],
    "N04a_Center_归纳A稿": [("模板.txt", ("var", "center_from_A", "P")), ("实发_op61.txt", ("run", "cA_op61"))],
    "N04b_Center_写句": [("模板.txt", ("var", "center_dag", "WRITE2")), ("实发_op61.txt", ("run", "cdw2_op61")), ("旧版模板_center_v3.txt", ("var", "center_v3", "P"))],
    "N04c_Center_测专属性": [("模板.txt", ("var", "centersel", "SPEC")), ("实发.txt", ("run", "csp_gpt56_1"))],
    "N04d_Center_测解释力": [("模板.txt", ("var", "centersel", "FIT")), ("实发_op61.txt", ("run", "cfit_op61_gpt6"))],
    "N05a_经历骨架": [("模板.txt", ("file", ROOT / "schemes" / "Q5_A1.txt"))],
    "N05b_选路": [("模板.txt", ("file", ROOT / "schemes" / "Q5_A2.txt"))],
    "N05c_体验性质": [("模板.txt", ("file", ROOT / "schemes" / "Q5_A3.txt"))],
    "N05d_写线": [("模板.txt", ("file", ROOT / "schemes" / "Q15_A4.txt"))],
    "N05a_写稿_主线": [("模板_SPINE.txt", ("var", "line8", "SPINE")), ("实发_op61.txt", ("run", "n8a_op61_r2"))],
    "N05b_写稿_成文": [("模板_LAY.txt", ("var", "line8", "LAY")), ("实发_op61.txt", ("run", "n8_op61_r2"))],
    "N06_转关系图": [("模板.txt", ("var", "tgraph4", "P")), ("实发_op61.txt", ("run", "tg4_n8_op61_r2_r2"))],
    "N07_抽词义": [("模板.txt", ("var", "v6gen", "GLOSS")), ("实发_op61.txt", ("run", "gl_op61"))],
    "N08_通用改写": [("模板.txt", ("var", "v6gen", "WRITE")), ("实发_op61.txt", ("run", "gw_op61_g1"))],
    "N09_人话_开放评审": [("模板.txt", ("var", "lang_open", "P2")), ("旧版模板_v1.txt", ("var", "lang_open", "P")), ("旧版实发_op61.txt", ("run", "lo_op61_line_g6_r1"))],
    "N09c_人话_按开放评审改": [("模板.txt", ("var", "v6human", "FIXOPEN"))],
    "N09a_人话_挑问题": [("模板.txt", ("var", "v6human", "FIND")), ("规则.txt", ("var", "v6human", "RULES")), ("实发_op61.txt", ("run", "hu_op61_b0"))],
    "N09b_人话_改写": [("模板_WRITE3.txt", ("var", "v6human", "WRITE3")), ("第六种替换_R1.txt", ("var", "v6human", "R1_6")),
                     ("第六种替换_R2.txt", ("var", "v6human", "R2_6")), ("心里话_INNER.txt", ("var", "v6human", "INNER")), ("实发_op61.txt", ("run", "hw_op61_h11"))],
    "N09v_句式多样化": [("模板.txt", ("var", "v6vary", "P")), ("实发_op61.txt", ("run", "vy_op61_h17v"))],
    "N09w_逐字精读": [("模板.txt", ("var", "v6word", "P")), ("实发_op61.txt", ("run", "wd_op61_g6_h17"))],
    "N10g_守覆盖": [("模板.txt", ("var", "v6guard", "FIX"))],
    "N10c_提覆盖": [("模板.txt", ("var", "v6boost", "FIX")), ("实发_op61.txt", ("run", "bo_op61_q4"))],
    "N03i_珠子语言_评审": [("模板.txt", ("var", "bead_lang", "REVIEW"))],
    "N03i_珠子语言_改写": [("模板.txt", ("var", "bead_lang", "FIX"))],
    "N03i_珠子语言_核对": [("模板.txt", ("var", "bead_lang", "CHECK"))],
    "N10a_测_覆盖": [("模板.txt", ("var", "v6cov", "COV")), ("实发_op61.txt", ("run", "cov_op61_g6_h11"))],
    "N10b_测_单独读": [("模板_ALONE.txt", ("var", "v6alone", "ALONE")), ("模板_TRANS.txt", ("var", "v6alone", "TRANS")), ("实发_op61.txt", ("run", "al_op61_g6_h11"))],
    "N10c_测_清单": [("模板_BUILD.txt", ("var", "v6check", "BUILD")), ("模板_CHECK.txt", ("var", "v6check", "CHECK")), ("实发_op61.txt", ("run", "chk_op61_g6_h11"))],
    "N10d_测_盲评": [("模板.txt", ("var", "v6fix", "BLIND")), ("实发_op61.txt", ("run", "v6b_op61_g6_h11_vsb0"))],
    "N11_补漏": [("模板.txt", ("var", "v6human", "FIXLOST")), ("实发_op61.txt", ("run", "hl_op61_h13"))],
    "N12a_片段对应": [("模板.txt", ("var", "span_links", "PROMPT")), ("实发_op61.txt", ("run", "span1_r49b_op61_S11_g6"))],
}


def get(src):
    kind = src[0]
    if kind == "file":
        return Path(src[1]).read_text(encoding="utf-8-sig")
    if kind == "var":
        v = getattr(importlib.import_module(src[1]), src[2])
        return v if isinstance(v, str) else repr(v)
    if kind == "run":
        d = ROOT / "runs" / src[1]
        for n in ("input.txt", "prompt.txt"):
            if (d / n).exists():
                return (d / n).read_text(encoding="utf-8")
        raise FileNotFoundError(d)
    if kind == "beadrun":
        return (BEAD / "runs" / src[1] / "S01.prompt.txt").read_text(encoding="utf-8")


if __name__ == "__main__":
    assert OUT.resolve() == (Path(__file__).resolve().parent / "DAG" / "prompts").resolve(), 'Unexpected snapshot target'
    shutil.rmtree(OUT); OUT.mkdir(parents=True)
    for node, files in SPEC.items():
        (OUT / node).mkdir()
        for name, src in files:
            try:
                (OUT / node / name).write_text(get(src), encoding="utf-8")
                print("ok ", node, name)
            except Exception as e:
                print("MISS", node, name, repr(e)[:120])
