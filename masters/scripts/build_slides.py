#!/usr/bin/env python3
"""Build branded GoIntBrands carousel slide graphics via Pillow.
Composites genuine product photography onto styled brand backgrounds
with typography — original, post-aligned, top-notch.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import os, glob

ASSETS = "/root/gointbrands_assets"
OUT = os.path.join(ASSETS, "social")
os.makedirs(OUT, exist_ok=True)

# ---- Canvas ----
W, H = 1080, 1350  # Instagram portrait 4:5

def find_font(size, bold=False):
    """Try common fonts; fall back graciously."""
    import subprocess
    cands = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    ]
    for c in cands:
        if os.path.exists(c):
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()

def rounded_mask(size, radius):
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([0,0,size[0]-1,size[1]-1], radius=radius, fill=255)
    return m

def load_product(path, max_w, max_h):
    im = Image.open(path).convert("RGBA")
    # Trim white background: remove near-white border, keep subject
    im.load()
    bg = Image.new("RGBA", im.size, (255,255,255,255))
    # Simple bg removal: near-white -> transparent
    px = im.convert("RGB")
    alpha = Image.new("L", im.size, 255)
    ad = ImageDraw.Draw(alpha)
    data = px.load()
    aw, ah = im.size
    for y in range(0, ah, 2):
        for x in range(0, aw, 2):
            r,g,bl = data[x,y]
            if r>245 and g>245 and bl>245:
                pass  # set transparent via mask at end
    # Build mask via threshold
    from PIL import ImageOps
    mask = ImageOps.invert(px.convert("L").point(lambda p: 255 if p>235 else 0))
    alpha = mask
    im.putalpha(alpha)
    # Also drop the pure-white around edges by eroding alpha slightly
    alpha_arr = alpha.load()
    return im

def paste_centered(base, overlay, cx, cy, scale):
    """Paste overlay centered at (cx,cy) scaled to fit."""
    im = overlay.copy()
    iw, ih = im.size
    # scale to square within bounds
    s = min(scale/ iw, scale/ ih) if iw and ih else 1
    nw, nh = int(iw*s), int(ih*s)
    im = im.resize((nw, nh), Image.LANCZOS)
    # drop shadow
    shadow = Image.new("RGBA", (nw+40, nh+40), (0,0,0,0))
    sh = ImageDraw.Draw(shadow)
    sh_im = im.split()[3].point(lambda p: int(p*0.35))
    sh_mask = Image.new("L", (nw,nh), 0); sh_mask.paste(sh_im, (0,0))
    shadow.paste((10,10,20), (20,20), sh_mask)
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))
    base.alpha_composite(shadow, (cx - (nw+40)//2, cy - (nh+40)//2 + 8))
    base.alpha_composite(im, (cx - nw//2, cy - nh//2))
    return base

def solid_gradient(size, top, bottom, vertical=True):
    top=Image.new("RGB",(1,1),top).convert("RGBA")
    bot=Image.new("RGB",(1,1),bottom).convert("RGBA")
    grad = Image.new("RGBA", size[0:2] if vertical else size[1:0])
    # build vertical gradient
    g = Image.new("RGBA", (size[0], 1))
    for x in range(size[0]):
        t = x/max(1,size[0]-1)
        g.putpixel((x,0), tuple(int(a+(b-a)*t) for a,b in zip(top.getpixel((0,0)), bot.getpixel((0,0)))))
    return g.resize((size[0], size[1]))

# ---- POST 1: La Banista - Carousel Slide 1 (hook / 6 variants) ----
print("Building La Banista slide 1 (6 variants triptych-fade)...")
slide1 = Image.new("RGBA", (W,H), (255,250,240))  # warm cream
# subtle background: soft warm gradient
bg = Image.new("RGBA", (W,H))
for i in range(H):
    t = i/H
    col = (int(255* (1-t)+ 250*t), int(244*(1-t)+ 235*t), int(230*(1-t)+ 214*t))
    for x in range(0,W,4): bg.putpixel((x,i), col+(255,))
bg = bg.resize((W,H), Image.BOX)
for x in range(W):
    for y in range(H): pass
slide1 = bg
d = ImageDraw.Draw(slide1)

# Decorative circle
d.ellipse([-300, 900, 900, 2100], fill=(235,220,200,120))
d.ellipse([700, -300, 1500, 500], fill=(240,225,205,100))

# Brand mark top
font_brand = find_font(44, True)
d.text((60,55), "GOINTBRANDS", font=font_brand, fill=(120,60,40,255))
font_sub = find_font(26)
d.text((62,110), "SANGRIAS + WINES OF SPAIN", font=font_sub, fill=(150,90,60,255))

# Headline
font_h1 = find_font(92, True)
font_h2 = find_font(52, True)
d.text((60, 320), "Six ways to", font=font_h1, fill=(60,30,15,255))
d.text((60, 420), "love sangria", font=font_h1, fill=(160,30,30,255))

# Product row: Trittico of the 6 (use 3 representative)
# Try to compose 6 variants. We have: tinta lata, rosada lata, pet (skip). Need tinta/blanca bottle+can urls.
# For the sample, place tinta lata + rosada lata + a wine bottle.
imgs = {
  "tinta_lata": "/root/gointbrands_assets/labanista/tinta_lata.jpg",
  "rosada_lata": "/root/gointbrands_assets/labanista/rosada_lata.jpg",
}
# Check what labanista files exist
print("La Banista files:", os.listdir("/root/gointbrands_assets/labanista") if os.path.exists("/root/gointbrands_assets/labanista") else "MISSING DIR")

print("Slide 1 partial build OK")
slide1.save(os.path.join(OUT, "lab_b1_slide1_sample.png"))
print("Saved sample:", os.path.join(OUT, "lab_b1_slide1_sample.png"))