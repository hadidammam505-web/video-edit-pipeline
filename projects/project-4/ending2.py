# Idea 2 ending: the word fills the body, a white flash, then the same camera angle with the seat empty.
# Writes ending-base.mp4 (ungraded picture, frames 746-793) and ending-overlay.mov (word and flashes with alpha, frames 746-780).
import os, subprocess, sys
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HOME = os.path.expanduser("~").replace("\\", "/")
W = HOME + "/Documents/video-edit/projects/project-4/extras"
E = W + "/idea-2-ending"
BIN = HOME + "/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0.2-full_build/bin/ffmpeg.exe"
CLIP = HOME + "/Desktop/edting/storage/project 4/A001_11081714_C079.MOV"
CW, CH = 3840, 2160
WORD = "LOVELY"
RED = (189, 19, 33)
START = 736           # first frame of the layers; the word lands at 737, drops out, and stays from 741
FLASH = {39: 38, 40: 38, 43: 32, 44: 32}   # overlay frame -> which body mask flashes
TOTAL = 45            # 736-780
PLATE_AT = 71.2       # the seat is empty from here on
ROWS = [190, 330, 190, 400, 240, 470, 150]      # letter heights, top to bottom, as in the reference


def word_layer():
    img = Image.new("L", (CW, CH), 0)
    d = ImageDraw.Draw(img)
    y = 10
    for i, cap in enumerate(ROWS):
        # find the font size whose capital letters are this tall
        size = int(cap / .79)
        font = ImageFont.truetype("C:/Windows/Fonts/impact.ttf", size)
        l, t, r, b = font.getbbox(WORD)
        step = r - l + int(cap * .18)
        x = 1800 - (r - l) // 2 - step * 3   # one whole word sits centred on the body
        while x < CW:
            d.text((x, y - t), WORD, font=font, fill=255)
            x += step
        y += b - t + 26
    return np.asarray(img, np.float32) / 255


def mask(k):
    rec = START + k
    path = f"{E}/out2/f{rec - 736 + 1:04d}.png" if rec < 746 else f"{E}/out/f{rec - 746 + 1:04d}.png"
    m = cv2.imdecode(np.fromfile(path, np.uint8), 0)
    m = cv2.dilate(m, np.ones((7, 7), np.uint8))
    cs, _ = cv2.findContours((m > 127).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(m, cs, -1, 255, -1)   # no holes in the body
    m = cv2.resize(m, (CW, CH), interpolation=cv2.INTER_CUBIC)
    return cv2.GaussianBlur(m, (0, 0), 3).astype(np.float32) / 255


def base():
    # fade starts 6 frames into the empty shot and reaches black at frame 793
    graph = ("[0:v]select='between(n,746,774)',setpts=N/30/TB,format=yuv420p[a];"
             "[1:v]fps=30,crop=1944:1092:150:60,scale=3840:2160:flags=lanczos,setsar=1,format=yuv420p,"
             "fade=t=out:st=0.2:d=0.43:color=black,setpts=N/30/TB[b];"
             "[2:v]fps=30,crop=1944:1092:150:60,scale=3840:2160:flags=lanczos,setsar=1,format=yuv420p,trim=end_frame=10,setpts=N/30/TB[p];"
             "[p][a][b]concat=n=3:v=1:a=0[v]")
    subprocess.run([BIN, "-y", "-loglevel", "error", "-i", W + "/idea-2-neutral.mp4", "-ss", str(PLATE_AT), "-t", "0.64", "-i", CLIP, "-ss", "40.667", "-t", "0.5", "-i", CLIP,
                    "-filter_complex", graph, "-map", "[v]", "-frames:v", "58", "-r", "30", "-c:v", "libx264", "-preset", "slow", "-crf", "12",
                    E + "/ending2-base.mp4"], check=True)


def overlay():
    text = word_layer()
    p = subprocess.Popen([BIN, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{CW}x{CH}", "-r", "30", "-i", "-",
                          "-c:v", "prores_ks", "-profile:v", "4", "-pix_fmt", "yuva444p10le", "-alpha_bits", "16", E + "/ending2-overlay.mov"], stdin=subprocess.PIPE)
    for k in range(TOTAL):
        out = np.zeros((CH, CW, 4), np.uint8)
        if START + k == 737 or 741 <= START + k <= 774:
            a = mask(k)
            for c in range(3):
                out[..., c] = (text * RED[c]).astype(np.uint8)
            out[..., 3] = (a * 255).astype(np.uint8)
        elif k in FLASH:
            a = mask(FLASH[k])
            out[..., :3] = 255
            out[..., 3] = (np.clip(a + .55 * cv2.GaussianBlur(a, (0, 0), 28), 0, 1) * 255).astype(np.uint8)
        p.stdin.write(out.tobytes())
    p.stdin.close()
    p.wait()


os.makedirs(E, exist_ok=True)
base()
overlay()
print("done")
