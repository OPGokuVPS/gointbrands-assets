#!/usr/bin/env python3
"""Proper background removal via edge flood-fill, then premium compositing.

The product studio shots are on pure-white backgrounds. Flood-fill from the
image border removes ONLY the connected outer white, preserving internal white
(label cream bands). Result is a clean cutout you can drop on any gradient.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from collections import deque
import os

ASSETS = "/root/gointbrands_assets"
OUT = os.path.join(ASSETS, "social")
os.makedirs(OUT, exist_ok=True)
W, H = 1080, 1350

FONTS = {
    "bold": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "reg":  "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
}
def F(size, bold=True):
    p = FONTS["bold" if bold else "reg"]
    return ImageFont.truetype(p, size) if os.path.exists(p) else ImageFont.load_default()

def flood_bg(path, tolerance=24):
    """Remove background connected to image border (flood fill). Kill white fringe."""
    im = Image.open(path).convert("RGBA")
    w, h = im.size
    px = im.convert("RGB")
    data = px.load()
    # visited / transparent mark via a set
    marked = [[False]*w for _ in range(h)]
    q = deque()
    for x in range(w):
        q.append((x,0)); q.append((x,h-1))
    for y in range(h):
        q.append((0,y)); q.append((w-1,y))
    ref = (255,255,255)
    def close(c):
        return all(abs(int(c[i])-ref[i]) <= tolerance for i in range(3))
    while q:
        x,y = q.popleft()
        if x<0 or x>=w or y<0 or y>=h or marked[y][x]: continue
        if not close(data[x,y]): continue
        marked[y][x] = True
        for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
            q.append((x+dx,y+dy))
    # build alpha
    alpha = Image.new("L", (w,h), 0)
    ap = alpha.load()
    for y in range(h):
        for x in range(w):
            if marked[y][x]:
                ap[x,y] = 0
            else:
                ap[x,y] = 255
    # feather: blur alpha slightly to soften edge
    alpha = alpha.filter(ImageFilter.GaussianBlur(1.2))
    im.putalpha(alpha)
    return im

def shadow_of(cutout, soft=26, strength=90, dy=24):
    """Soft drop shadow from the cutout's alpha."""
    a = cutout.split()[3]
    cw, ch = cutout.size
    sh = Image.new("L", (cw+2*soft, ch+2*soft), 0)
    sh.paste(a, (soft, soft))
    sh = sh.filter(ImageFilter.GaussianBlur(soft))
    # colorize shadow
    rgba = Image.new("RGBA", sh.size, (60,25,10,0))
    rgba.putalpha(sh.point(lambda p: int(p*strength/255)))
    return rgba, dy

def paste_cutout(base, cutout, cx, cy, max_h):
    im = cutout.copy()
    iw, ih = im.size
    s = max_h / ih if iw and ih else 1
    im = im.resize((int(iw*s), int(ih*s)), Image.LANCZOS)
    sh, dy = shadow_of(im)
    cw, ch = im.size
    sw, shh = sh.size
    base.alpha_composite(sh, (cx-sw//2, cy-shh//2+dy))
    base.alpha_composite(im, (cx-cw//2, cy-ch//2))
    return base

def gradient(size, top, bottom):
    g = Image.new("RGB", (size[0],1))
    px = g.load()
    for x in range(size[0]):
        t = x/max(1,size[0]-1)
        px[x,0] = tuple(int(a+(b-a)*t) for a,b in zip(top,bottom))
    return g.resize(size)

# ============ SLIDE 1: La Banista ============
def slide_labanista():
    base = Image.new("RGBA", (W,H), (0,0,0,0))
    base.paste(gradient((W,H),(247,235,215),(224,186,158)).convert("RGBA"),(0,0))
    d = ImageDraw.Draw(base)
    d.text((W//2,64),"GOINTBRANDS",font=F(44,True),fill=(108,52,32,255),anchor="mm")
    d.text((W//2,112),"LA BANISTA SANGRIA  ·  HECHO EN ESPA\u00d1A",font=F(23),fill=(136,88,58,255),anchor="mm")
    d.text((W//2,250),"One sangria.",font=F(72,True),fill=(55,28,14,255),anchor="mm")
    d.text((W//2,336),"Two ways to pour.",font=F(72,True),fill=(148,28,28,255),anchor="mm")
    d.text((W//2,428),"Tinta or rosada, both ready for summer.",font=F(30),fill=(90,58,40,255),anchor="mm")
    cws = [
        "/root/gointbrands_assets/labanista/tinta_lata.jpg",
        "/root/gointbrands_assets/labanista/rosada_lata.jpg",
    ]
    cuts = [flood_bg(p) for p in cws if os.path.exists(p)]
    cy = 870
    # place two side by side
    for i,cu in enumerate(cuts):
        # each cutout canvas is 1200 wide; place one center, or two overlapping
        if len(cuts)==2:
            cx0 = W//2 - 330
            paste_cutout(base, cu, cx0 + i*660, cy, 760)
        else:
            paste_cutout(base, cu, W//2, cy, 820)
    d.rounded_rectangle([110,1190,W-110,1282],radius=46,fill=(148,28,28,255))
    d.text((W//2,1236),"Which one is yours?",font=F(36,True),fill=(255,238,224,255),anchor="mm")
    d.text((W//2,1338),"Disponible en Riba Smith  ·  @labanista",font=F(26),fill=(120,80,52,255),anchor="mm")
    return base

def slide_labanista_2():
    base = Image.new("RGBA",(W,H),(0,0,0,0))
    base.paste(gradient((W,H),(247,235,215),(224,186,158)).convert("RGBA"),(0,0))
    d=ImageDraw.Draw(base)
    d.text((W//2,64),"GOINTBRANDS",font=F(44,True),fill=(108,52,32,255),anchor="mm")
    d.text((W//2,112),"LA BANISTA SANGRIA  ·  HECHO EN ESPA\u00d1A",font=F(23),fill=(136,88,58,255),anchor="mm")
    # quote from can label
    d.text((W//2,260),"In the shade, well chilled,",font=F(56,True),fill=(55,28,14,255),anchor="mm")
    d.text((W//2,330),"that is how sangria",font=F(56,True),fill=(55,28,14,255),anchor="mm")
    d.text((W//2,400),"is best enjoyed.",font=F(56,True),fill=(148,28,28,255),anchor="mm")
    d.text((W//2,485) if False else (W//2,500), "\u201CLa sangr\u00eda se disfruta a la sombra y bien fr\u00eda.\u201D", font=F(28), fill=(90,58,40,255), anchor="mm")
    cu = flood_bg("/root/gointbrands_assets/labanista/tinta_lata.jpg")
    paste_cutout(base, cu, W//2, 940, 880)
    d.rounded_rectangle([110,1190,W-110,1282],radius=46,fill=(148,28,28,255))
    d.text((W//2,1236),"Tag someone you would share it with",font=F(32,True),fill=(255,238,224,255),anchor="mm")
    return base

def slide_tapas():
    base = Image.new("RGBA",(W,H),(0,0,0,0))
    base.paste(gradient((W,H),(238,243,245),(202,214,222)).convert("RGBA"),(0,0))
    d=ImageDraw.Draw(base)
    d.text((W//2,64),"GOINTBRANDS",font=F(44,True),fill=(28,48,58,255),anchor="mm")
    d.text((W//2,112),"TAPAS DE ESPA\u00d1A",font=F(23),fill=(82,106,120,255),anchor="mm")
    d.text((W//2,250),"A tin of mussels,",font=F(64,True),fill=(24,40,50,255),anchor="mm")
    d.text((W//2,332),"a cold glass of cava.",font=F(64,True),fill=(22,58,78,255),anchor="mm")
    d.text((W//2,422),"That is a perfect evening.",font=F(38),fill=(70,95,110,255),anchor="mm")
    cus = [
        flood_bg("/root/gointbrands_assets/comodoro/mejillones_gallega.jpg"),
        flood_bg("/root/gointbrands_assets/avinyo/brut_reserva.jpg"),
    ]
    cy=880
    for i,cu in enumerate(cus):
        cx0 = W//2-360
        paste_cutout(base,cu,cx0+i*720,cy,720)
    d.rounded_rectangle([110,1190,W-110,1282],radius=46,fill=(22,58,78,255))
    d.text((W//2,1236),"On the table in two minutes",font=F(34,True),fill=(230,242,247,255),anchor="mm")
    d.text((W//2,1338),"Comodoro + Avinyo  ·  Riba Smith",font=F(26),fill=(70,95,110,255),anchor="mm")
    return base

slides = {
    "labanista_slide1": slide_labanista(),
    "labanista_slide2": slide_labanista_2(),
    "tapas_slide1": slide_tapas(),
}
for name,im in slides.items():
    im.convert("RGB").save(os.path.join(OUT,f"{name}.png"))
    print("Saved:",os.path.join(OUT,f"{name}.png"))