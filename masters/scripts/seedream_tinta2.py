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

b64=to_b64("/tmp/prod_tinta_clean.png")
body={"model":"bytedance-seed/seedream-5-0-pro",
  "prompt":("Photograph this exact tall slim sangria can standing on a warm cream linen table beside TWO kinds of drinkware: "
            "a classic stemmed wine glass filled with red sangria and a small rustic ceramic cup also with red wine. Scatter white "
            "daisies and orange/lemon slices around the base. Warm golden-hour Mediterranean sunlight, shallow depth of field, "
            "high-end editorial product photography. "
            "CRITICAL LABEL INSTRUCTION: reproduce the can label faithfully. The large words must read 'La Bañista' and 'Sangría'. "
            "The line above the bottom black band must read 'RED · ROUGE · TINTA'. The bottom black band text must read EXACTLY "
            "'BODEGAS ELOSEGI' - the words BODEGAS and ELOSEGI spelled precisely this way, no other variant."),
  "n":1,"aspect_ratio":"4:5","resolution":"2K",
  "input_references":[{"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{b64}"}}]}
st,resp=post("images",body)
ok=False
out="/root/gointbrands_assets/opt2/seedream/tinta_v2.png"
if st==200:
    d=resp.get("data",[])
    if d and d[0].get("b64_json"):
        open(out,"wb").write(base64.b64decode(d[0]["b64_json"])); ok=True
print(f"RESULT tinta_v2 status={st} saved={ok} cost={resp.get('usage',{}).get('cost')} err={resp.get('err')}", flush=True)
print("DONE", flush=True)