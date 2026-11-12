"""Op.52 N02：24 份 A 稿。GPT 限 3 路并发（主线也在跑），其余走既有 runner。提示词和模型与 corpus24 相同。"""
import os, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
B = Path('D:/musicclaude/_bead_op61_20261020/gen_A'); sys.path.insert(0, str(B)); sys.stdout.reconfigure(encoding='utf-8')
import gen
gen.WORK = 'op52'
import work_meta
jobs = gen.corpus_jobs('op52'); d = work_meta.load('op52'); dest = work_meta.source_dir(d); print('目标', dest, flush=True)
gpt = [j for j in jobs if j['family'].startswith('gpt')]
if len(sys.argv) > 1 and sys.argv[1] == 'gpt':
    with ThreadPoolExecutor(3) as ex: list(ex.map(lambda j: gen.run(j['name'], j['pv'], j['model'], j['prompt']), gpt))
    print('GPT 完成', sum((gen.output_dir()/(j['name']+'.md')).exists() for j in gpt), '/', len(gpt), flush=True)
else:
    runner_dir = Path('D:/musicclaude/music_work_since_1008v3_20261009/tools'); sys.path.insert(0, str(runner_dir)); import runner
    other = []
    for j in jobs:
        if j['family'].startswith('gpt'): continue
        item = {'job_id': j['name'], 'branch': 'A-'+j['branch'], 'model_key': j['model'], 'prompt': j['prompt'], 'prompt_version': j['pv'], 'work_key': 'op52', 'work_name': work_meta.name(d, True), 'sample': j['sample']}
        if j['branch'] == 'int':
            item['forbid_tools'] = ['search_web', 'read_url_content', 'browser_subagent', 'open_browser_url', 'read_browser_page', 'call_mcp_tool', 'run_command']; item['max_attempts'] = 6
        other.append(item)
    run_dir = gen.output_dir().parent/'other_models'
    res = runner.run_jobs(run_dir, other, max_workers=4, timeout=3600)
    print('其他模型', [(m.get('job_id'), m['status']) for m in res], flush=True)
