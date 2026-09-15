#!/usr/bin/env python3
"""Regenerate Reel 2 first frame: UNMISTAKABLY EMPTY dry coupe + Conscious bottle. 9:16.
The pour and the Spanish labels are left to Veo (per user: use AI labels, not burn-ins).
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
out = "/root/gointbrands_assets/opt_reel2/reel2_frame.png"

prompt = (
    "Photograph this exact Conscious low-calorie sparkling wine bottle with an EMPTY coupe glass that is completely "
    "dry: the glass is bone dry with no liquid, no drops, no moisture, no wine inside, completely empty and waiting "
    "to be filled. The clear glass coupe sits beside the bottle on a bright linen brunch table with fresh fruit "
    "(papaya, berries), granola and mint. Bright morning light, palm-garden bokeh. The glass interior is "
    "absolutely empty and clean. Reproduce the Conscious teal label faithfully. Vertical 9:16, bottle and empty "
    "dry coupe centered. No text, no chips, no overlays."
)
body = {"model": "bytedance-seed/seedream-5-0-pro", "prompt": prompt, "n": 1,
        "aspect_ratio": "9:16", "resolution": "2K",
        "input_references": [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{to_b64(BOT)}"}}]}
st, resp = post("images", body)
ok = False
if st == 200:
    d = resp.get("data", [])
    if d and d[0].get("b64_json"):
        open(out, "wb").write(base64.b64decode(d[0]["b64_json"])); ok = True
print(f"RESULT reel2_frame status={st} saved={ok} cost={resp.get('usage',{}).get('cost')} err={resp.get('err')}", flush=True)
print("DONE_EMPTYFRAME_R2", flush=True)