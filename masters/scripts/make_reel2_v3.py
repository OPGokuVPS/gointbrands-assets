#!/usr/bin/env python3
"""Reel 2 v3 — Conscious Wines: strict EMPTY glass -> pour from the Conscious bottle -> fills.
Explicitly NO on-screen text (the Spanish chips are burned in AFTER via ffmpeg to avoid duplication).
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
        req=urllib.request.Request(f"https://openrouter.ai/api/v1/videos/{job_id}", headers={"Authorization":f"Bearer {KEY}"})
        try:
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
        "A bone-dry completely empty crystal coupe glass sits on a bright Panamanian brunch table beside a teal-capped "
        "Conscious sparkling wine bottle (white CONSCIOUS label). Fresh fruit, granola and mint around. The camera is "
        "still as the Conscious bottle is lifted and pale sparkling wine is poured in one slow elegant stream into the "
        "empty coupe; the glass fills from completely empty to full with fine bubbles. Keep the Conscious bottle label "
        "and glass steady and in focus. NO text, NO words, NO labels, NO captions, NO on-screen graphics anywhere — "
        "the scene must have zero inscribed lettering. Clean bright wellness aesthetic, shallow depth of field, "
        "premium low-calorie wine ad."
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
jid=d0.get("id"); print(f"REEL2v3 submit id={jid} status={d0.get('status')}",flush=True)
done=poll(jid,"REEL2v3") if jid else {"status":"noid"}
if done and done.get("status") in ("completed","succeeded","done"):
    dl=f"https://openrouter.ai/api/v1/videos/{jid}/content?index=0"
    rq=urllib.request.Request(dl,headers={"Authorization":f"Bearer {KEY}"})
    with urllib.request.urlopen(rq,timeout=120) as r:
        open(os.path.join(OUT,"reel2_conscious_clean.mp4"),"wb").write(r.read())
    print("REEL2v3 saved",flush=True)
else:
    print(f"REEL2v3 not-done {done}",flush=True)
print("DONE_REEL2v3",flush=True)