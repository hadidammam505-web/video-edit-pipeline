# Vertical letterboxed gym edit, copying the project-3 reference's cuts, stack opening, flashes and song.
# usage: python3 build.py <version>
import os, subprocess, sys, shutil, wave
import numpy as np, cv2, onnxruntime as ort

V = sys.argv[1] if len(sys.argv) > 1 else "1"
HOME = os.path.expanduser("~").replace("\\", "/")
BIN = HOME + "/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0.2-full_build/bin/ffmpeg.exe"
DATA = HOME + "/Documents/video-edit"
W = DATA + "/projects/project-3"
SK = HOME + "/.claude/skills/video-edit/scripts"
SRC = HOME + "/Desktop/edting/storage/project 3/"
SONG = DATA + "/refs/project-3/song.wav"
OUT = HOME + "/Desktop/edting/results/project 3"
TMP = W + "/tmp"
FILES = {f.split("_")[-1][:4]: SRC + f for f in os.listdir(SRC) if f.upper().endswith(".MOV")}
FPS, PW, PH, CW, CH = 30, 2160, 1536, 2160, 3840   # picture sits in a 9:16 canvas like the reference
ASPECT = PW / PH
for d in (TMP, OUT):
    os.makedirs(d, exist_ok=True)

# dark, green-cream highlights like the reference, reds kept
GRADE = ("eq=contrast=1.22:gamma=0.8:saturation=1.0,"
         "curves=r='0/0 0.25/0.09 0.6/0.38 1/0.86':g='0/0 0.25/0.10 0.6/0.41 1/0.92':b='0/0 0.25/0.10 0.6/0.36 1/0.74',"
         "vignette=angle=PI/3.4,noise=alls=3:allf=t")
FLASH_BGR = (200, 240, 230)
FLASH_FRAMES = 3

def f(t):
    return int(round(t * FPS))

def ff(*args, cwd=None):
    r = subprocess.run([BIN, "-v", "error", "-y", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        print(r.stderr[-1500:]); sys.exit(1)

def crop(s, cx, cy):
    return f"crop=trunc(ih*{s}*{ASPECT}/2)*2:trunc(ih*{s}/2)*2:iw*{cx}-out_w/2:ih*{cy}-out_h/2"

def view(s, cx, cy, push=0, n=1):
    v = f"fps={FPS},{crop(s, cx, cy)},scale={PW}:{PH}:flags=lanczos,setsar=1"
    if push:
        v += f",zoompan=z='1+{push}*on/{n}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s={PW}x{PH}:fps={FPS}"
    return v

ENC = ["-c:v", "libx264", "-preset", "fast", "-crf", "15", "-pix_fmt", "yuv420p"]

# --- timeline: cuts measured from the reference, seconds ---
# a, b, clip, source second, crop size (of frame height), centre x, centre y, push-in, flash roi of the NEXT shot
S = [
    dict(a=1.376, b=1.501, c="C061", ss=12.0, s=1.0, x=.42, y=.5),
    dict(a=1.501, b=1.668, c="C053", ss=5.4,  s=.9,  x=.5,  y=.5),
    dict(a=1.668, b=2.294, c="C061", ss=29.85, s=1.0, x=.42, y=.5),
    dict(a=2.294, b=2.794, c="C061", ss=30.25, s=.7, x=.35, y=.36),
    dict(a=2.794, b=3.295, c="C063", ss=7.1,  s=1.0, x=.42, y=.5, flash=(.2, 1, 0, 1)),
    dict(a=3.295, b=3.670, c="C055", ss=29.5, s=1.0, x=.55, y=.5),
    dict(a=3.670, b=4.129, c="C054", ss=39.0, s=.9,  x=.55, y=.5),
    dict(a=4.129, b=5.047, c="C056", ss=27.0, s=1.0, x=.5,  y=.5),
    dict(a=5.047, b=5.505, c="C064", ss=41.75, s=.7, x=.45, y=.65),
    dict(a=5.505, b=5.756, c="C049", ss=39.0, s=1.0, x=.45, y=.5),
    dict(a=5.756, b=6.381, c="C049", ss=39.25, s=.72, x=.45, y=.45),
    dict(a=6.381, b=7.132, c="C052", ss=42.0, s=1.0, x=.42, y=.5, flash=(.0, 1, 0, 1)),
    dict(a=7.132, b=8.717, c="C053", ss=5.5, s=.92, x=.5, y=.5, plates=[(5.5, 7.132), (10.5, 7.36), (15.0, 7.62), (20.0, 7.94)]),
    dict(a=8.717, b=9.940, c="C068", ss=9.0,  s=.72, x=.45, y=.52, push=.07, extra="eq=saturation=.62:gamma=1.4,colorbalance=rm=-.06:bm=.05:rs=-.04:bs=.04"),
]
STACK_END = S[0]["a"]
FG = dict(c="C063", ss=3.4, s=.85, x=.45, y=.45)
BGS = [("C049", 1.0, 1, .42, .5), ("C054", 10.0, 1, .5, .5), ("C056", 51.5, 1, .5, .5), ("C063", 61.5, 1, .5, .5), ("C051", 6.0, 1, .4, .5),
       ("C064", 44.6, 1, .5, .5), ("C062", 49.5, 1, .5, .5), ("C053", 5.2, .8, .5, .5), ("C068", 46.0, 1, .4, .5), ("C049", 60.5, .7, .55, .4),
       ("C054", 14.0, .7, .55, .4), ("C063", 62.0, .7, .3, .5), ("C056", 52.0, .7, .3, .55), ("C062", 50.0, .7, .7, .5), ("C064", 39.75, .7, .4, .4),
       ("C051", 8.0, .7, .3, .6), ("C053", 5.6, 1, .5, .5)]

def render_stack():
    """Person held in place with a different gym shot behind every 2-3 frames."""
    n = f(STACK_END)
    edges = sorted({f(k * 2 / 23.976) for k in range(0, 40) if f(k * 2 / 23.976) < n} | {n})
    with open(f"{TMP}/bg.txt", "w", encoding="utf-8") as lst:
        for i, (e0, e1) in enumerate(zip(edges, edges[1:])):
            c, ss, s, x, y = BGS[i % len(BGS)]
            p = f"{TMP}/bg{i}.mp4"
            ff("-ss", str(ss), "-t", "0.3", "-i", FILES[c], "-vf", f"{view(s, x, y)},{GRADE},eq=brightness=-0.03", "-frames:v", str(e1 - e0), *ENC, p)
            lst.write(f"file '{p}'\n")
    ff("-f", "concat", "-safe", "0", "-i", f"{TMP}/bg.txt", "-c", "copy", f"{TMP}/bg.mp4")
    fd, gd, md, ad = (f"{TMP}/{x}" for x in ("fgin", "fgguide", "fgmatte", "fgalpha"))
    for d in (fd, gd, md, ad):
        shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    ff("-ss", str(FG["ss"]), "-t", str(n / FPS + .2), "-i", FILES[FG["c"]], "-vf", f"{view(FG['s'], FG['x'], FG['y'])},scale=1600:-2",
       "-frames:v", str(n), "-q:v", "2", f"{fd}/f%04d.jpg")
    # ISNet on a box around the person: MODNet lost the head and torso with the arms overhead
    x0, x1 = .16, .68
    for i in range(n):
        im = cv2.imdecode(np.fromfile(f"{fd}/f{i + 1:04d}.jpg", np.uint8), 1)
        h, w = im.shape[:2]
        l, r = int(x0 * w), int(x1 * w)
        x = cv2.resize(im[:, l:r], (1024, 1024), interpolation=cv2.INTER_AREA)[..., ::-1].astype(np.float32) / 255 - .5
        y = sess.run(None, {INP: x.transpose(2, 0, 1)[None]})[0][0, 0]
        y = cv2.resize((y - y.min()) / (y.max() - y.min() + 1e-6), (r - l, h))
        m = np.zeros((h, w), np.float32); m[:, l:r] = y
        cv2.imencode(".png", (m * 255).astype(np.uint8))[1].tofile(f"{md}/f{i + 1:04d}.png")
    rdm = lambda i: cv2.imdecode(np.fromfile(f"{md}/f{min(max(i, 0), n - 1) + 1:04d}.png", np.uint8), 0).astype(np.float32)
    for i in range(n):
        m = ((rdm(i - 1) + rdm(i) + rdm(i + 1)) / 3 / 255 - .45) / .3
        m = m.clip(0, 1)
        k, lab, st, _ = cv2.connectedComponentsWithStats((m > .5).astype(np.uint8))
        if k > 1:
            m = m * cv2.dilate((lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))).astype(np.uint8), np.ones((7, 7), np.uint8)).astype(np.float32)
        cv2.imencode(".png", (m * 255).astype(np.uint8))[1].tofile(f"{ad}/m{i:04d}.png")
    out = f"{TMP}/s_stack.mp4"
    fc = (f"[1:v]{view(FG['s'], FG['x'], FG['y'])},{GRADE}[fg0];[2:v]fps={FPS},scale={PW}:{PH},format=gray[mk];"
          f"[fg0][mk]alphamerge[fg];[0:v][fg]overlay=0:0[v]")
    ff("-i", f"{TMP}/bg.mp4", "-ss", str(FG["ss"]), "-t", str(n / FPS + .2), "-i", FILES[FG["c"]], "-framerate", str(FPS), "-i", f"{ad}/m%04d.png",
       "-filter_complex", fc, "-map", "[v]", "-frames:v", str(n), *ENC, out)
    return out

# --- flash: flat cream silhouette of the next shot's subject ---
sess = ort.InferenceSession(DATA + "/tools/models/isnet-general-use.onnx", providers=["CPUExecutionProvider"])
INP = sess.get_inputs()[0].name

def silhouette(nxt, roi, name):
    j = f"{TMP}/sil_{name}.jpg"
    ff("-ss", str(nxt["ss"]), "-i", FILES[nxt["c"]], "-frames:v", "1", "-q:v", "2", "-vf", f"{crop(nxt['s'], nxt['x'], nxt['y'])},scale={PW}:{PH}", j)
    bgr = cv2.imdecode(np.fromfile(j, np.uint8), 1)
    h, w = bgr.shape[:2]
    x0, x1, y0, y1 = int(roi[0] * w), int(roi[1] * w), int(roi[2] * h), int(roi[3] * h)
    x = cv2.resize(bgr[y0:y1, x0:x1], (1024, 1024), interpolation=cv2.INTER_AREA)[..., ::-1].astype(np.float32) / 255 - .5
    y = sess.run(None, {INP: x.transpose(2, 0, 1)[None]})[0][0, 0]
    y = cv2.resize((y - y.min()) / (y.max() - y.min() + 1e-6), (x1 - x0, y1 - y0))
    m = np.zeros((h, w), np.float32); m[y0:y1, x0:x1] = y
    m = ((m - .4) / .3).clip(0, 1)
    k, lab, st, _ = cv2.connectedComponentsWithStats((m > .5).astype(np.uint8))
    if k > 1:
        m = m * cv2.dilate((lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))).astype(np.uint8), np.ones((9, 9), np.uint8)).astype(np.float32)
    rgba = np.dstack([np.full_like(m, c) for c in FLASH_BGR] + [m * 255]).astype(np.uint8)
    p = f"{TMP}/sil_{name}.png"
    cv2.imencode(".png", rgba)[1].tofile(p)
    return p

def render_plates(s, out):
    """Plates appear one after another on the song's ticks: aligned stills of each loading stage, with a small hit on each tick."""
    stills = []
    for k, (ss, _) in enumerate(s["plates"]):
        j = f"{TMP}/pl{k}.jpg"
        ff("-ss", str(ss), "-i", FILES[s["c"]], "-frames:v", "1", "-q:v", "1", j)
        stills.append(cv2.imdecode(np.fromfile(j, np.uint8), 1))
    orb = cv2.ORB_create(6000)
    ref = stills[0]
    kr, dr = orb.detectAndCompute(cv2.cvtColor(ref, cv2.COLOR_BGR2GRAY), None)
    h, w = ref.shape[:2]
    for k in range(1, len(stills)):
        kp, dp = orb.detectAndCompute(cv2.cvtColor(stills[k], cv2.COLOR_BGR2GRAY), None)
        ms = sorted(cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True).match(dp, dr), key=lambda m: m.distance)[:400]
        M, inl = cv2.estimateAffinePartial2D(np.float32([kp[m.queryIdx].pt for m in ms]), np.float32([kr[m.trainIdx].pt for m in ms]), ransacReprojThreshold=4)
        print("  plate align", k, "inliers", int(inl.sum()), "shift", np.round(M[:, 2], 1).tolist(), "scale", round(float(np.hypot(M[0, 0], M[1, 0])), 3), flush=True)
        stills[k] = cv2.warpAffine(stills[k], M, (w, h), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)
    d = f"{TMP}/plateframes"
    shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    n = f(s["b"]) - f(s["a"])
    starts = [f(t) - f(s["a"]) for _, t in s["plates"]]
    cw = int(h * s["s"] * ASPECT); ch = int(h * s["s"])
    x0, y0 = int(w * s["x"] - cw / 2), int(h * s["y"] - ch / 2)
    for i in range(n):
        k = max(j for j, st in enumerate(starts) if st <= i)
        age = i - starts[k]
        z = 1 + (.045 if k else 0) * np.exp(-age / 1.8) + .0006 * i
        cz, cy = cw / z, ch / z
        xa, ya = x0 + (cw - cz) / 2, y0 + (ch - cy) / 2
        A = np.float32([[PW / cz, 0, -xa * PW / cz], [0, PH / cy, -ya * PH / cy]])
        cv2.imencode(".jpg", cv2.warpAffine(stills[k], A, (PW, PH), flags=cv2.INTER_CUBIC), [1, 96])[1].tofile(f"{d}/f{i:04d}.jpg")
    ff("-framerate", str(FPS), "-i", f"{d}/f%04d.jpg", "-vf", f"{GRADE}", "-frames:v", str(n), *ENC, out)

paths = [render_stack()]
for i, s in enumerate(S):
    n = f(s["b"]) - f(s["a"])
    out = f"{TMP}/s{i}.mp4"
    print("shot", i, s["c"], flush=True)
    if "plates" in s:
        render_plates(s, out)
        paths.append(out)
        continue
    chain = f"[0:v]{view(s['s'], s['x'], s['y'], s.get('push', 0), n)},{GRADE}" + ("," + s["extra"] if "extra" in s else "")
    args = ["-ss", str(s["ss"]), "-t", str(n / FPS + .2), "-i", FILES[s["c"]]]
    if "flash" in s:
        args += ["-i", silhouette(S[i + 1], s["flash"], str(i))]
        fc = f"{chain}[b];[b][1:v]overlay=enable='gte(n,{n - FLASH_FRAMES})'[v]"
    else:
        fc = chain + "[v]"
    ff(*args, "-filter_complex", fc, "-map", "[v]", "-frames:v", str(n), *ENC, out)
    paths.append(out)

with open(f"{TMP}/list.txt", "w", encoding="utf-8") as lst:
    for p in paths:
        lst.write(f"file '{p}'\n")

# --- sound: the song plus one effect on each flash ---
rng = np.random.default_rng(7)
with wave.open(SONG) as w:
    SR, CHN = w.getframerate(), w.getnchannels()
    song = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32).reshape(-1, CHN) / 32768
sfx = np.zeros(len(song), np.float32)

def add(t, x):
    i = int(t * SR); k = min(len(x), len(sfx) - i)
    if k > 0:
        sfx[i:i + k] += x[:k]

for s in S:
    if "flash" in s:
        cut = f(s["b"]) / FPS
        rise = FLASH_FRAMES / FPS + .08
        nr = int(rise * SR)
        air = np.diff(rng.standard_normal(nr).astype(np.float32), prepend=0) * np.linspace(0, 1, nr) ** 2.2 * .38
        add(cut - rise, air)
        t = np.arange(int(.5 * SR)) / SR
        add(cut, ((np.sin(2 * np.pi * (58 + 70 * np.exp(-t * 26)) * t) * np.exp(-t * 7.5) * .8) + rng.standard_normal(len(t)) * np.exp(-t * 85) * .3).astype(np.float32))
# a short metal clink on each plate tick
for s in S:
    for _, tick in s.get("plates", [])[1:]:
        t = np.arange(int(.22 * SR)) / SR
        clink = sum(a * np.sin(2 * np.pi * fr * t) * np.exp(-t * d) for a, fr, d in ((.35, 1870, 26), (.25, 2940, 34), (.18, 4310, 48)))
        add(f(tick) / FPS, (clink + rng.standard_normal(len(t)) * np.exp(-t * 160) * .25).astype(np.float32))
mix = song + (sfx * .5)[:, None]
need = np.minimum(1.0, .98 / np.maximum(np.abs(mix).max(axis=1), 1e-6))
win = int(.008 * SR) * 2 + 1
grown = cv2.erode(need.astype(np.float32).reshape(-1, 1), np.ones((win, 1), np.uint8)).ravel()
mix = mix * np.minimum(np.convolve(grown, np.ones(win) / win, mode="same"), 1.0)[:, None]
with wave.open(f"{TMP}/mix.wav", "wb") as w:
    w.setnchannels(CHN); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix.clip(-1, 1) * 32767).astype(np.int16).tobytes())

dest = f"{OUT}/project-3-v{V}.mp4"
ff("-f", "concat", "-safe", "0", "-i", f"{TMP}/list.txt", "-i", f"{TMP}/mix.wav", "-map", "0:v", "-map", "1:a",
   "-vf", f"pad={CW}:{CH}:0:{(CH - PH) // 2}:black", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
   "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", dest)
ff("-i", dest, "-vf", f"fps=6,crop={CW}:{PH}:0:{(CH - PH) // 2},scale=320:-2,tile=10x6,format=yuvj420p", "-frames:v", "1", "-update", "1", "-q:v", "2", f"{W}/sheet-v{V}.jpg")
print("OUT", dest)
