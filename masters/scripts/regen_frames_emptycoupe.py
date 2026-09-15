#!/usr/bin/env python3
"""Regenerate Reel 1 + Reel 2 FIRST FRAMES with an EMPTY coupe glass (for the pour arc).
Reel 1 = Avinyó Petillant can + empty coupe, Panamanian poolside golden hour.
Reel 2 = Conscious sparkling bottle + empty coupe, healthy brunch table, Spanish chip overlays.
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

os.makedirs("/root/gointbrands_assets/opt_reel1", exist_ok=True)
os.makedirs("/root/gointbrands_assets/opt_reel2", exist_ok=True)

jobs = [
  ("reel1_frame", "/root/gointbrands_assets/avinyo/spark_rose.jpg", "/root/gointbrands_assets/opt_reel1/reel1_frame.png",
   "this exact 250ml Avinyo Organic sparkling rose (Petillant) can",
   "A tall slim can of Avinyo Petillant sparkling rose wine standing upright on a polished warm teak bar top, "
   "light condensation beading down the silver top rim. Next to it an EMPTY crystal coupe glass, bone dry, waiting to be filled. "
   "Behind: tropical Panamanian poolside at golden hour, calm turquoise pool, palm fronds, warm late sun low on the horizon, "
   "soft Caribbean coast haze. Warm tropical golden light, shallow depth of field, high-end editorial beverage photography. "
   "Reproduce the Avinyo Petillant label faithfully on the can. Vertical 9:16 composition, can and empty coupe centered. No added text."),
  ("reel2_frame", "/root/gointbrands_assets/conscious/sparkling.png", "/root/gointbrands_assets/opt_reel2/reel2_frame.png",
   "the exact Conscious low-calorie sparkling wine bottle (teal capsule, white 'CONSCIOUS' label)",
   "A tall clear-glass Champagne bottle of Conscious low-calorie sparkling wine with teal capsule and label reading "
   "'LOW CALORIE WINE', standing on a bright linen brunch table NEXT TO AN EMPTY coupe glass, bone dry, awaiting a pour. "
   "The table: fresh fruit (papaya, mango, berries), granola, mint, bright morning light, palm-garden bokeh behind. "
   "Clean fresh wellness aesthetic, shallow depth of field, premium low-calorie wine ad. "
   "Reproduce the Conscious teal label and the vegan mark faithfully. Vertical 9:16, bottle and empty coupe centered. No added text."),
]

for slug, src, out, desc, prompt in jobs:
    b64 = to_b64(src)
    body = {"model": "bytedance-seed/seedream-5-0-pro", "prompt": f"Photograph {desc}: {prompt}",
            "n": 1, "aspect_ratio": "9:16", "resolution": "2K",
            "input_references": [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]}
    st, resp = post("images", body)
    ok = False
    if st == 200:
        d = resp.get("data", [])
        if d and d[0].get("b64_json"):
            open(out, "wb").write(base64.b64decode(d[0]["b64_json"])); ok = True
    print(f"RESULT {slug} status={st} saved={ok} cost={resp.get('usage',{}).get('cost')} err={resp.get('err')}", flush=True)
print("DONE_FRAMES_EMPTYCOUPE", flush=True)