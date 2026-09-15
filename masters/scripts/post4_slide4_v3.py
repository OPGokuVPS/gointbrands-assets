#!/usr/bin/env python3
"""Regenerate POST 4 slide 4 (close) v3: a man and a woman clinking WINE GLASSES in a toast,
distinct veranda/garden scenery (skyline only on hook slide). Real Conscious bottles on the table.
"""
import sys, json, urllib.request, base64, io, os
from PIL import Image

KEY=None
with open("/root/.hermes/.env") as fh:
    for line in fh:
        if line.startswith("OPENROUTER_API_KEY="):
            KEY=line.split("=",1)[1].strip().strip('"').strip("'"); break
if not KEY:
    print("RESULT NO_API_KEY", flush=True); sys.exit(1)

def post(path, body):
    req=urllib.request.Request(f"https://openrouter.ai/api/v1/{path}", data=json.dumps(body).encode(),
        headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req,timeout=280) as r: return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e: return e.code, json.loads(e.read().decode() or "{}")
    except Exception as e: return -1, {"err":str(e)}

def to_b64(path, maxdim=800):
    im=Image.open(path).convert("RGBA")
    bg=Image.new("RGB", im.size,(247,243,236)); bg.paste(im, mask=im.split()[3]); im=bg.convert("RGB")
    im.thumbnail((maxdim,maxdim)); b=io.BytesIO(); im.save(b,"JPEG",quality=93); return base64.b64encode(b.getvalue()).decode()

CONS="/root/gointbrands_assets/conscious"
refs_b64=[{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{to_b64(os.path.join(CONS,r))}"}} for r in ["red.png","sparkling.png"]]

descs="a bottle of Conscious wine red and a bottle of Conscious sparkling white"
prompt=("A warm Mediterranean-style veranda brunch in Panama at late-afternoon light: a smiling man and a "
 "woman raising their crystal wine glasses (one red, one sparkling) to clink in a toast over a table set "
 "with light healthy food (fresh fruit, green leaves, nuts, crackers). A bottle of Conscious red wine and "
 "a Conscious sparkling bottle sit on the warm cream linen table. Tropical plants and white daisies frame "
 "the scene; a soft, unfocused green-garden veranda backdrop (clearly NOT a city skyline). Warm gentle "
 "golden light, shallow depth of field, high-end editorial wellness lifestyle photography. Hands and faces "
 "natural and relaxed. Reproduce the Conscious labels faithfully. No added text.")
body={"model":"bytedance-seed/seedream-5-0-pro",
  "prompt":f"Photograph this exact {descs}: {prompt}",
  "n":1,"aspect_ratio":"4:5","resolution":"2K","input_references":refs_b64}
st,resp=post("images",body)
ok=False
if st==200:
    d=resp.get("data",[])
    if d and d[0].get("b64_json"):
        open("/root/gointbrands_assets/opt4pan/c4_slide4_close.png","wb").write(base64.b64decode(d[0]["b64_json"])); ok=True
print(f"RESULT s4_close status={st} saved={ok} cost={resp.get('usage',{}).get('cost')} err={resp.get('err')}", flush=True)