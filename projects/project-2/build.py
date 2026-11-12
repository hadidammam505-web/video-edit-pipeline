# Luxury gym edit, modelled on idea-1 (cuts and music) with flash and glitch transitions.
# usage: python3 build.py <version>
import os, subprocess, sys, shutil
import numpy as np, cv2, onnxruntime as ort

V = sys.argv[1] if len(sys.argv) > 1 else "1"
HOME = os.path.expanduser("~").replace("\\", "/")
BIN = HOME + "/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0.2-full_build/bin/ffmpeg.exe"
DATA = HOME + "/Documents/video-edit"
W = DATA + "/projects/project-2"
SRC = HOME + "/Desktop/edting/storage/project 2/"
SONG = DATA + "/refs/project-2/idea-1-song.wav"
OUT = HOME + "/Desktop/edting/results/project 2"
TMP = W + "/tmp"
FILES = {f.split("_")[-1][:4]: SRC + f for f in os.listdir(SRC) if f.upper().endswith(".MOV")}
FPS = 30
W4, H4 = 3840, 2160
for d in (TMP, OUT):
    os.makedirs(d, exist_ok=True)

FIT = f"scale={W4}:{H4}:force_original_aspect_ratio=increase:flags=lanczos,crop={W4}:{H4},setsar=1"
GRADE = ("eq=brightness=-0.05:contrast=1.28:saturation=0.58:gamma=0.72,"
         "curves=all='0/0 0.30/0.10 0.65/0.36 1/0.72',"
         "colorbalance=rs=-0.03:bs=0.05:rm=-0.02:bm=0.02,"
         "vignette=angle=PI/3,noise=alls=4:allf=t")
GRADE_AFTER = GRADE.replace("saturation=0.58", "saturation=1.2")  # everything after the opening carries more colour

def ff(*args, cwd=None):
    r = subprocess.run([BIN, "-v", "error", "-y", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        print(r.stderr[-1500:]); sys.exit(1)

# --- person mask (ISNet) ---
sess = ort.InferenceSession(DATA + "/tools/models/isnet-general-use.onnx", providers=["CPUExecutionProvider"])
INP = sess.get_inputs()[0].name

def rd(p):
    return cv2.imdecode(np.fromfile(p, np.uint8), cv2.IMREAD_COLOR)

def wr(p, im):
    cv2.imencode(os.path.splitext(p)[1], im)[1].tofile(p)

def isnet(bgr):
    h, w = bgr.shape[:2]
    x = cv2.resize(bgr, (1024, 1024), interpolation=cv2.INTER_AREA)[..., ::-1].astype(np.float32) / 255.0
    x = ((x - 0.5) / 1.0).transpose(2, 0, 1)[None]
    y = sess.run(None, {INP: x})[0][0, 0]
    y = (y - y.min()) / (y.max() - y.min() + 1e-6)
    return cv2.resize(y, (w, h), interpolation=cv2.INTER_LINEAR)

def person(bgr, roi, largest=True):
    """Mask inside a normalised region (x0,x1,y0,y1), optionally the largest blob only. The model runs on the region so other people matter less."""
    h, w = bgr.shape[:2]
    x0, x1, y0, y1 = int(roi[0] * w), int(roi[1] * w), int(roi[2] * h), int(roi[3] * h)
    m = np.zeros((h, w), np.float32)
    m[y0:y1, x0:x1] = isnet(bgr[y0:y1, x0:x1])
    if largest:
        n, lab, st, _ = cv2.connectedComponentsWithStats((m > 0.5).astype(np.uint8))
        if n > 1:
            k = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
            keep = cv2.dilate((lab == k).astype(np.uint8), np.ones((9, 9), np.uint8)).astype(np.float32)
            m = m * keep
    return m

def grab(clip, ss, name, width=1920, crop=None):
    p = f"{TMP}/{name}.jpg"
    vf = (crop_filter(crop) + "," if crop else "") + f"scale={width}:-2"
    ff("-ss", str(ss), "-i", FILES[clip], "-frames:v", "1", "-q:v", "2", "-vf", vf, p)
    return p

def crop_filter(c):
    cw, cx, cy = c
    return f"crop=trunc(iw*{cw}/2)*2:trunc(ih*{cw}/2)*2:iw*{cx}:ih*{cy}"

def silhouette(clip, ss, roi, name, crop=None):
    """White figure of a shot's first frame, same position, on a transparent 4K canvas."""
    bgr = rd(grab(clip, ss, "sil_" + name, crop=crop))
    a = person(bgr, roi)
    g = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY).astype(np.float32)
    v = 226 + 29 * g / 255.0
    rgba = np.dstack([v, v, v, a * 255]).clip(0, 255).astype(np.uint8)
    rgba = cv2.resize(rgba, (W4, H4), interpolation=cv2.INTER_CUBIC)
    p = f"{TMP}/sil_{name}.png"
    wr(p, rgba)
    return p

# --- timeline: cuts come from the reference, in seconds ---
# id, start, end, clip, source second, slow-motion factor, crop (size,x,y) or None
# flash = region where the NEXT shot's person is, shown white over the end of this shot
S = [
    dict(id="open",  a=0.100, b=3.167, c="C042", ss=15.0),
    dict(id="pose1", a=3.167, b=3.667, c="C044", ss=4.0,  roi=(0.25, 0.60, 0.25, 1.0)),    # flash in
    dict(id="pose2", a=3.667, b=4.200, c="C043", ss=12.0),
    dict(id="pose3", a=4.200, b=4.867, c="C046", ss=12.0),
    dict(id="glitch", a=4.867, b=5.933, c="C045", ss=24.0, plate=2.0),                      # glitch
    dict(id="tbar",  a=5.933, b=7.733, c="C036", ss=54.0, slow=2),
    dict(id="fly1",  a=7.733, b=8.467, c="C043", ss=33.0),
    dict(id="fly2",  a=8.467, b=8.867, c="C042", ss=27.0),
    dict(id="pull1", a=8.867, b=9.433, c="C044", ss=30.0),
    dict(id="zoom",  a=9.433, b=10.667, c="C045", ss=27.0, slow=2, punch=(0.55, 0.26, 0.10)),
    dict(id="pose4", a=10.667, b=11.400, c="C046", ss=36.0, roi=(0.38, 0.62, 0.0, 1.0)),   # flash in
    dict(id="row1",  a=11.400, b=11.933, c="C033", ss=9.0),
    dict(id="row2",  a=11.933, b=12.300, c="C034", ss=9.0),
    dict(id="fly3",  a=12.300, b=12.533, c="C043", ss=42.0),
    dict(id="pull2", a=12.533, b=12.867, c="C044", ss=42.0),
    dict(id="pose5", a=12.867, b=13.600, c="C046", ss=63.0),
    dict(id="end",   a=13.600, b=14.740, c="C045", ss=45.0, slow=2),
]
FLASH_FRAMES = 5
WORD = "DISCIPLINE"
PER_FRAME_MATTE = W + "/v2test/matte"  # frames made with personmask.py then matte.py; empty string = ISNet every third frame
# the song's fast ticks, measured with librosa: they start at 0.49, the bass drop comes at 3.03
TICKS = [0.49, 0.58, 0.67, 0.77, 0.86, 0.95, 1.03, 1.13, 1.22, 1.31, 1.40, 1.50, 1.58, 1.68, 1.76, 1.86, 1.95, 2.04, 2.14, 2.22, 2.38, 2.47, 2.57, 2.66, 2.76, 2.84, 3.03]
BAND_BITS = [("C033", 9.0), ("C043", 27.0), ("C044", 21.0), ("C036", 60.0), ("C046", 12.0), ("C045", 30.0), ("C042", 36.0), ("C034", 12.0),
             ("C043", 45.0), ("C036", 54.0), ("C044", 36.0), ("C046", 63.0), ("C045", 42.0), ("C033", 15.0), ("C042", 51.0), ("C043", 33.0),
             ("C044", 48.0), ("C036", 75.0), ("C034", 6.0), ("C045", 57.0), ("C046", 36.0), ("C042", 27.0), ("C043", 21.0), ("C044", 30.0),
             ("C036", 66.0), ("C033", 12.0), ("C045", 27.0)]
GLITCH_PATTERN = [("e", 4), ("s", 2), ("e", 3), ("s", 2), ("e", 2), ("s", 1), ("e", 2), ("s", 1), ("e", 1), ("s", 1)]

def frames(t):
    return int(round(t * FPS))

def src_filter(shot):
    slow = shot.get("slow", 1)
    return (f"setpts={slow}*PTS,fps={FPS}," if slow != 1 else f"fps={FPS},") + FIT

def render(shot, next_shot):
    n = frames(shot["b"]) - frames(shot["a"])
    du = n / FPS
    slow = shot.get("slow", 1)
    out = f"{TMP}/{shot['id']}.mp4"
    inputs = ["-ss", str(shot["ss"]), "-t", str(du * slow + 0.2), "-i", FILES[shot["c"]]]
    chain = f"[0:v]{src_filter(shot)},{GRADE_AFTER}"
    if "punch" in shot:
        # zoom transition: fast punch-in on the first 0.35s, then hold close
        z, x, y = shot["punch"]
        k = int(0.35 * FPS)
        zm = f"1+({1/z-1})*pow(min(1,on/{k}),2)"
        chain = (f"[0:v]{src_filter(shot)},zoompan=z='{zm}':x='iw*{x}*(zoom-1)/{1/z-1}':y='ih*{y}*(zoom-1)/{1/z-1}'"
                 f":d=1:s={W4}x{H4}:fps={FPS},{GRADE_AFTER}")
    fc = chain + "[v]"
    extra = []
    if next_shot is not None and "roi" in next_shot:
        sil = silhouette(next_shot["c"], next_shot["ss"], next_shot["roi"], next_shot["id"])
        extra = ["-i", sil]
        fc = f"{chain}[b];[b][1:v]overlay=enable='gte(n,{n - FLASH_FRAMES})'[v]"
    ff(*inputs, *extra, "-filter_complex", fc, "-map", "[v]", "-frames:v", str(n),
       "-c:v", "libx264", "-preset", "fast", "-crf", "15", "-pix_fmt", "yuv420p", out)
    return out

def render_glitch(shot):
    """Empty machine and the same locked shot with the person, flickering, then stay on the person."""
    n = frames(shot["b"]) - frames(shot["a"])
    pattern = list(GLITCH_PATTERN)
    head = sum(k for _, k in pattern)
    pattern.append(("s", n - head))
    plate, subj = f"{TMP}/g_plate.mp4", f"{TMP}/g_subj.mp4"
    for p, ss in ((plate, shot["plate"]), (subj, shot["ss"])):
        ff("-ss", str(ss), "-t", str(n / FPS + 0.2), "-i", FILES[shot["c"]], "-vf", f"fps={FPS},{FIT},{GRADE_AFTER}", "-frames:v", str(n),
           "-c:v", "libx264", "-preset", "fast", "-crf", "15", "-pix_fmt", "yuv420p", p)
    parts, pos, labels = [], 0, []
    for i, (w, k) in enumerate(pattern):
        idx = 0 if w == "e" else 1
        parts.append(f"[{idx}:v]trim=start_frame={pos}:end_frame={pos + k},setpts=PTS-STARTPTS[p{i}]")
        labels.append(f"[p{i}]")
        pos += k
    fc = ";".join(parts) + ";" + "".join(labels) + f"concat=n={len(pattern)}:v=1:a=0[v]"
    out = f"{TMP}/{shot['id']}.mp4"
    ff("-i", plate, "-i", subj, "-filter_complex", fc, "-map", "[v]", "-frames:v", str(n),
       "-c:v", "libx264", "-preset", "fast", "-crf", "15", "-pix_fmt", "yuv420p", out)
    return out

def render_open(shot, next_shot):
    """Back to camera, big red word behind the person, fast shots flickering in a band behind the word."""
    n = frames(shot["b"]) - frames(shot["a"])
    du = n / FPS
    # masks every third frame, blended in between
    md = f"{TMP}/openmask"
    shutil.rmtree(md, ignore_errors=True)
    os.makedirs(md)
    if PER_FRAME_MATTE:
        # one MODNet matte per frame (person only), averaged over 3 frames so edges don't shimmer
        rdm = lambda i: cv2.imdecode(np.fromfile(f"{PER_FRAME_MATTE}/f{min(i, n - 1) + 1:04d}.png", np.uint8), 0).astype(np.float32)
        for i in range(n):
            m = (rdm(max(i - 1, 0)) + rdm(i) + rdm(i + 1)) / 3 / 255
            # firm up the edge and drop half-transparent patches outside the body
            m = ((m - 0.45) / 0.3).clip(0, 1)
            cnt, lab, st, _ = cv2.connectedComponentsWithStats((m > 0.5).astype(np.uint8))
            if cnt > 1:
                k = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
                m = m * cv2.dilate((lab == k).astype(np.uint8), np.ones((7, 7), np.uint8)).astype(np.float32)
            wr(f"{md}/m{i:04d}.png", (m * 255).clip(0, 255).astype(np.uint8))
    else:
        ff("-ss", str(shot["ss"]), "-t", str(du + 0.2), "-i", FILES[shot["c"]], "-vf", f"fps={FPS / 3},scale=1280:-2", "-q:v", "3", f"{md}/k%03d.jpg")
        keys = sorted(f for f in os.listdir(md) if f.startswith("k"))
        ms = [person(rd(f"{md}/{f}"), (0.0, 1.0, 0.0, 1.0), largest=True) for f in keys]
        for i in range(n):
            p = i / 3
            a = min(int(p), len(ms) - 1)
            b = min(a + 1, len(ms) - 1)
            m = ms[a] * (1 - (p - int(p))) + ms[b] * (p - int(p))
            wr(f"{md}/m{i:04d}.png", (m * 255).clip(0, 255).astype(np.uint8))
    # box of fast shots: one shot per tick of the song's fast pattern, which starts at 0.49s
    first, last_full = frames(TICKS[0]) - frames(shot["a"]), n - FLASH_FRAMES
    edges = [frames(t) - frames(shot["a"]) for t in TICKS if frames(t) - frames(shot["a"]) < n] + [n]
    bl = f"{TMP}/band.txt"
    with open(bl, "w", encoding="utf-8") as f:
        for i, (e0, e1) in enumerate(zip(edges, edges[1:])):
            c, ss = BAND_BITS[i % len(BAND_BITS)]
            p = f"{TMP}/band{i}.mp4"
            ff("-ss", str(ss), "-t", "0.4", "-i", FILES[c], "-vf", f"fps={FPS},{FIT},{GRADE}", "-frames:v", str(e1 - e0), "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p", p)
            f.write(f"file '{p}'\n")
    band = f"{TMP}/band.mp4"
    ff("-f", "concat", "-safe", "0", "-i", bl, "-c", "copy", band)
    # the box grows from a thin line to the full frame, reaching it just before the flash
    bm = f"{TMP}/bandmask"
    shutil.rmtree(bm, ignore_errors=True)
    os.makedirs(bm)
    mh, mw = 1080, 1920
    for i in range(n - first):
        p = min(1.0, i / max(1, last_full - first - 1))
        h = int(mh * (0.012 + 0.988 * p ** 1.15))
        fr = np.zeros((mh, mw), np.uint8)
        fr[(mh - h) // 2:(mh + h) // 2, :] = 255
        wr(f"{bm}/b{i:04d}.png", fr)
    t_band0 = first / FPS
    t_in, t_out = 1.15, 2.77
    ty = int(H4 * 0.5)
    txt = (f"drawtext=fontfile=impact.ttf:text='{WORD}':fontsize=840:fontcolor=0xE5301C:x=(w-text_w)/2:y={ty}-text_h/2:"
           f"alpha='if(lt(t,{t_in}),0,if(lt(t,{t_in + 0.12}),(t-{t_in})/0.12,if(gt(t,{t_out}),max(0,1-(t-{t_out})/0.2),1)))'")
    fc = (f"[0:v]fps={FPS},{FIT},{GRADE},split=3[base][fg0][blur0];"
          f"[blur0]gblur=sigma=46,fade=out:st=0.25:d=0.45:alpha=1,format=yuva420p[blur];"
          f"[3:v]fps={FPS},scale={W4}:{H4}:flags=neighbor,format=gray[bmk];"
          f"[1:v]fps={FPS},format=yuv420p[bv];[bv][bmk]alphamerge,setpts=PTS+{t_band0}/TB[bd];"
          f"[base][bd]overlay=0:0:eof_action=pass[b1];"
          f"[b1]{txt}[b2];"
          f"[2:v]fps={FPS},scale={W4}:{H4},format=gray[mk];"
          f"[fg0][mk]alphamerge[fg];"
          f"[b2][fg]overlay=0:0[b3];[b3][blur]overlay=0:0[b4]")
    extra, last = [], "b4"
    if next_shot is not None and "roi" in next_shot:
        sil = silhouette(next_shot["c"], next_shot["ss"], next_shot["roi"], next_shot["id"])
        extra = ["-i", sil]
        fc += f";[b4][4:v]overlay=enable='gte(n,{n - FLASH_FRAMES})'[v]"
        last = "v"
    out = f"{TMP}/{shot['id']}.mp4"
    ff("-ss", str(shot["ss"]), "-t", str(du + 0.2), "-i", FILES[shot["c"]], "-i", band,
       "-framerate", str(FPS), "-i", f"{md}/m%04d.png", "-framerate", str(FPS), "-i", f"{bm}/b%04d.png", *extra,
       "-filter_complex", fc, "-map", f"[{last}]", "-frames:v", str(n),
       "-c:v", "libx264", "-preset", "fast", "-crf", "15", "-pix_fmt", "yuv420p", out, cwd="C:/Windows/Fonts")
    return out

paths = []
black = f"{TMP}/black.mp4"
ff("-f", "lavfi", "-i", f"color=black:s={W4}x{H4}:r={FPS}", "-frames:v", str(frames(S[0]["a"])), "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p", black)
paths.append(black)
MODE = sys.argv[2] if len(sys.argv) > 2 else ""  # audio = reuse all shots, open = only the opening, after = all but the opening
for i, s in enumerate(S):
    nxt = S[i + 1] if i + 1 < len(S) else None
    if MODE == "audio" or (MODE == "open" and s["id"] != "open") or (MODE == "after" and s["id"] == "open"):
        paths.append(f"{TMP}/{s['id']}.mp4")
        continue
    print("shot", s["id"], flush=True)
    if s["id"] == "open":
        paths.append(render_open(s, nxt))
    elif "plate" in s:
        paths.append(render_glitch(s))
    else:
        paths.append(render(s, nxt))

lst = f"{TMP}/list.txt"
with open(lst, "w", encoding="utf-8") as f:
    for p in paths:
        f.write(f"file '{p}'\n")

# --- sound: the song plus one synthesised effect per transition, placed on the frame it happens ---
import wave
rng = np.random.default_rng(7)
with wave.open(SONG) as w:
    SR, CH = w.getframerate(), w.getnchannels()
    song = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32).reshape(-1, CH) / 32768
sfx = np.zeros(len(song), np.float32)

def add(t, x):
    i = int(t * SR)
    if 0 <= i < len(sfx):
        k = min(len(x), len(sfx) - i)
        sfx[i:i + k] += x[:k]

def flash_sound(rise):
    """Air rising into the white frame, then a soft low hit and a bright tick on the cut."""
    n = int(rise * SR)
    air = rng.standard_normal(n).astype(np.float32)
    air = np.diff(air, prepend=0) * np.linspace(0, 1, n) ** 2.2 * 0.38
    m = int(0.55 * SR)
    t = np.arange(m) / SR
    hit = np.sin(2 * np.pi * (58 + 70 * np.exp(-t * 26)) * t) * np.exp(-t * 7.5) * 0.8
    tick = rng.standard_normal(m).astype(np.float32) * np.exp(-t * 85) * 0.3
    return air, (hit + tick).astype(np.float32)

def glitch_sound(dur, freq):
    """A short digital buzz, one per flicker."""
    n = max(int(dur * SR), 64)
    t = np.arange(n) / SR
    sq = np.sign(np.sin(2 * np.pi * freq * t))
    hold = max(2, int(SR / rng.integers(1800, 5200)))
    no = np.repeat(rng.standard_normal(n // hold + 1), hold)[:n]
    env = np.minimum(1, np.minimum(t * 900, (t[-1] - t) * 900 + 0.02))
    return ((0.42 * sq + 0.38 * no) * env).astype(np.float32)

for i, s in enumerate(S):
    nxt = S[i + 1] if i + 1 < len(S) else None
    if nxt is not None and "roi" in nxt:
        air, hit = flash_sound(FLASH_FRAMES / FPS)
        cut = frames(s["b"]) / FPS
        add(cut - FLASH_FRAMES / FPS, air)
        add(cut, hit)
    if "plate" in s:
        pos = frames(s["a"])
        for j, (_, k) in enumerate(GLITCH_PATTERN):
            add(pos / FPS, glitch_sound(k / FPS, float(rng.integers(140, 1500))))
            pos += k

SFX_GAIN = 0.5
mix = song + (sfx * SFX_GAIN)[:, None]
# the song stays at its own level: only the moments where an effect pushes the sum over the top are pulled down
over = np.maximum(np.abs(mix).max(axis=1), 1e-6)
need = np.minimum(1.0, 0.98 / over)
win = int(0.008 * SR) * 2 + 1
grown = cv2.erode(need.astype(np.float32).reshape(-1, 1), np.ones((win, 1), np.uint8)).ravel()
gain = np.convolve(grown, np.ones(win) / win, mode="same").astype(np.float32)
mix = mix * np.minimum(gain, 1.0)[:, None]
print("limiter: lowest gain", round(float(gain.min()), 3), "song peak", round(float(np.abs(song).max()), 3), "mix peak", round(float(np.abs(mix).max()), 3))
mixp = f"{TMP}/mix.wav"
with wave.open(mixp, "wb") as w:
    w.setnchannels(CH); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())

dest = f"{OUT}/project-2-v{V}.mp4"
ff("-f", "concat", "-safe", "0", "-i", lst, "-i", mixp, "-map", "0:v", "-map", "1:a",
   "-vf", "fade=out:st=13.95:d=0.75", "-af", "afade=out:st=14.2:d=0.5",
   "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
   "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", dest)
ff("-i", dest, "-vf", "fps=6,scale=320:-2,tile=12x8", "-frames:v", "1", "-q:v", "3", f"{W}/sheet-v{V}.jpg")
print("OUT", dest)
