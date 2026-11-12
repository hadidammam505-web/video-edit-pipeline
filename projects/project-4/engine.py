# One renderer for the five project-4 edits. Timelines live in specs.py.
# usage: engine.py <r1..r5> <version> [--scale .33] [--t a b] [--masks-only]
import os, subprocess, sys, shutil, wave
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
import specs4 as specs

HOME = os.path.expanduser("~").replace("\\", "/")
BIN = HOME + "/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0.2-full_build/bin/ffmpeg.exe"
DATA = HOME + "/Documents/video-edit"
W = DATA + "/projects/project-4"
SRC = HOME + "/Desktop/edting/storage/project 4/"
OUT = HOME + "/Desktop/edting/results/project 4"
FILES = {f.split("_")[-1][:4]: SRC + f for f in os.listdir(SRC) if f.upper().endswith(".MOV")}
FW, FH, FPS = 2160, 1214, 30
CUT = DATA + "/tools/cutout/Scripts/python.exe"
FONTS = "C:/Windows/Fonts/"

name, ver = sys.argv[1], sys.argv[2]
NOTEXT = "--notext" in sys.argv
NEUTRAL = "--neutral" in sys.argv
SCALE = float(sys.argv[sys.argv.index("--scale") + 1]) if "--scale" in sys.argv else 1.0
RANGE = (float(sys.argv[sys.argv.index("--t") + 1]), float(sys.argv[sys.argv.index("--t") + 2])) if "--t" in sys.argv else None
J = specs.JOBS[name]
if NEUTRAL:   # ungraded picture for colouring in Resolve
    J["grade"] = ""
    for _s in J["shots"]:
        _s.pop("grade", None)
        _s.pop("w", None)
even = lambda v: int(v / 2) * 2
CW, CH = even(J["canvas"][0] * SCALE), even(J["canvas"][1] * SCALE)
PX, PY, PW, PH = [even(v * SCALE) for v in J["pic"]]
f = lambda t: int(round(t * FPS))
MD = f"{W}/masks/{name}"


def geometry(s, pw, ph):
    aspect = pw / ph
    cw = FW * s.get("s", 1)
    ch = cw / aspect
    if ch > FH:
        ch, cw = FH, FH * aspect
    x0 = min(max(FW * s.get("x", .5) - cw / 2, 0), FW - cw)
    y0 = min(max(FH * s.get("y", .5) - ch / 2, 0), FH - ch)
    return even(cw), even(ch), even(x0), even(y0)


def source(s, n, pw, ph, grade=None, extra=None, start=None):
    cw, ch, x0, y0 = geometry(s, pw, ph)
    sp = s.get("speed", 1)
    vf = (f"setpts=PTS/{sp}," if sp != 1 else "") + f"fps={FPS},crop={cw}:{ch}:{x0}:{y0},scale={pw}:{ph}:flags=lanczos,setsar=1"
    if grade:
        vf += "," + grade
    ss = s["ss"] if start is None else start
    return [BIN, "-v", "error", "-ss", f"{ss:.3f}", "-t", f"{n / FPS * sp + .4:.3f}", "-i", FILES[s["c"]], "-vf", vf,
            "-frames:v", str(n), "-f", "rawvideo", "-pix_fmt", "bgr24", "-"]


def read_frames(cmd, pw, ph, n):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    size = pw * ph * 3
    last = None
    for _ in range(n):
        b = p.stdout.read(size)
        if len(b) == size:
            last = np.frombuffer(b, np.uint8).reshape(ph, pw, 3)
        yield last
    p.stdout.close()
    p.wait()


def shot_pic(s):
    ph = even(s["ph"] * SCALE) if "ph" in s else PH
    return PW, ph


def make_masks():
    """Dump the frames of every shot that needs a person mask, then run BiRefNet on them."""
    for i, s in enumerate(J["shots"]):
        if not s.get("mask"):
            continue
        n = 1 if s["mask"] == "first" else f(s["b"]) - f(s["a"])
        d = f"{MD}/s{i}"
        fr, ma = d + "/in", d + "/out"
        if os.path.isdir(ma) and len(os.listdir(ma)) >= n:
            continue
        shutil.rmtree(fr, ignore_errors=True)
        os.makedirs(fr)
        ratio = J["pic"][2] / (s.get("ph", J["pic"][3]))
        ph = even(1600 / ratio)
        for k, im in enumerate(read_frames(source(s, n, 1600, ph), 1600, ph, n)):
            cv2.imencode(".jpg", im, [1, 95])[1].tofile(f"{fr}/f{k:04d}.jpg")
        box = [str(v) for v in s.get("box", (0, 1, 0, 1))]
        print("masks", name, "shot", i, s["c"], n, "frames", flush=True)
        subprocess.run([CUT, DATA + "/tools/boxmask.py", fr, ma, *box], check=True)


class Masks:
    def __init__(self, i, n, pw, ph):
        self.d, self.n, self.size = f"{MD}/s{i}/out", n, (pw, ph)

    def raw(self, k):
        k = min(max(k, 0), self.n - 1)
        m = cv2.imdecode(np.fromfile(f"{self.d}/f{k:04d}.png", np.uint8), 0)
        return cv2.resize(m, self.size, interpolation=cv2.INTER_LINEAR).astype(np.float32) / 255

    def get(self, k):
        m = (self.raw(k - 1) + self.raw(k) + self.raw(k + 1)) / 3
        return ((m - .4) / .3).clip(0, 1)


# --- text -------------------------------------------------------------------
cache = {}


def text_img(t, font, px, track):
    key = (t, font, px, track)
    if key in cache:
        return cache[key]
    fnt = ImageFont.truetype(FONTS + font, px)
    if track:
        widths = [fnt.getlength(c) for c in t]
        tw = int(sum(widths) + track * px * (len(t) - 1)) + 8
    else:
        tw = int(fnt.getlength(t)) + 8
    h = int(px * 1.7)
    im = Image.new("L", (tw, h), 0)
    d = ImageDraw.Draw(im)
    if track:
        x = 4
        for c, wd in zip(t, widths):
            d.text((x, h / 2), c, font=fnt, fill=255, anchor="lm")
            x += wd + track * px
    else:
        d.text((4, h / 2), t, font=fnt, fill=255, anchor="lm")
    a = np.array(im, np.float32) / 255
    ys = np.where(a.max(axis=1) > 0)[0]
    a = a[ys[0]:ys[-1] + 1]
    cache[key] = a
    return a


def put_text(canvas, T, i, mask):
    """Text lives in picture coordinates. Behind-the-person text is masked by the current shot."""
    variant = T
    if "cycle" in T:
        c = T["cycle"][(i // T.get("every", 3)) % len(T["cycle"])]
        variant = {**T, "font": c[0], "size": T["size"] * c[1]}
    px = max(8, int(variant["size"] * J["pic"][3] * SCALE))
    a = text_img(T["text"], variant["font"], px, T.get("track", 0))
    h, w = a.shape
    x, y = PX + T["x"] * PW, PY + T["y"] * PH
    anc = T.get("anchor", "m")
    x0 = int(x) if anc == "l" else int(x - w) if anc == "r" else int(x - w / 2)
    y0 = int(y - h / 2)
    xa, ya, xb, yb = max(x0, 0), max(y0, 0), min(x0 + w, CW), min(y0 + h, CH)
    if xb <= xa or yb <= ya:
        return
    al = a[ya - y0:yb - y0, xa - x0:xb - x0]
    if T.get("behind") and mask is not None:
        mp = np.zeros((CH, CW), np.float32)
        mh, mw = mask.shape
        mp[PY:PY + mh, PX:PX + mw] = mask
        al = al * (1 - mp[ya:yb, xa:xb])
    col = np.array(T.get("color", (240, 240, 240)), np.float32)
    reg = canvas[ya:yb, xa:xb].astype(np.float32)
    canvas[ya:yb, xa:xb] = (reg * (1 - al[..., None]) + col * al[..., None]).astype(np.uint8)


# --- picture effects -------------------------------------------------------
def window(s, pw, ph):
    if "w" not in s:
        return None
    cx, cy, rx, ry = s["w"]
    yy, xx = np.mgrid[0:ph, 0:pw].astype(np.float32)
    d = ((xx / pw - cx) / rx) ** 2 + ((yy / ph - cy) / ry) ** 2
    m = np.exp(-d ** 1.15)
    fl = s.get("floor", J.get("floor", .32))
    return (fl + (1 - fl) * m)[..., None]


def zoom(frame, z, cx=.5, cy=.5):
    if abs(z - 1) < 1e-3:
        return frame
    h, w = frame.shape[:2]
    A = np.float32([[z, 0, (1 - z) * cx * w], [0, z, (1 - z) * cy * h]])
    return cv2.warpAffine(frame, A, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)


def pixelate(frame, block, tint=None):
    h, w = frame.shape[:2]
    sm = cv2.resize(frame, (max(1, w // block), max(1, h // block)), interpolation=cv2.INTER_AREA)
    out = cv2.resize(sm, (w, h), interpolation=cv2.INTER_NEAREST)
    if tint is not None:
        out = (out.astype(np.float32) * np.array(tint, np.float32)).clip(0, 255).astype(np.uint8)
    return out


def apply_fx(pic, s, t, tick, nxt_sil):
    """fx times are absolute edit seconds."""
    for x in s.get("fx", []):
        if not (x["a"] <= t < x["b"]):
            continue
        k = x["k"]
        if k == "white":
            pic[:] = x.get("color", (255, 255, 255))
        elif k == "black":
            pic[:] = 0
        elif k == "dim":
            pic[:] = (pic.astype(np.float32) * x["v"]).clip(0, 255).astype(np.uint8)
        elif k == "fadeout":
            pic[:] = (pic.astype(np.float32) * max(0, (x["b"] - t) / (x["b"] - x["a"]))).astype(np.uint8)
        elif k == "fadein":
            pic[:] = (pic.astype(np.float32) * min(1, (t - x["a"]) / (x["b"] - x["a"]))).astype(np.uint8)
        elif k == "pixel":
            tints = x.get("tints", [None])
            pic[:] = pixelate(pic, x.get("block", 16), tints[tick % len(tints)])
        elif k == "sil":
            if nxt_sil is not None:
                m = nxt_sil[..., None]
                c = np.array(x.get("color", (200, 240, 230)), np.float32)
                pic[:] = (pic.astype(np.float32) * (1 - m) + c * m).astype(np.uint8)
        elif k == "high":      # high-key flash: dark areas go white, logo stays dark
            g = cv2.cvtColor(pic, cv2.COLOR_BGR2GRAY).astype(np.float32)
            v = (255 - g * x.get("gain", 3.2)).clip(x.get("floor", 40), 255)
            pic[:] = np.dstack([v, v, v]).astype(np.uint8)
        elif k == "band":      # vertical strip of high-key picture
            h, w = pic.shape[:2]
            a, b = int(x["x0"] * w), int(x["x1"] * w)
            g = cv2.cvtColor(pic[:, a:b], cv2.COLOR_BGR2GRAY).astype(np.float32)
            v = (255 - g * 2.4).clip(60, 255)
            pic[:, a:b] = np.dstack([v, v, v]).astype(np.uint8)
        elif k == "hblur":
            h, w = pic.shape[:2]
            ln = max(3, int(x.get("amount", .12) * w)) | 1
            pic[:] = cv2.blur(pic, (ln, 1))
        elif k == "blur":
            r = max(1, int(x.get("r", .006) * pic.shape[1])) | 1
            pic[:] = cv2.GaussianBlur(pic, (r, r), 0)
    return pic


# --- rendering ---------------------------------------------------------------
def render_stack(s, pw, ph, grade):
    """Person held in place while a different gym shot flickers behind."""
    n = f(s["b"]) - f(s["a"])
    fg = list(read_frames(source(s, n, pw, ph, grade), pw, ph, n))
    m = Masks(J["shots"].index(s), n, pw, ph)
    every, bgs = s["every"], s["bgs"]
    frames, cur, idx = [], None, -1
    for i in range(n):
        if i // every != idx:
            idx = i // every
            b = dict(zip(("c", "ss", "s", "x", "y"), bgs[idx % len(bgs)]))
            cur = next(read_frames(source(b, 1, pw, ph, grade + ",eq=brightness=-0.04"), pw, ph, 1))
        a = m.get(i)[..., None]
        frames.append((cur.astype(np.float32) * (1 - a) + fg[i].astype(np.float32) * a).astype(np.uint8))
    return frames


def export_layers():
    """Transparent video of the person alone, for shots where words go behind the body."""
    d = f"{W}/extras/idea-{name[1:]}-body-layers{'-neutral' if NEUTRAL else ''}"
    os.makedirs(d, exist_ok=True)
    for i, s in enumerate(J["shots"]):
        if s.get("mask") is not True or "bgs" in s:
            continue
        n = f(s["b"]) - f(s["a"])
        sil = [x["a"] for x in s.get("fx", []) if x["k"] == "sil"]
        keep = f(sil[0]) - f(s["a"]) if sil else n
        pw, ph = shot_pic(s)
        win = window(s, pw, ph)
        mask = Masks(i, n, pw, ph)
        out = f"{d}/body-from-{s['a']:05.2f}s.mov"
        enc = [BIN, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{pw}x{ph}", "-r", str(FPS), "-i", "-",
               "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le", "-alpha_bits", "16", "-vendor", "apl0", out]
        pipe = subprocess.Popen(enc, stdin=subprocess.PIPE)
        for k, fr in enumerate(read_frames(source(s, keep, pw, ph, s.get("grade", J["grade"])), pw, ph, keep)):
            p = fr if win is None else (fr.astype(np.float32) * win).astype(np.uint8)
            pipe.stdin.write(np.dstack([p, (mask.get(k) * 255).astype(np.uint8)]).tobytes())
        pipe.stdin.close()
        pipe.wait()
        print("LAYER", out, keep, "frames", flush=True)


def main():
    os.makedirs(OUT, exist_ok=True)
    make_masks()
    if "--masks-only" in sys.argv:
        return
    if "--layers" in sys.argv:
        export_layers()
        return
    t0, t1 = RANGE or (0, J["dur"])
    dest = f"{OUT}/idea-{name[1:]}{'-no-text' if NOTEXT else ''}.mp4" if SCALE == 1 and not RANGE else f"{W}/preview-{name}-v{ver}.mp4"
    if NEUTRAL:
        dest = f"{W}/extras/idea-{name[1:]}-neutral.mp4"
    audio = mix_audio()
    enc = [BIN, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{CW}x{CH}", "-r", str(FPS), "-i", "-"]
    if RANGE:
        enc += ["-ss", str(t0), "-t", str(t1 - t0)]
    enc += ["-i", audio, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "ultrafast" if SCALE < 1 else "medium",
            "-crf", "24" if SCALE < 1 else "17", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", dest]
    pipe = subprocess.Popen(enc, stdin=subprocess.PIPE)
    shots, grade = J["shots"], J["grade"]
    written = 0
    for i, s in enumerate(shots):
        if s["b"] <= t0 or s["a"] >= t1:
            continue
        n = f(s["b"]) - f(s["a"])
        pw, ph = shot_pic(s)
        if s.get("black"):
            frames = [np.zeros((ph, pw, 3), np.uint8)] * n
        elif "bgs" in s:
            frames = render_stack(s, pw, ph, s.get("grade", grade))
        else:
            frames = read_frames(source(s, n, pw, ph, s.get("grade", grade)), pw, ph, n)
        mask = Masks(i, n, pw, ph) if s.get("mask") is True else None
        win = window(s, pw, ph)
        nxt = None
        if i + 1 < len(shots) and shots[i + 1].get("mask"):
            sp = shot_pic(shots[i + 1])
            if sp == (pw, ph):
                nxt = Masks(i + 1, 1, pw, ph).get(0) if os.path.isdir(f"{MD}/s{i + 1}/out") else None
        z0, z1 = s.get("z", (1, 1))
        for k, fr in enumerate(frames):
            t = (f(s["a"]) + k) / FPS
            if t < t0 - 1e-6 or t >= t1:
                continue
            p = fr.copy()
            u = k / max(1, n - 1)
            if s.get("ease"):
                u = 1 - (1 - u) ** 3
            p = zoom(p, z0 + (z1 - z0) * u, s.get("zx", .5), s.get("zy", .5))
            if win is not None:
                p = (p.astype(np.float32) * win).astype(np.uint8)
            p = apply_fx(p, s, t, k // 2, nxt)
            canvas = np.zeros((CH, CW, 3), np.uint8)
            y = PY + (PH - ph) // 2
            canvas[y:y + ph, PX:PX + pw] = p
            m = mask.get(k) if mask is not None else None
            for T in ([] if NOTEXT else J["texts"]):
                if T["a"] <= t < T["b"]:
                    put_text(canvas, T, f(t), m)
            pipe.stdin.write(canvas.tobytes())
            written += 1
        print("shot", i, s.get("c", "-"), flush=True)
    pipe.stdin.close()
    pipe.wait()
    print("OUT", dest, written, "frames")


def mix_audio():
    path = f"{W}/refs/{name}/audio.wav"
    rng = np.random.default_rng(7)
    with wave.open(path) as w:
        SR, CHN = w.getframerate(), w.getnchannels()
        song = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32).reshape(-1, CHN) / 32768
    need = int(J["dur"] * SR)
    if len(song) < need:
        song = np.vstack([song, np.zeros((need - len(song), CHN), np.float32)])
    sfx = np.zeros(len(song), np.float32)

    def add(t, x):
        i = int(t * SR)
        k = min(len(x), len(sfx) - i)
        if k > 0:
            sfx[i:i + k] += x[:k]

    for t, kind in J.get("sfx", []):
        if kind == "hit":
            rise = .16
            nr = int(rise * SR)
            add(t - rise, np.diff(rng.standard_normal(nr).astype(np.float32), prepend=0) * np.linspace(0, 1, nr) ** 2.2 * .38)
            a = np.arange(int(.5 * SR)) / SR
            add(t, ((np.sin(2 * np.pi * (58 + 70 * np.exp(-a * 26)) * a) * np.exp(-a * 7.5) * .8) + rng.standard_normal(len(a)) * np.exp(-a * 85) * .3).astype(np.float32))
        else:   # digital crackle for glitches
            a = np.arange(int(.32 * SR)) / SR
            g = (np.sign(np.sin(2 * np.pi * 38 * a)) > 0).astype(np.float32)
            add(t, (rng.standard_normal(len(a)) * g * np.exp(-a * 7) * .28 + np.sign(np.sin(2 * np.pi * 920 * a)) * g * np.exp(-a * 11) * .07).astype(np.float32))
    mix = song + (sfx * J.get("sfx_gain", .4))[:, None]
    need_g = np.minimum(1.0, .98 / np.maximum(np.abs(mix).max(axis=1), 1e-6))
    win = int(.008 * SR) * 2 + 1
    grown = cv2.erode(need_g.astype(np.float32).reshape(-1, 1), np.ones((win, 1), np.uint8)).ravel()
    mix = mix * np.minimum(np.convolve(grown, np.ones(win) / win, mode="same"), 1.0)[:, None]
    out = f"{W}/tmp-{name}-mix.wav"
    with wave.open(out, "wb") as w:
        w.setnchannels(CHN)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix.clip(-1, 1) * 32767).astype(np.int16).tobytes())
    return out


main()
