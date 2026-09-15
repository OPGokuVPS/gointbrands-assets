#!/usr/bin/env python3
"""POST 4 (Conscious Wines Brand Spotlight) — PANAMANIAN SCENERY via Seedream 5.0 Pro.
Real Conscious Wines product bottle photos (conscious-wine.com) restyled into
Panamanian editorial scenes. 4 slides. Cell count/vegan/low-cal cues in copy are
kept to caption; slides carry no text overlays.
"""
import sys, json, urllib.request, base64, io, os
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
    req=urllib.request.Request(f"https://openrouter.ai/api/v1/{path}", data=json.dumps(body).encode(),
        headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=280) as r: return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e: return e.code, json.loads(e.read().decode() or "{}")
    except Exception as e: return -1, {"err":str(e)}

def to_b64(path, maxdim=800):
    im=Image.open(path).convert("RGBA")
    # flatten any transparency onto a light cream ground so seedream sees a clean bottle
    bg=Image.new("RGB", im.size, (247,243,236)); bg.paste(im, mask=im.split()[3])
    im=bg.convert("RGB"); im.thumbnail((maxdim,maxdim))
    b=io.BytesIO(); im.save(b,"JPEG",quality=93); return base64.b64encode(b.getvalue()).decode()

CONS="/root/gointbrands_assets/conscious"
os.makedirs("/root/gointbrands_assets/opt4pan", exist_ok=True)

# (slug, outfile, [input refs], reference desc, Panamanian editorial scene)
jobs = [
  ("s1_hook","c4_slide1_hook.png",["red.png","white.png"],
   "two bottles of Conscious wine, one red and one white",
   "A bottle of Conscious red wine and a bottle of Conscious white wine standing side by side on a warm cream linen table, beside two crystal glasses, one with red and one with white wine, on a terrace overlooking the Panama City skyline at golden hour. Scatter sliced lime, white daisies and a sprig of mint. Warm tropical golden light, shallow depth of field, high-end editorial beverage photography. Reproduce the Conscious Wine label faithfully, including its clean minimal design. No added text."),
  ("s2_range","c4_slide2_range.png",["red.png","white.png","rose.png","sparkling.png"],
   "four bottles of Conscious wine: red, white, rose, and sparkling white",
   "Four bottles of Conscious wine lined up on a warm cream linen table, labels facing the camera, from left to right: red, white, rose, and sparkling white. A crystal glass at the end. Panamanian tropical accents along the base: sliced mango, passion fruit (maracuya), lime and white daisies. Warm golden-hour tropical light, shallow depth of field, high-end editorial beverage photography. Reproduce each Conscious label faithfully. No added text."),
  ("s3_life","c4_slide3_life.png",["rose.png"],
   "a bottle of Conscious wine rosé",
   "A bottle of Conscious rosé wine on a table by a calm Panamanian Caribbean beach at sunrise, fine sand and turquoise sea behind, a single glass of rosé beside the bottle. Scatter white daisies and a mango. Cool soft morning light, shallow depth of field, high-end editorial lifestyle photography. Reproduce the Conscious label faithfully. No added text."),
  ("s4_close","c4_slide4_close.png",["red.png","sparkling.png"],
   "a bottle of Conscious wine red and a bottle of Conscious sparkling white",
   "Two crystal glasses of wine toasting, one red and one sparkling, over a table set with light healthy food (fruit, greens, nuts, crackers), a bottle of Conscious red wine and a Conscious sparkling bottle on a warm cream linen table. Behind: the colorful Balboa Avenue / Casco Viejo of Panama City blurred at golden hour. Scatter white daisies, lime and mango. Warm tropical light, shallow depth of field, high-end editorial wellness-focused beverage photography. Reproduce the Conscious labels faithfully. No added text."),
]

for slug, out, refs, desc, prompt in jobs:
    refs_b64=[]
    for rp in refs:
        p=os.path.join(CONS, rp)
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
            open(f"/root/gointbrands_assets/opt4pan/{out}","wb").write(base64.b64decode(d[0]["b64_json"])); ok=True
    print(f"RESULT {slug} status={st} saved={ok} cost={resp.get('usage',{}).get('cost')} err={resp.get('err')}", flush=True)
print("DONE", flush=True)