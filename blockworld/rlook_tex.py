"""Draw the Roblox-look textures: round-head faces and clothes prints. Needs Pillow (system python, not Blender's).

    python3 -I blockworld/rlook_tex.py            # writes blockworld/rlook/faces/*.png and blockworld/rlook/clothes/*.png

Faces use the same names as the block faces (faces.py), so pose(c, face="shock") works in both looks.
A face is drawn on a transparent 512 x 512 square; the head shader projects it onto the front of the round head.
To add a face: add a row to FACES, run this script, and use the name in pose().
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

OUT = Path(__file__).resolve().parent / "rlook"
S = 512
INK = (22, 18, 20, 255)
WHITE = (255, 255, 255, 255)
BLUSH = (235, 120, 110, 70)
TEAR = (150, 205, 255, 255)

# name: brows (inner_y, outer_y), eyes, mouth, extras
FACES = {
    "smile":      ((142, 134), "open",   "smile",   ()),
    "happy":      ((132, 124), "closed", "grin",    ("blush",)),
    "laugh":      ((126, 118), "closed", "laugh",   ("blush",)),
    "stern":      ((156, 128), "open",   "flat",    ()),
    "angry":      ((166, 120), "small",  "growl",   ("vein",)),
    "determined": ((160, 132), "open",   "set",     ()),
    "sad":        ((124, 152), "open",   "frown",   ("tear",)),
    "scared":     ((118, 146), "small",  "wobble",  ("sweat",)),
    "shock":      ((104, 112), "wide",   "o",       ()),
    "smug":       ((140, 126), "lidded", "smirk",   ()),
    "sleepy":     ((150, 150), "shut",   "o_small", ()),
    "glasses":    ((150, 136), "open",   "flat",    ("glasses",)),
}


def brows(d, inner, outer):
    for sx in (-1, 1):
        cx = 256 + sx * 92
        x0, x1 = cx - sx * 30, cx + sx * 48
        d.line([(x0, inner), (x1, outer)], fill=INK, width=20)
        for x, y in ((x0, inner), (x1, outer)):
            d.ellipse([x - 10, y - 10, x + 10, y + 10], fill=INK)


def eyes(d, kind):
    for sx in (-1, 1):
        cx, ey = 256 + sx * 92, 236
        if kind in ("open", "lidded"):
            d.ellipse([cx - 30, ey - 40, cx + 30, ey + 40], fill=INK)
            d.ellipse([cx - 14 + sx * 4, ey - 28, cx + 6 + sx * 4, ey - 6], fill=WHITE)
            d.ellipse([cx + 6, ey + 14, cx + 16, ey + 24], fill=(255, 255, 255, 230))
            if kind == "lidded":                   # heavy upper lid
                d.rectangle([cx - 36, ey - 48, cx + 36, ey - 6], fill=(0, 0, 0, 0))
                d.line([(cx - 34, ey - 6), (cx + 34, ey - 6)], fill=INK, width=12)
        elif kind == "small":                      # tense: small pupils in white eyes
            d.ellipse([cx - 34, ey - 38, cx + 34, ey + 38], fill=WHITE, outline=INK, width=9)
            d.ellipse([cx - 13, ey - 13, cx + 13, ey + 13], fill=INK)
        elif kind == "wide":                       # shock: big white eyes, dot pupils
            d.ellipse([cx - 42, ey - 50, cx + 42, ey + 50], fill=WHITE, outline=INK, width=10)
            d.ellipse([cx - 11, ey - 11, cx + 11, ey + 11], fill=INK)
        elif kind == "closed":                     # happy arcs
            d.arc([cx - 34, ey - 20, cx + 34, ey + 40], 200, 340, fill=INK, width=14)
        elif kind == "shut":                       # sleepy lines
            d.arc([cx - 34, ey - 40, cx + 34, ey + 10], 20, 160, fill=INK, width=12)


def mouth(d, kind):
    if kind == "smile":
        d.arc([206, 300, 306, 370], 20, 160, fill=INK, width=13)
    elif kind == "grin":
        d.chord([196, 300, 316, 396], 0, 180, fill=INK)
        d.chord([214, 306, 298, 340], 0, 180, fill=WHITE)
    elif kind == "laugh":
        d.chord([186, 290, 326, 420], 0, 180, fill=INK)
        d.chord([206, 296, 306, 334], 0, 180, fill=WHITE)
        d.chord([226, 372, 286, 418], 180, 360, fill=(230, 100, 110, 255))
    elif kind == "flat":
        d.line([(222, 356), (290, 350)], fill=INK, width=13)
    elif kind == "set":
        d.line([(214, 352), (298, 352)], fill=INK, width=15)
        d.line([(214, 352), (206, 344)], fill=INK, width=10)
    elif kind == "growl":
        d.rounded_rectangle([206, 330, 306, 384], 12, fill=INK)
        d.rectangle([216, 336, 296, 356], fill=WHITE)
        for x in (236, 256, 276):
            d.line([(x, 336), (x, 356)], fill=INK, width=4)
    elif kind == "frown":
        d.arc([210, 340, 302, 410], 200, 340, fill=INK, width=13)
    elif kind == "wobble":
        pts = [(208 + i * 12, 360 + (8 if i % 2 else -8)) for i in range(9)]
        d.line(pts, fill=INK, width=11)
    elif kind == "o":
        d.ellipse([228, 320, 284, 396], fill=INK)
        d.ellipse([240, 360, 272, 388], fill=(200, 80, 90, 255))
    elif kind == "o_small":
        d.ellipse([242, 340, 272, 372], fill=INK)
    elif kind == "smirk":
        d.arc([220, 300, 320, 366], 20, 110, fill=INK, width=13)
        d.line([(222, 350), (262, 356)], fill=INK, width=12)


def extras(im, d, items):
    for it in items:
        if it == "blush":
            for sx in (-1, 1):
                d.ellipse([256 + sx * 122 - 30, 292, 256 + sx * 122 + 30, 318], fill=BLUSH)
        elif it == "tear":
            d.ellipse([356, 276, 380, 312], fill=TEAR)
            d.polygon([(358, 288), (368, 262), (378, 288)], fill=TEAR)
        elif it == "sweat":
            d.ellipse([386, 150, 416, 186], fill=TEAR)
            d.polygon([(388, 164), (401, 130), (414, 164)], fill=TEAR)
        elif it == "vein":
            for a, b in (((392, 108), (420, 136)), ((420, 108), (392, 136))):
                d.line([a, b], fill=(214, 40, 40, 255), width=9)
        elif it == "glasses":
            for sx in (-1, 1):
                cx = 256 + sx * 92
                d.rounded_rectangle([cx - 58, 186, cx + 58, 288], 18, outline=INK, width=11)
            d.line([(222, 228), (290, 228)], fill=INK, width=10)


def draw_faces():
    out = OUT / "faces"
    out.mkdir(parents=True, exist_ok=True)
    for name, (br, ey, mo, ex) in FACES.items():
        im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        if ey != "wide":
            brows(d, *br)
        else:
            brows(d, br[0] - 10, br[1] - 10)
        eyes(d, ey)
        mouth(d, mo)
        extras(im, d, ex)
        im.save(out / f"{name}.png")
    return sorted(FACES)


def folds(size, lines, col, blur=5):
    sh = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).line
    ds = ImageDraw.Draw(sh)
    for l in lines:
        ds.line(l, fill=col, width=10)
    return sh.filter(ImageFilter.GaussianBlur(blur))


def draw_clothes():
    out = OUT / "clothes"
    out.mkdir(parents=True, exist_ok=True)
    # "shade": a grey fold overlay multiplied onto ANY plain shirt colour (white = no change)
    im = Image.new("RGBA", (S, S), (255, 255, 255, 255))
    sh = folds((S, S), [[(60, 330), (120, 360), (190, 350)], [(330, 300), (390, 340), (450, 330)],
                        [(300, 400), (360, 420), (430, 410)], [(70, 410), (130, 430)], [(120, 290), (170, 300)],
                        [(150, 120), (200, 140)], [(330, 150), (380, 140)]], (0, 0, 0, 60))
    im.alpha_composite(sh)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 470, S, S], fill=(200, 200, 200, 255))                      # hem
    d.polygon([(186, 0), (256, 60), (326, 0)], fill=(170, 170, 170, 255))       # collar shadow
    im.convert("RGB").save(out / "shade.png")
    # "legs": the same for trousers (belt + folds)
    im = Image.new("RGBA", (256, 512), (255, 255, 255, 255))
    im.alpha_composite(folds((256, 512), [[(40, 250), (128, 270), (210, 250)], [(60, 290), (130, 300)],
                                          [(50, 420), (120, 440), (200, 425)], [(70, 120), (90, 200)]], (0, 0, 0, 70)))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 256, 36], fill=(70, 70, 76, 255))
    d.line([(200, 36), (190, 512)], fill=(180, 180, 180, 255), width=3)
    im.convert("RGB").save(out / "legs.png")
    # "jacket": a full varsity-jacket print (navy, white trim, gold zip, chest patch)
    im = Image.new("RGBA", (S, S), (31, 44, 92, 255))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 450, S, S], fill=(236, 236, 240, 255)); d.rectangle([0, 466, S, 482], fill=(214, 168, 58, 255))
    d.polygon([(150, 0), (256, 120), (362, 0)], fill=(236, 236, 240, 255))
    d.polygon([(178, 0), (256, 92), (334, 0)], fill=(31, 44, 92, 255))
    d.line([(256, 100), (256, 450)], fill=(214, 168, 58, 255), width=8)
    for y in range(110, 450, 26):
        d.line([(248, y), (264, y)], fill=(170, 130, 40, 255), width=3)
    d.rounded_rectangle([88, 150, 196, 270], 18, fill=(236, 236, 240, 255), outline=(214, 168, 58, 255), width=8)
    d.text((114, 152), "T", fill=(31, 44, 92, 255), font_size=110)
    im.alpha_composite(folds((S, S), [[(60, 330), (120, 360), (190, 350)], [(330, 300), (390, 340), (450, 330)],
                                      [(300, 400), (360, 420), (430, 410)]], (0, 0, 0, 70)))
    im.convert("RGB").save(out / "jacket.png")
    # "hoodie": white print (pocket, strings, hood shadow), multiplied onto the shirt colour
    im = Image.new("RGBA", (S, S), (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([120, 300, 392, 440], 30, fill=(200, 200, 200, 255))
    d.ellipse([140, -80, 372, 90], fill=(190, 190, 190, 255))
    d.rectangle([0, 470, S, S], fill=(205, 205, 205, 255))
    im.alpha_composite(folds((S, S), [[(80, 260), (150, 280)], [(360, 240), (430, 270)]], (0, 0, 0, 50)))
    for sx in (-1, 1):
        d = ImageDraw.Draw(im)
        d.line([(256 + sx * 40, 40), (256 + sx * 46, 200)], fill=(255, 255, 255, 255), width=10)
    im.convert("RGB").save(out / "hoodie.png")
    # "jeans": a full blue-jeans print
    im = Image.new("RGBA", (256, 512), (58, 70, 98, 255))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 256, 40], fill=(30, 30, 36, 255)); d.rectangle([100, 6, 150, 34], fill=(200, 170, 80, 255))
    d.line([(200, 40), (190, 512)], fill=(214, 168, 58, 255), width=3)
    im.alpha_composite(folds((256, 512), [[(40, 250), (128, 270), (210, 250)], [(50, 420), (120, 440), (200, 425)]],
                             (0, 0, 0, 80)))
    im.convert("RGB").save(out / "jeans.png")
    return ["shade", "legs", "jacket", "hoodie", "jeans"]


if __name__ == "__main__":
    print("faces:", ", ".join(draw_faces()))
    print("clothes:", ", ".join(draw_clothes()))
