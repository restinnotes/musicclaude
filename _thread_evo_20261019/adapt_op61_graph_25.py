"""Preserve the first graph, adapt only audited content and explicitly justified arrows."""
import copy
import json
import hashlib
import evo
import synth_v2
import finish_thread_25 as finish

if __name__=='__main__':
    old=finish.OUT/'C25op61classified_op61_graph.json'
    g=json.loads(old.read_text(encoding='utf-8'));before=copy.deepcopy(g)
    ix={i['id']:i for s in g['segments'] for i in s['items']}
    # These were incorrectly assigned the bodily bead by the earlier graph author.
    ix['I27']['explains']=['S04-B2','S04-B4']
    ix['I28']['explains']=['S04-B4']
    sg=next(s for s in g['segments'] if s['sec']=='S04')
    sg['items'].extend([
      {'id':'I78','text':'刚重新感到轻松、亲近，这份温暖还很鲜活，能留在其中多久却不由他。','key':'温暖鲜活却留不住','follows':False,'sources':[3],'explains':['S04-B3']},
      {'id':'I79','text':'过去已回不来，连眼下重现的亲近也在流逝；越不舍，越觉得时间推着自己走。','key':'连眼下的亲近也在流逝','follows':False,'sources':[3],'explains':['S04-B3']},
      {'id':'I80','text':'身体先紧起来，像没来得及停留就得向前；这种催迫不必等到反复自问才出现。','key':'身体的催迫不依赖反刍','follows':True,'sources':[3],'explains':['S04-B3']}])
    sg['because'].extend([{'from':'I21','to':'I78','rel':'提供理由'},{'from':'I5','to':'I79','rel':'限制'}])
    # A later spontaneous familiar sensation is not caused by the earlier familiar sensation.
    # A failed question does not itself prove a later wish will receive no response.
    removed=[]
    for s in g['segments']:
        keep=[]
        for a in s.get('because',[]):
            if (a['from'],a['to']) in {('I4','I45'),('I28','I43')}:
                removed.append({'sec':s['sec'],**a});continue
            if (a['from'],a['to'])==('I41','I48'):a['rel']='提供理由'
            keep.append(a)
        s['because']=keep
    changes={
      'I54':('最初沉重却无从安放的失落，如今有了内容：他舍不得曾有的温暖、轻松和亲近。','牵挂有了感受的内容','避免把认清感受误写成已辨认一个具体失去对象；原主线仍未指定人物或往事。'),
      'I49':('他反复想靠近又找不到着落；惊悸过去了，身体仍不肯停下这股靠近的冲动。','惊悸后仍停不下趋近','无出口限于当下愿望，不能升级为客观上一切可能都已不存在。'),
      'I65':('早先主要靠用力维持姿态，如今柔弱中的向往也能推着他走，压力仍在。','向往也进入向前的力量','早期脆弱与力量已经共存；变化是向往成为动力，不是过去完全没有柔弱，也不扩写成曾向公众表演无事的剧情。')}
    text_edits=[]
    for iid,(text,key,why) in changes.items():
        text_edits.append({'id':iid,'before':ix[iid]['text'],'after':text,'why':why})
        ix[iid]['text']=text;ix[iid]['key']=key
    source=json.loads((evo.ROOT/'evaluations/synth/C25op61body2_op61/run.json').read_text(encoding='utf-8'))
    finish.validate(g,source)
    synth_v2.dump(finish.OUT/'C25op61body2_op61_graph.json',g)
    synth_v2.dump(finish.OUT/'C25op61body2_op61_graph_adaptation.json',{'original_path':str(old),'original_sha256':hashlib.sha256(old.read_bytes()).hexdigest(),'added_items':['I78','I79','I80'],'new_source':'S04 chosen 3, independently reviewed bodily temporal pressure, persisted as H9b','corrected_bead_attribution':['I27','I28'],'removed_arrows':removed,'rel_precision':{'from':'I41','to':'I48','before':'限制','after':'提供理由','why':'此前已有完整愿望，使现在失去容身之处有实际内容。'},'text_edits':text_edits,'acceptance':'provisional graph adaptation; full source and graph reviews still required'})
    print('adapted graph; original preserved; full fidelity review pending',flush=True)
