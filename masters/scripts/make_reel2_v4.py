#!/usr/bin/env python3
"""Reel 2 v4 — Conscious Wines from a TRULY EMPTY dry coupe frame.
User: use the AI's own labels (in-video Spanish chips), remove my burn-ins.
Prompt: empty dry coupe -> Conscious bottle pours -> fills; AI draws SPANISH chips VEGANO/MENOS AZUCAR/BAJAS CALORIAS.
Veo 3.1 Lite, 8s, 9:16, 720p, audio.
"""
import json, urllib.request, os, sys, time

KEY = None
with open("/root/.hermes/.env") as fh:
    for line in fh:
        if line.startswith("OPENROUTER_API_KEY="):
            KEY = line.split("=", 1)[1].strip().strip('"').strip("'")
            break
if not KEY:
    print("RESULT NO_API_KEY", flush=True); sys.exit(1)

OUT = "/root/gointbrands_assets/opts/reels_out"
os.makedirs(OUT, exist_ok=True)
HG = "https://raw.githubusercontent.com/OPGokuVPS/gointbrands-assets/main"

def poll(job_id, hdr, timeout=260):
    t0=time.time()
    while time.time()-t0 < timeout:
        try:
            req=urllib.request.Request(f"https://openrouter.ai/api/v1/videos/{job_id}", headers={"Authorization":f"Bearer {KEY}"})
            with urllib.request.urlopen(req,timeout=60) as r: d=json.loads(r.read().decode())
        except Exception:
            time.sleep(8); continue
        st=d.get("status"); print(f"{hdr} poll {st}",flush=True)
        if st in ("completed","succeeded","done","failed","error","cancelled"): return d
        time.sleep(12)
    return {"status":"timeout"}

body = {
    "model": "google/veo-3.1-lite",
    "prompt": (
        "The coupe glass in this frame is completely empty and bone-dry. The teal-capped Conscious sparkling wine "
        "bottle beside it is lifted and pale sparkling wine is poured in one slow elegant stream into the empty dry "
        "coupe; the glass goes from completely empty to full with fine bubbles. Bright Panamanian brunch table with "
        "fruit, granola and mint, palm-garden bokeh. As the glass fills, three elegant Spanish label callouts fade in "
        "near the bottle: 'VEGANO', 'MENOS AZUCAR', and 'BAJAS CALORIAS' — clean minimal typography, one at a time. "
        "Keep the Conscious bottle, its label, and the glass steady and in focus. Premium low-calorie wine ad, "
        "shallow depth of field, bright fresh wellness mood."
    ),
    "aspect_ratio": "9:16",
    "duration": 8,
    "resolution": "720p",
    "frame_images": [{
        "frame_type": "first_frame",
        "type": "image_url",
        "image_url": {"url": f"{HG}/reel2_frame.jpg"},
    }],
}
req=urllib.request.Request("https://openrouter.ai/api/v1/videos", data=json.dumps(body).encode(),
    headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"}, method="POST")
with urllib.request.urlopen(req,timeout=90) as r: d0=json.loads(r.read().decode())
jid=d0.get("id"); print(f"REEL2v4 submit id={jid} status={d0.get('status')}",flush=True)
done=poll(jid,"REEL2v4") if jid else {"status":"noid"}
if done and done.get("status") in ("completed","succeeded","done"):
    dl=f"https://openrouter.ai/api/v1/videos/{jid}/content?index=0"
    rq=urllib.request.Request(dl,headers={"Authorization":f"Bearer {KEY}"})
    with urllib.request.urlopen(rq,timeout=120) as r:
        open(os.path.join(OUT,"reel2_conscious_ai_labels.mp4"),"wb").write(r.read())
    print("REEL2v4 saved",flush=True)
else:
    print(f"REEL2v4 not-done {done}",flush=True)
print("DONE_REEL2v4",flush=True)