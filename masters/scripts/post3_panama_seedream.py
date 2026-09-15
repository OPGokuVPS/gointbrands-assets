#!/usr/bin/env python3
"""POST 3 (Avinyó Brand Spotlight) — PANAMANIAN SCENERY edition via Seedream 5.0 Pro.
Same real Avinyó product inputs, Panamanian settings: Panamanian coast golden hour,
Boquete highlands, tropical table, Panama City skyline sunset. 4 slides.
"""
import re, json, urllib.request, base64, io, os, sys
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
    im=Image.open(path).convert("RGB"); im.thumbnail((maxdim,maxdim))
    b=io.BytesIO(); im.save(b,"JPEG",quality=93); return base64.b64encode(b.getvalue()).decode()

AVINYO="/root/gointbrands_assets/avinyo"
os.makedirs("/root/gointbrands_assets/opt3pan", exist_ok=True)

# (slug, outfile, [input ref photos], reference description, Panamanian scene prompt)
jobs = [
  ("s1_hook","pan_slide1_hook.png",["brut_nature.jpg"],
   "a bottle of Avinyo cava Brut Nature",
   "A bottle of Avinyo cava Brut Nature standing on a warm cream linen table beside a crystal flute of sparkling cava with fine bubbles, on a Caribbean coastline of Panama at golden hour: soft fine sand and calm turquoise sea blurred behind. Scatter white daisies, sliced lime and a wedge of mango around the base. Warm tropical golden light, shallow depth of field, high-end editorial beverage photography. Reproduce the Avinyo label faithfully. No added text."),
  ("s2_heritage","pan_slide2_heritage.png",["brut_reserva.jpg"],
   "a bottle of Avinyo cava Brut Reserva",
   "A bottle of Avinyo cava Brut Reserva standing on a rustic wooden table in the highlands of Boquete, Panama, at morning golden light: cool green coffee-farm and mountain slopes with soft haze behind, a thatched-roof finca in the distance. The same family's vine heritage, now in Panamanian countryside. Cinematic high-end editorial photography, shallow depth of field. Reproduce the Avinyo label faithfully. No added text."),
  ("s3_range","pan_slide3_range.png",["brut_nature.jpg","brut_reserva.jpg","gran_reserva.jpg","blanc_de_noris.jpg","rose_sublima.jpg"],
   "five bottles of Avinyo cava (Brut Nature, Brut Reserva, Gran Reserva, Blanc de Noirs, Rose Sublim)",
   "Five bottles of Avinyo cava lined up on a warm cream linen table, labels facing the camera, from left to right: Brut Nature, Brut Reserva, Gran Reserva, Blanc de Noirs, Rose Sublim. A crystal flute of sparkling cava at the far end. Tropical Panamanian accents along the base: sliced mango, passion fruit (maracuya), lime and white daisies. Bokeh of the colorful Balboa Avenue / Casco Viejo of Panama City blurred behind. Warm golden-hour tropical light, shallow depth of field, high-end editorial beverage photography. Reproduce each Avinyo label faithfully. No added text."),
  ("s4_close","pan_slide4_close.png",["brut_reserva.jpg"],
   "a bottle of Avinyo cava Brut Reserva",
   "Two crystal flutes of chilled cava toasting over a table set for a brindis at sunset, a bottle of Avinyo cava Brut Reserva on a warm cream linen table between them, fine bubbles rising. Behind them, the Panama City skyline at golden sunset over the bay. Scatter white daisies, lime and mango. Warm tropical golden light, shallow depth of field, high-end editorial celebration photography. Reproduce the Avinyo label faithfully. No added text."),
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
            open(f"/root/gointbrands_assets/opt3pan/{out}","wb").write(base64.b64decode(d[0]["b64_json"])); ok=True
    print(f"RESULT {slug} status={st} saved={ok} cost={resp.get('usage',{}).get('cost')} err={resp.get('err')}", flush=True)
print("DONE", flush=True)