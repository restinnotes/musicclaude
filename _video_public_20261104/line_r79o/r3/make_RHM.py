"""11-07 g68RHM = g68RHL 把修线改了原意的几处改回（疑问改断言、具体说法变笼统、加了定稿没有的话）。"""
import copy, sys
sys.stdout.reconfigure(encoding='utf-8')
from pub24 import S, rd, wr, to_script
FIX = {
 'op60': {9: '他几乎想把藏着的话全说出来，也盼对方喜欢他不再小心收着的样子。',
          10: '他盼着说出来能把眼下的好留得久一点。',
          40: '可就算听到了，越喜欢跟他待着，越觉得时间过得快，真能一直这样吗？'},
 'op61': {8: '从前那样的日子过不成了，离开后就一定会更好过吗？',
          9: '想起从前亲近的日子，他真盼着还能那样相处。',
          19: '当初只想着别再受气，却没料到离开后这么孤单，早知道这样还会走吗？',
          20: '他想找回从前的亲近，却不甘心回去受气，连当初离开的决心也找不着了。',
          25: '他忽然分不清，想回去是舍不得被当作自己人的日子，还是怕孤单到连那些气也肯再受。',
          27: '他慢慢明白，自己最舍不得的是从前有人把他当作自己人的日子，可回去还能像从前那样吗？',
          33: '他仍怕以后遇上难处只能自己扛，心里没底，却不想因为害怕就放弃打算。'}}
for w, fx in FIX.items():
    scr = copy.deepcopy(rd(S/f'screen_{w}_g68RHL.json')); old = rd(S/f'screen_{w}_g68RHH.json'); k = -1
    oldL = [x for s in old['sections'] for x in s['rows'] if x['kind'] == 'line']
    for s in scr['sections']:
        for x in s['rows']:
            if x['kind'] != 'line': continue
            k += 1
            if k in fx:
                x['text'] = fx[k]; x['keys'] = [q for q in (x.get('keys') or []) + (oldL[k].get('keys') or []) if q in fx[k]]; x['keys'] = list(dict.fromkeys(x['keys']))[:2]
                print(w, k, x['text'], x['keys'])
    wr(S/f'screen_{w}_g68RHM.json', scr); to_script(w, 'g68RHM', scr)
