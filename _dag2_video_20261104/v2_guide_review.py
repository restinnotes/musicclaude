"""Review the actual encoded correction to the one remaining visual blocker."""
import json,os,shutil,subprocess,sys
from dag2 import ROOT,EVO,read,write,sha,parse

def main():
    folder=ROOT/'runs/v2_center_guide_review';folder.mkdir(exist_ok=True);att=folder/'attachments';att.mkdir(exist_ok=True);clip=ROOT/'out/op60_v2_局部动画样片.mp4';paths=[]
    for label,t in [('pink',11),('purple',23)]:
        p=att/f'v2_encoded_center_{label}.png';subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(clip),'-frames:v','1',str(p)],check=True);paths.append(p)
    initial=ROOT/'qa/v2_design_review_initial.json'
    if not initial.exists():shutil.copyfile(ROOT/'qa/v2_design_review.json',initial)
    msg='''这是上一轮视频静帧审查的唯一阻断修补。前一轮已认可关系图节点/关系边、去除标题时间标签、Op52的空心/实心/横向音乐视觉与右栏减密；唯一blocking是粉色状态中间不够明确，容易把当前位置误读为普通音符。
附件是32秒样片实际编码后的粉色与紫色画面，不是未编码原图。现新增始终可见的中央时间指示：一条细竖线与底部小光点，与当前珠子同色。它是播放位置标记，即使音符间隙也存在；真正发声的音乐光点仍按原数据，不在无发声音符时伪造一颗“发声球”。请检验原阻断是否解除、有无新增裁切/遮挡。不要要求无音符时伪造声部事件，不要求改变音高、连接或时序来制造曲线。原右栏有三档，模型偏好适中是建议；按用户“太挤”优先成片暂用极简，另两档预览保留，此密度选择不是阻断。
只输出JSON：{"verdict":"pass或revise","blocking":[{"issue":"...","fix":"..."}],"resolved":["..."],"not_verified":["..."]}，只对看到的图片负责，不宣称看过全片或验证听觉同步。'''
    (folder/'prepared_input.txt').write_text(msg,encoding='utf8');write(folder/'attachments.json',{str(p):sha(p) for p in paths})
    os.environ['THREAD_ROUTE']='gpt3s';sys.path.insert(0,str(EVO));import evo,gpt3_call
    rid='dag2_20261104_v2_center_guide_review';(evo.RUNS/rid).mkdir(exist_ok=True);evo.check_submission()
    ans=evo.output(rid) if evo.done(rid) else gpt3_call.call(rid,msg,None,evo.G6,{'stage':'DAG2-encoded-center-guide-review','attach':[str(p) for p in paths],'web':True})
    if not ans:raise RuntimeError('No complete guide review; inspect existing run')
    (folder/'output.txt').write_text(ans,encoding='utf8');result=parse(ans);write(ROOT/'qa/v2_center_guide_review.json',result)
    first=read(initial)
    if result['verdict']=='pass' and not result['blocking']:
        assert len(first['blocking'])==1
        final={**first,'verdict':'pass','blocking':[],'initial_blocking':first['blocking'],'initial_review':str(initial),'center_guide_review':str(ROOT/'qa/v2_center_guide_review.json'),'center_guide_resolved':result['resolved'],'selected_density':0,'density_decision':'user prioritizes reduced simultaneous content; model preference 1 remains a nonblocking option'}
        write(ROOT/'qa/v2_design_review.json',final)
    print(json.dumps(result,ensure_ascii=False),flush=True)

if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf8');main()
