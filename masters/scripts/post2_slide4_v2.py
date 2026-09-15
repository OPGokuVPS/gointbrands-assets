#!/usr/bin/env python3
"""Regenerate slide4_close: pairing scene WITHOUT an open can - closed Comodoro tin + Avinyo bottle + cava flute."""
import re, json, urllib.request, base64, io, os
from PIL import Image

import os
# Resolve OpenRouter key at runtime from the canonical secrets file (never hardcode/log).
def _load_key():
    for cand in ("/root/.hermes/.env", "/root/.hermes/cache/terminal/hermes-snap-5dc9dfc8e660.sh"):
        try:
            with open(cand, errors="ignore") as fh: txt=fh.read()
            m = re.search(r'OPENROUTER_API_KEY[=:"\s]*([A-Za-z0-9_\-]+)', txt)
            if m: return m.group(1)
        except FileNotFoundError: continue
    raise RuntimeError("OPENROUTER_API_KEY not found")
KEY = _load_key()

def post(path, body):
    req=urllib.request.Request(f"https://openrouter.ai/api/v1/{path}",data=json.dumps(body).encode(),
        headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"},method="POST")
    try:
        with urllib.request.urlopen(req,timeout=240) as r: return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e: return e.code, json.loads(e.read().decode() or "{}")
    except Exception as e: return -1, {"err":str(e)}

def to_b64(path, maxdim=800):
    im=Image.open(path).convert("RGB"); im.thumbnail((maxdim,maxdim))
    b=io.BytesIO(); im.save(b,"JPEG",quality=93); return base64.b64encode(b.getvalue()).decode()

os.makedirs("/root/gointbrands_assets/opt2/post2", exist_ok=True)

refs = [f"/tmp/gointbrands-assets/{p}" for p in ["mejillones_gallega_cut.png","brut_reserva_cut.png"]]
refs_b64 = [{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{to_b64(p)}"}} for p in refs]

prompt=("Photograph this exact closed tin of Comodoro mejillones a la gallega (lid ON, unopened) together with a bottle of "
        "Avinyo cava and a crystal flute of chilled sparkling cava with fine bubbles, arranged on a warm cream linen table. "
        "The closed tin and the cava bottle stand side by side as the perfect Spanish pairing, with the flute in front. "
        "Scatter green olives, lemon wedges, crusty bread, and white daisies around. Warm golden-hour Mediterranean sunlight, "
        "shallow depth of field, high-end editorial food photography. Real product labels only, no added text, no open cans.")
body={"model":"bytedance-seed/seedream-5-0-pro","prompt":prompt,
      "n":1,"aspect_ratio":"4:5","resolution":"2K","input_references":refs_b64}
st,resp=post("images",body)
ok=False
if st==200:
    d=resp.get("data",[])
    if d and d[0].get("b64_json"):
        open("/root/gointbrands_assets/opt2/post2/slide4_close.png","wb").write(base64.b64decode(d[0]["b64_json"])); ok=True
print(f"RESULT s4_close status={st} saved={ok} cost={resp.get('usage',{}).get('cost')} err={resp.get('err')}", flush=True)
print("DONE", flush=True)