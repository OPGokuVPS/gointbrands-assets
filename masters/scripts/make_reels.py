#!/usr/bin/env python3
"""Generate Reels 1 & 2 via OpenRouter Veo 3.1 Lite (image-to-video).
Reel 1 = Avinyó Petillant can (from opt_reel1/reel1_frame.png)
Reel 2 = Conscious Wines sparkling (from opt_reel2/reel2_frame.png)
Outputs .mp4 in /root/gointbrands_assets/opts/reels_out/reelN.mp4
"""
import json, urllib.request, base64, io, os, sys, time
from PIL import Image

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

def please_status(jobhdr, resp):
    print(f"{jobhdr} {resp.get('status')} {resp.get('message','')}"[:160], flush=True)

def poll_video(job_id, hdr="JOB", timeout=240):
    url = f"https://openrouter.ai/api/v1/videos/{job_id}"
    t0 = time.time()
    while time.time() - t0 < timeout:
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {KEY}"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                d = json.loads(r.read().decode())
        except Exception as e:
            time.sleep(8); continue
        st = d.get("status")
        print(f"{hdr} poll {st}", flush=True)
        if st in ("completed", "succeeded", "done"):
            return d
        if st in ("failed", "error", "cancelled"):
            return d
        if st == "pending":
            time.sleep(10)
        else:
            time.sleep(12)
    return {"status": "timeout", "id": job_id}

# --- Reel 1: Avinyó can ---
frame1 = "/root/gointbrands_assets/opt_reel1/reel1_frame.png"
if not os.path.exists(frame1):
    print("RESULT reel1 MISSING_FRAME", flush=True)
else:
    # host the frame (push to gointbrands-assets as reel1_frame.jpg) before submitting — Veo must fetch a public URL
    READY = "/tmp/hosted_reel1_ready"
    if not os.path.exists(READY):
        print("RESULT reel1 FRAME_NOT_HOSTED — push reel1_frame.jpg to gointbrands-assets first", flush=True)
    # host frame to a public URL: assumed pushed to gointbrands-assets as reel1_frame.jpg before this runs
    body1 = {
        "model": "google/veo-3.1-lite",
        "prompt": (
            "Close-up of an Avinyo Organic sparkling rose Petillant 250ml can on a teak bar at golden hour, "
            "light condensation running down the silver top. The can pops open with a soft hiss and a delicate "
            "spray of fine bubbles; a slow golden-hour tilt follows the pour of pale rose sparkling wine into a "
            "chilled coupe. Warm tropical Panamanian poolside with palm fronds swaying softly behind, bokeh. "
            "Cinematic, shallow depth of field, premium beverage ad. Realistic product movement. Keep the Avinyo "
            "can and label steady and in focus."
        ),
        "aspect_ratio": "9:16",
        "duration": 8,
        "resolution": "720p",
        "frame_images": [{
            "frame_type": "first_frame",
            "type": "image_url",
            "image_url": {"url": f"{HG}/reel1_frame.jpg"},
        }],
    }
    req = urllib.request.Request("https://openrouter.ai/api/v1/videos", data=json.dumps(body1).encode(),
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            d1 = json.loads(r.read().decode())
        jid1 = d1.get("id")
        print(f"REEL1 submit id={jid1} status={d1.get('status')}", flush=True)
        done1 = poll_video(jid1, "REEL1") if jid1 else None
        if done1 and done1.get("status") in ("completed","succeeded","done"):
            dl = f"https://openrouter.ai/api/v1/videos/{jid1}/content?index=0"
            rq = urllib.request.Request(dl, headers={"Authorization": f"Bearer {KEY}"})
            with urllib.request.urlopen(rq, timeout=120) as r:
                open(os.path.join(OUT, "reel1_avinyo_can.mp4"), "wb").write(r.read())
            print("REEL1 saved", flush=True)
        else:
            print(f"REEL1 not-done {done1}", flush=True)
    except Exception as e:
        print(f"REEL1 submit err {e}", flush=True)

print("DONE_REELS", flush=True)