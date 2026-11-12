# 11-11 K28b 试看版（照 K11g 的分段渲染）
set -euo pipefail
cd /d/musicclaude/_video_public_20261104
export FILM_DATA=line_r79o OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
W=$1; DUR=$2; NAME=$3; O=out/大众版_K28b/chunks_$W; mkdir -p $O
python -c 'import json,sys; from alignment_guard import require_renderable; w=sys.argv[1]; require_renderable(json.load(open(f"input/{w}_music_aligned.json",encoding="utf-8")),json.load(open(f"plans/{w}_points.json",encoding="utf-8"))["audio"])' "$W"
: > "$O/list.txt"
s=0; i=0
while [ $s -lt $DUR ]; do
  e=$((s+60)); [ $e -gt $DUR ] && e=$DUR
  f=$O/$(printf %03d $i).mp4
  # 对齐数据或画面稿更新后，不能仅因旧分段存在就复用。
  fresh=1
  [ -s "$f" ] || fresh=0
  for dep in film_v8.py film_v6.py film_v3.py "input/${W}_music_aligned.json" "$FILM_DATA/r3/s24/screen_${W}_g68K28b.json" "$FILM_DATA/r3/script_${W}_g68K28b.json"; do
    [ "$dep" -nt "$f" ] && fresh=0
  done
  if [ "$fresh" -eq 0 ]; then
    python film_v8.py render --work "$W" --tag g68K28b --start "$s" --end "$e" --out "$f" >> "$O/log.txt" 2>&1
  fi
  printf "file '%03d.mp4'\n" "$i" >> "$O/list.txt"
  s=$e; i=$((i+1))
done
AUD=$(python -c "import json;print(json.load(open('plans/${W}_points.json',encoding='utf-8'))['audio'])")
ffmpeg -v error -y -f concat -safe 0 -i $O/list.txt -c:v copy -an $O/video.mp4 && ffmpeg -v error -y -i $O/video.mp4 -i "$AUD" -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 256k -shortest -movflags +faststart "out/大众版_K28b/$NAME" && echo "完成 $NAME"
