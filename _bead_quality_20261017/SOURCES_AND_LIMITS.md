# 来源、条件与产物归属

## 正式来源集

本轮保留30份既有A：Gemini 3.8 Flash、Muse、Luna、GPT-5.6w、GPT-6w各6份。原文件复制到sources，来源路径、原hash、实际hash与分组见 [SOURCE_MANIFEST.json](sources/SOURCE_MANIFEST.json)。其中名义int/web各3份仅是台账分组，不表示全部满足严格同条件。

旧名单里两个名为gpt56w的条目实为 `gpt-5.6-sol#xhigh (web,mimicgate)`，已排除，未改名冒充。替补 `SRC-gpt56w-int-r1` 与 `SRC-gpt56w-web-r1` 来自10月11日已完成的safechain存档；请求及服务端标签均为 `gpt-5-6-thinking`、max，对应int/web提示一致。不是本轮新采样。

Luna-int-3的旧“tool-free/noweb”描述不实：实际CLI请求 `gpt-6-luna`，观察到7条web_search事件。它作为用户允许的材料保留，但不能当第三次严格离线重复。生产上下文已更正显示说明；冻结试验中的旧标签没有暗中回写。历史int与GPT-w int提示也有文本差异。完整证据见 [来源审计](audits/SOURCE_POOL_AUDIT.md)。

GPro、Grok、Opus、其他Sol及T/H没有进入新生产来源。旧包作为对照存档，其中仍可能含旧来源；存档不等于本轮采用。历史V2A只用来比较表达质量，没有灌入新Pool。

## 三个输入版本

| 版本 | 用途 | 边界 |
|---|---|---|
| pilot28 | S02两轮及旧／A／B／C受控比较 | 发现并排除两份Sol后，尚未补入历史真5.6w时冻结；保留实际字节与hash |
| 正式30实验版 | S07、S13的GPT-6／Flash同输入，以及S13旧方法对照 | 同一对照的请求prompt hash相同；不存在静默缩输入 |
| production_context | 十四段编辑成稿的最终上下文 | 在正式30基础上补回原文继承标题、改正Luna条件说明；不改变正文、分段或路由 |

production_context是后续保真修复，不是假装早先模型已经看到这些新增标题。其23次标题恢复及前后hash见 [CONTEXT_REPAIR.json](production_context/CONTEXT_REPAIR.json)。跨28／30或实验／生产版本的输出，不当作纯模型或纯方法因果比较。

## 模型调用证据

GPT-6通道为safechain的 `gpt-6-thinking`，max，独立临时会话；输入文件实际以内联完整文本发出，本轮未使用附件。保留输入hash、请求参数、服务端model_slug及完成信号。没有因输出慢而降配置或裁短Pool。

Flash请求路由是 `antigravity-tools/gemini-3.8-flash-high`，通过OpenCode现有配置调用，工具禁用。完成证据是返回的关闭文本与CLI正常退出；该通道未提供与GPT同等强度的服务端模型身份核验，不能声称独立认证底层权重。旧A里某些模型也只有配置／路由层证据，详情保留在审计中。

实际执行清单在 [ACTUAL_CALLS.md](experiments/ACTUAL_CALLS.md)。jobs文件包含曾规划但未执行的条目，不能用jobs条目数充当实测次数。模型原始响应不作人工改写。

## 成稿与检查的责任边界

十四颗最终正文是本轮主编辑依据正式原A和生产上下文直接选材、整合、精编的稿件，包含从实际试写获得的取舍判断；不是十四次外部GPT-6调用的原样合集。主编辑未为填段新增A研究。最终JSON与来源账本明确标记 `external_model_verbatim: false`。

独立来源复核逐条核对了55次采用引用、49个不同UID，并回读18份原件；这些数目只是检查范围，不是质量指标。它发现的S14无据反应已删。有限事实复核发现的S13“猛地／没有真正松开”演法确定化已改，并限定S09低音停留为段初。复核报告保留原候选hash，最终解决记录另存，未篡改审查记录。

外部模型自写的“采材证据”表仍是待核声明，并非因为表格齐全就自动认证；例如空格、换行和表格显示处理可能不满足严格连续原文。最终内容对照里的41条原A短引句另作实际匹配，忽略Markdown强调符号后均可连续找到。这个最终核对不能被扩大成所有模型响应内每一条自引都已逐一认证。

本轮没有指定或亲听演奏录音，没有重新研究结构。事实边界使用已存乐谱及Kopp文献；本地谱是Eric Tran现代校订版，不能冒称Henle或所有版本完全一致。文学情景是听觉比喻，不是作曲家意图或传记事实。
