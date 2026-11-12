# 11-08：整片一次渲染时本机内存不够（WSL 占 15 GB，只剩 1.6 GB），MemoryError。改成每 60 秒一段、一次一个进程，最后拼接并换上完整原声。
cd /d/musicclaude/_video_public_20261104
export FILM_DATA=line_r79o OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
W=$1; DUR=$2; NAME=$3; O=out/大众版_K3A/chunks_$W; mkdir -p $O
s=0; i=0
while [ $s -lt $DUR ]; do
  e=$((s+60)); [ $e -gt $DUR ] && e=$DUR
  f=$O/$(printf %03d $i).mp4
  [ -s $f ] || python film_v8.py render --work $W --tag g68K3A --start $s --end $e --out $f >> $O/log.txt 2>&1 || echo "段 $i 失败" >> $O/log.txt
  s=$e; i=$((i+1))
done
ls $O/*.mp4 | sed "s#.*/#file '#; s#\$#'#" > $O/list.txt
AUD=$(python -c "import json;print(json.load(open('plans/${W}_points.json',encoding='utf-8'))['audio'])")
ffmpeg -v error -y -f concat -safe 0 -i $O/list.txt -c:v copy -an $O/video.mp4 && ffmpeg -v error -y -i $O/video.mp4 -i "$AUD" -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 256k -shortest -movflags +faststart "out/大众版_K3A/$NAME" && echo "完成 $NAME"
