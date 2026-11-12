"""Run the unchanged music-project cup question using a native Web effort."""
import asyncio
import argparse
import json
import os
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ["GPT2AGENT_SAFECHAIN_ROOT"] = str(ROOT)
os.environ["GPT2AGENT_RUNTIME_DIR"] = str(Path.home() / ".gpt2agent/codex-safechain-lab/accounts")

import cup_probe

cup_probe.EFFORT = "extended"


async def main(model="gpt-5-6-thinking", effort="extended"):
    cup_probe.MODEL = model
    cup_probe.EFFORT = effort
    run = ROOT / "runs" / (f"cup_{model}_{effort}_" + time.strftime("%Y%m%d_%H%M%S"))
    runner = cup_probe.Runner(run)
    ensure_client = runner.provider._ensure_client
    observed = []

    async def diagnostic_client():
        backend, client = await ensure_client()
        observed.append(client)
        prepare = client._prepare_conversation

        async def diagnostic_prepare(session, payload, headers):
            await prepare(session, payload, headers)
            summary = {key: payload.get(key) for key in (
                "model", "thinking_effort", "conversation_mode", "history_and_training_disabled",
                "timezone", "timezone_offset_min", "supported_encodings", "client_prepare_state",
                "force_parallel_switch", "paragen_cot_summary_display_override",
            )}
            run.mkdir(parents=True, exist_ok=True)
            (run / "request_summary.json").write_text(
                json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        client._prepare_conversation = diagnostic_prepare
        return backend, client

    runner.provider._ensure_client = diagnostic_client
    try:
        passed = await runner.probe(f"native Web {model}/{effort}; unchanged cup question and gate")
        if observed:
            message = observed[-1].last_turn_metadata.get("message") or {}
            summary = {key: message.get(key) for key in ("id", "channel", "status", "recipient", "end_turn")}
            metadata = message.get("metadata") or {}
            summary["metadata_keys"] = list(metadata)
            summary["routing"] = {key: metadata.get(key) for key in (
                "model_slug", "default_model_slug", "thinking_effort", "reasoning_effort"
            )}
            (run / "response_summary.json").write_text(
                json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        print(json.dumps({"run": str(run), "passed": passed}), flush=True)
    finally:
        await runner.provider.aclose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="gpt-5-6-thinking")
    parser.add_argument("--effort", default="extended")
    args = parser.parse_args()
    asyncio.run(main(args.model, args.effort))
