#!/usr/bin/env python3
"""Polished GoIntBrands carousel slide builder v2.
Products rendered on branded cream cards (no bg-removal fringe),
quiet gradient, consistent center alignment, legible type.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

ASSETS = "/root/gointbrands_assets"
OUT = os.path.join(ASSETS, "social")
os.makedirs(OUT, exist_ok=True)
W, H = 1080, 1350

FONTS = {
    "bold":  "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "reg":   "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
}
def F(size, bold=True):
    p = FONTS["bold" if bold else "reg"]
    return ImageFont.truetype(p, size) if os.path.exists(p) else ImageFont.load_default()

def gradient(size, top, bottom):
    g = Image.new("RGB", (size[0], 1))
    px = g.load()
    for x in range(size[0]):
        t = x/max(1,size[0]-1)
        px[x,0] = tuple(int(a+(b-a)*t) for a,b in zip(top,bottom))
    return g.resize(size)

def product_card(path, card_w, card_h, radius=40):
    """White/cream rounded card with product photo centered, soft shadow."""
    photo = Image.open(path).convert("RGB")
    # fit photo into card padding
    pad = card_w*0.12
    pw = int(card_w - 2*pad); ph = int(card_h - 2*pad)
    s = min(pw/photo.width, ph/photo.height)
    nw, nh = int(photo.width*s), int(photo.height*s)
    photo = photo.resize((nw,nh), Image.LANCZOS)
    card = Image.new("RGBA", (card_w, card_h), (255,252,245,255))
    card.paste(photo, ((card_w-nw)//2, (card_h-nh)//2))
    # rounded corners
    mask = Image.new("L", (card_w,card_h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0,0,card_w-1,card_h-1], radius=radius, fill=255)
    rgba = Image.new("RGBA", (card_w,card_h), (0,0,0,0))
    rgba.paste(card, (0,0), mask)
    # shadow
    sh = Image.new("RGBA", (card_w+60, card_h+60), (0,0,0,0))
    shd = ImageDraw.Draw(sh).rounded_rectangle([30,40,card_w+30-1,card_h+40-1], radius=radius, fill=(60,30,15,70))
    sh = sh.filter(ImageFilter.GaussianBlur(20))
    return rgba, (30,20), sh  # img, offset, shadow-layer

def paste_card(base, card_img, card_off, shadow, cx, cy):
    cw, ch = card_img.size
    base.alpha_composite(shadow, (cx-cw//2-30+card_off[0], cy-ch//2-30+card_off[1]))
    base.alpha_composite(card_img, (cx-cw//2, cy-ch//2))
    return base

# ============ SLIDE 1: La Banista spotlight ============
def slide_labanista():
    base = Image.new("RGBA", (W,H), (0,0,0,0))
    base.paste(gradient((W,H),(247,236,218),(226,189,160)).convert("RGBA"),(0,0))
    d = ImageDraw.Draw(base)

    # Brand header (centered)
    d.text((W//2, 60), "GOINTBRANDS", font=F(46,True), fill=(110,52,32,255), anchor="mm")
    d.text((W//2, 108), "LA BANISTA  ·  SANGRIAS OF SPAIN", font=F(24), fill=(140,90,60,255), anchor="mm")

    # Headline (centered, matches product count)
    d.text((W//2, 225), "One sangria.", font=F(76,True), fill=(55,28,14,255), anchor="mm")
    d.text((W//2, 312), "Two ways to open it.", font=F(76,True), fill=(150,28,28,255), anchor="mm")
    d.text((W//2, 408), "Tinta or rosada — both ready for summer.", font=F(32), fill=(90,58,40,255), anchor="mm")

    # Two product cards centered
    paths = [
        "/root/gointbrands_assets/labanista/tinta_lata.jpg",
        "/root/gointbrands_assets/labanista/rosada_lata.jpg",
    ]
    cw, ch, gap = 430, 560, 60
    ttotal = 2*cw + gap
    startx = (W-ttotal)//2 + cw//2
    cy = 780
    for i, p in enumerate(paths):
        if os.path.exists(p):
            card_img, card_off, shadow = product_card(p, cw, ch)
            cx = startx + i*(cw+gap)
            paste_card(base, card_img, card_off, shadow, cx, cy)

    # CTA footer
    d.rounded_rectangle([100, 1180, W-100, 1270], radius=45, fill=(150,28,28,255))
    d.text((W//2, 1225), "Which one is yours?", font=F(36,True), fill=(255,238,224,255), anchor="mm")
    d.text((W//2, 1320), "Disponible en Riba Smith  ·  @labanista", font=F(26), fill=(120,80,55,255), anchor="mm")
    return base

def slide_labanista_2():
    base = Image.new("RGBA", (W,H), (0,0,0,0))
    base.paste(gradient((W,H),(247,236,218),(226,189,160)).convert("RGBA"),(0,0))
    d = ImageDraw.Draw(base)
    d.text((W//2,60),"GOINTBRANDS",font=F(46,True),fill=(110,52,32,255),anchor="mm")
    d.text((W//2,108),"LA BANISTA  ·  SANGRIAS OF SPAIN",font=F(24),fill=(140,90,60,255),anchor="mm")
    d.text((W//2,280),"In the shade, well chilled,",font=F(58,True),fill=(55,28,14,255),anchor="mm")
    d.text((W//2,350),"that's how sangria is meant",font=F(58,True),fill=(55,28,14,255),anchor="mm")
    d.text((W//2,420),"to be enjoyed.",font=F(58,True),fill=(150,28,28,255),anchor="mm")
    return base

def slide_tapas():
    base = Image.new("RGBA", (W,H), (0,0,0,0))
    base.paste(gradient((W,H),(240,244,246),(205,215,222)).convert("RGBA"),(0,0))
    d = ImageDraw.Draw(base)
    d.text((W//2,60),"GOINTBRANDS",font=F(46,True),fill=(28,48,58,255),anchor="mm")
    d.text((W//2,108),"SPANISH TAPAS NIGHT",font=F(24),fill=(80,105,120,255),anchor="mm")
    d.text((W//2,230),"A tin of mussels,",font=F(68,True),fill=(24,40,50,255),anchor="mm")
    d.text((W//2,315),"a cold glass of cava.",font=F(68,True),fill=(24,60,80,255),anchor="mm")
    d.text((W//2,410),"That is a perfect evening.",font=F(40),fill=(70,95,110,255),anchor="mm")

    # Two cards: Comodoro + Avinyo
    paths = [
        "/root/gointbrands_assets/comodoro/mejillones_gallega.jpg",
        "/root/gointbrands_assets/avinyo/brut_reserva.jpg",
    ]
    cw, ch, gap = 430, 560, 60
    ttotal = 2*cw+gap
    startx = (W-ttotal)//2 + cw//2
    cy = 800
    for i,p in enumerate(paths):
        if os.path.exists(p):
            ci,co,sh=product_card(p,cw,ch)
            paste_card(base,ci,co,sh,startx+i*(cw+gap),cy)

    d.rounded_rectangle([100,1180,W-100,1270],radius=45,fill=(24,60,80,255))
    d.text((W//2,1225),"Abrir en 2 minutos",font=F(36,True),fill=(230,242,247,255),anchor="mm")
    d.text((W//2,1320),"Comodoro + Avinyo  ·  Riba Smith",font=F(26),fill=(70,95,110,255),anchor="mm")
    return base

# Build 3 slides
slides = {
    "labanista_slide1": slide_labanista(),
    "labanista_slide2": slide_labanista_2(),
    "tapas_slide1": slide_tapas(),
}
for name, im in slides.items():
    im.convert("RGB").save(os.path.join(OUT, f"{name}.png"))
    print("Saved:", os.path.join(OUT, f"{name}.png"))