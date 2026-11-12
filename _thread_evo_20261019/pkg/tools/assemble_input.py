#!/usr/bin/env python3
"""Convenience only: assemble identical P0 with one optional additional-material condition.
This script NEVER invokes any model. Agent should independently discover gpt3 CLI arguments.
"""
from pathlib import Path
import argparse

ROOT = Path(__file__).resolve().parents[1]
P0 = ROOT/'01_提示词与基准'/'P0_纯提示词_直接调用.txt'
DATA = ROOT/'02_Bead精简输入'
NAMES = {
    'D1': 'D1_十四段音乐锚点.md',
    'D2': 'D2_十四条主体验.md',
    'D3': 'D3_十四段reader.md',
    'D4': 'D4_五十一条完整Bead.md',
}
p = argparse.ArgumentParser()
p.add_argument('--condition', choices=['D0', *NAMES], required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
core = P0.read_text(encoding='utf-8').strip()
if a.condition == 'D0':
    msg = core + '\n'
else:
    extra = (DATA/NAMES[a.condition]).read_text(encoding='utf-8').strip()
    # Same wrapper across ALL nonzero conditions to avoid confounding the comparison.
    msg = core + '\n\n---\n以下是可供核对的额外参考材料（并非必须模仿的文章或固定剧情）。' \
        '请优先完成原提示词规定的 Thread 任务；材料只是可参考的局部体验依据。\n\n' + extra + '\n'
a.output.parent.mkdir(parents=True, exist_ok=True)
a.output.write_text(msg, encoding='utf-8')
print(f'{a.condition}: {len(msg)} characters, saved to {a.output}')
