#!/usr/bin/env python3
"""Burn Spanish callout chips onto reel2_conscious.mp4.
Chips: VEGANO / MENOS AZÚCAR / BAJAS CALORÍAS — timed overlays with rounded box, DejaVu Sans Bold.
Output: reel2_conscious_es.mp4 (same 720x1280 8s H.264+AAC, x264 + aac copy).
"""
import subprocess, sys, os

SRC = "/root/gointbrands_assets/opts/reels_out/reel2_conscious.mp4"
OUT = "/root/gointbrands_assets/opts/reels_out/reel2_conscious_es.mp4"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

chips = [
    # (text, start_sec, dur_sec, x_anchor, y)  — x anchored right (w-text_w-40)
    ("VEGANO",       1.0, 2.4, "right", 300),
    ("MENOS AZÚCAR", 3.6, 2.4, "right", 470),
    ("BAJAS CALORÍAS", 6.2, 1.8, "right", 640),
]

# Build filter_complex drawing all three as text with a box
drawtexts = []
for i,(txt,st,dur,anchor,y) in enumerate(chips):
    dt = (f"drawtext=fontfile={FONT}:text='{txt}':fontsize=46:fontcolor=white:"
          f"box=1:boxcolor=black@0.55:boxborderw=18:x=w-text_w-40:y={y}:"
          f"enable='between(t,{st},{st+dur})'")
    drawtexts.append(dt)

flt = ",".join(drawtexts)
cmd = ["ffmpeg","-y","-i",SRC,"-vf",flt,"-c:a","copy","-crf","20","-preset","medium",OUT]
print("Running overlay...")
p = subprocess.run(cmd, capture_output=True, text=True)
if p.returncode != 0:
    print("ERR", p.stderr[-2000:]); sys.exit(1)
print("saved", OUT)