# Idea 2: one word changes font on every frame, as in the reference. Writes an alpha overlay for Resolve (27 frames, 12.5-13.4s).
import os, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HOME = os.path.expanduser("~").replace("\\", "/")
OUT = HOME + "/Documents/video-edit/projects/project-4/extras/idea-2-ending/word-flicker2.mov"
BIN = HOME + "/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0.2-full_build/bin/ffmpeg.exe"
FONTS = "C:/Windows/Fonts/"
CW, CH, N = 3840, 2160, 27
RED = (189, 19, 33)
BOLD = ("impact.ttf", "VOICES", .28)
HAND = [f for f in [("MISTRAL.TTF", "Voices", .36), ("segoepr.ttf", "voices", .36), ("BRUSHSCI.TTF", "Voices", .36), ("Inkfree.ttf", "voices", .36),
                    ("FREESCPT.TTF", "Voices", .36), ("CHILLER.TTF", "VOICES", .34), ("mvboli.ttf", "voices", .36)] if os.path.exists(FONTS + f[0])]
print("hand fonts", [f[0] for f in HAND])


def frame(font_file, text, y):
    f = ImageFont.truetype(FONTS + font_file, 400)
    l, t, r, b = f.getbbox(text)
    f = ImageFont.truetype(FONTS + font_file, int(400 * 2000 / (r - l)))   # every style spans the same width
    l, t, r, b = f.getbbox(text)
    img = Image.new("L", (CW, CH), 0)
    ImageDraw.Draw(img).text((CW / 2 - (l + r) / 2, CH * y - (t + b) / 2), text, font=f, fill=255)
    a = np.asarray(img, np.uint8)
    out = np.zeros((CH, CW, 4), np.uint8)
    out[..., 0], out[..., 1], out[..., 2], out[..., 3] = RED[0], RED[1], RED[2], a
    return out


p = subprocess.Popen([BIN, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{CW}x{CH}", "-r", "30", "-i", "-",
                      "-c:v", "prores_ks", "-profile:v", "4", "-pix_fmt", "yuva444p10le", "-alpha_bits", "16", OUT], stdin=subprocess.PIPE)
for k in range(N):
    beat = k // 3                     # a new font every 3 frames
    style = BOLD if beat % 2 == 0 else HAND[(beat // 2) % len(HAND)]
    p.stdin.write(frame(*style).tobytes())
p.stdin.close()
p.wait()
print("done")
