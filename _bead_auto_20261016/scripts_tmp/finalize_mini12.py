import json, re, os, hashlib, zipfile
out = r'D:\musicclaude\_bead_auto_20261016\out'
inp = os.path.join(out, 'STEP4_inputs')
def resp(s):
    j = json.load(open(os.path.join(inp, 'mini_%s_out.json' % s), encoding='utf-8-sig'))
    return j['response']
def cc(t):
    return len(re.findall(r'[\u4e00-\u9fff]', t))
meta = {
 'S02':'mm.4-16 di1zhuTi','S03':'mm.17-23 jianJu','S04':'mm.24-34 di1zhuTi-queBao',
 'S05':'mm.35-39 jianJu','S06':'mm.40-50 di2qianBan','S07':'mm.51-61 di2qianBan-queBao',
 'S08':'mm.62-71 di2houBan','S10':'mm.78-83 chaRuJu','S11':'mm.84-92 di1zaiXian',
 'S12':'mm.93-102 di2houBan-zaiXian','S14':'mm.111-116 zhongJieJu'}
oksegs = ['S02','S03','S04','S05','S06','S07','S08','S10','S11','S12','S14']
trunc = set(['S02','S03','S05','S06','S14'])
times = {'S02':40,'S03':51,'S04':21,'S05':51,'S06':47,'S07':23,'S08':47,'S10':20,'S11':38,'S12':48,'S14':52}
R = {s: resp(s) for s in oksegs}
R['S01'] = resp('S01'); R['S09'] = resp('S09')
labels = {'S01':'mm.1-3 xuZou','S02':'mm.4-16 di1zhuTi','S03':'mm.17-23 jianJu','S04':'mm.24-34 di1zhuTi-queBao',
 'S05':'mm.35-39 jianJu','S06':'mm.40-50 di2qianBan','S07':'mm.51-61 di2qianBan-queBao',
 'S08':'mm.62-71 di2houBan','S09':'mm.72-77 jianJu','S10':'mm.78-83 chaRuJu','S11':'mm.84-92 di1zaiXian',
 'S12':'mm.93-102 di2houBan-zaiXian','S13':'mm.103-110 di2qianBan-zaiXian','S14':'mm.111-116 zhongJieJu'}
with open(os.path.join(out,'BEADS_PARTIAL.md'),'a',encoding='utf-8') as f:
    f.write('\n> mini12: S02-S08,S10-S12,S14 input STEP4_inputs/STEP4_mini_<S>.txt short-noattach fresh; S13 FAILED x2 pre_submit.\n')
    for s in oksegs:
        tg = ' [tail-tag-truncated,body-intact-verbatim]' if s in trunc else ''
        f.write('\n## %s %s -- mini success (verbatim)\n\n%s\n\n> in STEP4_mini_%s.txt; out mini_%s_out.json completed=True %ds exit0 len=%d chinese=%d%s.\n' % (s, labels[s], R[s], s, s, times[s], len(R[s]), cc(R[s]), tg))
    f.write('\n## S13 mm.103-110 -- FAILED (empty)\n\n> two tries 21s each headless_native_result_rejected/pre_submit exit1 no payload; evidence mini_S13_err.txt.\n')
with open(os.path.join(out,'BEAD_SOURCE_LEDGER.md'),'a',encoding='utf-8') as f:
    f.write('\n## mini12 ledger (GPT-6w only, short-noattach)\n\n11 success, S13 FAILED x2. minis under 500 chars: instruction+pool-compress (A07/A08 verbatim; other UIDs referenced; missing-4 A02/A09/A10/A11 absent). No attachments.\n\n| seg | label | result | evidence | len |\n|---|---|---|---|---|\n')
    for s in oksegs:
        tg = ' trunc-tail' if s in trunc else ''
        f.write('| %s | %s | OK | mini_%s_out.json | len=%d chinese=%d%s |\n' % (s, labels[s], s, len(R[s]), cc(R[s]), tg))
    f.write('| S13 | mm.103-110 | FAILEDx2 | mini_S13_err.txt | none |\n\n- Dropped: UNCERTAIN/LONG_RANGE/UNRESOLVED not in reader text; unexpanded int-PRIMARY only referenced, nothing fabricated.\n')
ub = []
ub.append('# BEADS_FOR_USER')
ub.append('')
ub.append('> 13 of 14 success; S13 FAILED empty. Each bead = GPT-6w fresh response verbatim. No fabricated A content.')
ub.append('> Frozen: C2 Asayama/PTNA2008 S01-S14 (1-116). Link: GPT-6w only, short-noattach.')
ub.append('')
for s in ['S01','S02','S03','S04','S05','S06','S07','S08','S09','S10','S11','S12','S13','S14']:
    if s == 'S13':
        ub.append('## S13 mm.103-110 -- FAILED (empty)\n\n> pre_submit rejected twice, no payload, left empty.\n')
        continue
    tg = ' [tail-tag-truncated,body-intact-verbatim]' if s in trunc else ''
    ub.append('## %s %s (len=%d)%s\n\n%s\n' % (s, labels[s], len(R[s]), tg, R[s]))
total = sum(len(R[s]) for s in R)
ub.append('- Total bead chars: %d (13 success payloads incl punctuation/tags; S13 empty).' % total)
ub.append('- UNRESOLVED/LONG_RANGE excluded. Missing 4 (A02/A09/A10/A11) absent, not used.')
open(os.path.join(out,'BEADS_FOR_USER.md'),'w',encoding='utf-8').write('\n'.join(ub) + '\n')
with open(os.path.join(out,'RUN_CALLS_AND_FILES.md'),'a',encoding='utf-8') as f:
    f.write('\n## mini12 calls (GPT-6w short-noattach fresh)\n\n| id | time UTC+8 | cmd | result |\n|---|---|---|---|\n')
    for s in oksegs:
        f.write('| M4-%s | 2026-10-16 03:29-03:37 | ask --file STEP4_mini_%s.txt --model gpt-6-thinking --json | exit0 %ds completed=true |\n' % (s, s, times[s]))
    f.write('| M4-S13 | 2026-10-16 03:37 | ask --file STEP4_mini_S13.txt x2 | exit1x2 21s pre_submit FAILED |\n\n- S09/S01 prior success kept (53s/50s). 12 serial: 11 first-try OK, S13 FAILED after 2 (within limit). No git/score/T/H/Thread/WHY/E7/blind.\n- New files: STEP4_mini_S02..S14.txt, mini_<S>_out.json/.err, mini12_timing.txt, run_mini12.ps1, mini_responses_extract.txt.\n')
zp = r'C:\Users\zuoyi\Downloads\music_bead_auto_20261016.zip'
if os.path.exists(zp):
    os.remove(zp)
with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as z:
    for root, ds, fs in os.walk(out):
        for fn in fs:
            p = os.path.join(root, fn)
            z.write(p, os.path.relpath(p, os.path.dirname(out)))
h = hashlib.sha256(open(zp,'rb').read()).hexdigest()
open(os.path.join(inp,'mini12_zip.txt'),'w',encoding='utf-8').write('ZIP=%s BYTES=%d SHA256=%s TOTAL=%d\n' % (zp, os.path.getsize(zp), h, total))
print('ZIP=' + zp)
print('BYTES=%d' % os.path.getsize(zp))
print('SHA256=' + h)
print('TOTAL_CHARS=%d' % total)
