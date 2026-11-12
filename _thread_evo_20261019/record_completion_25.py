"""Record an unambiguous restart point only after successful export verification."""
import json,hashlib
from pathlib import Path
import evo,synth_v2
import finish_thread_25 as f

def load(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
gp=f.OUT/'final_acceptance.json';gate=load(gp)
vp=f.OUT/'export_verification.json';verification=load(vp)
assert gate['decision']=='accept_complete' and verification['all_passed'] and verification['gate_sha256']==sha(gp)
provenance=load(f.OUT/'model_provenance_verification.json');assert provenance['passed']
pointer={'status':'two_concrete_works_completed_and_verified','gate_path':str(gp),'gate_sha256':sha(gp),'export_verification_path':str(vp),'export_verification_sha256':sha(vp),'works':gate['works'],'outputs':r'C:\Users\zuoyi\Documents\Codex\2026-10-25\n-n\outputs','limitations':'Documented human edits; general high-probability automation on new works remains unproven.','historical_startup_files':'acceptance_scope.json, pilot_gate.json and provisional comparisons describe earlier stages. Retained verbatim as history; final_acceptance.json is the final content decision.'}
synth_v2.dump(evo.ROOT/'CONTINUATION_LATEST_20261025.json',pointer)
old=load(evo.ROOT/'evaluations/continuation_20261025/op61_old_value_main_comparison.json')
synth_v2.dump(f.OUT/'op61_final_non_regression.json',{'status':'accepted_for_current_concrete_work','historical_comparison':old,'current_source':gate['works']['op61']['source_tag'],'final_gate_sha256':sha(gp),'main_reason':'S02 retains real strength without resolution, familiarity that exposes distance, growing control cost while attachment remains, dignity with vulnerability, and resistance to disappearance without an invented biography. S04 adds independently grounded bodily time pressure and rechecks all affected dependencies. Final graph and Center retain these values; no new external event or strategy plot was added.'})
text='''2026-10-25 续作完成位置

先读 CONTINUATION_LATEST_20261025.json，再读其指向的 final_acceptance.json。
Op.60最终综合：evaluations/synth/C25whole60_op60/run.json
Op.61最终综合：evaluations/synth/C25op61body2_op61/run.json
最终人话关系图、Center及评审：evaluations/continuation_20261025/finalization/
可读与完整交付：C:\\Users\\zuoyi\\Documents\\Codex\\2026-10-25\\n-n\\outputs

两个具体作品已完成验收与导出。不要再按早期 acceptance_scope.json 中的“试跑前五段”当作当前待办。
早期失败、批评和修订前文件全部保留；source、graph、评审和交付之间的哈希与语义对应以最终 gate 和 export_verification.json 为准。
已修正回收匹配模型/附件的错误；结构化stderr中的已提交上游错误也应记录为已提交，不可当成未发送而反复补发。无正文调用不算通过。
原始珠子与去处自动独立附在关系图记录，不能强塞进主心理步骤。历史关系“改写”指后来经验改变原来意义，不指同义换说法。人话化保留比较基线、正向增量和两种原因。未概念化不自动意味着“还说不清”。
本次包含有记录的人工修订，尚未验证新作品的高概率全自动成功率。若另行研究通用稳定性，需在新作品上重新验证，不把本次两份最终稿当作该结论。
'''
(evo.ROOT/'CONTINUATION_20261025.txt').write_text(text,encoding='utf-8-sig')
print('Canonical restart pointer and final non-regression record saved',flush=True)
