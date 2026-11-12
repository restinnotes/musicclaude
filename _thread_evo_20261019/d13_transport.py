"""Use the bound GPT4 CLI unchanged, with its existing diagnostic no-buffering option.

Only the advertised streaming capability changes. Account checks, model/max,
privacy flags, terminal verification and the CLI's failure handling are retained.
No authentication data or raw stream is read or emitted here.
"""
import sys
sys.path.insert(0,'D:/musicclaude/gpt2agent-safechain/tools/chatgpt_web')
import gpt4_cli
import gpt3_cli

original_run=gpt3_cli.subprocess.run
def transport_run(command,*args,**kwargs):
 if len(command)>1 and str(command[1]).endswith('pro_bridge_http_probe.py'):
  command=[*command,'--disable-buffering']
 return original_run(command,*args,**kwargs)

if __name__=='__main__':
 sys.stdout.reconfigure(encoding='utf-8');sys.stderr.reconfigure(encoding='utf-8')
 gpt3_cli.subprocess.run=transport_run
 raise SystemExit(gpt4_cli.main())
