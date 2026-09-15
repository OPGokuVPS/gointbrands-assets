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
os.makedirs("/root/gointbrands_assets/opt2/gemini_flash", exist_ok=True)
outs=[("TINTA","tinta.png","/tmp/prod_tinta_clean.png","tall slim sangria can","tinta (red)"),
      ("BLANCA","blanca.png","/root/gointbrands_assets/opt2/inputs/prod_blanca.jpg","sangria can","blanca (white)"),
      ("ROSADA","rosada.png","/root/gointbrands_assets/opt2/inputs/prod_rosada.jpg","sangria can","rosada (rose)")]
for name,fn,img,desc,sty in outs:
    b64=to_b64(img)
    body={"model":"google/gemini-3.1-flash-image",
      "prompt":(f"Photograph this exact {desc} standing on a warm cream linen table with scattered white daisies and a glass of "
                f"the matching {sty} sangria, warm golden-hour Mediterranean sunlight, shallow depth of field, high-end editorial "
                f"product photography. Reproduce the printed label EXACTLY as shown, including the words 'La Bañista' and 'Sangría' "
                f"and all fine Spanish text rendered perfectly legible with correct spelling."),
      "n":1,"aspect_ratio":"4:5",
      "input_references":[{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}}]}
    st,resp=post("images",body)
    ok=False
    if st==200:
        d=resp.get("data",[])
        if d and d[0].get("b64_json"):
            open(f"/root/gointbrands_assets/opt2/gemini_flash/{fn}","wb").write(base64.b64decode(d[0]["b64_json"])); ok=True
    print(f"RESULT {name} status={st} saved={ok} cost={resp.get('usage',{}).get('cost')} err={resp.get('err')}", flush=True)
print("DONE", flush=True)