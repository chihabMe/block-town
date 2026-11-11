"""Draw the flat cartoon face decals (our own drawings, no Roblox catalog faces) as transparent PNGs.

Usage: python3 -I faces.py OUT_DIR     (needs Pillow; writes OUT_DIR/<expression>.png, 512x512)
The square maps onto the whole front of the block head. Features sit in the middle so hair can cover the top.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

S = 1024  # draw big, shrink for smooth edges
K = (20, 16, 18, 255)
WHITE = (255, 255, 255, 255)
BLUSH = (236, 120, 110, 120)
MOUTH = (120, 22, 30, 255)
TONGUE = (226, 96, 96, 255)
EX, EY = 190, 500  # eye offset from centre x, eye height


def eye_dot(d, cx, cy, w=58, h=82):
    d.ellipse([cx - w, cy - h, cx + w, cy + h], fill=K)
    d.ellipse([cx - w * 0.05, cy - h * 0.7, cx + w * 0.55, cy - h * 0.12], fill=WHITE)


def eye_wide(d, cx, cy, r=104, pr=44, look=(0, 0)):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=K)
    d.ellipse([cx - r + 20, cy - r + 20, cx + r - 20, cy + r - 20], fill=WHITE)
    px, py = cx + look[0], cy + look[1]
    d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=K)
    d.ellipse([px + 4, py - pr * 0.75, px + pr * 0.6, py - pr * 0.15], fill=WHITE)


def eye_closed(d, cx, cy, up=True, w=74):
    box = [cx - w, cy - 46, cx + w, cy + 70] if up else [cx - w, cy - 70, cx + w, cy + 46]
    d.arc(box, 200 if up else 20, 340 if up else 160, fill=K, width=26)


def brow(d, cx, cy, tilt=0, w=96, t=26):
    """tilt > 0 lowers the inner end (angry); tilt < 0 raises it (worried)."""
    side = 1 if cx > S / 2 else -1
    inner, outer = (cx - side * w, cy + tilt), (cx + side * w, cy - tilt)
    d.line([inner, outer], fill=K, width=t)
    for p in (inner, outer):
        d.ellipse([p[0] - t / 2, p[1] - t / 2, p[0] + t / 2, p[1] + t / 2], fill=K)


def arc(d, cx, cy, w, h, smile=True, t=26):
    d.arc([cx - w, cy - h, cx + w, cy + h], 20 if smile else 200, 160 if smile else 340, fill=K, width=t)


def zigzag(d, cx, cy, w=150, h=34, n=7, t=22):
    pts = [(cx - w + 2 * w * i / (n - 1), cy + (h if i % 2 else -h)) for i in range(n)]
    d.line(pts, fill=K, width=t, joint="curve")


def blush(img, y=640, w=84, h=46):
    layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    for sx in (-1, 1):
        cx = S / 2 + sx * 300
        ld.ellipse([cx - w, y - h, cx + w, y + h], fill=BLUSH)
    img.alpha_composite(layer)


def face(name):
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    L, R = S / 2 - EX, S / 2 + EX
    if name == "smile":
        eye_dot(d, L, EY), eye_dot(d, R, EY)
        arc(d, S / 2, 640, 120, 110)
    elif name == "happy":
        blush(img)
        eye_closed(d, L, EY), eye_closed(d, R, EY)
        d.pieslice([S / 2 - 130, 560, S / 2 + 130, 800], 0, 180, fill=MOUTH, outline=K, width=18)
        d.pieslice([S / 2 - 80, 700, S / 2 + 80, 800], 0, 180, fill=TONGUE)
    elif name == "stern":
        blush(img)
        eye_dot(d, L, EY + 10, 50, 70), eye_dot(d, R, EY + 10, 50, 70)
        brow(d, L, 380, 30), brow(d, R, 380, 30)
        d.line([(S / 2 - 90, 720), (S / 2 + 90, 720)], fill=K, width=26)
    elif name == "angry":
        eye_dot(d, L, EY + 20, 50, 62), eye_dot(d, R, EY + 20, 50, 62)
        brow(d, L, 390, 52, t=32), brow(d, R, 390, 52, t=32)
        arc(d, S / 2, 800, 110, 100, smile=False)
    elif name == "sad":
        blush(img)
        eye_dot(d, L, EY + 10), eye_dot(d, R, EY + 10)
        brow(d, L, 360, -40), brow(d, R, 360, -40)
        arc(d, S / 2, 800, 100, 90, smile=False)
    elif name == "scared":
        blush(img)
        eye_wide(d, L, EY, look=(0, 10)), eye_wide(d, R, EY, look=(0, 10))
        brow(d, L, 340, -44), brow(d, R, 340, -44)
        zigzag(d, S / 2, 740)
    elif name == "shock":
        eye_wide(d, L, EY, pr=36), eye_wide(d, R, EY, pr=36)
        brow(d, L, 330, -24), brow(d, R, 330, -24)
        d.ellipse([S / 2 - 52, 670, S / 2 + 52, 810], fill=MOUTH, outline=K, width=16)
    elif name == "smug":
        eye_dot(d, L, EY + 10, 50, 60), eye_dot(d, R, EY + 10, 50, 60)
        brow(d, L, 400, 34), brow(d, R, 370, -10)
        d.arc([S / 2 - 150, 560, S / 2 + 110, 760], 20, 120, fill=K, width=26)
    elif name == "laugh":
        eye_closed(d, L, EY + 10, up=False), eye_closed(d, R, EY + 10, up=False)
        brow(d, L, 380, 40), brow(d, R, 380, 40)
        d.pieslice([S / 2 - 150, 540, S / 2 + 150, 830], 0, 180, fill=MOUTH, outline=K, width=18)
        d.rectangle([S / 2 - 110, 690, S / 2 + 110, 722], fill=WHITE)
    elif name == "determined":
        eye_dot(d, L, EY + 16, 52, 66), eye_dot(d, R, EY + 16, 52, 66)
        brow(d, L, 390, 40), brow(d, R, 390, 40)
        d.arc([S / 2 - 110, 640, S / 2 + 110, 780], 30, 150, fill=K, width=26)
    elif name == "glasses":  # stern with square glasses, for a teacher
        for cx in (L, R):
            d.rounded_rectangle([cx - 120, EY - 90, cx + 120, EY + 100], 24, outline=K, width=24)
            eye_dot(d, cx, EY + 10, 36, 48)
        d.line([(L + 120, EY), (R - 120, EY)], fill=K, width=24)
        brow(d, L, 360, 40), brow(d, R, 360, 40)
        arc(d, S / 2, 830, 90, 80, smile=False)
    return img.resize((512, 512), Image.LANCZOS)


NAMES = ["smile", "happy", "stern", "angry", "sad", "scared", "shock", "smug", "laugh", "determined", "glasses"]
if __name__ == "__main__":
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    for n in NAMES:
        face(n).save(out / f"{n}.png")
    sheet = Image.new("RGBA", (512 * 6, 512 * 2), (222, 178, 122, 255))
    for i, n in enumerate(NAMES):
        sheet.alpha_composite(face(n), (512 * (i % 6), 512 * (i // 6)))
    sheet.convert("RGB").resize((1536, 512)).save(out / "_sheet.jpg")
    print("wrote", len(NAMES), "faces to", out)
