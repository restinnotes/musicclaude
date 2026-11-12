#!/bin/bash
cd /d/musicclaude/_video_public_20261104/line_r79o
export PUB_SRC=r2c
python r3/skeleton.py g68K11g run1 > r3/skel_K11g1.log 2>&1 &
python r3/skeleton.py g68K11g run2 > r3/skel_K11g2.log 2>&1 &
python r3/skeleton.py g68K11gSR run1 > r3/skel_SR.log 2>&1 &
PUB_SRC=r2k23b python r3/skeleton.py g68K23bN run1 > r3/skel_K23b.log 2>&1 &
wait
python r3/skeleton.py sum g68K11g run1 run2; python r3/skeleton.py sum g68K11gSR run1; PUB_SRC=r2k23b python r3/skeleton.py sum g68K23bN run1
echo "== 骨架测校准完 $(date)"
