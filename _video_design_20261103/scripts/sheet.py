import sys,os,cv2,numpy as np
sys.path.insert(0,'scripts')
import engine
film=engine.Film('work/op60_music.json','work/op60_spec.json')
ts=[float(x) for x in sys.argv[2:]]
cols=4
tiles=[]
for t in ts:
    im=film.frame(t)[:,:,::-1]
    im=cv2.resize(im,(640,360),interpolation=cv2.INTER_AREA)
    cv2.putText(im,f'{int(t//60)}:{int(t%60):02d}',(8,350),cv2.FONT_HERSHEY_SIMPLEX,0.45,(170,170,170),1,cv2.LINE_AA)
    tiles.append(im)
while len(tiles)%cols: tiles.append(np.zeros_like(tiles[0]))
rows=[np.hstack(tiles[i:i+cols]) for i in range(0,len(tiles),cols)]
cv2.imwrite(sys.argv[1],np.vstack(rows))
