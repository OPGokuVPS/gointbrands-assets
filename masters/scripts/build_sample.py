#!/usr/bin/env python3
"""Build polished GoIntBrands carousel slide sample via Pillow."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import os

ASSETS = "/root/gointbrands_assets"
OUT = os.path.join(ASSETS, "social")
os.makedirs(OUT, exist_ok=True)

W, H = 1080, 1350

def find_font(size, bold=False):
    cands = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for c in cands:
        if os.path.exists(c):
            try: return ImageFont.truetype(c, size)
            except: pass
    return ImageFont.load_default()

def remove_bg(im, threshold=215):
    """Turn near-white bg transparent."""
    im = im.convert("RGBA")
    data = im.load()
    w, h = im.size
    # build alpha from luminance; >threshold -> transparent
    mask = im.convert("L").point(lambda p: 0 if p > threshold else 255)
    im.putalpha(mask)
    # erode alpha slightly to kill white fringe
    return im

def add_shadow(base, overlay, cx, cy, max_dim):
    im = overlay.copy()
    iw, ih = im.size
    s = max_dim / max(iw, ih)
    im = im.resize((int(iw*s), int(ih*s)), Image.LANCZOS)
    w2, h2 = im.size
    # shadow layer
    sh = Image.new("RGBA", (w2+80, h2+80), (0,0,0,0))
    alpha = im.split()[3].point(lambda p: int(p*0.4))
    sh_mask = Image.new("L", (w2, h2), 0); sh_mask.paste(alpha, (0,0))
    sh.paste((20,10,5), (40, 40), sh_mask)
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    base.alpha_composite(sh, (cx-(w2+80)//2, cy-(h2+80)//2 + 20))
    base.alpha_composite(im, (cx-w2//2, cy-h2//2))
    return base

def vertical_gradient(size, top, bottom):
    g = Image.new("RGB", (size[0], 1))
    for x in range(size[0]):
        t = x / max(1,size[0]-1)  # rows
        g.putpixel((x,0), tuple(int(a+(b-a)*t) for a,b in zip(top,bottom)))
    return g.resize(size)

# --- La Banista slide: warm terracotta gradients matching can label ---
base = Image.new("RGB", (W,H))
base = vertical_gradient((W,H), (250,240,225), (225,190,165)).convert("RGBA")
d = ImageDraw.Draw(base)

# soft decorative arcs / texture
for i in range(0,H,6):
    tint = (245,230,215, 22) if (i//6)%2==0 else (0,0,0,0)
    d.rectangle([0,i,W,i+3], fill=tint if isinstance(tint,tuple) and len(tint)==4 else tint)

# Brand header
font_brand = find_font(42, True)
font_sub = find_font(24)
d.text((60,48), "GOINTBRANDS", font=font_brand, fill=(110,55,35,255))
d.text((62,100), "Sangrias de Espana  |  Spanish Sangrias", font=font_sub, fill=(150,95,70,255))

# Headline
font_h1 = find_font(78, True)
font_h2 = find_font(60, True)
d.text((60, 260), "Six ways to", font=font_h1, fill=(60,30,15,255))
d.text((60, 345), "love sangria", font=font_h1, fill=(160,30,30,255))
font_sub2 = find_font(34)
d.text((60, 445), "Una sangria para cada tarde", font=font_sub2, fill=(90,55,40,255))

# Product row: 3 can shots side by side at bottom-mid
can_paths = [
    "/root/gointbrands_assets/labanista/tinta_lata.jpg",
    "/root/gointbrands_assets/labanista/rosada_lata.jpg",
]
# Also try pet as third (but note it's not sold; use a bottle if available). For sample use two cans centered.
products = [remove_bg(Image.open(p)) for p in can_paths if os.path.exists(p)]
# place 2 cans centered
n = len(products)
spacing = 640 if n==2 else 480
startx = W//2 - (n-1)*spacing//2
y = 820
for i, p in enumerate(products):
    cx = startx + i*spacing
    base = add_shadow(base, p, cx, y, 700)

# CTA footer bar
footer_y = 1200
d.rounded_rectangle([70, footer_y, W-70, footer_y+90], radius=45, fill=(160,30,30,255))
font_cta = find_font(34, True)
d.text((W//2, footer_y+45), "Your favourite one: tinta or rosada?", font=font_cta, fill=(255,235,225,255), anchor="mm")

# Small tag under footer
font_tag = find_font(24)
d.text((W//2, footer_y+140), "Disponible en Riba Smith  |  @labanista", font=font_tag, fill=(120,80,60,255), anchor="mm")

out_path = os.path.join(OUT, "labanista_slide1_sample.png")
base.convert("RGB").save(out_path)
print("Saved:", out_path, base.size)