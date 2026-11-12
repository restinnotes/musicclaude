# Music Claude 项目资料

音乐体验分析、Bead（珠子）与 Thread（线）生成、提示词迭代、独立评审及视频呈现的工作资料。此仓库是 `D:\musicclaude` 当前项目中适合存入 Git 的文件快照。

## 内容导航

| 目录 | 内容 |
| --- | --- |
| `bead_chain/` | 原稿体验池 → 结构化珠子 → 独立审稿 → 交付的可复用链路 |
| `_bead_*/` | 珠子生成、消融、覆盖、质量审计、饱和度及 Op.61 实验 |
| `_thread_20261018/` | 早期 Thread 实验及交付 |
| `_thread_evo_20261019/` | 主线提示词演化、作品输入、生成结果、盲评和验收记录；从 `README_FIRST.md`、`STATUS.md`、`THREAD_SPEC.md`、`DAG.md` 开始 |
| `_thread_evo_claude_20261019/` | 另一组 Thread 研究和交付资料 |
| `_video_public_20261104/` | 大众版呈现标准、主线版本、视频合成与对齐脚本、审查记录 |
| `_dag2_video_20261104/` | DAG2 视频流程、状态、实验和制作代码 |
| `_video_design_20261103/`、`bead_video/` | 视频方案与渲染源码（含 Remotion 工程） |
| `_review_*/` | 阶段审阅与修订材料 |
| `_baseline_*/`、`_harness_source_20261029/` | 基线对照、恢复与调用实验 |
| `music_since_v3_precise_20261009/`、`unified_run_handoff_20260924/` | 历史阶段归档和交接资料 |
| `project_dialogues/`、`ai_log/` | 项目讨论与日志资料 |
| `mimic-cli/`、`gpt2agent-safechain-codex/`、`webchat-nodegrade/` | 当前目录内未作为独立 Git 仓库排除的调用工具源码和实验资料 |

## 上传范围

- 保留适中的源码、文档、提示词、JSON 数据、实验结果、图片、参考 PDF 及字幕等文件。
- 单文件上限为 **10 MiB**；超过上限的具体路径已写入 `.gitignore`。
- 排除渲染视频和音频、压缩包及其编码副本、安装包、依赖、虚拟环境、缓存、浏览器配置、登录状态和临时文件。
- 检出疑似凭据的文件整体排除，原始文件保留在本地。自动扫描不能保证识别所有形式的敏感信息。
- 不包含目录内的独立仓库：`gpt2agent-safechain/`、`gpt2agent-upstream/`、`gpt2agent-upstream-control-20261008/`、`music_work_since_1008v3_20261009/`。

本仓库保留研究与制作记录，不是一个统一安装即可完整复现的应用；一些脚本依赖本地工具、原始媒体或其他未上传资源。各子目录的说明和状态文件是具体流程的入口。

完整清点统计及排除路径见 `PROJECT_INVENTORY.json`。统计基于首次上传时可枚举的候选文件，未计入已跳过的依赖、浏览器数据等目录，不代表磁盘全部占用。
