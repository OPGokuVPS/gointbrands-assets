#!/usr/bin/env python3
"""Final Reels — pour into empty glass + SPANISH overlays.
Reel 1 = Avinyó Petillant can, empty coupe gets the pour, poolside golden hour.
Reel 2 = Conscious sparkling, empty coupe gets the pour + Spanish chips VEGANO/MENOS AZÚCAR/BAJAS CALORÍAS.
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

# Reel 1: Avinyó can -> empty glass filled by the pour
submit("reel1_avinyo_can.mp4","reel1_frame.jpg",
    "Close-up: an Avinyo Organic sparkling rose Petillant 250ml can and a bone-dry empty crystal coupe on a teak bar "
    "at golden hour, tropical Panamanian poolside with palm fronds behind. The can is tilted and sparkling rose is "
    "poured in a slow, elegant stream into the empty coupe; the glass fills with fine bubbling rose, condensation runs "
    "down the can. Warm golden-hour light, shallow depth of field, premium beverage ad. Keep the Avinyo can, label and "
    "glass steady and in focus. No text.")

# Reel 2: Conscious -> empty glass filled + Spanish overlays
submit("reel2_conscious.mp4","reel2_frame.jpg",
    "Slow elegant shot: a teal-capped Conscious low-calorie wine bottle beside a bone-dry empty coupe on a bright "
    "Panamanian brunch table with fruit, granola and mint. Pale sparkling wine is poured in a gentle stream into the "
    "empty coupe as it fills with fine bubbles. Softy blurred translucent Spanish callout chips fade up around the "
    "bottle reading 'VEGANO', 'MENOS AZUCAR' and 'BAJAS CALORIAS'. Clean bright wellness aesthetic, shallow depth of "
    "field, premium low-calorie wine ad. Keep the Conscious bottle, label and glass steady. Spanish text only.")

print("DONE_FINAL_REELS", flush=True)