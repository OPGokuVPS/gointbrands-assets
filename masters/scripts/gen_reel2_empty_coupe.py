#!/usr/bin/env python3
"""Generate a TRUE empty Reel 2 first frame: NO bottle in shot, only empty dry coupe + fruit brunch table.
No Conscious bottle anywhere. Used as Veo first frame so the video opens bottle-free and the
bottle+hand appear together to pour.
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

out = "/root/gointbrands_assets/opt_reel2/reel2_frame_EMPTY.png"
prompt = (
    "Photograph an empty clean bone-dry coupe champagne glass standing on a bright beige linen brunch table "
    "at a sunny Panamanian garden. Beside the glass is a white plate of fresh fruit (papaya slices, blueberries, "
    "raspberries), granola and a mint sprig, with a few crumbs on the cloth. In the background: blurred palm "
    "fronds, green garden foliage and warm morning sunlight bokeh. The coupe glass is completely empty and dry — "
    "no liquid, no wine, no bottle anywhere in the photo. THERE IS NO WINE BOTTLE IN THIS SCENE AT ALL. Only the "
    "empty glass, the plate of fruit and the garden table. Clean, bright, fresh wellness brunch mood. Shallow "
    "depth of field. Vertical 9:16, the empty coupe glass centered. No text, no chips, no overlays, no products."
)
body = {"model": "bytedance-seed/seedream-5-0-pro", "prompt": prompt, "n": 1,
        "aspect_ratio": "9:16", "resolution": "2K"}
st, resp = post("images", body)
ok = False
if st == 200:
    d = resp.get("data", [])
    if d and d[0].get("b64_json"):
        open(out, "wb").write(base64.b64decode(d[0]["b64_json"])); ok = True
print(f"RESULT empty_frame status={st} saved={ok} err={resp.get('err')}", flush=True)
print("DONE_EMPTYFRAME2", flush=True)