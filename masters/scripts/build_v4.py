#!/usr/bin/env python3
"""Premium v4: rembg AI cutouts + realistic drop shadows + branded gradients."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from rembg import remove, new_session
import os, sys, time

ASSETS = "/root/gointbrands_assets"
OUT = os.path.join(ASSETS, "social")
os.makedirs(OUT, exist_ok=True)
W, H = 1080, 1350
CACHE = os.path.join(ASSETS, "cutouts")
os.makedirs(CACHE, exist_ok=True)

FONTS = {"bold": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
         "reg": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"}
def F(size, bold=True):
    p = FONTS["bold" if bold else "reg"]
    return ImageFont.truetype(p, size) if os.path.exists(p) else ImageFont.load_default()

_sess = None
def get_cutout(path):
    """rembg cutout with caching."""
    global _sess
    key = os.path.basename(path).replace(".jpg","_cut.png")
    cpath = os.path.join(CACHE, key)
    if os.path.exists(cpath):
        return Image.open(cpath).convert("RGBA")
    if _sess is None:
        print("Loading rembg session...")
        _sess = new_session("isnet-general-use")
    im = Image.open(path).convert("RGBA")
    out = remove(im, session=_sess)
    # slight edge defringe: cutout is clean, just save
    out.save(cpath)
    return out

def paste_cutout(base, cutout, cx, cy, max_h, shadow_alpha=90, blur=22, dy=26):
    im = cutout.copy()
    iw, ih = im.size
    s = max_h / ih if iw and ih else 1
    w2 = max(1,int(iw*s)); h2=max(1,int(ih*s))
    im = im.resize((w2,h2), Image.LANCZOS)
    # realistic-ish shadow: gaussian of alpha, offset down
    a = im.split()[3]
    sh = Image.new("L", (w2+2*blur, h2+2*blur), 0)
    sh.paste(a, (blur,blur))
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    rgba = Image.new("RGBA", sh.size, (40,15,5,0))
    rgba.putalpha(sh.point(lambda p: int(p*shadow_alpha/255)))
    sw, sht = rgba.size
    base.alpha_composite(rgba, (cx-sw//2, cy-sht//2+dy))
    base.alpha_composite(im, (cx-w2//2, cy-h2//2))
    return base

def gradient(size, top, bottom):
    g = Image.new("RGB", (size[0],1)); px=g.load()
    for x in range(size[0]):
        t=x/max(1,size[0]-1)
        px[x,0]=tuple(int(a+(b-a)*t) for a,b in zip(top,bottom))
    return g.resize(size)

B = "\u00d1"  # Ñ

def slide_labanista():
    base = Image.new("RGBA",(W,H),(0,0,0,0))
    base.paste(gradient((W,H),(247,235,215),(222,184,156)).convert("RGBA"),(0,0))
    d=ImageDraw.Draw(base)
    d.text((W//2,60),"GOINTBRANDS",font=F(44,True),fill=(108,52,32,255),anchor="mm")
    d.text((W//2,110),"LA BANISTA SANGRIA  ·  HECHO EN ESPA"+B,font=F(22),fill=(136,88,58,255),anchor="mm")
    d.text((W//2,245),"One sangria.",font=F(70,True),fill=(55,28,14,255),anchor="mm")
    d.text((W//2,330),"Two ways to pour.",font=F(70,True),fill=(148,28,28,255),anchor="mm")
    d.text((W//2,420),"Tinta or rosada, both ready for summer.",font=F(30),fill=(90,58,40,255),anchor="mm")
    tinta = get_cutout("/root/gointbrands_assets/labanista/tinta_lata.jpg")
    rosa  = get_cutout("/root/gointbrands_assets/labanista/rosada_lata.jpg")
    cy=900
    # slight overlap for a cohesive duo
    paste_cutout(base, tinta, W//2-250, cy, 800)
    paste_cutout(base, rosa,  W//2+250, cy, 800)
    d.rounded_rectangle([120,1240,W-120,1332],radius=46,fill=(148,28,28,255))
    d.text((W//2,1286),"Which one is yours?",font=F(34,True),fill=(255,238,224,255),anchor="mm")
    return base

def slide_labanista_2():
    base = Image.new("RGBA",(W,H),(0,0,0,0))
    base.paste(gradient((W,H),(247,235,215),(222,184,156)).convert("RGBA"),(0,0))
    d=ImageDraw.Draw(base)
    d.text((W//2,60),"GOINTBRANDS",font=F(44,True),fill=(108,52,32,255),anchor="mm")
    d.text((W//2,110),"LA BANISTA SANGRIA  ·  HECHO EN ESPA"+B,font=F(22),fill=(136,88,58,255),anchor="mm")
    d.text((W//2,250),"In the shade, well chilled,",font=F(54,True),fill=(55,28,14,255),anchor="mm")
    d.text((W//2,320),"that is how sangria",font=F(54,True),fill=(55,28,14,255),anchor="mm")
    d.text((W//2,390),"is best enjoyed.",font=F(54,True),fill=(148,28,28,255),anchor="mm")
    d.text((W//2,470),"\u201CLa sangr\u00eda se disfruta a la sombra y bien fr\u00eda.\u201D",font=F(27),fill=(90,58,40,255),anchor="mm")
    cu=get_cutout("/root/gointbrands_assets/labanista/tinta_lata.jpg")
    paste_cutout(base,cu,W//2,960,900)
    d.rounded_rectangle([120,1240,W-120,1332],radius=46,fill=(148,28,28,255))
    d.text((W//2,1286),"Tag someone you would share it with",font=F(30,True),fill=(255,238,224,255),anchor="mm")
    return base

def slide_tapas():
    base = Image.new("RGBA",(W,H),(0,0,0,0))
    base.paste(gradient((W,H),(238,243,245),(202,214,222)).convert("RGBA"),(0,0))
    d=ImageDraw.Draw(base)
    d.text((W//2,60),"GOINTBRANDS",font=F(44,True),fill=(28,48,58,255),anchor="mm")
    d.text((W//2,110),"TAPAS DE ESPA"+B,font=F(22),fill=(82,106,120,255),anchor="mm")
    d.text((W//2,245),"A tin of mussels,",font=F(62,True),fill=(24,40,50,255),anchor="mm")
    d.text((W//2,325),"a cold glass of cava.",font=F(62,True),fill=(22,58,78,255),anchor="mm")
    d.text((W//2,415),"That is a perfect evening.",font=F(36),fill=(70,95,110,255),anchor="mm")
    mu=get_cutout("/root/gointbrands_assets/comodoro/mejillones_gallega.jpg")
    av=get_cutout("/root/gointbrands_assets/avinyo/brut_reserva.jpg")
    cy=900
    paste_cutout(base,mu,W//2-320,cy,680)
    paste_cutout(base,av,W//2+320,cy,720)
    d.rounded_rectangle([120,1240,W-120,1332],radius=46,fill=(22,58,78,255))
    d.text((W//2,1286),"On the table in two minutes",font=F(32,True),fill=(230,242,247,255),anchor="mm")
    return base

slides = {
    "labanista_slide1": slide_labanista(),
    "labanista_slide2": slide_labanista_2(),
    "tapas_slide1": slide_tapas(),
}
for name,im in slides.items():
    im.convert("RGB").save(os.path.join(OUT,f"{name}.png"))
    print("Saved:",os.path.join(OUT,f"{name}.png"))