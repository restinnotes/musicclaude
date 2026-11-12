#!/bin/bash
cd /d/musicclaude/_video_design_20261103
A61="/d/archive/classical-op52-legacy-2026-08-29/classical/里赫特 61 布拉格_trimmed.m4a"
date +%T > work/run_all.log
export MUSIC=work/op60_music_v3.json
WORKERS=13 python scripts/render.py clip -5 516 "out/船歌_主片样片_底部字幕.mp4" >> work/run_all.log 2>&1; date +%T >> work/run_all.log
LAYOUT=rail CHUNKS=work/ch_rail WORKERS=13 python scripts/render.py clip 107.6 190 "out/对比A_一段一页.mp4" >> work/run_all.log 2>&1
SPEC=work/op60_spec_person.json CHUNKS=work/ch_person WORKERS=13 python scripts/render.py clip 107.6 190 "out/对比B_第一人称.mp4" >> work/run_all.log 2>&1
MUSIC=work/op61_music_v3.json SPEC=work/op61_spec.json AUDIO="$A61" CHUNKS=work/ch_61 WORKERS=13 python scripts/render.py clip -5 160 "out/幻想波兰舞曲_开头样片.mp4" >> work/run_all.log 2>&1
date +%T >> work/run_all.log; ls -la out >> work/run_all.log; tail -8 work/run_all.log
