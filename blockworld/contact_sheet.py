"""One picture with a still of every shot, numbered, for review.   python3 -I SKILL/blockworld/contact_sheet.py EPISODE

Uses the "b" stills (85% through each shot) from the stills mode. Writes EPISODE/CONTACT_SHEET.jpg. Needs Pillow."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ep = Path(sys.argv[1]).resolve()
files = sorted((ep / "stills").glob("*_b.jpg"))
if not files:
    sys.exit(f"no stills in {ep / 'stills'}: run the stills mode first")
font_path = Path(__file__).resolve().parent / "fonts" / "DejaVuSans-Bold.ttf"
font = ImageFont.truetype(str(font_path), 20)
W, H, cols = 240, 427, 7
rows = (len(files) + cols - 1) // cols
sheet = Image.new("RGB", (cols * (W + 4), rows * (H + 4)), "white")
d = ImageDraw.Draw(sheet)
for i, p in enumerate(files):
    x, y = (i % cols) * (W + 4), (i // cols) * (H + 4)
    sheet.paste(Image.open(p).convert("RGB").resize((W, H)), (x, y))
    d.text((x + 5, y + 5), f"{i + 1} {p.stem.split('_', 1)[1][:-2]}", fill="white", font=font, stroke_width=3,
           stroke_fill="black")
sheet.save(ep / "CONTACT_SHEET.jpg", quality=82)
print("wrote", ep / "CONTACT_SHEET.jpg", f"({len(files)} shots)")
