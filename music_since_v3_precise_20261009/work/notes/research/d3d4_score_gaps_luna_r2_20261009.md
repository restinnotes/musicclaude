# D3/D4 首版谱图缺口补充与既有来源校核（Luna r2，2026-10-09）

## 范围与判读口径

本记录仅补充 Op.52 mm.191–203、Op.61 m.24 的可读首版谱证据，并校核既有 Op.60 m.24 / m.34 研究与指定文件的字节来源。原来的 d3d4_score_sources_luna_20261009.md/.json 保持只读。

- **页定位**：CFEO 页面或馆藏扫描标出的页码/小节范围；若未进一步数谱，只证明材料在该页段内。
- **谱面直读**：从所存高分辨率公有页面图上辨认的记谱事实。历史谱上没有连续印刷小节号；具体小节以 CFEO 的页段定位为起点，逐个数小节线。
- **评论**：Kopp、PTNA 等作者或网站的文字判断，与本次谱面直读分开。
- **字节核对**：只比较文件长度与 SHA-256；不把 PDF 内容用于音乐或心理推论。

所有音频状态均为 **audio-unverified**：没有打开或聆听音频；不作 Affect 或切点判断，也不涉及 H4/H5/Center。没有执行任何下载物中的脚本。Kopp 的 Henle Example 5 仅核对文章中的例号和小节范围，没有保存或复制现代商业谱例。

## 小节定位依据

- **Op.52**：CFEO 将首版 p.11 标为 bars 185–202、p.12 标为 bars 203–222。p.11 共 18 小节；按谱面小节线顺数，m.191 是前两个各 3 小节系统之后的下一系统起始处，p.11 余下目标段至 m.202。p.12 的首小节为 m.203。小节号是 CFEO 页段定位加顺数所得，未印在旧谱本身。
- **Op.61**：CFEO 将 p.2 标为 bars 20–43。数第一系统的四个小节后，第二系统第一小节是 m.24。谱面本身不印连续小节号。
- **Op.60**：CFEO 将 p.3 标为 bars 24–33、p.4 标为 bars 34–45；两页第一系统分别从 m.24 和 m.34 起。旧谱不印连续小节号。

## 谱面直读

### Chopin, Ballade No. 4, Op.52

1. **m.191–202（p.11；页段定位 + 直读）**：目标段跨越数个系统。可读到上声部在和弦攻击与较短的连线/分组音型之间交替；下声部持续出现快速分组音符、低音落点与分解式运动。页面还可见踏板记号、连线/延音线和渐强/渐弱型发夹。这里记录的是该 12 小节页段内的整体记谱变化，不把某个局部音型硬配到未复核的小节。
2. **m.191–202（p.11 后段；范围定位）**：目标页段后部清楚印有 *stretto*，随后出现 *fff*；可确认这是谱面印字和动态标记。此处不把二者解释成情绪或段落边界，且不声称已把每个标记精确分配到单一小节。
3. **m.203（p.12 第一系统首小节；直读）**：旧记录中“图空/不可读”的缺项已补上。首小节可读到 *pp*、较长时值的和弦性声部与踏板记号；上、下谱表都有持续/连结的和弦音响。没有转写具体音高或和弦名称。

### Chopin, Polonaise-Fantaisie, Op.61

4. **m.24（p.2 第二系统首小节；页段定位 + 直读）**：旧记录中“图空/不可读”的缺项已补上。上谱表起始有休止，随后进入连线下的较长音；下谱表可见较密集的分组音符运动，并有低音区音符与踏板记号。此处只记声部、节奏/织体与音区对照；未从一小节推出调性、和声功能或段落/情绪判断。

### Chopin, Barcarolle, Op.60（既有研究校核）

5. **m.24（p.3 第一系统起始；直读）**：高声部可见延长的颤音记号/持音和强音标记 *f*；下方声部有较活跃的分解式音型和踏板记号。可把“m.24 在谱面上有织体加厚材料”作为谱面候选事实。Kopp 对“主题 A / Rink 的 A′ 回归、双颤音、旋律缩减、织体扩张”的说法另列为评论，不冒充本条的独立逐音转写。
6. **m.34（p.4 第一系统起始；直读）**：原谱印字清楚为 **rallent.**。本次确认该词，不改写成 **rit.**。PTNA 关于从第二拍开始的说法属于二级演奏/练习评论；首版谱字本身在本次核读中只用于确认 rallent.，不凭字形单独推出拍内起点。
7. **m.20–24、m.24–35、m.35（评论，非本次独立和声分析）**：Kopp 论文第 16–17 段称 mm.20–22 有延长的 A♯ pedal，并把 m.24 的回归描述为由 A♯ 大三和弦直接回到 F♯；第 17 段称 theme A（Rink A′）在 m.24 回归，伴随双颤音、旋律缩减和织体扩张；另称内声 A♯4 在 m.35 变为 A-natural。这些均标为 **Kopp 的分析/文字判断**。本次只确认相关首版页面清楚可读，没有把 Kopp 整体叙述替代为新的逐音和声还原，也没有从 m.24 提出切点。Kopp Example 5 的标题范围核对为 mm.23–35；例图来自 Henle 1978 商业 Urtext，本次仅查定位，不保存、不复制。

## 来源与保存文件

下列图像从 CFEO 页面及其公开 IIP 图像服务取得。保存的是高分辨率页面 JPEG 原图服务输出，图中保留扫描页边、尺规/色卡；请求尺寸 4312×6496，图像服务实际输出高度上限为 5000 px。每组来源各自位于独立新目录。具体 SHA-256、字节数和像素尺寸见同目录 JSON 清单。

| 作品/页 | CFEO 页面定位 | 公开页面 / 原图服务 |
|---|---|---|
| Op.52 p.11，bars 185–202 | [CFEO pageview 74780](https://chopinonline.ac.uk/cfeo/browse/pageview/74780/) | [IIP 原图 6756.jp2](https://chopinonline.ac.uk/iipsrv/fcgi-bin/iipsrv.fcgi?FIF=jp2/newjp2/6756.jp2&WID=4312&HEI=6496&CVT=JPG) |
| Op.52 p.12，bars 203–222 | [CFEO pageview 74781](https://chopinonline.ac.uk/cfeo/browse/pageview/74781/) | [IIP 原图 6757.jp2](https://chopinonline.ac.uk/iipsrv/fcgi-bin/iipsrv.fcgi?FIF=jp2/newjp2/6757.jp2&WID=4312&HEI=6496&CVT=JPG) |
| Op.61 p.2，bars 20–43 | [CFEO pageview 61907](https://chopinonline.ac.uk/cfeo/browse/pageview/61907/) | [IIP 原图 61-1-BR_USCu p02](https://chopinonline.ac.uk/iipsrv/fcgi-bin/iipsrv.fcgi?FIF=jp2/ocvejp2-proc/61/35/02/61-1-BR_USCu_p02.jp2&WID=4312&HEI=6496&CVT=JPG) |
| Op.60 p.3，bars 24–33 | [CFEO pageview 66644](https://chopinonline.ac.uk/cfeo/browse/pageview/66644/) | [IIP 原图 p03](https://chopinonline.ac.uk/iipsrv/fcgi-bin/iipsrv.fcgi?FIF=jp2/cfeojp2-proc/60-1-BR/60-1-BR_GBLbl_p03.jp2&WID=4312&HEI=6496&CVT=JPG) |
| Op.60 p.4，bars 34–45 | [CFEO pageview 66645](https://chopinonline.ac.uk/cfeo/browse/pageview/66645/) | [IIP 原图 p04](https://chopinonline.ac.uk/iipsrv/fcgi-bin/iipsrv.fcgi?FIF=jp2/cfeojp2-proc/60-1-BR/60-1-BR_GBLbl_p04.jp2&WID=4312&HEI=6496&CVT=JPG) |

历史首版的公共领域状态由 [IMSLP Op.52](https://imslp.org/wiki/Ballade_No.4,_Op.52_(Chopin,_Frederic))、[IMSLP Op.60](https://imslp.org/wiki/Barcarolle_Op.60_(Chopin,_Frederic))、[IMSLP Op.61](https://imslp.org/wiki/Polonaise-Fantasie,_Op.61_(Chopin,_Frederic)) 的首版/版权元数据交叉核对。Op.61 另有 [Wikimedia Commons 首版扫描条目](https://commons.wikimedia.org/wiki/File:Polonaise-fantaisie,_Op.61_(IA_imslp-op61-chopin-frdric).pdf)。CFEO 自身的馆藏/数字化介绍见 [CFEO About](https://chopinonline.ac.uk/cfeo/about/)。以上核对支持旧谱内容为公有领域资料；**没有独立确认 CFEO 数字化图像是否另有整体再利用许可**，故此处记录来源和核验信息，不据此作额外许可承诺。

- Op.52 首版印版标记可见 M.S.3957；CFEO impression 为 52-1-Sm。
- Op.61 p.2 馆藏来源为 University of Chicago Library，首版页脚印有 B. et Cie. 4610。
- Op.60 p.3–4 馆藏来源为 British Library，首版页脚印有 B. et Cie. 4609。
- Kopp 论文：[On Performing Chopin’s Barcarolle](https://www.mtosmt.org/issues/mto.14.20.4/mto.14.20.4.kopp.html)，重点核对 paras. 16–17；Example 5 PDF 仅查标题/范围：[kopp_examples.pdf](https://www.mtosmt.org/issues/mto.14.20.4/kopp_examples.pdf)。
- PTNA 二级评论：[Chopin Barcarolle Op.60](https://enc.piano.or.jp/en/musics/543)。仅保留其为评论来源的身份，不把拍内说法并入首版谱直读。

## 字节/来源核对（旧文件只读）

- 既有 JSON notes/research/d3d4_score_sources_luna_20261009.json：11,227 bytes，SHA-256 593EC4BA96DD3B239021EA22F1B35956F5AD92FC03501CAAB7C08AA65E0B3480。
- 既有 UConn 作者 PDF research_assets/d3d4_20261009_luna/uconn_author_pdf/Memory-and-Expression-11-18-24.pdf：2,200,228 bytes，SHA-256 D2364894B6BA53909795419D8E0DBC2DB0CD83599A5C179748B8D60830CDD1FB。
- UConn 来源 URL：[musiclab.media.uconn.edu PDF](https://musiclab.media.uconn.edu/wp-content/uploads/sites/290/2024/11/Memory-and-Expression-11-18-24.pdf)。HTTP 头核对为 200 / application/pdf / 2,200,228 bytes；远端响应流在内存中计算的 SHA-256 与既有本地 PDF 一致。未另存副本、未提取 PDF 文字、未据其推出任何音乐心理结论。
- 旧 Markdown 和旧 JSON 没有被修改；r1 目录没有覆盖。

## 仍然受限之处

- 谱面只提供上述可辨事实；未完整逐音转写，也未作新和声还原。
- Op.52 m.191–202 的整体织体描述使用已标定的连续小节范围；该段每一个细节未独立映射到唯一小节。
- Op.61 m.24 不作精确音高、和弦名称或调性功能断言。
- 无音频，因此音响/演奏层命题全部为 **audio-unverified**。
- 此研究不是音乐流水线服务健康判定，不代表三作品 StepB/C 或原验收，也不清 hold、不选 production 切点。

