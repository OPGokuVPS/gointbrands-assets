#!/usr/bin/env python3
"""Reel 2 v8 - NO AI overlay text (burn-in will add crisp Spanish chips).
Same empty opening, single bottle + hand pour. Larger, sharper bottle. 1080p 8s."""
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

def poll(job_id, hdr, timeout=300):
    t0=time.time()
    while time.time()-t0 < timeout:
        try:
            req=urllib.request.Request(f"https://openrouter.ai/api/v1/videos/{job_id}", headers={"Authorization":f"Bearer {KEY}"})
            with urllib.request.urlopen(req,timeout=60) as r: d=json.loads(r.read().decode())
        except Exception:
            time.sleep(10); continue
        st=d.get("status"); print(f"{hdr} poll {st}",flush=True)
        if st in ("completed","succeeded","done","failed","error","cancelled"): return d
        time.sleep(12)
    return {"status":"timeout"}

def submit(outname, frame, prompt):
    body = {"model":"google/veo-3.1-lite","prompt":prompt,"aspect_ratio":"9:16",
            "duration":8,"resolution":"1080p",
            "frame_images":[{"frame_type":"first_frame","type":"image_url","image_url":{"url":f"{HG}/{frame}"}}]}
    req=urllib.request.Request("https://openrouter.ai/api/v1/videos", data=json.dumps(body).encode(),
        headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req,timeout=90) as r: d0=json.loads(r.read().decode())
    except Exception as e:
        print(f"{outname} SUBMIT_ERR {e}",flush=True); return
    jid=d0.get("id"); print(f"{outname} submit id={jid} status={d0.get('status')}",flush=True)
    done=poll(jid,outname,300) if jid else {"status":"noid"}
    if done and done.get("status") in ("completed","succeeded","done"):
        dl=f"https://openrouter.ai/api/v1/videos/{jid}/content?index=0"
        rq=urllib.request.Request(dl,headers={"Authorization":f"Bearer {KEY}"})
        with urllib.request.urlopen(rq,timeout=150) as r:
            open(os.path.join(OUT,outname),"wb").write(r.read())
        print(f"{outname} saved",flush=True)
    else:
        print(f"{outname} not-done {done}",flush=True)

submit("reel2_conscious_raw.mp4","reel2_frame.jpg",
    "A bright Panamanian brunch table with an empty dry coupe glass on a beige linen tablecloth, a white plate of "
    "fresh fruit (papaya, blueberries, raspberries), granola and mint, palm-garden bokeh behind. No wine bottle is "
    "on the table at the start. A natural, realistic human hand and a single Conscious low-calorie sparkling wine "
    "bottle (teal capsule, clean white CONSCIOUS label) enter together from the right; the hand tilts the bottle "
    "and pours a slow elegant stream of pale sparkling wine into the empty coupe, filling it from empty to full "
    "with fine bubbles. The bottle is sharply in focus and fills a prominent part of the frame so its clean label "
    "is crisp and legible. Only this one bottle appears, held by the hand - no second bottle, and no bottle ever "
    "stands on the table. No text overlays, no captions, no labels on screen, no chips - keep the scene clean. "
    "Keep the bottle, hand and glass in sharp focus. Bright fresh wellness mood, shallow depth of field. Audio: "
    "relaxed instrumental music and gentle wine pouring and fizz. No voices, no speech.")

print("DONE_V8_RAW", flush=True)