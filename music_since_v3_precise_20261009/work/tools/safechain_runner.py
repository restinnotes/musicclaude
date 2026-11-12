"""Opt-in local safechain batch route; leaves runner.py's model routes intact.
R1 (2026-10-08): 旧直连路由保留作回退；gpt56w/gpt6w 默认走 gpt2_adapter。"""
from pathlib import Path
import os
import sys

REPO = Path(os.environ.get("GPT2AGENT_SAFECHAIN_ROOT", str(
    Path(__file__).resolve().parents[3] / "gpt2agent-safechain")))
sys.path.insert(0, str(REPO / "tools" / "chatgpt_web"))
from music_runner import main, run_jobs

if __name__ == "__main__":
    raise SystemExit(main())
