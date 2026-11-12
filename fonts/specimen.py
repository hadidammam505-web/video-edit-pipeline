# Font specimen sheet for the curated OFL set; checks each file loads.
import glob, os
from PIL import Image, ImageDraw, ImageFont, features
D = os.path.dirname(os.path.abspath(__file__))
fs = sorted(glob.glob(D + "/*/*.ttf"))
img = Image.new("RGB", (1800, 90 * len(fs) + 40), (14, 14, 16)); d = ImageDraw.Draw(img)
raqm = features.check("raqm")
for i, f in enumerate(fs):
    arabic = "Arabic" in f or "tajawal" in f.lower()
    text = ("ابدأ الآن · DAY 47" if arabic and raqm else "DAY 47 ") + "  STRONGER EVERY REP  Muscle 0123"
    font = ImageFont.truetype(f, 56)
    d.text((30, 20 + 90 * i), text, font=font, fill=(240, 240, 240))
    d.text((1450, 40 + 90 * i), os.path.basename(f)[:28], font=ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 18), fill=(150, 150, 150))
img.save(D + "/specimen.png"); print(len(fs), "fonts, raqm:", raqm)
