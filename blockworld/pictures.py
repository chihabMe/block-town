"""Pictures for props: phone screens, the lock screen on hand-held phones, a paper town map.

    python3 -I SKILL/blockworld/pictures.py EPISODE        draws everything in EPISODE/pictures.json -> EPISODE/pictures/
    python3 -I SKILL/blockworld/pictures.py --defaults     redraws the kit's own lock.png and map.png (blockworld/pictures/)

Props find a picture by name: EPISODE/pictures/<name>.png first, then blockworld/pictures/<name>.png
(rprops.big_phone(screen=...), phone_in_hand(picture=...), paper_map(picture=...), picture_quad(...)).

pictures.json maps a name to a recipe. Kinds:
  {"kind": "wifi_search", "title": "Wi-Fi", "status": "Searching...", "hint": ["No networks found", "Be nice"]}
  {"kind": "calling", "name": "Grandma", "who": "gran"}                       (who: a cast name below, or "avatar")
  {"kind": "hotspot", "big": "100%", "count": "312 phones", "names": ["Grandma's tablet", ...], "more": "+ 308 more"}
  {"kind": "chat", "name": "Grandma", "who": "gran",
   "bubbles": [["time", "Today 6:02 PM"], ["text", ["line 1", "line 2"]], ["hearts", 21, "x47"]]}
  {"kind": "notice", "title": "Wi-Fi", "big": "0 BARS", "lines": ["...", "..."], "colour": [230, 60, 60]}
  {"kind": "lock"}                                                             the hand-held phone lock screen
  {"kind": "town_map", "title": "TOWN MAP"}                                    the folded paper map
"avatar": {"face": "smile", "skin": [235, 200, 168], "hair": [222, 226, 232]} draws any contact picture.

Phone screens are 1080 x 2216 (big_phone's 5.6 x 11.5 stud screen). big_phone's 3D loading spinner turns at 37.8 %
from the bottom: wifi_search and calling leave that area empty. Generic phone look only: no brand, app or logo.
"""
import json, sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

KIT = Path(__file__).resolve().parent
FACES = KIT / "rlook" / "faces"
W, H = 1080, 2216
RADIUS = 118
BEZEL = (21, 22, 27)
INK, WHITE, GREEN, BLUE, RED = (20, 22, 30), (255, 255, 255), (52, 199, 89), (0, 122, 255), (232, 38, 79)
CAST = {                                                         # contact pictures for the recurring cast
    "gran": dict(face="smile", skin=(235, 200, 168), hair=(222, 226, 232), bun=True),
    "max": dict(face="smile", skin=(201, 138, 90), hair=(43, 98, 217), bun=False),
    "teacher": dict(face="smile", skin=(228, 181, 138), hair=(92, 60, 40), bun=True),
    "dad": dict(face="smile", skin=(122, 74, 44), hair=(20, 20, 24), bun=False),
}
_FONTS = {}


def font(weight, size):
    """Inter if the system has it, else the kit's Inter Display Black / DejaVu Sans Bold."""
    key = (weight, size)
    if key in _FONTS:
        return _FONTS[key]
    names = {"regular": "Regular", "medium": "Medium", "semibold": "SemiBold", "bold": "Bold", "black": "Black"}
    for path in ("/usr/share/fonts/inter/Inter.ttc", "/usr/share/fonts/truetype/inter/Inter.ttc",
                 "/Library/Fonts/Inter.ttc", str(Path.home() / ".local/share/fonts/Inter.ttc")):
        if Path(path).exists():
            for i in range(40):
                try:
                    f = ImageFont.truetype(path, size, index=i)
                except OSError:
                    break
                if f.getname() == ("Inter", names[weight]):
                    _FONTS[key] = f
                    return f
    fb = KIT / "fonts" / ("InterDisplay-Black.ttf" if weight in ("bold", "black") else "DejaVuSans-Bold.ttf")
    _FONTS[key] = ImageFont.truetype(str(fb), size)
    return _FONTS[key]


def emoji(ch, size):
    for path in ("/usr/share/fonts/noto/NotoColorEmoji.ttf", "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
                 "/System/Library/Fonts/Apple Color Emoji.ttc"):
        if Path(path).exists():
            try:
                f = ImageFont.truetype(path, 109 if "Noto" in path else 96)
                im = Image.new("RGBA", (140, 132), (0, 0, 0, 0))
                ImageDraw.Draw(im).text((0, 0), ch, font=f, embedded_color=True)
                return im.resize((size, round(size * 132 / 140)), Image.LANCZOS)
            except OSError:
                pass
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((0, 0), "♥", font=font("black", size), fill=RED)
    return im


# ---------------------------------------------------------------- phone pieces
def base(top, bottom):
    im = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(im)
    for y in range(H):
        k = y / (H - 1)
        d.line([(0, y), (W, y)], fill=tuple(round(a + (b - a) * k) for a, b in zip(top, bottom)))
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, W - 1, H - 1], RADIUS, fill=255)
    out = Image.new("RGB", (W, H), BEZEL)
    out.paste(im, (0, 0), mask)
    return out


def _dim(c):
    return tuple(round(v * 0.35 + 128 * 0.65) for v in c[:3])


def status(im, ink, bars=0, label=None):
    """Time, signal bars (or a "No Service" label), Wi-Fi fan, battery, camera pill, home bar."""
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([W / 2 - 150, 34, W / 2 + 150, 120], 43, fill=(0, 0, 0))
    d.text((110, 52), "9:41", font=font("semibold", 54), fill=ink)
    if label:
        d.text((712, 64), label, font=font("medium", 34), fill=ink)
    else:
        for i in range(4):
            h = 18 + i * 10
            d.rounded_rectangle([W - 330 + i * 22, 98 - h, W - 316 + i * 22, 98], 4, fill=ink if i < bars else _dim(ink))
        for r, wdt in ((40, 9), (26, 9), (12, 12)):
            d.arc([W - 220 - r, 96 - r, W - 220 + r, 96 + r], 225, 315, fill=ink if bars else _dim(ink), width=wdt)
    bx = W - 165
    d.rounded_rectangle([bx, 62, bx + 78, 98], 9, outline=ink, width=4)
    d.rounded_rectangle([bx + 7, 69, bx + 58, 91], 4, fill=ink)
    d.rectangle([bx + 81, 73, bx + 86, 87], fill=ink)
    d.rounded_rectangle([W / 2 - 180, H - 40, W / 2 + 180, H - 28], 6, fill=ink)


def centred(d, y, text, f, fill, x=W / 2):
    d.text((x - d.textlength(text, font=f) / 2, y), text, font=f, fill=fill)


def avatar(spec, size):
    a = CAST.get(spec.get("who", ""), None) or spec.get("avatar") or CAST["gran"]
    skin, hair = tuple(a["skin"]), tuple(a["hair"])
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([0, 0, size - 1, size - 1], fill=(205, 222, 240))
    d.rounded_rectangle([size * 0.2, size * 0.24, size * 0.8, size * 0.86], size * 0.12, fill=skin)
    d.pieslice([size * 0.16, size * 0.06, size * 0.84, size * 0.62], 180, 360, fill=hair)
    if a.get("bun"):
        d.ellipse([size * 0.38, 0, size * 0.62, size * 0.2], fill=hair)
    f = Image.open(FACES / f"{a.get('face', 'smile')}.png").convert("RGBA").resize((round(size * 0.52),) * 2)
    im.alpha_composite(f, (round(size * 0.24), round(size * 0.36)))
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size - 1, size - 1], fill=255)
    im.putalpha(mask)
    return im


# ---------------------------------------------------------------- screens
def wifi_search(s):
    im = base((246, 247, 251), (236, 239, 246))
    status(im, INK, label="No Service")
    d = ImageDraw.Draw(im)
    d.text((70, 230), s.get("title", "Wi-Fi"), font=font("bold", 96), fill=INK)
    d.rounded_rectangle([50, 390, W - 50, 530], 36, fill=WHITE)
    d.text((100, 430), "Wi-Fi", font=font("medium", 52), fill=INK)
    d.rounded_rectangle([W - 250, 420, W - 100, 500], 40, fill=GREEN)
    d.ellipse([W - 178, 424, W - 104, 496], fill=WHITE)
    d.text((80, 590), "NETWORKS", font=font("medium", 38), fill=(120, 124, 136))
    d.rounded_rectangle([50, 650, W - 50, 1040], 36, fill=WHITE)
    for i, y in enumerate((690, 820, 950)):
        d.rounded_rectangle([110, y, 110 + (520 - i * 90), y + 44], 22, fill=(232, 235, 242))
    centred(d, 1110, s.get("status", "Searching..."), font("semibold", 64), INK)
    for i, ln in enumerate(s.get("hint", ["No networks found nearby"])):
        centred(d, 1560 + 65 * i, ln, font("medium" if i else "regular", 42), BLUE if i else (120, 124, 136))
    return im


def calling(s):
    im = base((44, 58, 92), (14, 18, 34))
    status(im, WHITE, label="No Service")
    d = ImageDraw.Draw(im)
    av = avatar(s, 360)
    im.paste(av, ((W - 360) // 2, 330), av)
    centred(d, 740, s.get("name", "Grandma"), font("semibold", 92), WHITE)
    centred(d, 870, s.get("status", "calling..."), font("regular", 54), (200, 208, 230))
    for x, label in ((W * 0.22, "mute"), (W * 0.5, "keypad"), (W * 0.78, "speaker")):
        d.ellipse([x - 95, 1525, x + 95, 1715], fill=(70, 80, 106))
        centred(d, 1735, label, font("regular", 38), (220, 226, 240), x=x)
    d.ellipse([W / 2 - 105, 1775, W / 2 + 105, 1985], fill=(255, 59, 48))
    d.rounded_rectangle([W / 2 - 62, 1866, W / 2 + 62, 1896], 15, fill=WHITE)
    return im


def hotspot(s):
    im = base((236, 252, 241), (214, 245, 224))
    status(im, INK, bars=4)
    d = ImageDraw.Draw(im)
    d.text((70, 230), s.get("title", "Hotspot"), font=font("bold", 96), fill=INK)
    d.rounded_rectangle([50, 400, W - 50, 900], 44, fill=GREEN)
    centred(d, 450, s.get("label", "SIGNAL"), font("bold", 70), WHITE)
    centred(d, 540, s.get("big", "100%"), font("black", 230), WHITE)
    centred(d, 960, s.get("sub", "Sharing with"), font("medium", 60), (40, 60, 48))
    centred(d, 1040, s.get("count", ""), font("black", 120), (20, 120, 60))
    names = s.get("names", [])
    if names:
        d.rounded_rectangle([50, 1240, W - 50, 1240 + 130 * len(names)], 36, fill=WHITE)
        for i, n in enumerate(names):
            y = 1240 + 130 * i
            d.ellipse([90, y + 40, 140, y + 90], fill=GREEN)
            d.text((175, y + 38), n, font=font("medium", 50), fill=INK)
    if s.get("more"):
        centred(d, 1260 + 130 * len(names), s["more"], font("semibold", 54), (20, 120, 60))
    return im


def chat(s):
    im = base((250, 250, 252), (243, 244, 248))
    status(im, INK, label="No Service")
    d = ImageDraw.Draw(im)
    d.rectangle([0, 150, W, 440], fill=(244, 245, 249))
    av = avatar(s, 150)
    im.paste(av, ((W - 150) // 2, 175), av)
    centred(d, 340, s.get("name", "Grandma"), font("semibold", 46), INK)
    d.line([(0, 440), (W, 440)], fill=(222, 224, 230), width=3)
    y = 520
    for b in s.get("bubbles", []):
        if b[0] == "text":
            f = font("medium", 58)
            w = max(d.textlength(t, font=f) for t in b[1]) + 80
            h = 74 * len(b[1]) + 50
            d.rounded_rectangle([60, y, 60 + w, y + h], 46, fill=(229, 231, 237))
            for i, t in enumerate(b[1]):
                d.text((100, y + 26 + 74 * i), t, font=f, fill=INK)
            y += h + 40
        elif b[0] == "hearts":
            n, label = b[1], b[2] if len(b) > 2 else ""
            h = 30 + 100 * ((n + 6) // 7) + 110
            d.rounded_rectangle([60, y, W - 160, y + h], 46, fill=(229, 231, 237))
            em = emoji("❤️", 96)
            for i in range(n):
                im.paste(em, (100 + (i % 7) * 108, y + 30 + (i // 7) * 100), em)
            d.text((W - 400, y + h - 105), label, font=font("black", 80), fill=RED)
            y += h + 40
        elif b[0] == "time":
            centred(d, y, b[1], font("medium", 38), (140, 144, 156))
            y += 80
    d.rounded_rectangle([50, H - 190, W - 50, H - 90], 50, outline=(210, 213, 222), width=4)
    d.text((100, H - 168), "Message", font=font("regular", 46), fill=(160, 164, 176))
    return im


def notice(s):
    """A big status card: a warning, a counter, a result."""
    colour = tuple(s.get("colour", [230, 60, 60]))
    im = base((246, 247, 251), (236, 239, 246))
    status(im, INK, label=s.get("status_label", "No Service"))
    d = ImageDraw.Draw(im)
    d.text((70, 230), s.get("title", ""), font=font("bold", 96), fill=INK)
    d.rounded_rectangle([50, 400, W - 50, 900], 44, fill=colour)
    centred(d, 560, s.get("big", ""), font("black", 200), WHITE)
    for i, ln in enumerate(s.get("lines", [])):
        centred(d, 1000 + 90 * i, ln, font("semibold", 64), INK)
    return im


def lock(s=None):
    w, h = 520, 960
    im = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(im)
    for y in range(h):
        k = y / (h - 1)
        d.line([(0, y), (w, y)], fill=(round(70 + 120 * k), round(170 - 60 * k), round(255 - 40 * k)))
    for cx, cy, r in ((120, 300, 220), (420, 700, 260), (300, 980, 200)):
        blob = Image.new("L", (w, h), 0)
        ImageDraw.Draw(blob).ellipse([cx - r, cy - r, cx + r, cy + r], fill=110)
        im.paste(WHITE, (0, 0), blob.filter(ImageFilter.GaussianBlur(60)))
    d = ImageDraw.Draw(im)
    f = font("semibold", 150)
    d.text(((w - d.textlength("9:41", font=f)) / 2, 140), "9:41", font=f, fill=WHITE)
    for i in range(3):
        d.rounded_rectangle([40, 520 + i * 120, w - 40, 610 + i * 120], 28, fill=WHITE)
        d.rounded_rectangle([70, 545 + i * 120, 110, 585 + i * 120], 10, fill=GREEN if i == 0 else BLUE)
        d.rounded_rectangle([130, 550 + i * 120, 390 - i * 50, 572 + i * 120], 10, fill=(200, 205, 215))
    return im


def town_map(s=None):
    s = s or {}
    w, h = 1530, 1080
    im = Image.new("RGB", (w, h), (238, 226, 192))
    d = ImageDraw.Draw(im)
    for x in range(0, w, 6):
        d.line([(x, 0), (x, h)], fill=(234, 221, 186) if (x // 6) % 2 else (240, 229, 196))
    d.rounded_rectangle([40, 40, w - 40, h - 40], 18, fill=(246, 238, 214), outline=(120, 100, 70), width=6)
    d.polygon([(40, 640), (300, 560), (560, 600), (820, 520), (1100, 560), (1490, 470), (1490, 560), (1100, 650),
               (820, 610), (560, 690), (300, 650), (40, 730)], fill=(140, 196, 232))
    d.rounded_rectangle([1000, 150, 1360, 420], 30, fill=(150, 205, 120))
    for cx, cy in ((1080, 230), (1200, 300), (1290, 210), (1120, 350)):
        d.ellipse([cx - 28, cy - 28, cx + 28, cy + 28], fill=(90, 160, 80))
    for x in (300, 700, 1000):
        d.rectangle([x - 22, 40, x + 22, h - 40], fill=WHITE, outline=(180, 170, 150), width=3)
    for y in (300, 860):
        d.rectangle([40, y - 22, w - 40, y + 22], fill=WHITE, outline=(180, 170, 150), width=3)
    d.rectangle([40, 456, w - 40, 504], fill=(250, 210, 90), outline=(190, 150, 60), width=3)
    for x, y in ((520, 170), (520, 400), (180, 170), (850, 170), (180, 760), (520, 760), (850, 760), (1200, 760)):
        d.rounded_rectangle([x - 90, y - 70, x + 90, y + 70], 10, fill=(225, 210, 180))
    lab = font("bold", 34)
    for (x, y), t in zip(((70, 420), (70, 265), (70, 825)), s.get("streets", ["MAIN ST", "OAK AVE", "RIVER RD"])):
        d.text((x, y), t, font=lab, fill=(110, 80, 30))
    d.text((1040, 180), "PARK", font=font("black", 40), fill=(40, 100, 40))
    d.rounded_rectangle([640, 670, 760, 750], 8, fill=(200, 80, 70))
    d.text((620, 776), s.get("landmark", "TOWN HALL"), font=font("bold", 28), fill=(110, 40, 30))
    route = [(160, 960), (300, 960), (300, 480), (700, 480), (700, 300), (1000, 300), (1000, 220)]
    for (x0, y0), (x1, y1) in zip(route, route[1:]):
        n = max(1, int(((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5 // 36))
        for k in range(0, n, 2):
            a, b = k / n, min(1, (k + 1) / n)
            d.line([(x0 + (x1 - x0) * a, y0 + (y1 - y0) * a), (x0 + (x1 - x0) * b, y0 + (y1 - y0) * b)],
                   fill=(220, 40, 40), width=14)
    px, py = 160, 960
    d.ellipse([px - 34, py - 34, px + 34, py + 34], fill=(220, 40, 40), outline=WHITE, width=6)
    d.rounded_rectangle([px + 40, py - 70, px + 330, py - 18], 12, fill=WHITE, outline=(220, 40, 40), width=4)
    d.text((px + 56, py - 64), "YOU ARE HERE", font=font("black", 34), fill=(220, 40, 40))
    cx, cy = w - 150, h - 170
    d.ellipse([cx - 70, cy - 70, cx + 70, cy + 70], fill=(250, 244, 226), outline=(120, 100, 70), width=5)
    d.polygon([(cx, cy - 62), (cx - 16, cy), (cx + 16, cy)], fill=(200, 50, 40))
    d.polygon([(cx, cy + 62), (cx - 16, cy), (cx + 16, cy)], fill=(90, 80, 70))
    d.text((cx - 13, cy - 118), "N", font=font("black", 40), fill=(90, 70, 40))
    d.rounded_rectangle([w / 2 - 220, 56, w / 2 + 220, 126], 14, fill=(120, 90, 50))
    centred(d, 60, s.get("title", "TOWN MAP"), font("black", 54), (250, 240, 210), x=w / 2)
    for k in (1, 2):
        x = w * k / 3
        d.line([(x, 0), (x, h)], fill=(205, 190, 155), width=6)
        d.line([(x + 6, 0), (x + 6, h)], fill=(250, 244, 226), width=3)
    d.line([(0, h / 2), (w, h / 2)], fill=(222, 208, 172), width=3)
    return im


KINDS = {"wifi_search": wifi_search, "calling": calling, "hotspot": hotspot, "chat": chat, "notice": notice,
         "lock": lock, "town_map": town_map}


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    if sys.argv[1] == "--defaults":
        out = KIT / "pictures"
        out.mkdir(exist_ok=True)
        for name, im in (("lock", lock()), ("map", town_map())):
            im.save(out / f"{name}.png")
            print("wrote", out / f"{name}.png")
        return
    ep = Path(sys.argv[1]).resolve()
    spec = json.loads((ep / "pictures.json").read_text())
    out = ep / "pictures"
    out.mkdir(exist_ok=True)
    for name, s in spec.items():
        if s.get("kind") not in KINDS:
            sys.exit(f"{name}: kind must be one of {', '.join(KINDS)}")
        KINDS[s["kind"]](s).save(out / f"{name}.png")
        print("wrote", out / f"{name}.png")


if __name__ == "__main__":
    main()
