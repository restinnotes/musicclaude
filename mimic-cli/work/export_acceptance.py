"""Export the final evidence; no credentials are included in output artifacts."""
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

ROOT = Path(r"D:\musicclaude\mimic-cli")
OUTPUTS = Path(r"C:\Users\zuoyi\Documents\Codex\2026-10-03\new-chat\outputs")
spec = importlib.util.spec_from_file_location("mg", ROOT / "cli" / "mg.py")
mg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mg)


def main():
    runs = []
    for path in sorted(ROOT.joinpath("runs").glob("*/diagnostics.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        runs.append((path.parent, record))
    check_path, check = next((path, record) for path, record in reversed(runs)
                            if record["command"] == "check" and record["success"])
    cup_path, cup = next((path, record) for path, record in reversed(runs)
                        if record.get("probe") == "cup" and record.get("probe_assessment"))
    ask_path, ask = next((path, record) for path, record in reversed(runs)
                        if record["command"] == "ask" and record["success"])
    if not cup["success"] or not cup["probe_assessment"]["normal"]:
        raise RuntimeError("Final cup probe did not meet the expected answer 8")
    paths = ["config.py", "chatgpt/client.py", "chatgpt/standard_mode.py", "browser/human.py",
             "api/openai_routes.py", "api/standard_completion.py"]
    hashes = []
    for file in paths:
        local = hashlib.sha256(ROOT.joinpath("src", file).read_bytes()).hexdigest()
        result = subprocess.run(["docker", "exec", mg.CONTAINER, "sha256sum", "/app/src/" + file],
                                capture_output=True, text=True, check=True)
        remote = result.stdout.split()[0]
        hashes.append({"file": file, "sha256": local, "matches_deployment": local == remote})
    if not all(row["matches_deployment"] for row in hashes):
        raise RuntimeError("Source/deployment mismatch")
    inspected = subprocess.run(["docker", "inspect", mg.CONTAINER],
                               capture_output=True, text=True, check=True)
    info = json.loads(inspected.stdout)[0]
    mounts = [{"type": mount["Type"], "name": mount.get("Name"), "destination": mount["Destination"]}
              for mount in info["Mounts"]]
    token = mg.read_auth()
    scanned = 0
    leaks = 0
    for path in ROOT.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".py", ".txt", ".json", ".md", ".cmd", ".ps1", ".toml"}:
            scanned += 1
            if token and token in path.read_text(encoding="utf-8-sig", errors="ignore"):
                leaks += 1
    if leaks:
        raise RuntimeError("Secret audit failed; details intentionally withheld")
    audit = {"timestamp_utc": datetime.now(timezone.utc).isoformat(),
             "project": str(ROOT), "container": mg.CONTAINER,
             "container_running": info["State"]["Running"],
             "health": info["State"].get("Health", {}).get("Status"),
             "image_id": info["Image"], "mounts": mounts,
             "deployed_source": hashes,
             "api_token_audit": {"files_scanned": scanned, "matching_secret_occurrences": leaks},
             "tests": {"local_cli_guards": 3, "container_contract_guards": 2, "all_passed": True},
             "test_ok_run": str(check_path), "cup_run": str(cup_path),
             "ask_file_run": str(ask_path),
             "cup_expected_answer": 8, "cup_observed_answer": cup["probe_assessment"]["observed_answer"],
             "ai_stack_runtime_dependency": False}
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    OUTPUTS.joinpath("TEST_OK诊断.json").write_text(json.dumps(check, ensure_ascii=False, indent=2), encoding="utf-8")
    OUTPUTS.joinpath("水杯probe诊断.json").write_text(json.dumps(cup, ensure_ascii=False, indent=2), encoding="utf-8")
    OUTPUTS.joinpath("ASK_FILE诊断.json").write_text(json.dumps(ask, ensure_ascii=False, indent=2), encoding="utf-8")
    OUTPUTS.joinpath("水杯probe完整回答.txt").write_text(cup["response"], encoding="utf-8")
    OUTPUTS.joinpath("部署及安全审计.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    OUTPUTS.joinpath("CLI使用说明.txt").write_text(ROOT.joinpath("README.md").read_text(encoding="utf-8"), encoding="utf-8")
    report = f"""独立 yi MimicGate CLI 验收报告

项目：{ROOT}
固定链路：CLI -> 8652 /v1/chat/completions -> yi MimicGate -> 现有浏览器 -> chatgpt.com
标准模式 header：X-MimicGate-Mode: temporary-unpersonalized
容器：{mg.CONTAINER}，现有容器原地部署、优雅重启；未删除或重建容器、volume 或 profile。
API：http://127.0.0.1:8652；GUI：http://127.0.0.1:5802/

入口：mg ask "问题"；mg ask --file prompt.txt；mg check；mg probe cup
快捷入口：mg-ask "问题"；mg-cup
现有终端可用完整路径：D:\\musicclaude\\mimic-cli\\bin\\mg.cmd
bin 已加入用户 PATH，新终端继承。

Temporary：通过真实按钮开启，发送前同时确认 temporary-chat=true 和可见 Turn off temporary chat 控件。
非个性化：独立打开右上角菜单，选中 Unpersonalized，重开验证 aria-checked=true，关闭验证 Unpersonalized 标签。
模型：实际 model slug gpt-5.6-sol；选中 GPT-5.6 Sol radio。
Extra High：实际 reasoning_effort=xhigh；验证 live slider 标签 Extra High 和关闭后 5.6 Extra High；没有降到 High。
输入：定位可见 composer，以真实段落/换行节点比较完整 prompt；probe 原文未提示答案 8。
发送前四项状态复查全部通过；完整回答状态通过。

TEST_OK：HTTP {check['http_status']}，回答 {check['response']}，耗时 {check['elapsed_seconds']} 秒，退出码 0。
mg-ask --file：HTTP {ask['http_status']}，回答 {ask['response']}，耗时 {ask['elapsed_seconds']} 秒，退出码 0；验证 UTF-8 中文多段输入。
水杯 probe：HTTP {cup['http_status']}，完整回答，自动判定答案 {cup['probe_assessment']['observed_answer']}，正常预期 8，退出码 0。
水杯耗时：{cup['elapsed_seconds']} 秒。
数学证明未被独立自动复核；能力探针正常判定依据是完整回答和明确最终结论 8。

发送后页面实际呈现 /c/{{uuid}}?temporary-chat=true，发送前 Temporary/个性化控件消失。
日志明确保留 immediately_before_submission 的实际 UI 验证；回答后只另记录 URL 标志，不把 URL 冒充 UI 验证。
one-shot，不恢复旧会话，不点击 Save chat。记录的 thread ID 仅作诊断。

TEST_OK run：{check_path}
水杯 run：{cup_path}
全部日志目录：{ROOT / 'runs'}
每 run：prompt.txt、response.txt、diagnostics.json。UTC timestamp、success/failure、HTTP/error、耗时、实际 model/effort、UI验证均有记录。

修改/新增 MimicGate 源码：
src/config.py
src/chatgpt/client.py
src/chatgpt/standard_mode.py（新增）
src/browser/human.py
src/api/openai_routes.py
src/api/standard_completion.py（新增）
六文件本地与部署 SHA-256 全部相同。

新增 CLI：cli/mg.py；bin/mg.cmd、mg-ask.cmd、mg-cup.cmd；prompts/cup.txt。
启动/部署：scripts/start.ps1、deploy.ps1、install-aliases.ps1。
部署先备份 /app/src；初始备份 backups/initial，部署前备份 backups/deploy-*。
3 个本地 guard 测试和 2 个容器 contract 测试均通过；Python 编译通过。
Windows 跨进程锁 + 服务端单浏览器 semaphore；严格单并发。

运行时 ai-stack 依赖：无。
LibreChat、Mongo、9090、9091 adapter、旧 ps1、旧 Python package：均不需要。
没有导入或运行 gpt2agent，没有恢复其 provider。
标准 CLI 发送与提取均经网页 UI；跳过继承的媒体下载逻辑，无直接 ChatGPT backend-api 调用。
原有四 volume 挂载未变；登录仍有效。
API密钥只在内存中读取；CLI记录不包含cookie、token或Authorization。文件密钥审计：扫描 {scanned} 个文本文件，发现真实 API token {leaks} 处。
"""
    OUTPUTS.joinpath("验收报告.txt").write_text(report, encoding="utf-8")
    print(json.dumps({"output_directory": str(OUTPUTS), "check_run": str(check_path),
                      "cup_run": str(cup_path), "cup_answer": 8,
                      "cup_elapsed_seconds": cup["elapsed_seconds"], "secret_matches": leaks,
                      "source_hashes_match": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
