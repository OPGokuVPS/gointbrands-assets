#!/usr/bin/env python3
"""Reel 2 v7B - empty opening (bottle appears with hand) + Reel 1 v4B (hand LEFT, proper grip, pour).
Veo 3.1 Lite, 1080p, 8s. Reel2 first frame is now HOSTED EMPTY (no bottle)."""
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

# Reel 1: hand LEFT, secure grip, ACTUAL pour stream
submit("reel1_avinyo_can.mp4","reel1_frame.jpg",
    "A natural human hand enters from the LEFT side of the frame and firmly grips a chilled silver-white Avinyo "
    "Petillant sparkling rose 250ml can to pour it. The hand holds the can securely from the left with a "
    "realistic full grip - thumb wrapped over the front, fingers around the body - and smoothly tilts it so a "
    "visible, continuous slow stream of sparkling rose pours from the can opening into an empty coupe glass on "
    "the right side of the frame. The coupe fills from empty to full with fine bubbles. The can is open and "
    "clearly pouring a stream into the glass. The hand stays on the left of the screen the whole time, holding "
    "the can naturally like a real person. Teak bar at golden hour, tropical Panamanian poolside with palms "
    "behind. Keep the can, its label, the hand, the stream and the glass in focus. Premium beverage ad, warm "
    "golden light. Audio: can opening, wine pour and soft fizz over light tropical instrumental. No voices.")

# Reel 2: EMPTY opening (hosted empty frame) -> single bottle + hand appear together and pour
submit("reel2_conscious_ai_labels.mp4","reel2_frame.jpg",
    "The scene begins with the empty dry coupe glass and fruit brunch table with NO wine bottle present - the "
    "glass is empty and clean. Moments later a natural hand and a single Conscious low-calorie sparkling wine "
    "bottle (teal capsule, white CONSCIOUS label) enter together from the right side of the frame. The hand "
    "holds the one bottle and tilts it to pour a slow elegant stream of pale sparkling wine into the empty "
    "coupe, filling it from empty to full with fine bubbles. Only this one bottle appears, held by the hand - "
    "no second bottle, and no bottle ever stands or sits on the table. As the glass fills, three clean Spanish "
    "label callouts fade in near the bottle one at a time: 'VEGANO', 'BAJO EN CALORIAS', 'BAJO EN AZUCAR'. Keep "
    "the bottle, hand, labels and glass in focus. Bright fresh wellness brunch mood, palm-garden bokeh, shallow "
    "depth of field. Audio: relaxed instrumental music and gentle wine pouring and fizz. No voices, no speech.")

print("DONE_V7B", flush=True)