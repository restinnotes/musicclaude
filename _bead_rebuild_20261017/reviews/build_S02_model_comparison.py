import json, re, hashlib
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
RAW = 'scripts/call_results/S02_G6_relations_r1_attachment/response.txt'
GP = 'drafts/S02_G6_relations_r1.json'
FP = 'drafts/S02_FLASH_relations_r1.json'
def read(p):
    return (ROOT / p).read_text(encoding='utf-8-sig')
def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
before = {p: sha(p) for p in [RAW, FP, 'inputs/S02.txt', 'reference/S02_ledger.json']}
raw = read(RAW).strip()
assert raw.startswith('<escape>') and raw.endswith('</escape>')
g = json.loads(raw[len('<escape>'):-len('</escape>')].strip())
(ROOT / GP).write_text(json.dumps(g, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
f = json.loads(read(FP))
ledger = json.loads(read('reference/S02_ledger.json'))
inp = read('inputs/S02.txt')
pool_start = inp.index('【完整原A】')
pool_end = inp.index('【原意逐项账本')
headers = list(re.finditer(r'^\[(SRC-[^\]]+)\]', inp[pool_start:pool_end], re.M))
units = {}
for i, m in enumerate(headers):
    start = pool_start+m.start()
    end = pool_start+headers[i+1].start() if i+1 < len(headers) else pool_end
    units[m.group(1)] = (start, end, inp[start:end])

def span(path, pointer, text, start, end):
    assert 0 <= start < end <= len(text)
    return {'file': path, 'json_pointer': pointer, 'start': start, 'end': end, 'quote': text[start:end]}

def output_spans(model, bnum, keys):
    if bnum == 0:
        return []
    doc, path = (g, GP) if model == 'gpt' else (f, FP)
    text = doc['pages'][0]['blocks'][bnum-1]['text']
    ranges = []
    # Select actual sentence/clause spans using manually chosen content anchors.
    # No meaning_ids or model evidence participates in this match.
    for key in keys.split('~'):
        pos = text.find(key)
        assert pos >= 0, (model, bnum, key)
        left = max([text.rfind(c, 0, pos) for c in '。；\n'])+1
        ends = [text.find(c, pos+len(key)) for c in '。；\n']
        right = min([x for x in ends if x >= 0], default=len(text)-1)+1
        ranges.append((left, right))
    merged = []
    for left, right in sorted(set(ranges)):
        if merged and left <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(right, merged[-1][1]))
        else:
            merged.append((left, right))
    return [span(path, f'/pages/0/blocks/{bnum-1}/text', text, a, b) for a,b in merged]

def source_spans(item):
    result=[]
    for ev in item['evidence']:
        start,end,unit=units[ev['uid']]
        pos=unit.find(ev['quote'])
        if pos >= 0:
            s=span('inputs/S02.txt', None, inp, start+pos, start+pos+len(ev['quote']))
            s['selection']='ledger_quote_verified_in_original_pool'
        else:
            s=span('inputs/S02.txt', None, inp, start,end)
            s['selection']='complete_original_unit; ledger quote not a literal contiguous match'
        s['uid']=ev['uid']
        result.append(s)
    return result

# Independent manual reading map: ID | GPT block | content anchors | Flash block | content anchors | retained distinctions.
DATA = '''
1|1|偷来的安宁|1|偷来的安宁|疲惫、卸下戒备及安宁像偷来，三个限定均在正文。
2|1|没有尽头的水浪|1|像心跳|12/8、心跳和无尽水浪均有直接表达。
3|3|三度、六度|2|三度和六度|主旋律由三度六度并行双音构成，未只写泛称歌声。
4|4|肩贴肩|3|两个人肩并肩~声音放得极低~肢体触碰|近身双人、身体相贴与低声耳语均可从正文还原。
5|4|怕稍大的喧哗|3|任何大声喧哗|低声保护易碎幻觉的动因明确，没有只用彼此听见代替。
6|11|鼻酸~水在流|5|水在流|水与时间不可逆、清醒知幸福留不住及鼻酸的关系有表达。
7|8|午后暖金色|3|下午斜照|午后暖金斜光、并肩和摇晃船舱位置均在。
8|4|心照不宣|3|两对声线依偎~话说得不多却彼此都懂|双声相依与双方默契亲密均在，未用单方爱慕代替。
9|11|经历过离别|5|经历过离别|离别前史、成年人防卫及期限预问全部写出。
10|1|主动放弃|1|放弃对重力|全身主动交托、温热及深不可测水体均在。
11|1|陆地上的病痛|1|陆地上的病痛|陆地病痛琐碎沉重被隔绝，保留负担解除的具体内容。
12|4|语调也同频|3|语调完全同频|同频和容不下第三人均在，不只写呼吸同步。
13|8|黄昏的倦意|4|黄昏时的倦意|黄昏倦意、微醺及与初恋欢跃的区别都在。
14|8|潮湿温热|4|潮湿、温热|夏末傍晚、湿热微风裹皮肤及黏稠触感保留。
15|8|成熟到近乎颓废|4|成熟到近乎颓废|近颓废的成熟温存、呼吸与体温化不开的程度保留。
16|11|没有根基|5|没有根基|幸福浮水无根与持续每秒倒数均写出。
17|4|肩贴肩~呼吸同步|3|呼吸和肢体触碰同步|双声的同步呼吸与身体接触均可还原；GPT的接触落实为肩贴肩。
18|4|连外人都不该旁观|3|这场景甚至不是给外人看的|相会本身不供旁观、只属于两人，保留观看位置而非只说音量。
19|0||0||原A确写第4小节双音主题，正文均改用4—5伴奏、6主题；不把更正当原义已覆盖。
20|1|催眠般的安全感|1|催眠般的安全感|托举、催眠安全和抚平先前惊悸均在。
21|13|近乡情怯|2|近乡情怯|相爱的人相见后近乡情怯、还不能自信倾诉，均直接保留。
22|13|向高处伸展|2|音往上走|上行时渐弱的反常方向明确，未变成只写普遍克制。
23|14|同一个升A~温柔的刺|6|升A音~温柔的刺|相同升A尾音、伴奏变色、确认与惆怅并存及温柔的刺均在。
24|14|一碰就散|6|一碰就会散|水面浮光一碰即散的具体脆弱意象保留。
25|6|已相识很久|4|已经相识很久|久识、靠近、无需找话题、私人柔软舒适而非狂喜均在。
26|7|成年后重见|5|重见重要的人|成年重逢、自然笑谈、不再以为时刻无穷均在。
27|2|安静地拥有|4|安静拥有|能够安静拥有这种感觉的安顿保留。
28|11|并没有发生坏事|5|并不是发生了坏事|幸福自身引发忧伤及结束担忧，区别于坏事后悲伤。
29|12|手掌托着|4|手掌托着|手掌托着珍贵易碎之物的身体动作保留。
30|2|外层很稳|1|外层稳定|外层稳从容有礼、内层复杂期待重量均在。
31|2|夜里走熟悉的路|1|夜里走在极熟悉|夜走熟路、规律脚步与不平静念头的反差保留。
32|7|共同生活多年|4|共同生活过一段时间|共同生活后的普通晚间重新珍惜在场、知道非理所当然均在；GPT年限有增写，见反向复核。
33|12|手正抚过~还不是悲伤|4|伸手抚摸|抚脸时突闪不永存、靠近又警觉的层次可核，是否尚非悲伤另作严格判断。
34|5|内心互相依偎|3|内心两种声音|同一人内在双声作为另种读法保留，没有必定变成两位恋人。
35|20|第12—16小节|7|呼吸逐渐收紧|12—16呼吸变短、情绪赶在理智前的内容保留；合并关系另查。
36|0||8|必要前提|原稿解释当前自我压抑使后面高潮成立，是对当下的前瞻解释，不等于把高潮写成现在已发生。
37|4|身边有人|3|声音不需要投射给远方|因为旁边有人，只需彼此听见而不必远投，动因和声音方向保留。
38|7|全部重量|4|全部重量|靠近却不压上全部重量、不粗暴占有的分寸保留。
39|5|独自沉浸|3|独自沉浸在珍贵|独自而非必有相会人物的珍贵沉浸读法存在。
40|7|夜晚散步|4|夜晚散步|散步时多望一眼以确认亲近真实，与被望即满足的A047分开保留。
41|16|还没到痛苦|5|幸福开始催生依恋|幸福初生依恋、盼更久及尚非痛苦是本项三个限制。
42|1|绷紧的身体|1|绷着的身体|音乐开始流动后绷紧身体才逐渐松开，前后顺序保留。
43|16|什么都不想做|5|甚至不想做什么|此人此下午的重要、不需做事、只盼时间慢均在。
44|16|还没有失去|5|还没有失去|尚未失去，因为太喜欢已提前舍不得，时态及动因保留。
45|12|不愿把自己完全暴露|2|不愿把自己完全暴露|感情深与不全暴露自己的自我保护保留。
46|6|平时惯于克制|3|平时习惯克制自己|惯常克制与终于不用时时警惕的反差保留。
47|6|偶尔望过来|4|对方偶尔望你|对方主动望来便满足，未用我多望对方确认代替。
48|6|主动愿意信任|4|主动靠近|信任和靠近的主动意愿保留，不只是被动舒适。
49|16|快要安顿下来|5|快要安顿下来|将落定又舍不得停，渴望因太值得留恋而非缺少均在。
50|12|美好刚出现|2|美好刚出现|美好初现却不敢用力拥抱，身体动作保留。
51|12|热情太明显|2|热情太明显|害怕自己热情显露吓跑美好这一特殊动因保留。
52|18|第6—11小节~第12—14小节~重新柔和|7|第6至11小节~第12至14小节~回到柔和|收回→上涌→呼气回柔和的时间顺序存在；Flash加串别种读法另记。
53|3|第4—5小节|1|真正的歌唱尚未浮现~第4至5小节|伴奏先于第6小节歌唱的次序可由相邻块核实。
54|12|仔细挑说话的语气|2|小心地选择说话语气|选语气怕重动作破坏珍贵氛围、并非感情浅均在。
55|11|尚未完全放心|5|始终没有完全放下心|幸福和未完全放心同时存在，未变为先幸福后不安。
56|4|各留一点空间|3|各自保留了一点空间|双声回应又留空间、亲密不急证明均写出。
57|13|第8—11小节|6|第8至11小节|本可停却继续说以充分表达同一感受，动因和范围保留。
58|20|第16小节附近|7|第16小节左右|16附近忽明忽暗并开始担心美好改变的层次保留。
59|2|舒服地悬在半空|1|人不害怕|舒服、悬空、不急抵达、享景不怕但未到岸须同时核；Flash缺悬空和不急抵达。
60|11|远非绝望或失恋|5|绝望或失恋般|知道好时光不长的悲伤限定及非绝望失恋，结合收住倾诉可还原。
61|6|夜里一点点聊近|3|在夜聊中慢慢靠近|夜聊渐近、暖意、含蓄诱惑、话少却懂均在。
62|18|感情终于忍不住|7|情绪明显往上涌|只保留上涌，未完整表达愉悦增浓使情绪不必藏好且不代表问题解决。
63|8|感官上如此陶醉|4|在感官陶醉中|感官陶醉和不敢相信亲近持久同时保留。
64|20|第12—16小节~接下来会怎样|7|呼吸逐渐收紧~接下来会怎样|12—16呼吸收紧及对接下来变化的期待均在。
65|19|第14—15小节|7|第14至15小节~短暂地落稳~声音很快又漂浮|短暂落稳、相视获回应、又漂起且未说定心事均在。
66|19|第11—15小节|7|第11至15小节~到第14至16小节|原稿11—15呼吸拉长、抬高后吐气而非全释然；Flash把拉长改为线条，并把吐气重定至14—16。
67|9|光很好|5|看黄昏时|看黄昏同时享受和难过将逝、身旁喜欢之人及心中时刻不多均在。
68|9|靠在船舷|4|靠在船舷|船舷、望远、目光不敢用力怕看碎的独特细节保留。
69|17|不想回去|5|并不想回去|已逝好过去、回不去且不想回去、有过即已没了均在。
70|17|轻轻摸头安慰|5|轻轻摸头安慰|暖长旋律抚慰与不停水上摇荡提醒托不住的上下层关系保留。
71|17|有分寸的怀念|5|不哭，但眼眶是热的|成年怀念、不哭、眼眶热的具体状态须保留；Flash将之移接到哄爱人的现在场景。
72|3|第一条完整的长旋律|2|第一支完整的长旋律|第一次完整长旋律及升F大调均明确。
73|17|中年人笑着哄|5|中年人哄着最爱|中年人主动笑着哄爱人，知留不住仍眼热唱完的动作保留。
74|15|我们在这里|6|我们在这里|在此确认→还在吗→待不久的三次次序均完整；与其他三次读法的关系另查。
75|5|一个人分饰两角|3|一个人分饰两角|一人扮双角、怕吵醒水面及甜中孤独均在。
76|13|抵抗一升高|8|必须抵抗|抵抗直接做大、先克制为后文留余地均在；Flash作者意图断言另查。
77|3|女高音|3|意大利歌剧里的二重唱|原意的独特主体是女高音；Flash保留歌剧风格却将主体换成二重唱。
78|14|安慰与叹气的反复交替|6|一会儿是安慰，一会儿是叹气|同尾音和声变化的安慰/叹气交替内容均在，不能由此推成必然单向加痛。
79|10|夏夜深绿近黑|3|夏夜深绿近黑|夏夜深绿近黑、浑凉以及又怕又爽三个感官层次均需保留。
80|10|独自而清醒的想念|3|夜里一个人极清醒|独处清醒想念与暖凉同时均在；GPT措辞暖和凉虽稍拗口，不判漏义。
81|10|死亡曾突然威胁|3|受到死亡威胁|恋人二重唱的死亡威胁意象保留；署名与权威有效性另查。
82|15|第一次是安慰|6|第一次是安慰|安慰→犹豫→疼完整保留；GPT本块说同样三次、7/9/11定位在相邻B14。
83|18|第14—15小节~梯田|7|第14至15小节~梯田|小峰顶随后梯田般逐层降落的过程和范围保留。
84|13|千言万语|2|千言万语|千言万语涌来与第一句反而轻如叹息的反差完整保留。
85|1|水流自己在呼吸|1|水流本身的呼吸|水流自身呼吸的拟人主体保留，不用人体呼吸替代。
'''

overrides = {
 ('flash',6): ('partial','水与时间不可逆、幸福留不住的核心都在B05，但未写清醒知道留不住才鼻酸的具体反应。“忧伤”较宽泛，末尾哄爱人的眼眶热又属A073，不能自动补回此项反应及其动因。'),
 ('gpt',19): ('pending','正文没有照写第4小节主题起点，decision明确挂起源内4/6冲突。属于有理由的待核，不计full；本次不查外部乐谱。'),
 ('flash',19): ('omitted','正文删除原A第4小节双音主题的定位，decision将其判错；源内多数支持6小节，但S02-A053只是条目，不能独自充当谱面核准。删除有内部依据，尚未外证。'),
 ('gpt',36): ('omitted','正文只留先克制为后来留余地(A076)，没有当前压抑与后面高潮释放的具体关系。out_of_scope裁决过严：原稿是在解释当前自我约束，未声称高潮已在本段发生；仍计85分母。'),
 ('flash',36): ('altered','保留当前压抑与后面释放的原关系，但加成“必要前提”“深深刻意”“彻底释放”，把原稿听感解释强化成必然且彻底的情感剧情。'),
 ('flash',33): ('partial','抚脸与不永存念头、薄影在正文；但未明说“尚未成为悲伤”，并被置入“这种幸福始终…带防备”的共同叙述，弱化原稿限定。'),
 ('flash',41): ('partial','幸福催生依恋与希望持续写出，但“这还不是痛苦”未保留；B06已进入疼，不能用该疼替代本项未痛苦的限定。'),
 ('flash',59): ('partial','保留舒服、不害怕、享景且知未到岸；删去暂时停在半空、不急抵达的状态，不能用未到岸推定不急抵达。'),
 ('gpt',62): ('partial','B18有感情上涌，未说愉悦越来越浓、终于不必藏好，亦未说起伏不等于解决。decision的“已写出”只能证实部分近义核心，不能算无损；跨至34不证明所有限定只能归32/34。'),
 ('flash',62): ('partial','B07有上涌，缺愉悦增浓使情绪不必藏得那么好及问题并未解决。decision把“不解决”主要归S04，源文却把它用于整段起伏；不能默默缩分母。'),
 ('flash',66): ('altered','11—15“呼吸逐渐拉长”被改成“线条被拉长”，吐出憋气又移接14—16；用“与此同时”拼接另一来源呼吸越来越短，牺牲呼吸主体和时间范围来求连续。'),
 ('flash',71): ('partial','“不哭，眼眶热”字面在B05，却移接在中年人哄爱人的场景；缺“成年人有分寸的怀念”限定，前面的过去回忆不足以让后段这个情绪归属唯一可还原。'),
 ('flash',77): ('altered','正文写“意大利歌剧里的二重唱”，女高音这一原意的发声主体消失且被双人改写；evidence里的“女高音”不能抵销正文缺失。'),
 ('flash',79): ('partial','暗绿浑凉水色及幸福的害怕在正文，原文“又怕又爽”中的爽感没有独立表达，不能从害怕或幸福自动推回。'),
}

rows=[]
for line in DATA.strip().splitlines():
    num,gb,gk,fb,fk,reason=line.split('|')
    num=int(num); item=ledger[num-1]
    assert item['id']==f'S02-A{num:03d}'
    row={'id':item['id'],'original_meaning':item['meaning'],'dimension':item['dimension'], 'source_spans':source_spans(item)}
    for model,bnum,keys in [('gpt',int(gb),gk),('flash',int(fb),fk)]:
        status,why=overrides.get((model,num),('full',reason))
        spans=output_spans(model,bnum,keys)
        # Explicitly include adjacent music context where required by an item.
        if num==82 and model=='gpt': spans+=output_spans('gpt',14,'第7、9、11小节')
        if num==53 and model=='flash': spans+=output_spans('flash',2,'第6小节起')
        if num==6 and model=='flash': spans+=output_spans('flash',5,'心里明白留不住')
        if num==70 and model=='gpt': spans+=output_spans('gpt',17,'温暖的长旋律')
        if num==60:
            spans+=output_spans(model,13 if model=='gpt' else 7,'倾诉')
        doc=g if model=='gpt' else f
        claims=[b['id'] for b in doc['pages'][0]['blocks'] if item['id'] in b.get('meaning_ids',[])]
        decisions=[d for d in doc['pages'][0].get('decisions',[]) if item['id'] in d.get('meaning_ids',[])]
        row[model]={'status':status,'spans':spans,'reason':why,'model_self_report_for_comparison_only':{'blocks':claims,'decisions':decisions}}
    rows.append(row)

def finding(fid, model, category, blocks, anchors, ids, explanation, severity='medium'):
    ss=[]
    for bn,ks in zip(blocks,anchors): ss+=output_spans(model,bn,ks)
    return {'id':fid,'model':model,'category':category,'severity':severity,'output_spans':ss,
            'related_old_ids':[f'S02-A{x:03d}' for x in ids],
            'source_spans':[s for x in ids for s in source_spans(ledger[x-1])], 'judgment':explanation}

reverse = [
 finding('RF01','flash','invented_co_reference_and_time',[3],['下午斜照~在夜聊中慢慢靠近'],[7,37,61], '同一“其一”从午后暖金船舱一路写到夜聊，无“另一种画面”或换时标记；各画面单独有来源，午后的人就是夜聊的人以及同一场景的连续性没有来源。'),
 finding('RF02','flash','invented_subject_link',[3],['一个平时习惯克制自己的人'],[39,46,79,80], '把惯于克制者终于不用警惕，独自珍贵沉浸，夏夜暗水、独自想念并为同一人的同一读法。原稿A046是亲近他人的语境，A039只是另一个可选主体，A079/A080又来自另一来源；单项有据不支持这条绑定。'),
 finding('RF03','flash','invented_equivalence_between_readings',[6],['每一次的心事都层层加重~从话语的探问上看'],[74,78,82], '安慰/叹气交替、确认/疑问/期限、安慰/犹豫/疼各有来源。B06将它们套入同一三次、同一层层加重，并称后者是话语层面的同一转变；这是新增等价关系。每条局部顺序仍可完整读到，故A074/A078/A082局部记full，关系错误在此另计。','high'),
 finding('RF04','flash','invented_simultaneity_and_subject_change',[7],['与此同时~线条被拉长'],[35,64,66], '原稿有呼吸越来越短，也有另一来源呼吸逐渐拉长。Flash用与此同时、把后一呼吸换为线条，制造可同时成立的一条发展；这是消解来源分歧而非保存并列读法。','high'),
 finding('RF05','flash','invented_sequence_between_alternative_movements',[7],['然而它没有顺势爆发~声音很快又漂浮'],[52,65,83], '落稳相视→漂起与峰顶→梯田落下各有来源；Flash加“然而…而是”，串成落稳→梯田下降→漂起的单一动作链，并增加“深情”相视。原A未给这两个读法的先后绑定。'),
 finding('RF06','flash','causal_intensification',[8],['必要前提~深深刻意压住'],[36,76], 'A036本来确有前瞻因果，不能全部说自造。但必要、深深刻意、彻底释放均加强原文；“肖邦的意图”虽复述原A，仍把解释变成作者意图断言。','high'),
 finding('RF07','flash','unsupported_authority',[3],['被乐评形容'],[81], '死亡威胁的比喻确在原A；本次未外证Marceli Szulc归属。Flash保留“被乐评形容”的权威包装，不能从附件内有该说法便证实历史归属。属于继承的未核权威，不是凭空创造死亡意象。'),
 finding('RF08','gpt','unsupported_duration',[7],['共同生活多年'],[32], '原A只说共同生活过一段时间，GPT增写“多年”。关系核心保留，但年限无来源，是小幅具体化；不将该外围修辞单独推翻A032核心full。','low'),
 finding('RF09','gpt','invented_hierarchy_between_readings',[15],['另一种听法则分得更细'],[74,82], '两种三次尾音读法均完整、并列明确；“分得更细”却添加后者是更细一层的层级，原文只支持不同解释，并无细粗关系。“没有被…吞掉”又是审计话语漏进正文。','low'),
 finding('RF10','gpt','unnecessary_opposition',[19,20],['另有一条关于呼吸的听法','相反的呼吸'],[35,66], '分开拉长与收紧有效，且本段时间部分重叠；但把不同来源直接称“相反”，会暗示必须对立，原稿允许并列而不必互斥。这比Flash改主体拼接轻，但仍有编辑附加关系。','low'),
 finding('RF11','gpt','overstrict_scope_decision',[13],['先克制'],[36,76], 'GPT把A036整项out_of_scope，留下A076。前者是“此时克制如何使后面释放成立”，属于解释当前段落，并非断言高潮现在发生；该裁决丢了不同于演奏留余地的意义。','high'),
 finding('RF12','gpt','unsupported_scope_partition',[18],['感情终于忍不住'],[62], 'GPT decision把“问题并未解决”主要归32/34；源文在谈整段起伏时已给这个限定，未限定仅在32/34。B18虽有起伏，却未无损恢复A062；Flash的同类裁决亦过窄。'),
]

def stats(doc):
    page=doc['pages'][0]
    fields=[page.get('title',''),page.get('intro','')]+[v for b in page['blocks'] for v in [b.get('label',''),b['text']]]
    body=''.join(b['text'] for b in page['blocks'])
    lens=[len(b['text']) for b in page['blocks']]
    return {'block_count':len(lens),'body_characters_including_punctuation':len(body),
            'body_han_characters':len(re.findall(r'[\u3400-\u4dbf\u4e00-\u9fff]',body)),
            'visible_characters_title_intro_labels_body':sum(map(len,fields)),
            'block_text_characters':lens,'longest_block_characters':max(lens),
            'mean_block_characters':round(sum(lens)/len(lens),1)}

report={
 'scope':'仅S02本次两份真实输出对inputs/S02.txt完整原A的内容与关系审计；不改正文、不评整套pipeline、不作新研究。',
 'files':{'input':'inputs/S02.txt','ledger':'reference/S02_ledger.json','gpt_raw':RAW,'gpt_parsed':GP,'flash':FP},
 'provenance':{'sha256_original_files':before,'gpt_parsed_sha256':sha(GP),'wrapper_removed':['<escape>','</escape>'],'parsed_object_equal_to_unwrapped_raw':json.loads(read(GP))==g},
 'method':{
  'denominator':85,'basis':'完整原A优先；ledger只固定85个旧ID和辅助定位。逐项读实际title/intro/block.text；meaning_ids、evidence和decisions均仅作模型自报对照。未用字符串命中自动判覆盖；内容锚点仅将人工裁决定位为可复核span。',
  'pool_units_read':list(units),'input_pool_span':{'start':pool_start,'end':pool_end},
  'span_convention':'start/end为0基半开Unicode码点偏移；先UTF-8-sig解码并将CRLF转LF。source相对完整inputs/S02.txt；output相对json_pointer所指已解码字符串，不是JSON文件字节位置。quote必须与该区间逐字相等。空spans表示正文无对应表达；pending/omitted的decision另附且不能充当正文证据。',
  'statuses':{'full':'本项可区别核心、动作/动因/时态及必要限定能由正文无损还原；不代表整块跨项关系无错误，关系单查reverse_findings。','partial':'有原义核心，但失去独特成分/限定。','omitted':'正文未表达原义；有理由拒绝仍不计full。','altered':'以另一个主体、过程、范围或更强因果替换原义。','pending':'正文未落实且输出明确保留待核冲突。'},
  'boundary_policy':'保留固定分母85；错位/冲突不静默删分母。前瞻解释可说明当前意义，不因提到后文自动跨段；后文具体已发生事件不得提前放入S02。',
  'attribution_policy':'不联网核验原A引用及音乐学主张；比较的是对原A保留与关系忠实度，不认证乐谱或史家署名。意象可保留为读法，来源署名有效性独立待核。',
 },
 'items':rows,
 'summary':{model:{'counts':{status:sum(r[model]['status']==status for r in rows) for status in ['full','partial','omitted','altered','pending']},'full_fraction':f"{sum(r[model]['status']=='full' for r in rows)}/85",'text_metrics':stats(doc)} for model,doc in [('gpt',g),('flash',f)]},
 'reverse_findings':reverse,
 'naturalness_and_length':{
  'counting_rule':'字数不使用模型自报。body按所有block.text串联计Unicode字符（含标点和换行），另报汉字数；visible另加标题、intro、label。排除ID、引文、evidence、decisions、method_notes。无预设硬上限。',
  'gpt':{'judgment':'句子和块更短，画面切换较易读；20块带来标题和换块成本，仍显账本组织痕迹，不能因块多就判好。','issues':['B15“另一种听法则分得更细”附加层级；“没有被安慰或疼痛吞掉”像在答审计。','B20“相反的呼吸”把不同读法对立化。','B10“心里同时暖和凉”措辞不够顺。'],'overall':'两份中更易读、跨来源关系更忠实，但仍需要编辑处理，非自然度已完全过关。'},
  'flash':{'judgment':'8块外观紧凑，块内分号长链、反复“绝非/并不是”以及然而/与此同时连接显著；B03/B04/B05的大段列举要求读者自行分离时间、主体与动因。','issues':['B03同一双人耳语读法同时容纳午后与夜聊，B04连续抚脸/掌托/望船舷堆叠。','B05把前史、当下舍不得、逝去怀念、哄爱人串成一大段。','B07为求连贯改呼吸主体并拼合不同动作次序。'],'overall':'信息量高但不能用8块声称阅读负担低；单块密度和自造联系损害自然度。'},
  'length_judgment':'两者都没有必要仅为字数删异质意思；先修关系和限定。GPT是否更短及幅度按summary实际字符计，不按视觉块数或模型自述。'
 },
 'key_five_differences':[
  {'topic':'女高音主体','ids':['S02-A077'],'gpt':'女高音与双人二重唱明确分开，full。','flash':'以歌剧二重唱顶替女高音，altered；引文不能补正文。'},
  {'topic':'互异呼吸的处理','ids':['S02-A035','S02-A064','S02-A066'],'gpt':'拉长、收紧分开作为读法，A066 full，但“相反”仍多一层对立。','flash':'与此同时把呼吸拉长换成线条拉长，并改吐气范围，A066 altered。'},
  {'topic':'人物与时间关系','ids':['S02-A007','S02-A039','S02-A046','S02-A061','S02-A079'],'gpt':'更多用一幅/另一幅、也许、另种听法分开主体时间；A079又怕又爽完整。','flash':'午后与夜聊、克制者与独自暗水沉浸被绑定；A079还漏爽感。'},
  {'topic':'三种尾音变化','ids':['S02-A074','S02-A078','S02-A082'],'gpt':'三次顺序均保留，交替与另外两种听法分开；“更细”层级仍是附加。','flash':'三项也均能逐项恢复，并未漏中间犹豫，但把交替、加重和话语探问当同一变化的不同层面，新增等价关系。'},
  {'topic':'克制与后文的关系及阅读负担','ids':['S02-A036','S02-A076','S02-A062'],'gpt':'当前压抑解释后文高潮被过严裁成跨段，A036 omitted；A062 partial，不接受自报已保留。20块句子较短。','flash':'A036保留但强化成必要/刻意/彻底，altered；A062同样partial。8块较少却长链更重，不能直接以卡数判断自然度。'}
 ],
 'mechanism_assessment':{
  'useful_observed':['关系标注配合正文中的显式“另一种/也许/一幅…另一幅”，对防止一人双声/双人/独处，以及呼吸长短被串成同一剧情有用；GPT展示较好实例。','明确保护三次变化及中间项：两份均保住A082的犹豫，A074亦完整；不能将此说成GPT独有进步。','固定85分母＋原A到正文span＋反向逐句关系检查，能抓到Flash A077和A066以及GPT A036的自报偏差。'],
  'not_sufficient':['仅kind=alternatives不能保证块内仍保持并列，Flash B03便在同一其一中混入午后夜聊。','仅meaning_ids齐全或evidence贴原句不证明正文full。','仅分小块改善密度不自动解决前瞻边界、年限增写和元审计措辞。'],
  'causal_limit':'这是同一输入上的两份单次成品对比，未见对照消融，无法声称某条提示或机制单独导致结果。此处“有用”仅指成品中可见的作用，不推断整套pipeline或模型总体优劣。',
  'overall':'此S02样本优先GPT作为关系组织更清楚的比较对象，但不以模型自报或full数代替审计；GPT的A036拒绝仍需明确指出，不能当全胜。'
 }
}
assert len(rows)==85 and len({r['id'] for r in rows})==85
def verify_span(s):
    if s['json_pointer'] is None:
        text=inp
    else:
        doc=json.loads(read(s['file']))
        for part in s['json_pointer'].strip('/').split('/'):
            doc=doc[int(part)] if isinstance(doc,list) else doc[part]
        text=doc
    assert text[s['start']:s['end']]==s['quote'], s
for row in rows:
    for model in ['gpt','flash']:
        assert row[model]['status'] in ['full','partial','omitted','altered','pending']
        if row[model]['status'] not in ['pending','omitted']:
            assert row[model]['spans'], (row['id'],model)
        for s in row['source_spans']:
            verify_span(s)
        for s in row[model]['spans']:
            verify_span(s)
for rf in reverse:
    for s in rf['source_spans']+rf['output_spans']:
        verify_span(s)
assert before == {p:sha(p) for p in before}, 'Original file changed'
report['validation']={'unique_old_ids':85,'model_judgments':170,'all_selected_quotes_exact':True,'original_files_sha256_unchanged':True,'gpt_parse_roundtrip_equal':True}
dest=ROOT/'reviews/S02_model_comparison.json'
dest.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'output':str(dest),'summary':report['summary']},ensure_ascii=False,indent=2))
