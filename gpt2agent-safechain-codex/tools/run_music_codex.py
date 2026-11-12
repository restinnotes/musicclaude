"""Use the music queue with this isolated provider and account-native effort."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ["GPT2AGENT_SAFECHAIN_ROOT"] = str(ROOT)
os.environ["GPT2AGENT_RUNTIME_DIR"] = str(Path.home() / ".gpt2agent/codex-safechain-lab/accounts")

import cup_probe

cup_probe.EFFORT = "extended"

if __name__ == "__main__":
    raise SystemExit(cup_probe.main())
