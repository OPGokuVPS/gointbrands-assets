#!/usr/bin/env python3
"""Reel 1 — Avinyó Petillant 250ml can, FIRST-FRAME scene (9:16, 1080x1920) for Veo 3.1 Lite.
Real can photo (spark_rose.jpg) input via Seedream image-edit; tropical Panamanian bar/pool golden hour.
Output: /root/gointbrands_assets/opt_reel1/reel1_frame.png
"""
import json, urllib.request, base64, io, os, sys
from PIL import Image

KEY = None
with open("/root/.hermes/.env") as fh:
    for line in fh:
        if line.startswith("OPENROUTER_API_KEY="):
            KEY = line.split("=", 1)[1].strip().strip('"').strip("'")
            break
if not KEY:
    print("RESULT NO_API_KEY", flush=True); sys.exit(1)

def post(path, body):
    req = urllib.request.Request(f"https://openrouter.ai/api/v1/{path}", data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=280) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")
    except Exception as e:
        return -1, {"err": str(e)}

def to_b64(path, maxdim=900):
    im = Image.open(path).convert("RGB"); im.thumbnail((maxdim, maxdim))
    b = io.BytesIO(); im.save(b, "JPEG", quality=93)
    return base64.b64encode(b.getvalue()).decode()

CAN = "/root/gointbrands_assets/avinyo/spark_rose.jpg"
os.makedirs("/root/gointbrands_assets/opt_reel1", exist_ok=True)

slug = "reel1_frame"
CAN_B64 = to_b64(CAN)
prompt = (
    "Photograph this exact 250ml Avinyo Organic sparkling rose (Petillant) can: "
    "a tall slim can of Avinyo Petillant sparkling rose wine standing upright on a polished warm teak bar top, "
    "light condensation beading down the silver top rim. Behind it, a tropical Panamanian poolside at golden hour: "
    "calm turquoise pool, palm fronds, warm late sun low on the horizon, soft Caribbean coast haze. "
    "A single chilled crystal coupe of pale rose sparkling wine catching the light beside the can. "
    "Warm tropical golden light, shallow depth of field, high-end editorial beverage photography. "
    "Reproduce the Avinyo Petillant label faithfully on the can. Vertical 9:16 composition, can centered. No added text."
)
body = {
    "model": "bytedance-seed/seedream-5-0-pro",
    "prompt": prompt,
    "n": 1,
    "aspect_ratio": "9:16",
    "resolution": "2K",
    "input_references": [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{CAN_B64}"}}],
}
st, resp = post("images", body)
ok = False
if st == 200:
    d = resp.get("data", [])
    if d and d[0].get("b64_json"):
        open("/root/gointbrands_assets/opt_reel1/{0}.png".format(slug), "wb").write(base64.b64decode(d[0]["b64_json"]))
        ok = True
print(f"RESULT {slug} status={st} saved={ok} cost={resp.get('usage',{}).get('cost')} err={resp.get('err')}", flush=True)
print("DONE_REEL1_FRAME", flush=True)