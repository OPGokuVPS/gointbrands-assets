#!/usr/bin/env python3
"""Reel 2 — Conscious Wines sparkling, FIRST-FRAME scene (9:16, 1080x1920) for Veo 3.1 Lite.
Real Conscious sparkling bottle (sparkling.png) via Seedream image-edit; healthy tropical table,
vegan/low-calorie angle highlighted. Output: /root/gointbrands_assets/opt_reel2/reel2_frame.png
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

BOT = "/root/gointbrands_assets/conscious/sparkling.png"
os.makedirs("/root/gointbrands_assets/opt_reel2", exist_ok=True)

slug = "reel2_frame"
BOT_B64 = to_b64(BOT)
prompt = (
    "Photograph this exact Conscious low-calorie sparkling wine bottle: a tall clear-glass Champagne bottle "
    "with teal capsule and the white 'CONSCIOUS' label reading 'LOW CALORIE WINE', 'MADE WITH ORGANIC GRAPES', "
    "'91 CALORIES PER 250ML', and 'VEGAN', standing on a bright linen table beside a coupe of pale sparkling wine. "
    "The table is a light, healthy Panamanian brunch setting: fresh fruit (papaya, mango, berries), a small bowl "
    "of granola, mint sprigs, in bright airy morning light with soft palm-garden bokeh behind. "
    "Clean, bright, fresh wellness aesthetic, shallow depth of field, high-end editorial food-and-beverage photography. "
    "Reproduce the Conscious label faithfully including the teal band and the 'VEGAN' and calorie text. "
    "Vertical 9:16 composition, bottle centered. No added text."
)
body = {
    "model": "bytedance-seed/seedream-5-0-pro",
    "prompt": prompt,
    "n": 1,
    "aspect_ratio": "9:16",
    "resolution": "2K",
    "input_references": [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{BOT_B64}"}}],
}
st, resp = post("images", body)
ok = False
if st == 200:
    d = resp.get("data", [])
    if d and d[0].get("b64_json"):
        open("/root/gointbrands_assets/opt_reel2/{0}.png".format(slug), "wb").write(base64.b64decode(d[0]["b64_json"]))
        ok = True
print(f"RESULT {slug} status={st} saved={ok} cost={resp.get('usage',{}).get('cost')} err={resp.get('err')}", flush=True)
print("DONE_REEL2_FRAME", flush=True)