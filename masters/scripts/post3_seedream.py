#!/usr/bin/env python3
"""POST 3 (Avinyó Brand Spotlight) editorial slides via Seedream 5.0 Pro image-edit.
Restyles REAL Avinyó product photos into the approved Mediterranean editorial look
(golden light, linen, daisies) matching POST 1/2. 4 slides per draft outline.
"""
import re, json, urllib.request, base64, io, os
from PIL import Image

# Load OPENROUTER_API_KEY from .env at runtime (never hardcode/log).
KEY = None
with open("/root/.hermes/.env") as fh:
    for line in fh:
        if line.startswith("OPENROUTER_API_KEY="):
            KEY = line.split("=", 1)[1].strip().strip('"').strip("'")
            break
if not KEY:
    print("RESULT NO_API_KEY", flush=True); raise SystemExit(1)

def post(path, body):
    req=urllib.request.Request(f"https://openrouter.ai/api/v1/{path}", data=json.dumps(body).encode(),
        headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=270) as r: return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e: return e.code, json.loads(e.read().decode() or "{}")
    except Exception as e: return -1, {"err":str(e)}

def to_b64(path, maxdim=800):
    im=Image.open(path).convert("RGB"); im.thumbnail((maxdim,maxdim))
    b=io.BytesIO(); im.save(b,"JPEG",quality=93); return base64.b64encode(b.getvalue()).decode()

AVINYO="/root/gointbrands_assets/avinyo"
os.makedirs("/root/gointbrands_assets/opt3", exist_ok=True)

# (slug, outfile, [input ref photos], reference description, scene prompt)
jobs = [
  ("s1_hook", "p3_slide1_hook.png", ["brut_nature.jpg"],
   "a bottle of Avinyo cava Brut Nature",
   "A bottle of Avinyo cava Brut Nature standing on a warm cream linen table beside a crystal flute of sparkling cava filled with fine bubbles, the cork and foil on the table. Behind it, a soft-focus organic vineyard at golden hour. Scatter white daisies and green grapes around the base. Warm golden-hour Mediterranean sunlight, shallow depth of field, high-end editorial beverage photography. Reproduce the Avinyo label faithfully. No added text."),
  ("s2_heritage", "p3_slide2_heritage.png", ["brut_reserva.jpg"],
   "a bottle of Avinyo cava Brut Reserva",
   "A bottle of Avinyo cava Brut Reserva standing on a rustic wooden crate in the foreground of an organic Catalan vineyard at golden hour, long neat rows of vines stretching into the warm light, a soft haze. The same family's land, generations cultivated. Cinematic high-end editorial photography, shallow depth of field, warm Mediterranean light. Reproduce the Avinyo label faithfully. No added text."),
  ("s3_range", "p3_slide3_range.png", ["brut_nature.jpg","brut_reserva.jpg","gran_reserva.jpg","blanc_de_noris.jpg","rose_sublima.jpg"],
   "five bottles of Avinyo cava (Brut Nature, Brut Reserva, Gran Reserva, Blanc de Noirs, Rose Sublim)",
   "Five bottles of Avinyo cava lined up on a warm cream linen table, labels facing the camera, from left to right: Brut Nature, Brut Reserva, Gran Reserva, Blanc de Noirs, Rose Sublim. A crystal flute of sparkling cava at the far end of the line. Scattered white daisies and green grapes along the base. Warm golden-hour Mediterranean sunlight, shallow depth of field, high-end editorial beverage photography. Reproduce each Avinyo label faithfully. No added text."),
  ("s4_close", "p3_slide4_close.png", ["brut_reserva.jpg"],
   "a bottle of Avinyo cava Brut Reserva",
   "Two crystal flutes of chilled cava toasting over a table set for a brindis, a bottle of Avinyo cava Brut Reserva on a warm cream linen table between them, fine bubbles rising in the glasses. Scattered white daisies and green grapes. Warm golden-hour Mediterranean sunlight, shallow depth of field, high-end editorial celebration photography. Reproduce the Avinyo label faithfully. No added text."),
]

for slug, out, refs, desc, prompt in jobs:
    refs_b64=[]
    for rp in refs:
        p=os.path.join(AVINYO, rp)
        if not os.path.exists(p):
            print(f"RESULT {slug} MISSING_REF={rp}", flush=True); continue
        refs_b64.append({"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{to_b64(p)}"}})
    if not refs_b64:
        print(f"RESULT {slug} NO_REFS", flush=True); continue
    body={"model":"bytedance-seed/seedream-5-0-pro",
      "prompt":f"Photograph this exact {desc}: {prompt}",
      "n":1,"aspect_ratio":"4:5","resolution":"2K",
      "input_references":refs_b64}
    st,resp=post("images",body)
    ok=False
    if st==200:
        d=resp.get("data",[])
        if d and d[0].get("b64_json"):
            open(f"/root/gointbrands_assets/opt3/{out}","wb").write(base64.b64decode(d[0]["b64_json"])); ok=True
    print(f"RESULT {slug} status={st} saved={ok} cost={resp.get('usage',{}).get('cost')} err={resp.get('err')}", flush=True)
print("DONE", flush=True)