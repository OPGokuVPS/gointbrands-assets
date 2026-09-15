#!/usr/bin/env python3
"""Reel 1 v2 — Avinyó Petillant can: NO awkward hand grab (or any hand), clean gold-high can pour.
Reel 2 v4b — Conscious: single bottle pours (no duplicate on table), POUR+SOFT MUSIC, NO VOICE.
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

# Reel 1 v2: no hand; the can sits and pours on its own / tilted naturally by weight, clean golden pour
submit("reel1_avinyo_can.mp4","reel1_frame.jpg",
    "A chilled silver-and-white Avinyo Petillant sparkling rose 250ml can rests on a polished teak bar top at golden "
    "hour, tropical Panamanian poolside with palm fronds behind. NO hands anywhere. The can gently tilts on its own "
    "and pours a slow elegant stream of sparkling rose into a clean empty coupe glass beside it; the glass fills "
    "from empty to full with fine bubbles. Warm golden-hour light, shallow depth of field, premium beverage ad. "
    "Keep the Avinyo can, label and glass steady and in focus. Natural realistic motion, high-end advertising. "
    "Only the sound of the can opening and wine pouring, soft relaxed tropical music. No voices, no dialogue.")

# Reel 2 v4b: single Conscious bottle, no duplicate; pour + music + pour sound, NO voice
submit("reel2_conscious_ai_labels.mp4","reel2_frame.jpg",
    "A single teal-capped Conscious sparkling wine bottle stands on a bright Panamanian brunch table next to a "
    "completely empty bone-dry coupe glass, fruit, granola and mint, palm-garden bokeh. The SAME bottle — the only "
    "bottle — is lifted and pale sparkling wine is poured in one slow stream into the empty coupe, filling it with fine "
    "bubbles. There is NO second bottle left on the table; only the one being poured, then it is set back beside the "
    "now-full glass. As it pours, three Spanish label callouts fade in near the bottle one at a time: 'VEGANO', "
    "'MENOS AZUCAR', 'BAJAS CALORIAS'. Keep the Conscious bottle and glass steady and in focus. Bright fresh wellness "
    "mood, shallow depth of field. Audio: relaxed instrumental music and the sound of wine pouring. No voices, no "
    "dialogue, no voiceover.")

print("SUBMITTING", flush=True)