#!/usr/bin/env python3
"""POST 2 (Mediterranean tapas) editorial slides via Seedream 5.0 Pro image-edit.
Restyles REAL Comodoro + Avinyo product photos into editorial Mediterranean table scenes.
"""
import re, json, urllib.request, base64, io, os
from PIL import Image

KEYFILE="/root/.hermes/cache/terminal/hermes-snap-ce16e242b88c.sh"
with open(KEYFILE, errors='ignore') as fh: txt=fh.read()
KEY = list(dict.fromkeys(re.findall(r'OPENROUTER_API_KEY[="]*([\w-]+)', txt)))[0]

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

# (slug, outfile, [input photos], reference description, scene prompt)
jobs = [
  ("s1_hook", "slide1_hook.png", ["mejillones_gallega_cut.png","brut_reserva_cut.png"],
   "an open tin of Comodoro mejillones a la gallega (mussels in red Galician sauce) and a bottle of Avinyo cava",
   "Open tin of mussels on a rustic ceramic plate with a wedge of bread, and beside it a flute of chilled cava being poured from the Avinyo bottle. A warm Spanish tapas table: pork-free, scattered sprigs of parsley, chili pepper, lemon half. Cream linen tablecloth, warm golden-hour Mediterranean light, shallow depth of field, high-end editorial food photography. No text or logos other than the real product labels."),
  ("s2_comodoro", "slide2_comodoro.png", ["mejillones_gallega_cut.png","tentaculos_gallega.jpg"],
   "tins of Comodoro conservas - mejillones a la gallega and tentaculos a la gallega",
   "A small line-up of Comodoro conservas tins on a warm cream linen table, one tin open showing mussels in rich red sauce, a plate of mixed conservas tapas (mussels, octopus tentacles, breadsticks) beside them. Scattered olives, lemon wedges, daisies. Warm golden-hour Mediterranean light, shallow depth of field, high-end editorial food photography. Real product labels only."),
  ("s3_avinyo", "slide3_avinyo.png", ["brut_reserva_cut.png","brut_nature.jpg"],
   "a bottle of Avinyo cava reserva",
   "A bottle of Avinyo cava standing on a warm cream linen table beside a crystal flute of sparkling cava with fine bubbles. Scattered white daisies, a few green grapes and citrus. Warm golden-hour Mediterranean sunlight, shallow depth of field, high-end editorial beverage photography. Reproduce the Avinyo label faithfully."),
  ("s4_close", "slide4_close.png", ["mejillones_gallega_cut.png","brut_reserva_cut.png"],
   "an open tin of Comodoro mejillones a la gallega and a bottle of Avinyo cava",
   "The perfect Spanish pairing: an open tin of Comodoro mejillones a la gallega on a rustic plate and a flute of chilled Avinyo cava side by side on a warm cream linen table. Scattered olives, bread, lemon, daisies. Warm golden-hour Mediterranean light, shallow depth of field, high-end editorial food photography. Real product labels only, no added text."),
]

for slug, out, refs, desc, prompt in jobs:
    refs_b64 = []
    for rp in refs:
        p = f"/tmp/gointbrands-assets/{rp}"
        if not os.path.exists(p):
            print(f"RESULT {slug} MISSING_REF={rp}", flush=True); continue
        refs_b64.append({"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{to_b64(p)}"}})
    body={"model":"bytedance-seed/seedream-5-0-pro",
      "prompt":f"Photograph this exact {desc}: {prompt}",
      "n":1,"aspect_ratio":"4:5","resolution":"2K",
      "input_references":refs_b64}
    st,resp=post("images",body)
    ok=False
    if st==200:
        d=resp.get("data",[])
        if d and d[0].get("b64_json"):
            open(f"/root/gointbrands_assets/opt2/post2/{out}","wb").write(base64.b64decode(d[0]["b64_json"])); ok=True
    print(f"RESULT {slug} status={st} saved={ok} cost={resp.get('usage',{}).get('cost')} err={resp.get('err')}", flush=True)
print("DONE", flush=True)