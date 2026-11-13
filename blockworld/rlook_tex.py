"""Draw the Roblox-look textures: round-head faces and clothes prints. Needs Pillow (system python, not Blender's).

    python3 -I blockworld/rlook_tex.py            # writes blockworld/rlook/faces/*.png and blockworld/rlook/clothes/*.png

Faces use the same names as the block faces (faces.py), so pose(c, face="shock") works in both looks.
A face is drawn on a transparent 512 x 512 square; the head shader projects it onto the front of the round head.
To add a face: add a row to FACES, run this script, and use the name in pose().
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

OUT = Path(__file__).resolve().parent / "rlook"
S = 512                      # the clothes prints; faces are drawn in the same 512 grid, 4x bigger, and saved at 1024
FS, K = 1024, 4
INK = (22, 18, 20, 255)
WHITE = (255, 255, 255, 255)
BLUSH = (240, 110, 110, 90)
TEAR = (150, 205, 255, 255)
RED = (226, 60, 70, 255)
EX, EY = 98, 236             # eye centres: 256 +- EX, EY

# name: brows (inner_y, outer_y) or None, eyes, mouth, extras
FACES = {
    "smile":      ((150, 140), "open",    "smile",   ()),
    "happy":      ((138, 128), "closed",  "grin",    ("blush",)),
    "laugh":      ((130, 120), "closed",  "laugh",   ("blush",)),
    "stern":      ((170, 138), "open",    "flat",    ()),
    "angry":      ((184, 128), "small",   "growl",   ("vein",)),
    "determined": ((176, 142), "open",    "set",     ()),
    "sad":        ((128, 160), "open",    "frown",   ("tear",)),
    "scared":     ((120, 152), "small",   "wobble",  ("sweat",)),
    "shock":      ((96, 104),  "wide",    "o",       ()),
    "smug":       ((150, 134), "lidded",  "smirk",   ()),
    "sleepy":     ((156, 156), "shut",    "o_small", ()),
    "glasses":    ((150, 140), "open",    "flat",    ("glasses",)),
    # new in world v2
    "cry":        ((124, 158), "squeeze", "wail",    ("streams",)),
    "wink":       ((146, 138), "wink",    "grin",    ("blush",)),
    "love":       ((132, 126), "heart",   "grin",    ("blush",)),
    "wow":        ((112, 110), "sparkle", "open",    ("blush",)),
    "dizzy":      ((140, 150), "dizzy",   "wobble",  ()),
    "worried":    ((126, 156), "open",    "frown",   ("sweat",)),
    "evil":       ((186, 124), "lidded",  "fang",    ()),
    "sideeye":    ((152, 150), "side",    "flat",    ()),
    "shy":        ((140, 146), "side",    "small",   ("blush", "blush")),
    "talk":       ((148, 140), "open",    "open",    ()),
    "proud":      ((150, 132), "closed",  "smirk",   ()),
    "disgust":    ((170, 150), "lidded",  "yuck",    ()),
}
BLINKS = ("open", "lidded", "small", "wide", "side", "sparkle")     # eye kinds that get a <name>_blink.png


class Pen:
    """ImageDraw in the 512 grid, drawn K times bigger (the picture is shrunk afterwards, so edges are smooth)."""

    def __init__(self, im):
        self.d = ImageDraw.Draw(im)

    @staticmethod
    def _k(v):
        return [tuple(c * K for c in q) if isinstance(q, (tuple, list)) else q * K for q in v]

    def ellipse(self, box, **kw):
        if "width" in kw:
            kw["width"] *= K
        self.d.ellipse(self._k(box), **kw)

    def line(self, pts, fill, width):
        pts = self._k(pts)
        self.d.line(pts, fill=fill, width=width * K, joint="curve")
        r = width * K / 2
        for x, y in (pts[0], pts[-1]):                              # round ends
            self.d.ellipse([x - r, y - r, x + r, y + r], fill=fill)

    def arc(self, box, a0, a1, fill, width):
        self.d.arc(self._k(box), a0, a1, fill=fill, width=width * K)
        x0, y0, x1, y1 = box
        import math
        for a in (a0, a1):                                          # round ends
            cx = (x0 + x1) / 2 + (x1 - x0 - width) / 2 * math.cos(math.radians(a))
            cy = (y0 + y1) / 2 + (y1 - y0 - width) / 2 * math.sin(math.radians(a))
            self.ellipse([cx - width / 2, cy - width / 2, cx + width / 2, cy + width / 2], fill=fill)

    def chord(self, box, a0, a1, fill):
        self.d.chord(self._k(box), a0, a1, fill=fill)

    def polygon(self, pts, fill):
        self.d.polygon(self._k(pts), fill=fill)

    def rect(self, box, fill, r=0, outline=None, width=0):
        self.d.rounded_rectangle(self._k(box), r * K, fill=fill, outline=outline, width=width * K)


def brows(d, inner, outer):
    for sx in (-1, 1):
        cx = 256 + sx * EX
        d.line([(cx - sx * 34, inner), (cx + sx * 50, outer)], INK, 24)


def _shine(d, cx, ey, big=1.0):
    d.ellipse([cx - 26 * big, ey - 38 * big, cx - 2 * big, ey - 8 * big], fill=WHITE)
    d.ellipse([cx + 10 * big, ey + 18 * big, cx + 24 * big, ey + 32 * big], fill=(255, 255, 255, 235))


def _heart(d, cx, cy, r, col):
    d.ellipse([cx - r, cy - r, cx, cy], fill=col)
    d.ellipse([cx, cy - r, cx + r, cy], fill=col)
    d.polygon([(cx - r * 0.96, cy - r * 0.3), (cx + r * 0.96, cy - r * 0.3), (cx, cy + r * 0.95)], fill=col)


def eyes(d, kind):
    import math
    for sx in (-1, 1):
        cx, ey = 256 + sx * EX, EY
        k = "closed" if kind == "wink" and sx > 0 else "open" if kind == "wink" else kind
        if k in ("open", "lidded", "sparkle"):
            g = 1.14 if k == "sparkle" else 1.0
            d.ellipse([cx - 42 * g, ey - 54 * g, cx + 42 * g, ey + 54 * g], fill=INK)
            d.ellipse([cx - 30 * g, ey + 2 * g, cx + 30 * g, ey + 48 * g], fill=(74, 46, 38, 255))   # a warm lower iris
            d.ellipse([cx - 22 * g, ey - 20 * g, cx + 22 * g, ey + 26 * g], fill=INK)                 # the pupil
            _shine(d, cx, ey, g)
            if k == "sparkle":
                d.ellipse([cx + 8, ey - 44, cx + 24, ey - 28], fill=WHITE)
            if k == "lidded":                      # a heavy upper lid: cut the top off, then a thick lid line
                d.rect([cx - 50, ey - 62, cx + 50, ey - 12], fill=(0, 0, 0, 0))
                d.line([(cx - 44, ey - 12), (cx + 44, ey - 12)], INK, 14)
            else:                                  # the upper lash line, with a small flick outward
                d.arc([cx - 48 * g, ey - 60 * g, cx + 48 * g, ey + 30 * g], 198, 342, INK, 11)
                d.line([(cx + sx * 44 * g, ey - 30 * g), (cx + sx * 58 * g, ey - 44 * g)], INK, 9)
        elif k == "small":                         # tense: small pupils in white eyes
            d.ellipse([cx - 42, ey - 48, cx + 42, ey + 48], fill=WHITE, outline=INK, width=10)
            d.ellipse([cx - 15, ey - 15, cx + 15, ey + 15], fill=INK)
            d.ellipse([cx - 9, ey - 10, cx - 2, ey - 3], fill=WHITE)
        elif k == "wide":                          # shock: big white eyes, dot pupils
            d.ellipse([cx - 50, ey - 62, cx + 50, ey + 62], fill=WHITE, outline=INK, width=11)
            d.ellipse([cx - 13, ey - 13, cx + 13, ey + 13], fill=INK)
        elif k == "side":                          # looking to the side under half-closed lids
            d.ellipse([cx - 44, ey - 46, cx + 44, ey + 46], fill=WHITE, outline=INK, width=10)
            d.ellipse([cx + 8, ey - 14, cx + 40, ey + 26], fill=INK)
            d.rect([cx - 52, ey - 56, cx + 52, ey - 14], fill=(0, 0, 0, 0))
            d.line([(cx - 44, ey - 14), (cx + 44, ey - 14)], INK, 13)
        elif k == "closed":                        # happy arcs
            d.arc([cx - 42, ey - 26, cx + 42, ey + 52], 200, 340, INK, 17)
        elif k == "shut":                          # sleepy lines
            d.arc([cx - 42, ey - 52, cx + 42, ey + 16], 20, 160, INK, 14)
        elif k == "blink":                         # a blink: the closed lid with lashes
            d.arc([cx - 44, ey - 44, cx + 44, ey + 22], 22, 158, INK, 13)
            d.line([(cx + sx * 38, ey + 8), (cx + sx * 52, ey + 16)], INK, 8)
        elif k == "squeeze":                       # crying: eyes squeezed shut  > <
            d.line([(cx - sx * 36, ey - 26), (cx + sx * 30, ey), (cx - sx * 36, ey + 26)], INK, 15)
        elif k == "heart":
            _heart(d, cx, ey + 6, 46, RED)
            d.ellipse([cx - 30, ey - 30, cx - 14, ey - 14], fill=(255, 255, 255, 220))
        elif k == "dizzy":                         # a spiral
            pts = [(cx + (6 + 3.2 * i) * math.cos(i * 0.55), ey + (6 + 3.2 * i) * math.sin(i * 0.55)) for i in range(15)]
            d.line(pts, INK, 9)


def mouth(d, kind):
    pink = (232, 104, 116, 255)
    if kind == "smile":
        d.arc([192, 286, 320, 386], 18, 162, INK, 15)
    elif kind == "small":
        d.arc([228, 318, 284, 370], 20, 160, INK, 12)
    elif kind == "grin":
        d.chord([184, 292, 328, 416], 0, 180, fill=INK)
        d.chord([204, 300, 308, 344], 0, 180, fill=WHITE)
    elif kind in ("laugh", "open"):
        w = 86 if kind == "laugh" else 62
        d.chord([256 - w, 280, 256 + w, 444], 0, 180, fill=INK)
        d.chord([256 - w + 22, 290, 256 + w - 22, 336], 0, 180, fill=WHITE)
        d.chord([256 - w + 34, 388, 256 + w - 34, 446], 180, 360, fill=pink)
    elif kind == "flat":
        d.line([(214, 362), (298, 354)], INK, 15)
    elif kind == "set":
        d.line([(206, 360), (306, 360)], INK, 17)
        d.line([(206, 360), (196, 350)], INK, 11)
    elif kind == "growl":
        d.rect([196, 330, 316, 396], INK, r=14)
        d.rect([208, 338, 304, 362], WHITE)
        for x in (232, 256, 280):
            d.line([(x, 340), (x, 360)], INK, 4)
    elif kind == "fang":                           # an evil grin with two fangs
        d.chord([178, 290, 334, 420], 0, 180, fill=INK)
        d.chord([196, 298, 316, 340], 0, 180, fill=WHITE)
        for x in (214, 298):
            d.polygon([(x - 12, 352), (x + 12, 352), (x, 384)], fill=WHITE)
    elif kind == "frown":
        d.arc([202, 344, 310, 428], 200, 340, INK, 15)
    elif kind == "wail":                           # crying out loud: a wide wobbly open mouth
        d.rect([196, 322, 316, 412], INK, r=40)
        d.chord([220, 362, 292, 420], 180, 360, fill=pink)
    elif kind == "wobble":
        d.line([(200 + i * 14, 366 + (9 if i % 2 else -9)) for i in range(9)], INK, 12)
    elif kind == "o":
        d.ellipse([222, 312, 290, 408], fill=INK)
        d.ellipse([236, 362, 276, 400], fill=(200, 80, 90, 255))
    elif kind == "o_small":
        d.ellipse([238, 338, 276, 380], fill=INK)
    elif kind == "smirk":
        d.arc([214, 296, 330, 376], 18, 112, INK, 15)
        d.line([(214, 358), (262, 366)], INK, 14)
    elif kind == "yuck":                           # tongue out
        d.line([(206, 352), (306, 352)], INK, 15)
        d.rect([238, 352, 290, 400], pink, r=22)


def extras(d, items):
    n_blush = items.count("blush")
    for it in set(items):
        if it == "blush":
            for sx in (-1, 1):
                d.ellipse([256 + sx * 142 - 36, 296, 256 + sx * 142 + 36, 330],
                          fill=(BLUSH[0], BLUSH[1], BLUSH[2], 150 if n_blush > 1 else BLUSH[3]))
        elif it == "tear":
            d.ellipse([372, 286, 400, 328], fill=TEAR)
            d.polygon([(374, 300), (386, 268), (398, 300)], fill=TEAR)
        elif it == "streams":
            for sx in (-1, 1):
                cx = 256 + sx * EX
                d.rect([cx - 14, 262, cx + 14, 420], TEAR, r=14)
                d.ellipse([cx - 20, 400, cx + 20, 446], fill=TEAR)
        elif it == "sweat":
            d.ellipse([402, 150, 436, 192], fill=TEAR)
            d.polygon([(404, 166), (419, 126), (434, 166)], fill=TEAR)
        elif it == "vein":
            for a, b in (((404, 100), (436, 132)), ((436, 100), (404, 132))):
                d.line([a, b], (214, 40, 40, 255), 10)
        elif it == "glasses":
            for sx in (-1, 1):
                cx = 256 + sx * EX
                d.rect([cx - 66, 170, cx + 66, 304], None, r=22, outline=INK, width=12)
            d.line([(222, 226), (290, 226)], INK, 11)


def _face(br, ey, mo, ex):
    im = Image.new("RGBA", (S * K, S * K), (0, 0, 0, 0))
    d = Pen(im)
    if br:
        brows(d, *br)
    eyes(d, ey)
    mouth(d, mo)
    extras(d, ex)
    return im.resize((FS, FS), Image.LANCZOS)


def draw_faces():
    """Every face, plus a <name>_blink.png for the ones with open eyes (the life layer blinks with them)."""
    out = OUT / "faces"
    out.mkdir(parents=True, exist_ok=True)
    for name, (br, ey, mo, ex) in FACES.items():
        _face(br, ey, mo, ex).save(out / f"{name}.png")
        if ey in BLINKS:
            _face((br[0] + 8, br[1] + 8), "blink", mo, ex).save(out / f"{name}_blink.png")
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
    return ["shade", "legs", "jacket", "hoodie", "jeans"] + draw_overlays(out)


# ---------------------------------------------------------------- overlay prints (world v2): drawn OVER any shirt colour
def _overlay():
    """The shared start of an overlay print: see-through, with soft folds, a darker hem and a round neckline."""
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    im.alpha_composite(folds((S, S), [[(60, 330), (120, 360), (190, 350)], [(330, 300), (390, 340), (450, 330)],
                                      [(300, 400), (360, 420), (430, 410)], [(70, 410), (130, 430)]], (0, 0, 0, 55)))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 474, S, S], fill=(0, 0, 0, 46))
    d.ellipse([176, -70, 336, 58], fill=(0, 0, 0, 70))                 # neckline shadow
    d.arc([170, -76, 342, 64], 0, 180, fill=(255, 255, 255, 120), width=8)   # neckline trim
    return im, d


def _star(d, cx, cy, r, fill):
    import math
    pts = []
    for i in range(10):
        a = math.radians(-90 + i * 36)
        rr = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=fill)


def draw_overlays(out):
    white, cream, dark = (255, 255, 255, 255), (250, 244, 228, 255), (30, 32, 40, 255)
    names = []

    def save(im, name):
        im.save(out / f"{name}.png")
        names.append(name)

    im, d = _overlay()                                                 # a T-shirt with a big white star
    _star(d, 256, 250, 120, white)
    save(im, "tee_star")
    im, d = _overlay()                                                 # two chest stripes
    d.rectangle([0, 170, S, 226], fill=white)
    d.rectangle([0, 250, S, 282], fill=white)
    save(im, "tee_stripe")
    im, d = _overlay()                                                 # a heart
    d.ellipse([146, 170, 262, 286], fill=white); d.ellipse([250, 170, 366, 286], fill=white)
    d.polygon([(152, 250), (360, 250), (256, 380)], fill=white)
    save(im, "tee_heart")
    im, d = _overlay()                                                 # a sports number
    d.text((256, 262), "7", fill=white, font_size=260, anchor="mm", stroke_width=6, stroke_fill=white)
    d.rectangle([0, 96, S, 116], fill=white)
    save(im, "tee_number")
    im, d = _overlay()                                                 # a lightning bolt
    d.polygon([(290, 110), (176, 280), (250, 280), (214, 410), (346, 226), (268, 226)], fill=(255, 221, 60, 255))
    save(im, "tee_bolt")
    im, d = _overlay()                                                 # a button shirt: collar, placket, buttons, pocket
    d.polygon([(150, 0), (256, 110), (220, 0)], fill=(255, 255, 255, 235)); d.polygon([(362, 0), (256, 110), (292, 0)], fill=(255, 255, 255, 235))
    d.line([(256, 110), (256, 474)], fill=(0, 0, 0, 70), width=6)
    for y in range(160, 460, 70):
        d.ellipse([244, y - 12, 268, y + 12], fill=white, outline=(0, 0, 0, 90), width=3)
    d.rounded_rectangle([318, 190, 410, 280], 10, outline=(0, 0, 0, 80), width=6)
    save(im, "shirt")
    im, d = _overlay()                                                 # an open cardigan over a cream blouse
    d.polygon([(190, 0), (322, 0), (300, 474), (212, 474)], fill=cream)
    d.line([(190, 0), (212, 474)], fill=(0, 0, 0, 90), width=8); d.line([(322, 0), (300, 474)], fill=(0, 0, 0, 90), width=8)
    for y in (150, 250, 350, 440):
        d.ellipse([318, y - 13, 344, y + 13], fill=(255, 235, 200, 255), outline=(0, 0, 0, 90), width=3)
    for x in range(206, 312, 21):                                      # a pearl necklace
        d.ellipse([x, 64 + int(18 * (1 - abs(x - 256) / 56) ** 0.5) if abs(x - 256) < 56 else 64, x + 16,
                   80 + int(18 * (1 - abs(x - 256) / 56) ** 0.5) if abs(x - 256) < 56 else 80], fill=white)
    save(im, "cardigan")
    im, d = _overlay()                                                 # an open dark jacket over a light T-shirt
    d.polygon([(176, 0), (336, 0), (318, 474), (194, 474)], fill=(214, 216, 222, 255))
    d.polygon([(120, 0), (176, 0), (220, 200), (194, 474), (150, 474)], fill=(0, 0, 0, 60))
    d.polygon([(392, 0), (336, 0), (292, 200), (318, 474), (362, 474)], fill=(0, 0, 0, 60))
    d.line([(194, 474), (220, 200), (176, 0)], fill=(190, 150, 60, 255), width=7)
    d.line([(318, 474), (292, 200), (336, 0)], fill=(190, 150, 60, 255), width=7)
    save(im, "jacket_open")
    im, d = _overlay()                                                 # dungarees: a denim bib with straps and buttons
    denim = (62, 92, 150, 255)
    d.rectangle([0, 330, S, S], fill=denim)
    d.rounded_rectangle([146, 150, 366, 360], 16, fill=denim)
    for x0, x1 in ((166, 120), (346, 392)):
        d.line([(x0, 160), (x1, 0)], fill=denim, width=44)
    for x in (176, 336):
        d.ellipse([x - 16, 166, x + 16, 198], fill=(240, 200, 80, 255))
    d.rounded_rectangle([206, 220, 306, 300], 10, outline=(40, 62, 110, 255), width=7)
    save(im, "dungarees")
    im, d = _overlay()                                                 # a hoodie: pocket, hood shadow, two strings
    d.rounded_rectangle([120, 310, 392, 446], 30, fill=(0, 0, 0, 44), outline=(0, 0, 0, 70), width=6)
    d.ellipse([130, -90, 382, 96], fill=(0, 0, 0, 60))
    for sx in (-1, 1):
        d.line([(256 + sx * 40, 50), (256 + sx * 46, 210)], fill=white, width=11)
        d.ellipse([256 + sx * 46 - 10, 204, 256 + sx * 46 + 10, 228], fill=white)
    save(im, "hoodie2")
    return names


if __name__ == "__main__":
    print("faces:", ", ".join(draw_faces()))
    print("clothes:", ", ".join(draw_clothes()))
