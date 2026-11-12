# -*- coding: utf-8 -*-
"""Rebuild prompt_S01_files.md / prompt_S01_zip.md from the body template.

The first build lost every CJK character in the {{INPUT}} paragraph to '?'
(the sentence was written through a non-UTF-8 console).  The body is intact.
This script substitutes the input paragraph with explicit UTF-8 text, keeping
the single intended difference between the two harness prompts.
"""
from pathlib import Path

ROOT = Path(r"D:\musicclaude\_harness_source_20261029")
body = (ROOT / "prompt_S01_body.md").read_text(encoding="utf-8")

FILES_INPUT = (
    "工作目录下有 `input/A/`（24 份原稿，文件名即来源 ID，如 `SRC-gpt6w-web-1`）"
    "和 `input/structure.json`（冻结的 PTNA／朝山十四段，mm.1–116）。"
    "这些原稿是研究素材，不保证全对：小节号可能有误（有的稿按错误的总小节数编号）、"
    "范围可能过宽、引语可能不可靠。"
)
ZIP_INPUT = (
    "附件 `input_bundle.zip` 内有 `A/`（24 份原稿，文件名即来源 ID，如 `SRC-gpt6w-web-1`）"
    "和 `structure.json`（冻结的 PTNA／朝山十四段，mm.1–116）。"
    "这些原稿是研究素材，不保证全对：小节号可能有误（有的稿按错误的总小节数编号）、"
    "范围可能过宽、引语可能不可靠。"
)

for name, text in [("prompt_S01_files.md", FILES_INPUT), ("prompt_S01_zip.md", ZIP_INPUT)]:
    out = body.replace("{{INPUT}}", text)
    assert "{{INPUT}}" not in out
    assert "?" not in out, name
    (ROOT / name).write_text(out, encoding="utf-8")
    print(name, len(out), "chars, '?' count:", out.count("?"))
