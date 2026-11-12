# 用无界面浏览器真实点一下全文页：确认点句子后音乐时间确实跳到那里
import json, os, re, subprocess, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')
CH = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
src = open('out/全文页/船歌_全文页.html', encoding='utf-8').read()
os.makedirs('work/click', exist_ok=True)
shutil.copyfile('out/全文页/船歌_录音.m4a', 'work/click/a.m4a')
page = src.replace('船歌_录音.m4a', 'a.m4a')
inject = """
<script>
a.addEventListener('loadedmetadata',()=>{
  const items=[...document.querySelectorAll('.bead')];
  const target=items[20];
  const want=D.flatMap(s=>s.rows).filter(r=>r.k==='bead')[20].t;
  target.click();
  setTimeout(()=>{
    const pre=document.createElement('pre');pre.id='res';
    pre.textContent=JSON.stringify({want,got:a.currentTime,dur:a.duration,on:document.querySelectorAll('section.on').length});
    document.body.appendChild(pre);
  },1500);
});
</script></body>"""
page = page.replace('</body>', inject)
open('work/click/t.html', 'w', encoding='utf-8').write(page)
url = 'file:///' + os.path.abspath('work/click/t.html').replace('\\', '/')
r = subprocess.run([CH, '--headless=new', '--disable-gpu', '--no-sandbox', '--autoplay-policy=no-user-gesture-required',
                    '--user-data-dir=' + os.path.abspath('work/chrome_tmp2'), '--virtual-time-budget=9000', '--dump-dom', url],
                   capture_output=True, timeout=280)
out = r.stdout.decode('utf-8', 'ignore')
m = re.search(r'<pre id="res">(.*?)</pre>', out)
print('结果', m.group(1) if m else '没有拿到结果')
