#!/usr/bin/env python3
"""Reel 1 v3 + Reel 2 v5 — tight-framed pours (NO hand in shot), Veo-generated audio (music+pour, no voice).
Reel 1: Avinyó can pouring into coupe, crop so no hand visible.
Reel 2: single Conscious bottle pours into empty coupe, no duplicate, Spanish chips omitted (use caption).
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

def submit(outname, frame, prompt):
    body = {"model":"google/veo-3.1-lite","prompt":prompt,"aspect_ratio":"9:16",
            "duration":8,"resolution":"720p",
            "frame_images":[{"frame_type":"first_frame","type":"image_url","image_url":{"url":f"{HG}/{frame}"}}]}
    req=urllib.request.Request("https://openrouter.ai/api/v1/videos", data=json.dumps(body).encode(),
        headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"}, method="POST")
    with urllib.request.urlopen(req,timeout=90) as r: d0=json.loads(r.read().decode())
    jid=d0.get("id"); print(f"{outname} submit id={jid} status={d0.get('status')}",flush=True)
    done=poll(jid,outname) if jid else {"status":"noid"}
    if done and done.get("status") in ("completed","succeeded","done"):
        dl=f"https://openrouter.ai/api/v1/videos/{jid}/content?index=0"
        rq=urllib.request.Request(dl,headers={"Authorization":f"Bearer {KEY}"})
        with urllib.request.urlopen(rq,timeout=120) as r:
            open(os.path.join(OUT,outname),"wb").write(r.read())
        print(f"{outname} saved",flush=True)
    else:
        print(f"{outname} not-done {done}",flush=True)

# Reel 1 v3: TIGHT FRAME on can + coupe only, product pours itself, NO hand/skin/human anywhere
submit("reel1_avinyo_can.mp4","reel1_frame.jpg",
    "Ultra-close macro shot showing ONLY the chilled silver-and-white Avinyo Petillant sparkling rose 250ml can and a "
    "clean empty coupe glass on a teak bar top, tropical Panamanian poolside golden hour bokeh behind. NO hands, NO "
    "people, NO skin, NO human body parts anywhere in frame. The can very gently tips forward on its own and pours a "
    "slow elegant stream of sparkling rose into the empty coupe, filling it from empty to full with fine bubbles and a "
    "delicate foam. Condensation runs down the can. Keep the Avinyo can, its label and the glass steady and in focus. "
    "Natural realistic product motion, premium advertising. Audio: only the sound of the can being opened, the soft "
    "fizz and the wine pouring, over a light relaxing tropical instrumental. No voices, no speech, no dialogue.")

# Reel 2 v5: single bottle, tight pour into empty coupe, NO duplicate, NO on-screen text
submit("reel2_conscious_ai_labels.mp4","reel2_frame.jpg",
    "Tight close-up of ONE single Conscious sparkling wine bottle (teal capsule, white CONSCIOUS label) beside a "
    "completely empty bone-dry coupe glass on a bright Panamanian brunch table with fruit, granola and mint, "
    "palm-garden bokeh. The one and only bottle is tilted and pours pale sparkling wine in one slow stream into the "
    "empty coupe, filling it with fine bubbles. NO second bottle, NO duplicate, NO other bottle on the table. NO hands, "
    "NO people, NO text, NO captions, NO on-screen graphics anywhere. Keep the bottle, label and glass steady and in "
    "focus. Bright fresh wellness mood, shallow depth of field. Audio: relaxed soft instrumental music and the gentle "
    "sound of wine pouring and fizz. No voices, no speech, no dialogue.")

print("DONE_V6", flush=True)