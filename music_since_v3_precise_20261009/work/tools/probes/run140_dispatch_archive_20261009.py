"""run140 Mech 独立评审：派发归档助手（离线工程脚本）.

只做工程归档，不做任何音乐分类或裁决，不碰 production/hold。
流程（每任务）：
  1. 核冻结：driver SHA / run138 cases SHA / 全部 prompt SHA，任一不符即报错退出，不重新冻结。
  2. 用冻结 driver 的 load_and_validate / build_packs / render_pack_prompt 重建
     pack，核 render 字节 == 落盘冻结 prompt 字节 == 本任务特许 SHA。
  3. 建 reviews/<pack>_<reviewer>_r1/（非空即拒，禁覆盖）→ task.txt 写冻结字节。
  4. response.txt 必须已由派发员按 T3 completed summary 原文逐字写入；本脚本只读。
  5. 外层严格解析：裸完整 JSON 或一个完整 ```json fence（拒前言尾言），
     拒重复键，拒 NaN/Infinity；再调冻结 driver parse_review 作全部语义核验
     （pack_id、12 条、blindID 集合 exact+unique、quoted 逐字、explains 覆盖）。
  6. 写 meta.json / parse_report.json；失败保留原文，不自动重采样。
  7. 只新建 report；schema_pass != 音乐分类 pass；不汇总、不多数票、不判胜负。

用法：
  python -I -B tools/probes/run140_dispatch_archive_20261009.py --check-frozen
  python -I -B tools/probes/run140_dispatch_archive_20261009.py --archive \
      --pack pack02 --reviewer luna \
      --client-request-id music-20261009-run140-pack02-luna-r1 \
      --requested-provider codex --requested-model gpt-6-luna \
      --requested-option reasoningEffort=max \
      --observed-provider codex --observed-model gpt-6-luna \
      --status completed \
      --submitted-at 2026-10-09T09:00:00+00:00 \
      --terminal-at 2026-10-09T09:25:00+00:00
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

PROBE = Path(__file__).resolve()
TOOLS = PROBE.parent.parent
ROOT = TOOLS.parent
sys.path.insert(0, str(TOOLS))

from run140_mech_independent_review import (  # noqa: E402
    build_packs,
    load_and_validate,
    parse_review,
    render_pack_prompt,
)

FROZEN_DRIVER_SHA = "aa2ef7e09747de4b56aad3b8974d408c2e6ad909166c4e6d86c9754d382abaf1"
FROZEN_CASES_SHA = "8f30ef391dce919fd8c0e5f8c112d7b40a7c5248b1498b575b011d4663ae78aa"
FROZEN_PROMPT_SHA = {
    "pack01": "082a8dedd3c91875f47e4e3899f5a289732db5633ea9757caffcd2b7b910b16e",
    "pack02": "9745925a131a30b08adb4e363c01f8989007d170fb0e1a3d1d971009f01c1211",
    "pack03": "37c7843c17b4278886427362eb3bdf2fe509922d317fcbe8964d3d316d889e5f",
    "pack04": "57f2a129293edf5aaf008141a881134d0016f5e697e4f4d76d41fa64da73075c",
    "pack05": "bd1025da30705ccddcb3192d9b31196897ac5a72356803492039531a3d462efc",
}
OUT = ROOT / "runs/run140_mech_independent_review"
VERDICT_ORDER = ["insight", "restatement", "manufactured", "imported", "undetermined"]


def sha_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def check_frozen() -> dict:
    """核 driver / cases / 全部 prompt 特许 SHA；返回逐项结果."""
    result = {}
    result["driver"] = sha_bytes((TOOLS / "run140_mech_independent_review.py").read_bytes())
    result["driver_ok"] = result["driver"] == FROZEN_DRIVER_SHA
    result["cases"] = sha_bytes((ROOT / "runs/run138_e5_counterfactual/cases.json").read_bytes())
    result["cases_ok"] = result["cases"] == FROZEN_CASES_SHA
    prompts = {}
    for pack_id, want in FROZEN_PROMPT_SHA.items():
        got = sha_bytes((OUT / ("review_prompts/%s.txt" % pack_id)).read_bytes())
        prompts[pack_id] = {"sha256": got, "ok": got == want}
    result["prompts"] = prompts
    result["all_ok"] = bool(result["driver_ok"] and result["cases_ok"]
                            and all(v["ok"] for v in prompts.values()))
    return result


def _reject_constant(value: str):
    raise ValueError("非法 JSON 常量：" + value)


def _no_dup_object(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError("重复键：" + str(key))
        obj[key] = value
    return obj


def strict_outer_load(text: str):
    """外层严格装载：裸完整 JSON 或一个完整 fence；拒重复键与 NaN/Infinity."""
    if not isinstance(text, str):
        raise ValueError("输出不是文本")
    clean = text.strip()
    if clean.startswith("```"):
        match = re.fullmatch(r"```(?:json)?\s*\n(.*?)\n```", clean, re.S)
        if not match:
            raise ValueError("JSON fence 不完整")
        clean = match.group(1)
    return json.loads(clean, object_pairs_hook=_no_dup_object,
                      parse_constant=_reject_constant)


def write_json(path: Path, obj: dict) -> None:
    path.write_bytes((json.dumps(obj, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def archive(a: argparse.Namespace) -> dict:
    frozen = check_frozen()
    if not frozen["all_ok"]:
        raise SystemExit("冻结不符，拒绝归档（不重新冻结）：" + json.dumps(frozen, ensure_ascii=False))
    pack_id = a.pack
    reviewer = a.reviewer
    if pack_id not in FROZEN_PROMPT_SHA or reviewer not in ("luna", "muse"):
        raise SystemExit("pack/reviewer 非法")
    dirname = "%s_%s_r1" % (pack_id, reviewer)
    dest = OUT / "reviews" / dirname
    if dest.exists():
        existing = sorted(p.name for p in dest.iterdir())
        # 仅允许派发员预置的 response.txt；task/meta/report 任一存在即禁覆盖
        if any(n != "response.txt" for n in existing):
            raise SystemExit("目标非空，禁止覆盖：" + str(dest))
    dest.mkdir(parents=True, exist_ok=True)

    cases = load_and_validate()
    packs, _mapping = build_packs(cases)
    pack = next(p for p in packs if p["pack_id"] == pack_id)
    rendered = render_pack_prompt(pack).encode("utf-8")
    frozen_bytes = (OUT / ("review_prompts/%s.txt" % pack_id)).read_bytes()
    if sha_bytes(rendered) != FROZEN_PROMPT_SHA[pack_id] or rendered != frozen_bytes:
        raise SystemExit("render 字节与冻结 prompt 不一致，拒绝归档")
    (dest / "task.txt").write_bytes(frozen_bytes)

    resp_path = dest / "response.txt"
    if not resp_path.is_file():
        raise SystemExit("response.txt 缺失：须先按 completed summary 原文逐字写入")
    resp_bytes = resp_path.read_bytes()
    try:
        resp_text = resp_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise SystemExit("response.txt 非 UTF-8") from exc

    opt_key, _, opt_val = a.requested_option.partition("=")
    if not opt_key or not opt_val:
        raise SystemExit("requested-option 须是 key=value")
    requested_target = {"providerInstanceId": a.requested_provider,
                        "model": a.requested_model,
                        "options": {opt_key: opt_val}}

    parsed = None
    error = None
    try:
        strict_outer_load(resp_text)
        parsed, error = parse_review(resp_text, pack)
        if parsed is None:
            raise ValueError(error)
    except (ValueError, TypeError) as exc:
        parsed = None
        error = str(exc)
    schema_pass = parsed is not None

    meta = {
        "schema": "t3-public-delegation-archive/1",
        "client_request_id": a.client_request_id,
        "pack_id": pack_id,
        "reviewer": reviewer,
        "role": "review",
        "mode": "async",
        "submitted_at": a.submitted_at,
        "terminal_observed_at": a.terminal_at,
        "requested_target": requested_target,
        "observed_t3_provider": a.observed_provider,
        "observed_t3_model": a.observed_model,
        "observed_status": a.status,
        "task_sha256": sha_bytes(frozen_bytes),
        "response_sha256": sha_bytes(resp_bytes),
        "task_utf8_bytes": len(frozen_bytes),
        "response_utf8_bytes": len(resp_bytes),
        "task_source": "frozen prompt file bytes == render_pack_prompt bytes; dispatcher attests tool payload identical",
        "evidence_scope": "exact parent transcript tool payload and terminal result; T3 reported model is not independent remote backend attestation",
        "backend_session_handles": "not archived",
        "production_ready": False,
    }
    report = {
        "schema": "run140-return-parse/1",
        "date": "2026-10-09",
        "pack_id": pack_id,
        "reviewer": reviewer,
        "client_request_id": a.client_request_id,
        "schema_pass": schema_pass,
        "error": error,
        "response_sha256": sha_bytes(resp_bytes),
        "response_utf8_bytes": len(resp_bytes),
        "actual_task_sha256": sha_bytes(frozen_bytes),
        "actual_task_equals_frozen": sha_bytes(frozen_bytes) == FROZEN_PROMPT_SHA[pack_id],
        "requested_target": requested_target,
        "observed_t3_provider": a.observed_provider,
        "observed_t3_model": a.observed_model,
        "observed_status": a.status,
        "production_ready": False,
        "music_verdict": "not adjudicated by parser",
        "limits": "Legacy-input diagnosis; T3 reported identity not independent remote attestation; historical backend unknown.",
        "identity_limit": "legacy producer identity limited to mapping gen_canonical with actual backend unknown_in_legacy_record; no exact-producer or self-review claim",
        "quoted_items_exact": bool(schema_pass),
        "quoted_relation_exact": bool(schema_pass),
        "parsed": parsed,
    }
    if schema_pass:
        counts = {}
        for item in parsed["reviews"]:
            counts[item["verdict"]] = counts.get(item["verdict"], 0) + 1
        report["verdict_counts_raw_reviewer_only"] = {
            key: counts[key] for key in VERDICT_ORDER if key in counts}
    write_json(dest / "meta.json", meta)
    write_json(dest / "parse_report.json", report)
    return {"archived": dirname, "schema_pass": schema_pass, "error": error,
            "task_sha256": meta["task_sha256"], "response_sha256": meta["response_sha256"]}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check-frozen", action="store_true")
    ap.add_argument("--archive", action="store_true")
    ap.add_argument("--pack", default="")
    ap.add_argument("--reviewer", default="")
    ap.add_argument("--client-request-id", default="")
    ap.add_argument("--requested-provider", default="")
    ap.add_argument("--requested-model", default="")
    ap.add_argument("--requested-option", default="")
    ap.add_argument("--observed-provider", default="")
    ap.add_argument("--observed-model", default="")
    ap.add_argument("--status", default="")
    ap.add_argument("--submitted-at", default="")
    ap.add_argument("--terminal-at", default="")
    args = ap.parse_args()
    if args.check_frozen and not args.archive:
        frozen = check_frozen()
        print(json.dumps(frozen, ensure_ascii=False))
        raise SystemExit(0 if frozen["all_ok"] else 2)
    if args.archive and not args.check_frozen:
        summary = archive(args)
        print(json.dumps(summary, ensure_ascii=False))
        raise SystemExit(0 if summary["schema_pass"] else 5)
    raise SystemExit("须二选一：--check-frozen 或 --archive")


if __name__ == "__main__":
    main()
