# Project 5: copy of the "locked in" reference (17.5 s, 525 frames at 30 fps), rebuilt with the user's gym and kitchen footage.
# Words are my own, written to the reference's rhythm; the user will swap them.
# Audio: song-noig.wav is the reference song cut at 13.30 s, because the Instagram download ends with the Instagram outro sound (13.8-15.5 s).
# usage: build5.py [preview]   (preview = 1280x720, fast)
import json, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HOME = os.path.expanduser("~").replace("\\", "/")
BIN = HOME + "/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0.2-full_build/bin/ffmpeg.exe"
ST = HOME + "/Desktop/edting/storage/project 5/"
REF = HOME + "/Documents/video-edit/refs/project-5"
W = HOME + "/Documents/video-edit/projects/project-5"
FONTS = HOME + "/Documents/video-edit/fonts/"
OUT = HOME + "/Desktop/edting/results/project 5/idea-1.mp4"
PREVIEW = "preview" in sys.argv
CW, CH = (720, 1280) if PREVIEW else (2160, 3840)   # vertical, as the user filmed it
TMP = W + ("/tmp-preview" if PREVIEW else "/tmp")
os.makedirs(TMP, exist_ok=True)
RED = (190, 20, 34)

CLIP = {k: ST + f for k, f in [("C086", "A001_11091651_C086.mov"), ("C087", "A001_11091657_C087.mov"), ("C088", "A001_11091714_C088.mov"),
                               ("C089", "A001_11091719_C089.mov"), ("C090", "A001_11091723_C090.mov"), ("C091", "A001_11091750_C091.mov"), ("C092", "A001_11091756_C092.mov"),
                               ("COOK", "100E8BE3-D509-4B0F-BCFD-F8C9E03A9F53.MP4")]}
CLIP["C085"] = HOME + "/Desktop/edting/storage/project 4/A001_11081757_C085.MOV"   # held double biceps, landscape (2160x1214)
# moody look close to the reference: low key, warm shadows, soft edges
GRADE = "eq=contrast=1.12:brightness=-0.09:saturation=0.82:gamma=0.82,colorbalance=rs=0.06:gs=-0.01:bs=-0.04:rm=0.03:bm=-0.02,vignette=angle=PI/4.2"

# crop = (w, h, x, y) in the rotated source picture; the gym clips are 2160x3840 portrait, the kitchen clip is 1440x2560 with a landscape band (kept whole, as filmed)
SHOTS = [  # name, clip, start s, frames, crop, extra filter
    ("open", "C087", 40.10, 44, (2160, 3840, 0, 0), ""),
    # the words now sit on calm, clean first reps instead of black and white cards (the user's idea, 2026-11-11)
    ("k1",   "C090", 37.00, 34, (2160, 3840, 0, 0), "text"),          # T-bar row from behind
    ("k2",   "C088", 20.90, 33, (2160, 3840, 0, 0), "text"),          # T-bar row, pull ends at the top
    ("k3",   "C086", 42.60, 44, (1620, 2880, 270, 790), "text"),      # seated leg machine, the feet travel the whole rep
    ("k4",   "C090", 40.00, 34, (2160, 3840, 0, 0), "text"),          # T-bar row from behind, wide
    ("k5",   "C088", 26.267, 43, (1440, 2560, 300, 640), "text"),     # the same exercise, close from the front; the pull ends at the top (user, 2026-11-11)
    ("pose", "C085", 33.60, 60, (1440, 810, 470, 200), "band"),       # "locked in." on the held double biceps, letterboxed as filmed (landscape)
    ("k6",   "C087", 45.467, 7, (2160, 3840, 0, 0), "text"),          # leg press again, as at the start; the push ends locked out at 46.0 s
    ("k7",   "C087", 45.70, 8, (1440, 2560, 720, 1100), "text"),      # the same push, closer, feet in frame
    ("A",    "C088", 32.20, 74, (2160, 3840, 0, 0), ""),
    ("B",    "COOK", 12.00, 8,  (1440, 2560, 0, 0), ""),
    ("C",    "C086", 45.40, 14, (1620, 2880, 270, 790), ""),
    ("E",    "C089", 34.63, 5,  (2160, 3840, 0, 0), ""),
    ("F",    "C089", 34.80, 6,  (1440, 2560, 360, 620), ""),          # same moment, closer
    ("G",    "C091", 25.90, 16, (1800, 3200, 360, 400), ""),
    ("H",    "C091", 26.433, 17, (1800, 3200, 360, 400), "dark"),    # same move, sinking into the dark
    ("I",    "COOK", 22.50, 6,  (1440, 2560, 0, 0), ""),
    ("J",    "C092", 45.20, 11, (2160, 3840, 0, 0), ""),
]
# timeline in frames, matching the reference cuts
TL = [("open", 0), ("k1", 44, "no shortcuts"), ("k2", 78, "no days off"),
      ("k3", 111, "nobody's doing the reps for me."), ("k4", 155, "i"), ("k5", 189, "i just"),
      ("A", 232), ("B", 306), ("C", 314), ("E", 328), ("F", 333), ("G", 339), ("H", 355), ("I", 372), ("J", 378),
      ("pose", 389, "locked in."),
      ("blank", 449), ("end", 450)]   # "locked in." holds 2 s on a held pose (user, 2026-11-11)   # "locked in." holds 1.5 s on the frozen lockout, as the music stops
TOTAL = 525


def inter_bold(size):
    f = ImageFont.truetype(FONTS + "inter/Inter-Variable.ttf" if os.path.exists(FONTS + "inter/Inter-Variable.ttf") else FONTS + "inter/Inter[opsz,wght].ttf", size)
    f.set_variation_by_axes([32, 800])
    return f


def serif_italic(size):
    return ImageFont.truetype(FONTS + "instrumentserif/InstrumentSerif-Italic.ttf", size)


SIZE = int(CW * 0.058)       # the longest card line fills about 88% of the vertical width       # reference text: about 24% of the width for a 13-letter line


# Arabic line under each English line (my wording; the user can change it). PIL can't join Arabic letters,
# so Arabic is drawn by headless Edge with Tajawal ExtraBold and trimmed to its ink.
AR = {"no shortcuts": "بلا طرق مختصرة", "no days off": "بلا أيام راحة", "nobody's doing the reps for me.": "محد بيسوي العدّات عني.",
      "i": "أنا", "i just": "أنا بس", "locked in.": "مركّز تمامًا.", "the 100 day journey": "رحلة الـ100 يوم"}
EDGE = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
_ar_cache = {}


def ar_img(text, px):
    """White Arabic text on transparent, trimmed, rendered at px font size."""
    key = (text, px)
    if key in _ar_cache:
        return _ar_cache[key]
    d = TMP + "/ar"
    os.makedirs(d, exist_ok=True)
    name = "ar%03d" % len(_ar_cache)
    w, h = int(px * len(text) * 1.2) + 200, int(px * 2.2)
    html = (f'<!doctype html><html><head><meta charset="utf-8"><style>@font-face{{font-family:"TJ";src:url("file:///{FONTS}tajawal/Tajawal-ExtraBold.ttf");}}'
            f'html,body{{margin:0;background:transparent;width:{w}px;height:{h}px}}div{{font-family:"TJ";font-size:{px}px;color:#fff;direction:rtl;'
            f'text-align:center;line-height:{h}px;white-space:nowrap}}</style></head><body><div>{text}</div></body></html>')
    with open(f"{d}/{name}.html", "w", encoding="utf-8") as fh:
        fh.write(html)
    png = f"{d}/{name}.png"
    win = lambda p: p.replace("/", "\\")       # Edge wants Windows paths for the profile and the screenshot
    subprocess.run([EDGE, "--headless=new", "--user-data-dir=" + win(f"{TMP}/edge-profile-{name}"), "--no-first-run", "--disable-gpu", "--hide-scrollbars",
                    "--force-device-scale-factor=1", "--default-background-color=00000000", f"--window-size={w},{h}",
                    "--screenshot=" + win(png), f"file:///{d}/{name}.html"], check=True, capture_output=True, timeout=90)
    import time
    for _ in range(120):        # Edge writes the file a moment after its launcher exits
        if os.path.exists(png) and os.path.getsize(png) > 0:
            time.sleep(0.3)
            break
        time.sleep(0.25)
    im = Image.open(png).convert("RGBA")
    im = im.crop(im.getchannel("A").getbbox())
    _ar_cache[key] = im
    return im


def text_png(path, text, font, color, scale=1.0, shadow=False, ar=True, cy=0.5):
    img = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    f = font(int(SIZE * scale))
    d = ImageDraw.Draw(img)
    l, t, r, b = d.textbbox((0, 0), text, font=f)
    a = ar_img(AR[text], int(SIZE * 1.05)) if ar and text in AR else None
    gap = SIZE * 0.42
    block = (b - t) + (gap + a.height if a else 0)
    top = CH * cy - block / 2
    pos = ((CW - (r - l)) / 2 - l, top - t)
    layer = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    ImageDraw.Draw(layer).text(pos, text, font=f, fill=color)
    if a:
        tint = Image.new("RGBA", a.size, color[:3] + (255,))
        tint.putalpha(a.getchannel("A"))
        layer.alpha_composite(tint, (int((CW - a.width) / 2), int(top + (b - t) + gap)))
    if shadow:   # a soft dark bed under the words so they read on footage; no glow
        sh = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
        sh.putalpha(layer.getchannel("A").point(lambda v: v * 200 // 255))
        sh = sh.transform(sh.size, Image.AFFINE, (1, 0, 0, 0, 1, -SIZE * 0.04)).filter(ImageFilter.GaussianBlur(SIZE * 0.22))
        img = Image.alpha_composite(sh, img)
    img = Image.alpha_composite(img, layer)
    img.save(path)
    return path


def run(args):
    subprocess.run([BIN, "-nostdin", "-y", "-loglevel", "error"] + args, check=True)


ENC = ["-r", "30", "-c:v", "libx264", "-preset", "medium" if PREVIEW else "slow", "-crf", "20" if PREVIEW else "14", "-pix_fmt", "yuv420p"]


def shot(name, clip, ss, n, crop, extra, out):
    w, h, x, y = crop
    vf = f"crop={w}:{h}:{x}:{y},scale={CW}:{CH}:flags=lanczos,setsar=1,fps=30,{GRADE}"
    if extra == "text":        # a touch darker so the words stay clear
        vf += ",eq=brightness=-0.04:gamma=0.92"
    if extra == "dark":
        vf += f",eq=brightness='-0.22*t/{n / 30:.3f}':eval=frame"
    if extra == "band":        # a landscape picture across the middle of the vertical frame, black above and below
        bh = int(CW * 9 / 16) // 2 * 2
        vf = f"crop={w}:{h}:{x}:{y},scale={CW}:{bh}:flags=lanczos,setsar=1,fps=30,{GRADE},pad={CW}:{CH}:0:{(CH - bh) // 2}:color=0x050505"
    run(["-ss", f"{ss:.3f}", "-i", CLIP[clip], "-vf", vf, "-frames:v", str(n), "-an"] + ENC + [out])


def card(color, text, n, out):
    fg = (12, 12, 12, 255) if color == "white" else (242, 242, 242, 255)
    png = text_png(f"{out}.png", text, inter_bold, fg)
    run(["-f", "lavfi", "-i", f"color=c={'0xF7F7F7' if color == 'white' else '0x050505'}:s={CW}x{CH}:r=30", "-i", png,
         "-filter_complex", "[0][1]overlay", "-frames:v", str(n)] + ENC + [out])


def opening(n, out):
    bold = text_png(TMP + "/open-bold.png", "no shortcuts", inter_bold, (242, 242, 242, 255), shadow=True)
    ital = text_png(TMP + "/open-ital.png", "no shortcuts", serif_italic, (242, 242, 242, 255), scale=1.08, shadow=True)
    raw = TMP + "/open-raw.mp4"
    shot(*SHOTS[0], raw)
    run(["-i", raw, "-loop", "1", "-i", bold, "-loop", "1", "-i", ital, "-filter_complex",
         "[0][1]overlay=enable='eq(mod(n\\,2)\\,0)'[a];[a][2]overlay=enable='eq(mod(n\\,2)\\,1)'", "-frames:v", str(n)] + ENC + [out])


def endcard(n, out):
    # the reference end card: pops in white (405-412), fades to colour (419-428), holds, fades back to white (481-490)
    frames = TMP + "/end"
    os.makedirs(frames, exist_ok=True)
    txt = "the 100 day journey"
    a_full = ar_img(AR[txt], int(SIZE * 1.6 * 1.05))
    for k in range(n):
        # same moves as the reference end card, fitted to its shorter length: pop in, fade to red, back to white
        pop = min(1.0, 0.9 + 0.1 * k / 7)
        mix = np.clip((k - 10) / 9, 0, 1) * (1 - np.clip((k - (n - 15)) / 9, 0, 1))
        col = tuple(int(242 + (c - 242) * mix) for c in RED) + (255,)
        img = Image.new("RGBA", (CW, CH), (5, 5, 5, 255))
        fnt = inter_bold(int(SIZE * 1.6 * pop))
        d = ImageDraw.Draw(img)
        l, t, r, b = d.textbbox((0, 0), txt, font=fnt)
        a = a_full.resize((max(1, int(a_full.width * pop)), max(1, int(a_full.height * pop))), Image.LANCZOS)
        gap = SIZE * 1.6 * pop * 0.42
        top = CH * 0.5 - ((b - t) + gap + a.height) / 2
        d.text(((CW - (r - l)) / 2 - l, top - t), txt, font=fnt, fill=col)
        tint = Image.new("RGBA", a.size, col[:3] + (255,))
        tint.putalpha(a.getchannel("A"))
        img.alpha_composite(tint, (int((CW - a.width) / 2), int(top + (b - t) + gap)))
        img.convert("RGB").save(f"{frames}/f{k:04d}.png")
    run(["-framerate", "30", "-i", frames + "/f%04d.png", "-frames:v", str(n)] + ENC + [out])


TRACK = json.load(open(W + "/track/centroids.json"))   # weight centre per frame, from SAM 2.1 (tools/sam2track.py) on 720x1280 copies of each shot


def tracked_words(kind, text, n, raw, out):
    """The words ride on the weight: a thin line and a dot tie them to the plate, pad or feet that SAM 2 tracked."""
    full = Image.open(text_png(out[:-4] + "-text.png", text, inter_bold, (242, 242, 242, 255), shadow=True))
    box = full.getchannel("A").point(lambda v: 255 if v > 40 else 0).getbbox()
    block = full.crop(box)
    k = CW / 720
    pts = np.array([c[:2] for c in TRACK[kind][:n]], float) * k
    pts = np.array([pts[max(0, i - 2):i + 3].mean(0) for i in range(len(pts))])   # steady, but still moves with the rep
    radius = np.sqrt(max(c[2] for c in TRACK[kind][:n]) / np.pi) * k
    lw, dot, stem = max(2, int(SIZE * 0.03)), max(4, int(SIZE * 0.09)), SIZE * 1.3
    frames = out[:-4] + "-layer"
    os.makedirs(frames, exist_ok=True)
    for i in range(n):
        ax, ay = pts[min(i, len(pts) - 1)]
        ay -= radius * 0.85                                   # top of the weight
        bw, bh = block.size
        bx = min(max(ax, bw / 2 + CW * 0.05), CW - bw / 2 - CW * 0.05)
        by = max(ay - stem - bh, CH * 0.12)                   # block top
        layer = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
        g = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
        d = ImageDraw.Draw(g)
        grow = min(1.0, (i + 1) / 4)                           # the line draws itself over the first 4 frames
        top = (bx, by + bh + SIZE * 0.25)
        end = (ax + (top[0] - ax) * grow, ay + (top[1] - ay) * grow)
        d.line([(ax, ay), end], fill=(242, 242, 242, 235), width=lw)
        d.ellipse([ax - dot, ay - dot, ax + dot, ay + dot], fill=(242, 242, 242, 255))
        sh = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
        sh.putalpha(g.getchannel("A").point(lambda v: v * 180 // 255))
        layer = Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(SIZE * 0.12)), g)
        layer.alpha_composite(block, (int(bx - bw / 2), int(by)))
        layer.save(f"{frames}/f{i:04d}.png", compress_level=1)
    run(["-i", raw, "-framerate", "30", "-i", frames + "/f%04d.png", "-filter_complex", "[0][1]overlay", "-frames:v", str(n)] + ENC + [out])


def main():
    parts = []
    spans = [(TL[i], (TL[i + 1][1] if i + 1 < len(TL) else TOTAL) - TL[i][1]) for i in range(len(TL))]
    shots = {s[0]: s for s in SHOTS}
    for i, (item, n) in enumerate(spans):
        out = f"{TMP}/p{i:02d}.mp4"
        kind = item[0]
        if kind == "open":
            opening(n, out)
        elif kind == "card":
            card(item[2], item[3], n, out)
        elif kind == "blank":
            run(["-f", "lavfi", "-i", f"color=c=0x050505:s={CW}x{CH}:r=30", "-frames:v", str(n)] + ENC + [out])
        elif kind == "end":
            endcard(n, out)
        elif kind == "freeze":     # hold the last frame of the shot before, words and all
            prev_n = TL[i - 1][1] and (item[1] - TL[i - 1][1])
            run(["-i", parts[-1], "-vf", f"select='eq(n\,{prev_n - 1})',loop={n - 1}:1:0,setpts=N/30/TB", "-frames:v", str(n)] + ENC + [out])
        else:
            s = shots[kind]
            assert s[3] == n, (kind, s[3], n)
            if s[5] == "band":     # words sit in the black space above the picture
                raw = out[:-4] + "-raw.mp4"
                shot(*s, raw)
                png = text_png(out[:-4] + ".png", item[2], inter_bold, (242, 242, 242, 255), scale=1.25, shadow=True, cy=0.27)
                run(["-i", raw, "-loop", "1", "-i", png, "-filter_complex", "[0][1]overlay", "-frames:v", str(n)] + ENC + [out])
            elif len(item) > 2:       # footage with words on it
                raw = out[:-4] + "-raw.mp4"
                shot(*s, raw)
                tracked_words(kind, item[2], n, raw, out)
            else:
                shot(*s, out)
        parts.append(out)
        print("part", i, kind, n, "frames", flush=True)
    lst = TMP + "/list.txt"
    with open(lst, "w") as fh:
        fh.write("".join(f"file '{p}'\n" for p in parts))
    dest = TMP + "/preview.mp4" if PREVIEW else OUT
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    # re-timed join: every frame gets its own slot, so a one-frame part can't be swallowed by its neighbour
    ins = sum([["-i", p] for p in parts], [])
    norm = "".join(f"[{j}:v]format=yuv420p,setsar=1,setpts=N/30/TB[v{j}];" for j in range(len(parts)))
    graph = norm + "".join(f"[v{j}]" for j in range(len(parts))) + f"concat=n={len(parts)}:v=1:a=0,setpts=N/30/TB[v]"
    run(ins + ["-i", REF + "/song-noig.wav", "-filter_complex", graph, "-map", "[v]", "-map", f"{len(parts)}:a",
         "-frames:v", str(TOTAL)] + ENC +
        ["-af", f"apad=whole_dur={TOTAL / 30}", "-c:a", "aac", "-b:a", "320k", "-t", f"{TOTAL / 30}", dest])
    print("written", dest)


main()
