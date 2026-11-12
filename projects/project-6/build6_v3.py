"""Project 6: morning routine (landscape band, copies the reference) -> band opens to vertical -> car singing -> fast gym edit.
usage: build6.py [preview]      preview = 720x1280 for checking, otherwise 2160x3840 30 fps.
Landscape morning shots come from enh/ (Real-ESRGAN, see enhance.sh). Run with the vision venv (needs PIL + numpy).
"""
import json, os, subprocess, sys, math
from PIL import Image, ImageDraw, ImageFont

PREVIEW = len(sys.argv) > 1 and sys.argv[1] == "preview"
S = 1 / 3 if PREVIEW else 1.0                     # everything is laid out at 2160x3840 and scaled by S
W, H = int(2160 * S), int(3840 * S)
BX, BY, BW, BH = [int(v * S) for v in (66, 1350, 2028, 1140)]   # reference band: rows 450-829, cols 22-697 of 720x1280, x3
FPS = 30
P = "C:/Users/ZGAMES/Documents/video-edit/projects/project-6"
ENH = P + "/enh/"
ST6 = "C:/Users/ZGAMES/Desktop/edting/storage/project 6/"
REF = "C:/Users/ZGAMES/Documents/video-edit/refs/project-6/"
FONTS = "C:/Users/ZGAMES/Documents/video-edit/fonts/"
SFX = "C:/Users/ZGAMES/Documents/video-edit/sfx/sonniss-gdc2026/library/"
WHOOSH = SFX + "344 Audio - Elemental Palette Designed Vol. 1/WINDDsgn_Wind, Rush, Whoosh, Long x5 01_344 Audio_Elemental Palette Designed Vol 1.wav"
BIGHIT = SFX + "Cinematic Sound Design - Colossal Impacts/Impact Cut Sweep.wav"
OUT = "C:/Users/ZGAMES/Desktop/edting/results/project 6/idea-1.mp4"
WORK = P + ("/work_prev/" if PREVIEW else "/work/")
os.makedirs(WORK, exist_ok=True)

WARM = ("eq=contrast=1.06:saturation=0.80:gamma=0.97,"
        "colorbalance=rs=0.07:gs=0.01:bs=-0.09:rm=0.05:bm=-0.07:rh=0.04:bh=-0.06,vignette=PI/5")
GYM = "eq=contrast=1.10:saturation=1.02:gamma=0.97,colorbalance=rs=0.03:bs=-0.03:rm=0.02:bm=-0.02,vignette=PI/5"
GRAIN = "noise=alls=5:allf=t"

# ---- timeline (frames at 30 fps) ----
# Revision 2 (user's notes, 2026-11-12): alarm twice with the phone on screen, then wake; shower -> towel -> closet;
# short cooking; hoodie, shoes, the shoe hop; out of the house, to the car and in; then Monster, car singing cut in with gym.
# (name, kind, source, source start s, frames, extra)
#   band  : landscape file -> band     bandv : vertical file, band-shaped crop at y (2160 px space) -> band
#   open  : vertical file, band opens to full frame    full : vertical full frame    black
SEG = [
    ("sleep",  "band",  ENH + "sleep.mov",   0.00, 90, {}),
    ("phone",  "bandv", ST6 + "IMG_6917.MOV", 4.00, 45, {"y": 1650, "lift": True}),   # rings, the Gymbro message lands at +0.67 s
    ("eye",    "band",  ENH + "eye.mov",     0.10, 51, {}),
    ("wake2",  "band",  ENH + "wake2.mov",   0.40, 66, {}),     # eyes open, lifts off the pillow
    ("stretch","band",  ENH + "stretch.mov", 0.20, 41, {}),
    ("getup",  "band",  ENH + "getup.mov",   0.30, 34, {}),
    ("enter",  "band",  ENH + "enter.mov",   0.40, 30, {}),     # quick: into the shower
    ("towel",  "band",  ENH + "towel.mov",   0.20, 54, {}),     # out, drying his head
    ("throw",  "bandv", ST6 + "A001_11111624_C093.mov", 33.90, 36, {"y": 700}),   # throws the clothes he had on over the closet door
    ("grab",   "bandv", ST6 + "A001_11111624_C093.mov", 57.90, 51, {"y": 700}),   # pulls the hoodie
    ("pour",   "band",  ENH + "pour.mov",    0.70, 27, {}),
    ("mix",    "band",  ENH + "mix.mov",     0.30, 27, {}),
    ("sauce",  "band",  ENH + "sauce.mov",   0.30, 27, {}),
    ("plate",  "band",  ENH + "plate.mov",   1.00, 36, {}),
    ("hoodie", "open",  ST6 + "A001_11111628_C095.mov", 10.00, 45, {}),
    ("shoes",  "full",  ST6 + "A001_11111629_C096.mov",  2.00, 40, {}),
    ("hop",    "full",  ST6 + "A001_11111630_C097.mov",  8.70, 45, {}),   # hopping to get the foot in
    ("bag",    "full",  ST6 + "A001_11111641_C101.mov",  3.40, 36, {}),
    ("door",   "full",  ST6 + "A001_11111642_C102.mov", 12.00, 60, {}),
    ("tocar",  "full",  ST6 + "A001_11111643_C103.mov", 16.50, 36, {}),
    ("getin",  "full",  ST6 + "A001_11111643_C103.mov", 19.30, 61, {}),
]
PART1_END = sum(s[4] for s in SEG)                 # 938 = 31.27 s, where the reference song ends
assert PART1_END == 938, PART1_END
CAR_AT = PART1_END

# Monster (screen recording in storage). Car clip t=0 is song t=3.652, found by onset cross-correlation (2026-11-12).
SONG = ST6 + "ScreenRecording_11-12-2026 21-29-43_1.MP4"
SONG_AT_CAR0 = 3.652
SONG_GAIN, CAR_GAIN = -9.0, -5.0                   # song file is -5 LUFS; bring it to ~-14, your voice a bit under it
BEATS = [9.787, 10.24, 10.681, 11.134, 11.575, 12.016, 12.458, 12.91, 13.363, 13.804, 14.245, 14.687, 15.128, 15.569,
         16.022, 16.463, 16.904, 17.357, 17.798, 18.239, 18.692, 19.133, 19.574, 20.016, 20.468, 20.91, 21.362, 21.804,
         22.245, 22.686, 23.127, 23.568, 24.021, 24.462, 24.915, 25.356, 25.797, 26.239, 26.68, 27.121]   # librosa, 136 BPM
vf = lambda song_t: round(FPS * (CAR_AT / FPS + song_t - SONG_AT_CAR0))
CAR = ST6 + "A001_11111703_C106.mov"
# singing in the car cut in with gym reps on the beat (song times); car shots keep lip sync: source t = song t - 3.652
MIX = [("car1", None, 3.652, 4.899), ("gC114", ("A001_11111906_C114.MOV", 45.80), 4.899, 5.782),
       ("car2", None, 5.782, 6.687), ("gC125", ("A001_11121802_C125.mov", 30.50), 6.687, 7.581),
       ("car3", None, 7.581, BEATS[0])]           # last sung word, then the flash into the gym on the first beat after it
for n, g, a0, a1 in MIX:
    fr = vf(a1) - vf(a0)
    if g is None:
        SEG.append((n, "full", CAR, a0 - SONG_AT_CAR0, fr, {"white_out": 4} if n == "car3" else {}))
    else:
        SEG.append((n, "full", ST6 + g[0], g[1], fr, {"white_in": 3, "gym": True}))
GYM_AT = vf(BEATS[0])

# Gym: one hard concentric rep per shot, 4 beats each, cut on the song's real beats; the last shot holds 2 more beats.
GYMS = [("C122", "A001_11121739_C122.mov", 100.00),   # C120 (filmed from behind) removed at the user's request
        ("C121", "A001_11121734_C121.mov",  86.00), ("C110", "A001_11111814_C110.mov", 117.20),
        ("C109", "A001_11111803_C109.mov",  92.20), ("C111", "A001_11111824_C111.MOV", 102.00),
        ("C124", "A001_11121754_C124.mov",  25.70)]
cuts = [vf(BEATS[4 * k]) for k in range(len(GYMS))] + [vf(BEATS[4 * len(GYMS) + 2])]
for i, (n, f, t) in enumerate(GYMS):
    last = i == len(GYMS) - 1
    SEG.append(("g" + n, "full", ST6 + f, t, cuts[i + 1] - cuts[i],
                {"white_in": 8 if i == 0 else 5, "white_out": 0 if last else 3, "gym": True, "fade_end": last}))
TOTAL = sum(s[4] for s in SEG)
START = {}
_f = 0
for s_ in SEG: START[s_[0]] = _f; _f += s_[4]

# ---- text: credits (my own words, same joke as the reference), each inside one shot ----
_C = [("getup", "Produced by", "a 5 AM alarm", 0.27, 0.70), ("towel", "Stolen from", "every gym reel ever", 0.27, 0.70),
      ("grab", "Color Graded:", "Very fast & very bad", 0.72, 0.42), ("plate", "Edited:", "somehow", 0.30, 0.46)]
CRED = [(START[n] + 3, START[n] + dict((x[0], x[4]) for x in SEG)[n] - 3, l1, l2, x, y) for n, l1, l2, x, y in _C]
RING = ("CB_Sounddesign - Applicable Sounds - Organic UI and Building Games SFX/"
        "UIMisc_Xylophone Ringtone 2_CB Sounddesign_APPlicable Sounds.wav")
PING = ("CB_Sounddesign - Applicable Sounds - Organic UI and Building Games SFX/"
        "UIMisc_Kalimba 3 Up_CB Sounddesign_APPlicable Sounds.wav")

def font(name, size, wght=None):
    f = ImageFont.truetype(FONTS + name, int(size))
    if wght:
        try: f.set_variation_by_axes([wght])
        except Exception: pass
    return f

def ff_files(d, pat):
    import glob
    return sorted(glob.glob(os.path.join(FONTS, d, pat)))

INTER = os.path.relpath(ff_files("inter", "Inter*.ttf")[0], FONTS)
PLAY = os.path.relpath(ff_files("playfairdisplay", "*.ttf")[0], FONTS)
ANTON = os.path.relpath(ff_files("anton", "*.ttf")[0], FONTS)
INSTR = os.path.relpath(ff_files("instrumentserif", "*Regular*.ttf")[0], FONTS)

def shadowed(img):
    """soft dark glow under white text so it reads on bright walls"""
    a = img.split()[3]
    from PIL import ImageFilter
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0)); sh.putalpha(a.filter(ImageFilter.GaussianBlur(6 * S + 1)).point(lambda v: v * 0.55))
    return Image.alpha_composite(sh, img)

def credit_png(path, l1, l2):
    s1, s2 = 54 * S, 64 * S
    f1, f2 = font(INTER, s1, 600), font(INTER, s2, 700)
    im = Image.new("RGBA", (BW, BH), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    w1 = d.textlength(l1, font=f1) if l1 else 0; w2 = d.textlength(l2, font=f2)
    lay = Image.new("RGBA", (int(max(w1, w2) + 60 * S), int((s1 + s2) * 1.5)), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
    cx = lay.width / 2
    if l1: dl.text((cx - w1 / 2, 0), l1, font=f1, fill="white")
    dl.text((cx - w2 / 2, s1 * 1.05 if l1 else 0), l2, font=f2, fill="white")
    lay = lay.transform(lay.size, Image.AFFINE, (1, 0.16, -0.16 * lay.height / 2, 0, 1, 0), Image.BICUBIC)  # italic slant
    lay.save(path)
    return lay.size

def loser_frames(out_dir, n, src_frames):
    """LOSER stacked down the left wall edge, switching fonts like the reference (serif, then a burst, then spaced)."""
    os.makedirs(out_dir, exist_ok=True)
    styles = []
    for k in range(n):
        if k < 4: styles.append(None)
        elif k < 37: styles.append((PLAY, 1.00, 0.0, 700))
        elif k < 40: styles.append((PLAY, 0.92, 0.0, 400))
        elif k < 44: styles.append((ANTON, 1.05, 0.0, None))
        elif k < 48: styles.append((INSTR, 1.00, 0.25, None))
        else: styles.append((INTER, 0.70, 0.55, 500))
    cache = {}
    for k, st in enumerate(styles):
        p = os.path.join(out_dir, "%04d.png" % k)
        if st not in cache:
            im = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
            if st:
                fn, sc, spread, wg = st
                size = 215 * S * sc; f = font(fn, size, wg)
                col = Image.new("RGBA", (int(size * 1.6), BH), (0, 0, 0, 0)); d = ImageDraw.Draw(col)
                step = min(size * (0.98 + spread), BH * 0.188); y0 = (BH - step * 5) / 2 + size * 0.08
                for i, ch in enumerate("LOSER"):
                    w = d.textlength(ch, font=f)
                    d.text((col.width / 2 - w / 2, y0 + i * step), ch, font=f, fill="white")
                col = col.rotate(6, resample=Image.BICUBIC, center=(col.width / 2, BH / 2))
                im.alpha_composite(col, (int(BW * 0.115 - col.width / 2), 0))
                im = shadowed(im)
            cache[st] = im
        cache[st].save(p)

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: print(" ".join(cmd)); print(r.stderr[-3000:]); sys.exit(1)

def seg_video(i, seg, start_frame):
    name, kind, src, t0, n, ex = seg
    out = WORK + "%02d_%s.mp4" % (i, name)
    ins, fc = [], []
    if kind == "black":
        ins += ["-f", "lavfi", "-i", f"color=black:s={W}x{H}:r={FPS}"]
        fc.append("[0:v]format=yuv420p[v0]")
    else:
        ins += ["-ss", "%.3f" % t0, "-i", src]
        base = f"[0:v]fps={FPS},setsar=1"
        if kind == "band":
            fc.append(f"{base},scale={BW}:{BH}:flags=lanczos,{WARM},{GRAIN},pad={W}:{H}:{BX}:{BY}:black[v0]")
        elif kind == "bandv":
            y = ex["y"]
            lift = ",eq=brightness=0.06:gamma=1.45:saturation=1.1" if ex.get("lift") else ""
            fc.append(f"{base},crop=2160:1215:0:{y}{lift},scale={BW}:{BH}:flags=lanczos,{WARM},{GRAIN},pad={W}:{H}:{BX}:{BY}:black[v0]")
        else:
            g = GYM if ex.get("gym") else WARM
            fc.append(f"{base},scale={W}:{H}:flags=lanczos,{g}[v0]")
        if kind == "open":   # black bars slide away: band -> full frame between frames 8 and 26
            p = "(1-cos(PI*min(max((t*30-8)/18,0),1)))/2"
            ins += ["-f", "lavfi", "-i", f"color=black:s={W}x{BY}:r={FPS}", "-f", "lavfi", "-i", f"color=black:s={W}x{H-BY-BH}:r={FPS}",
                    "-f", "lavfi", "-i", f"color=black:s={BX}x{H}:r={FPS}", "-f", "lavfi", "-i", f"color=black:s={W-BX-BW}x{H}:r={FPS}"]
            fc.append(f"[v0][1:v]overlay=x=0:y='-{BY}*{p}':shortest=1[o1];[o1][2:v]overlay=x=0:y='{BY+BH}+{H-BY-BH}*{p}':shortest=1[o2];"
                      f"[o2][3:v]overlay=x='-{BX}*{p}':y=0:shortest=1[o3];[o3][4:v]overlay=x='{BX+BW}+{W-BX-BW}*{p}':y=0:shortest=1[v0b]")
    last = "v0b" if kind == "open" else "v0"
    # overlays: LOSER sequence on the first shot, credits by absolute frame
    idx = sum(1 for a in ins if a == "-i")
    if name == "sleep":
        ld = WORK + "loser"; loser_frames(ld, n, None)
        ins += ["-framerate", str(FPS), "-i", ld + "/%04d.png"]
        fc.append(f"[{last}][{idx}:v]overlay={BX}:{BY}:shortest=0[t{idx}]"); last = f"t{idx}"; idx += 1
    for (a, b, l1, l2, fx, fy) in CRED:
        if a >= start_frame + n or b <= start_frame: continue
        png = WORK + "cred_%d.png" % a; cw, chh = credit_png(png, l1, l2)
        x = int(BX + BW * fx - cw / 2); y = int(BY + BH * fy - chh / 2)
        ra, rb = (a - start_frame) / FPS, (b - start_frame) / FPS
        ins += ["-loop", "1", "-framerate", str(FPS), "-i", png]
        fc.append(f"[{idx}:v]format=rgba,fade=in:st={ra:.3f}:d=0.12:alpha=1,fade=out:st={rb-0.15:.3f}:d=0.15:alpha=1[c{idx}];"
                  f"[{last}][c{idx}]overlay={x}:{y}:enable='between(t,{ra:.3f},{rb:.3f})'[t{idx}]"); last = f"t{idx}"; idx += 1
    # white flashes (smooth): fade from white at the head, to white at the tail
    if ex.get("white_in"):
        fc.append(f"[{last}]fade=in:s=0:n={ex['white_in']}:color=white[wi]"); last = "wi"
    if ex.get("white_out"):
        fc.append(f"[{last}]fade=out:s={n-ex['white_out']}:n={ex['white_out']}:color=white[wo]"); last = "wo"
    if ex.get("fade_end"):
        fc.append(f"[{last}]fade=out:s={n-12}:n=12[fe]"); last = "fe"
    fc.append(f"[{last}]format=yuv420p,setpts=N/{FPS}/TB[out]")
    run(["ffmpeg", "-nostdin", "-v", "error", "-y"] + ins + ["-filter_complex", ";".join(fc), "-map", "[out]",
         "-frames:v", str(n), "-an", "-c:v", "libx264", "-preset", "fast" if PREVIEW else "slow", "-crf", "20" if PREVIEW else "11",
         "-pix_fmt", "yuv420p", out])
    return out

def audio(path):
    """reference song for part 1; from the car on: Monster (clean, louder) + your car sound under it until the gym,
    then Monster alone; a soft hit on the car->gym flash and a whoosh on each gym flash"""
    car_t, gym_t = CAR_AT / FPS, GYM_AT / FPS
    end = TOTAL / FPS
    car_len = gym_t - car_t
    ins = ["-i", REF + "song.wav", "-t", "%.3f" % (car_len + 0.3), "-i", ST6 + "A001_11111703_C106.mov",
           "-ss", "%.3f" % SONG_AT_CAR0, "-i", SONG, "-i", BIGHIT, "-i", WHOOSH, "-i", SFX + RING, "-i", SFX + PING]
    d = lambda t: f"adelay={int(t*1000)}|{int(t*1000)}"
    p1 = START["phone"] / FPS
    ring = [f"[5:a]aresample=48000,atrim=0:2.4,afade=t=out:st=1.8:d=0.6,volume=0.7,{d(p1)}[ra]",
            f"[6:a]aresample=48000,volume=0.9,{d(p1 + 0.67)}[pg]"]
    fc = [f"[0:a]atrim=0:{car_t:.3f},afade=t=out:st={car_t-0.12:.3f}:d=0.12,aresample=48000[a0]",
          f"[1:a]aresample=48000,volume={CAR_GAIN}dB,afade=t=in:d=0.04,atrim=0:{car_len+0.12:.3f},afade=t=out:st={car_len:.3f}:d=0.12,{d(car_t)}[a1]",
          f"[2:a]aresample=48000,volume={SONG_GAIN}dB,afade=t=in:d=0.06,atrim=0:{end-car_t:.3f},afade=t=out:st={end-car_t-0.6:.3f}:d=0.6,{d(car_t)}[a2]",
          f"[3:a]aresample=48000,volume=0.45,{d(gym_t-0.15)}[a3]"]
    fc += ring
    mix = ["[a0]", "[a1]", "[a2]", "[a3]", "[ra]", "[pg]"]
    flashes = cuts[1:-1] + [START[n] for n in ("gC114", "gC125")]
    for j, c in enumerate(flashes):
        t = c / FPS - 0.12
        fc.append(f"[4:a]aresample=48000,atrim=0:0.6,afade=t=out:st=0.4:d=0.2,volume=0.35,{d(t)}[w{j}]"); mix.append(f"[w{j}]")
    fc.append("".join(mix) + f"amix=inputs={len(mix)}:normalize=0:duration=longest,atrim=0:{end:.3f},alimiter=limit=0.7:level=0[a]")
    run(["ffmpeg", "-nostdin", "-v", "error", "-y"] + ins + ["-filter_complex", ";".join(fc), "-map", "[a]", "-c:a", "pcm_s16le", path])

if __name__ == "__main__":
    parts, f0 = [], 0
    for i, s in enumerate(SEG):
        print("seg", i, s[0], f0, s[4]); parts.append(seg_video(i, s, f0)); f0 += s[4]
    aud = WORK + "mix.wav"; audio(aud)
    ins = []
    for p in parts: ins += ["-i", p]
    fc = "".join(f"[{k}:v]format=yuv420p,setsar=1,setpts=N/{FPS}/TB[p{k}];" for k in range(len(parts)))
    fc += "".join(f"[p{k}]" for k in range(len(parts))) + f"concat=n={len(parts)}:v=1:a=0[v]"
    out = OUT if not PREVIEW else WORK + "preview.mp4"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    run(["ffmpeg", "-nostdin", "-v", "error", "-y"] + ins + ["-i", aud, "-filter_complex", fc, "-map", "[v]", "-map", f"{len(parts)}:a",
         "-frames:v", str(TOTAL), "-r", str(FPS), "-c:v", "libx264", "-preset", "medium" if PREVIEW else "slow",
         "-crf", "20" if PREVIEW else "14", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart", out])
    print("done", out, TOTAL, "frames")
