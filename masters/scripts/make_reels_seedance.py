#!/usr/bin/env python3
"""Attempt bytedance/seedance-2.0-mini for both reels (OpenRouter), from hosted first frames.
Reel 1: Avinyó can -> pour into empty coupe, NO hands, keep audio music+pour.
Reel 2: ONE Conscious bottle -> pours into empty coupe, NO duplicate, no on-screen text.
Duration 8, 9:16, 720p, audio true (seedance supports audio).
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
MODEL = "bytedance/seedance-2.0-mini"

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
        time.sleep(14)
    return {"status":"timeout"}

def submit(outname, frame, prompt):
    body = {"model":MODEL,"prompt":prompt,"aspect_ratio":"9:16",
            "duration":8,"resolution":"720p","generate_audio":True,
            "frame_images":[{"frame_type":"first_frame","type":"image_url","image_url":{"url":f"{HG}/{frame}"}}]}
    req=urllib.request.Request("https://openrouter.ai/api/v1/videos", data=json.dumps(body).encode(),
        headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req,timeout=90) as r: d0=json.loads(r.read().decode())
    except Exception as e:
        print(f"{outname} SUBMIT_ERR {e}",flush=True)
        try:
            print((e.read() or b'').decode()[:600])
        except Exception:
            pass
        return
    jid=d0.get("id"); print(f"{outname} submit id={jid} status={d0.get('status')} err={d0.get('error',{}).get('message') if isinstance(d0.get('error'),dict) else d0.get('error')}",flush=True)
    done=poll(jid,outname) if jid else {"status":"noid"}
    if done and done.get("status") in ("completed","succeeded","done"):
        dl=f"https://openrouter.ai/api/v1/videos/{jid}/content?index=0"
        rq=urllib.request.Request(dl,headers={"Authorization":f"Bearer {KEY}"})
        with urllib.request.urlopen(rq,timeout=150) as r:
            open(os.path.join(OUT,outname),"wb").write(r.read())
        print(f"{outname} saved",flush=True)
    else:
        print(f"{outname} not-done {done}",flush=True)

# Reel 1 — Avinyó can pour, no hands
submit("reel1_avinyo_can.mp4","reel1_frame.jpg",
    "A chilled silver-and-white Avinyo Petillant sparkling rose 250ml can pours its sparkling rose into a clear dry "
    "coupe glass on a teak bar at golden hour, tropical Panamanian poolside with palm fronds. The can tilts on its "
    "own and pours a slow stream; the glass fills from empty to full with fine bubbles. NO hands, NO people, NO skin "
    "anywhere in the frame; the can moves naturally without being held. Audio: the soft sound of the can opening, the "
    "wine fizz and pouring, over light relaxed tropical instrumental. No voices, no speech.")

# Reel 2 — ONE Conscious bottle pours, no duplicate, no text
submit("reel2_conscious_ai_labels.mp4","reel2_frame.jpg",
    "ONE single Conscious low-calorie sparkling wine bottle (teal capsule, white CONSCIOUS label) tipped to pour pale "
    "sparkling wine into a completely empty dry coupe glass on a bright Panamanian brunch table with fruit, granola "
    "and mint, palm-garden bokeh. The only bottle pours; it fills the glass from empty to full with fine bubbles. NO "
    "second bottle anywhere, NO other bottle on the table, NO hands, NO people, NO text, NO captions, NO on-screen "
    "graphics. Audio: relaxed soft instrumental music and the gentle sound of wine pouring and fizz. No voices.")

print("DONE_SEEDANCE", flush=True)