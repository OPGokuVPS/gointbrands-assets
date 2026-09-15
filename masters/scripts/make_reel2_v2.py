#!/usr/bin/env python3
"""Reel 2 v2 — Conscious Wines, Veo 3.1 Lite, 8s, generic 'LOW CALORIES' messaging (no numeric claim).
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

def poll(job_id, hdr, timeout=240):
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
        "Slow elegant tilt over a bright morning table in Panama: a teal-capped Conscious low-calorie sparkling wine "
        "bottle with the clean white CONSCIOUS label. A coupe of pale sparkling wine catches soft sunlight beside it, "
        "with fresh fruit (papaya, mango, berries), granola and mint on light linen. The camera gently zooms in on "
        "the bottle as softly blurred translucent callout chips fade up around it reading 'VEGAN', 'LESS SUGAR' "
        "and 'LOW CALORIES'. Clean bright wellness aesthetic, shallow depth of field, premium low-calorie wine ad. "
        "Keep the Conscious bottle and label steady, sharp and in focus."
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
jid=d0.get("id"); print(f"REEL2v2 submit id={jid} status={d0.get('status')}",flush=True)
done=poll(jid,"REEL2v2") if jid else {"status":"noid"}
if done and done.get("status") in ("completed","succeeded","done"):
    dl=f"https://openrouter.ai/api/v1/videos/{jid}/content?index=0"
    rq=urllib.request.Request(dl,headers={"Authorization":f"Bearer {KEY}"})
    with urllib.request.urlopen(rq,timeout=120) as r:
        open(os.path.join(OUT,"reel2_conscious.mp4"),"wb").write(r.read())
    print("REEL2v2 saved",flush=True)
else:
    print(f"REEL2v2 not-done {done}",flush=True)
print("DONE_REEL2v2",flush=True)