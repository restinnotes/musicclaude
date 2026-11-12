# Web 思考档位修复

这是 `D:\musicclaude\gpt2agent-safechain` 当前工作区的独立副本，使用自己的 `.venv`。
音乐项目的原脚本和原仓库文件保持原样。登录凭据只读；运行时写入当前用户的
`~/.gpt2agent/codex-safechain-lab/accounts`。首次建立时复制已有账号的身份、cookie
和冷却状态，保留已有 device/session ID，不重新生成身份。测试与生产不要同时运行。

## 已确认的问题

原实现直接把 `max` 发送为 Web 的 `thinking_effort`，未校验账号能力。
HTTP 成功、模型 slug 正确，并不证明该档位被接受。
2026-09-26 当前账号的 `/backend-api/models?history_and_training_disabled=true`
返回 `gpt-5-6-thinking` 的可选档位为 `standard`、`extended`，见 `audit/models.json`。
这不代表其他账号或模型不能提供 `max`。

修复在显式指定档位时读取并缓存当前账号、当前聊天模式的模型能力；档位或模型
不在返回列表中时，在 Sentinel 和 conversation POST 之前报错，避免悄悄使用默认档位。
不做通用的 `max → extended` 映射。新音乐入口明确使用 `extended`。
结果中新增 `provider_meta.sent_thinking_effort`，记录发送值，而不是声称服务端已确认档位。

safechain 的提交边界、错误分类、提交不明时禁止重发、artifact 处理保持原逻辑。
校验以账号接口返回值为准；如果其他账号明确返回 `max`，会允许该值。

## 接入音乐队列

原 `tools/chatgpt_run.py` 已只读复制为本目录 `tools/cup_probe.py`；原题和判定门槛保持原样。
下面入口会将默认档位设为 `extended`，任务仍可显式指定账号支持的 `thinking_effort`。

```powershell
Set-Location D:\musicclaude\gpt2agent-safechain-codex
.\.venv\Scripts\python.exe -B .\tools\run_cup_probe.py
.\.venv\Scripts\python.exe -B .\tools\run_music_codex.py --jobs .\jobs.json --run-dir .\runs\music_extended
```

`jobs.json` 格式与原音乐队列相同。默认先测水杯题，通过后串行执行任务。
保护响应、探针失败或提交结果不明时，沿用原来的停止与防重复提交规则。

## 检查

离线回归覆盖账号支持 `extended`、另一账号支持 `max`、无效模型/档位在提交前失败、
档位写入请求与结果元数据，以及原会话、artifact、防重复提交检查。
真实水杯题结果保存在本目录 `runs/cup_extended_*`，未修改音乐项目的结果或索引。
