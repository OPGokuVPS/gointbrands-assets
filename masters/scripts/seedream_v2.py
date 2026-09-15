#!/usr/bin/env python3
import re, json, urllib.request, base64, io, os
from PIL import Image
KEYFILE="/root/.hermes/cache/terminal/hermes-snap-ce16e242b88c.sh"
with open(KEYFILE, errors='ignore') as fh: txt=fh.read()
KEY=list(dict.fromkeys(re.findall(r'OPENROUTER_API_KEY[="]*([\w-]+)', txt)))[0]
def post(path, body):
    req=urllib.request.Request(f"https://openrouter.ai/api/v1/{path}",data=json.dumps(body).encode(),
        headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"},method="POST")
    try:
        with urllib.request.urlopen(req,timeout=240) as r: return r.status,json.loads(r.read().decode())
    except urllib.error.HTTPError as e: return e.code,json.loads(e.read().decode() or "{}")
    except Exception as e: return -1,{"err":str(e)}
def to_b64(path, maxdim=700):
    im=Image.open(path).convert("RGB"); im.thumbnail((maxdim,maxdim))
    b=io.BytesIO(); im.save(b,"JPEG",quality=92); return base64.b64encode(b.getvalue()).decode()
os.makedirs("/root/gointbrands_assets/opt2/seedream", exist_ok=True)
jobs=[("BLANCA","blanca_v2.png","/root/gointbrands_assets/opt2/inputs/prod_blanca.jpg","sangria can","blanca (white)",
       "the large words read 'La Bañista' and 'Sangría', line reads 'BLANC · BLANC · BLANCA', bottom black band reads exactly 'BODEGAS ELOSEGI'"),
      ("ROSADA","rosada_v2.png","/root/gointbrands_assets/opt2/inputs/prod_rosada.jpg","sangria can","rosada (rosé)",
       "the large words read 'La Bañista' and 'Sangría', line reads 'ROSÉ · ROSÉ · ROSADA', bottom black band reads exactly 'BODEGAS ELOSEGI'")]
for name,fn,img,desc,sty,label in jobs:
    b64=to_b64(img)
    body={"model":"bytedance-seed/seedream-5-0-pro",
      "prompt":(f"Photograph this exact {desc} standing on a warm cream linen table beside TWO kinds of drinkware: "
                f"a classical transparent clear-stemmed wine glass filled with {sty} sangria and a small rustic ceramic cup "
                f"also with the same {sty} sangria. The wine glass must be perfectly transparent/clear glass. Scatter white "
                f"daisies and citrus slices around the base. Warm golden-hour Mediterranean sunlight, shallow depth of field, "
                f"high-end editorial product photography. "
                f"CRITICAL LABEL INSTRUCTION: reproduce the can label faithfully - {label}."),
      "n":1,"aspect_ratio":"4:5","resolution":"2K",
      "input_references":[{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}}]}
    st,resp=post("images",body)
    ok=False
    if st==200:
        d=resp.get("data",[])
        if d and d[0].get("b64_json"):
            open(f"/root/gointbrands_assets/opt2/seedream/{fn}","wb").write(base64.b64decode(d[0]["b64_json"])); ok=True
    print(f"RESULT {name} status={st} saved={ok} cost={resp.get('usage',{}).get('cost')} err={resp.get('err')}", flush=True)
print("DONE", flush=True)