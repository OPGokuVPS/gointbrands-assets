#!/usr/bin/env python3
"""v5: premium slides with rembg cutouts + realistic contact shadows."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
import os, numpy as np

ASSETS = "/root/gointbrands_assets"
OUT = os.path.join(ASSETS, "social")
CUT = os.path.join(ASSETS, "cutouts")
W, H = 1080, 1350

FONTS = {"bold": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
         "reg": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"}
def F(size, bold=True):
    p = FONTS["bold" if bold else "reg"]
    return ImageFont.truetype(p, size) if os.path.exists(p) else ImageFont.load_default()

def get_cut(name):
    return Image.open(os.path.join(CUT, name)).convert("RGBA")

def make_grad(size, top, bottom):
    g = Image.new("RGB", (size[0],1)); px=g.load()
    for x in range(size[0]):
        t=x/max(1,size[0]-1)
        px[x,0]=tuple(int(a+(b-a)*t) for a,b in zip(top,bottom))
    return g.resize(size)

def contact_shadow(cutout):
    """Return a grounded contact-shadow layer sized/positioned to sit under the object."""
    a = cutout.split()[3]
    iw, ih = cutout.size
    arr = np.asarray(a, dtype=np.uint8)
    ys, xs = np.where(arr > 40)
    if len(ys)==0: return None
    top = ys.min(); bot = ys.max()
    obj_cx = int(xs.mean())
    obj_w = xs.max()-xs.min()
    # shadow width ~ 1.4x object width; height modest
    sw = int(obj_w*1.45)
    shh = max(60, int((bot-top)*0.28))
    sh = Image.new("L", (sw, shh), 0)
    d = ImageDraw.Draw(sh)
    cx = sw//2
    # tight core (dark, near ground line at bottom)
    d.ellipse([cx-sw*0.24, shh*0.35, cx+sw*0.24, shh*1.05], fill=150)
    # mid
    d.ellipse([cx-sw*0.36, shh*0.42, cx+sw*0.36, shh*1.05], fill=80)
    # wide soft ambient
    d.ellipse([cx-sw*0.5, shh*0.30, cx+sw*0.5, shh*1.12], fill=45)
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    # warm-tint color
    rgba = Image.new("RGBA", sh.size, (55,25,10,0))
    rgba.putalpha(sh)
    return rgba, obj_cx, bot

def paste_object(base, cutout, cx_px, ground_y, max_h):
    im = cutout.copy()
    iw, ih = im.size
    s = max_h / ih if ih else 1
    nw, nh = max(1,int(iw*s)), max(1,int(ih*s))
    im = im.resize((nw,nh), Image.LANCZOS)
    # drop a contact shadow proportional to this placement
    sh_layer, obj_cx, obj_bot = contact_shadow(im)
    if sh_layer:
        sw, shh = sh_layer.size
        # bottom of object in placed coords
        place_bot = ground_y
        # place shadow so its bottom ~ at ground_y, centered under object
        sx = cx_px - sw//2
        sy = ground_y - shh + 18
        base.alpha_composite(sh_layer, (sx, sy))
    base.alpha_composite(im, (cx_px - nw//2, ground_y - nh))
    return base

B="\u00d1"

def slide_labanista():
    base=Image.new("RGBA",(W,H),(0,0,0,0))
    base.paste(make_grad((W,H),(247,235,215),(222,184,156)).convert("RGBA"),(0,0))
    d=ImageDraw.Draw(base)
    d.text((W//2,58),"GOINTBRANDS",font=F(44,True),fill=(108,52,32,255),anchor="mm")
    d.text((W//2,108),"LA BANISTA SANGRIA  ·  HECHO EN ESPA"+B,font=F(22),fill=(136,88,58,255),anchor="mm")
    d.text((W//2,240),"One sangria.",font=F(70,True),fill=(55,28,14,255),anchor="mm")
    d.text((W//2,324),"Two ways to pour.",font=F(70,True),fill=(148,28,28,255),anchor="mm")
    d.text((W//2,410),"Tinta or rosada, both ready for summer.",font=F(30),fill=(90,58,40,255),anchor="mm")
    tinta=get_cut("tinta_lata_cut.png"); rosa=get_cut("rosada_lata_cut.png")
    ground=1180
    paste_object(base,tinta,W//2-240,ground,680)
    paste_object(base,rosa,W//2+240,ground,680)
    d.rounded_rectangle([110,1235,W-110,1323],radius=44,fill=(148,28,28,255))
    d.text((W//2,1279),"Which one is yours?",font=F(34,True),fill=(255,238,224,255),anchor="mm")
    d.text((W//2,1360),"Disponible en Riba Smith  ·  @labanista",font=F(24),fill=(120,80,52,255),anchor="mm")
    return base

def slide_labanista_2():
    base=Image.new("RGBA",(W,H),(0,0,0,0))
    base.paste(make_grad((W,H),(247,235,215),(222,184,156)).convert("RGBA"),(0,0))
    d=ImageDraw.Draw(base)
    d.text((W//2,58),"GOINTBRANDS",font=F(44,True),fill=(108,52,32,255),anchor="mm")
    d.text((W//2,108),"LA BANISTA SANGRIA  ·  HECHO EN ESPA"+B,font=F(22),fill=(136,88,58,255),anchor="mm")
    d.text((W//2,250),"In the shade, well chilled,",font=F(52,True),fill=(55,28,14,255),anchor="mm")
    d.text((W//2,318),"that is how sangria",font=F(52,True),fill=(55,28,14,255),anchor="mm")
    d.text((W//2,386),"is best enjoyed.",font=F(52,True),fill=(148,28,28,255),anchor="mm")
    d.text((W//2,468),"\u201CLa sangr\u00eda se disfruta a la sombra y bien fr\u00eda.\u201D",font=F(26),fill=(90,58,40,255),anchor="mm")
    cu=get_cut("tinta_lata_cut.png")
    paste_object(base,cu,W//2,1120,940)
    d.rounded_rectangle([110,1210,W-110,1298],radius=44,fill=(148,28,28,255))
    d.text((W//2,1254),"Tag someone you would share it with",font=F(30,True),fill=(255,238,224,255),anchor="mm")
    return base

def slide_tapas():
    base=Image.new("RGBA",(W,H),(0,0,0,0))
    base.paste(make_grad((W,H),(238,243,245),(202,214,222)).convert("RGBA"),(0,0))
    d=ImageDraw.Draw(base)
    d.text((W//2,58),"GOINTBRANDS",font=F(44,True),fill=(28,48,58,255),anchor="mm")
    d.text((W//2,108),"TAPAS DE ESPA"+B,font=F(22),fill=(82,106,120,255),anchor="mm")
    d.text((W//2,242),"A tin of mussels,",font=F(60,True),fill=(24,40,50,255),anchor="mm")
    d.text((W//2,322),"a cold glass of cava.",font=F(60,True),fill=(22,58,78,255),anchor="mm")
    d.text((W//2,410),"That is a perfect evening.",font=F(34),fill=(70,95,110,255),anchor="mm")
    mu=get_cut("mejillones_gallega_cut.png"); av=get_cut("brut_reserva_cut.png")
    ground=1120
    paste_object(base,mu,W//2-330,ground,700)
    paste_object(base,av,W//2+330,ground,760)
    d.rounded_rectangle([110,1210,W-110,1298],radius=44,fill=(22,58,78,255))
    d.text((W//2,1254),"On the table in two minutes",font=F(32,True),fill=(230,242,247,255),anchor="mm")
    d.text((W//2,1360),"Comodoro + Avinyo  ·  Riba Smith",font=F(24),fill=(70,95,110,255),anchor="mm")
    return base

slides = {
    "labanista_slide1": slide_labanista(),
    "labanista_slide2": slide_labanista_2(),
    "tapas_slide1": slide_tapas(),
}
for name,im in slides.items():
    im.convert("RGB").save(os.path.join(OUT,f"{name}.png"))
    print("Saved:",os.path.join(OUT,f"{name}.png"))