"""Project 6 transitions between shots, made on the GPU from the rendered segment files.
  flash  : body flash. In the last 4 frames of A, a glowing white silhouette of the person in B appears where B's person
           will be (A dims); after the cut, the white leaves B's body over 5 frames, following its SAM 2 mask.
  slide  : whip pan. A slides out and B slides in over 8 frames (4 + 4) with horizontal motion blur. dir +1 = to the left.
  glitch : 6 frames (3 + 3) flickering between A and B with RGB split, displaced horizontal bands and scanlines.
Masks: track/<B name>/masks/00000.png ... (720x1280, from tools/sam2track.py).
"""
import os, subprocess, numpy as np, torch, torch.nn.functional as F
from PIL import Image

K = {"flash": (4, 5), "slide": (4, 4), "glitch": (3, 3)}
DEV = "cuda"

def read_frames(path, first, count, W, H):
    vf = f"select='between(n\\,{first}\\,{first+count-1})'"
    r = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", path, "-vf", vf, "-fps_mode", "passthrough", "-f", "rawvideo",
                        "-pix_fmt", "rgb24", "-"], capture_output=True)
    a = np.frombuffer(r.stdout, np.uint8)
    n = a.size // (W * H * 3)
    assert n == count, (path, first, count, n)
    return torch.from_numpy(a.reshape(n, H, W, 3).copy()).to(DEV).permute(0, 3, 1, 2).float() / 255

def write_frames(frames, path, fps, crf, preset):
    p = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{frames.shape[3]}x{frames.shape[2]}", "-r", str(fps), "-i", "-", "-c:v", "libx264",
                          "-preset", preset, "-crf", str(crf), "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    for f in frames:
        p.stdin.write((f.clamp(0, 1) * 255).round().byte().permute(1, 2, 0).cpu().numpy().tobytes())
    p.stdin.close(); p.wait()

def gblur(x, sigma):
    """separable gaussian on (N,C,H,W)"""
    r = max(1, int(sigma * 3)); t = torch.arange(-r, r + 1, device=x.device).float()
    k = torch.exp(-t * t / (2 * sigma * sigma)); k = k / k.sum(); c = x.shape[1]
    x = F.conv2d(F.pad(x, (r, r, 0, 0), mode="replicate"), k.view(1, 1, 1, -1).repeat(c, 1, 1, 1), groups=c)
    return F.conv2d(F.pad(x, (0, 0, r, r), mode="replicate"), k.view(1, 1, -1, 1).repeat(c, 1, 1, 1), groups=c)

def load_mask(track_dir, j, W, H, S):
    from scipy import ndimage
    m = np.asarray(Image.open(os.path.join(track_dir, "masks", "%05d.png" % j)).convert("L")) > 127
    m = ndimage.binary_opening(m, iterations=2)              # drop the speckle SAM leaves on machines
    lab, n = ndimage.label(m)
    if n > 1:                                               # keep the person: the biggest piece
        m = lab == (np.bincount(lab.ravel())[1:].argmax() + 1)
    m = ndimage.binary_closing(m, iterations=4); m = ndimage.binary_fill_holes(m)
    m = torch.from_numpy(m.astype(np.float32)).to(DEV)[None, None]
    m = F.interpolate(m, size=(H, W), mode="bilinear", align_corners=False)
    return gblur(m, 3 * S + 0.5).clamp(0, 1)

def flash(A, B, mdir, S):
    W, H = A.shape[3], A.shape[2]
    m0 = load_mask(mdir, 0, W, H, S); glow0 = gblur(m0, 40 * S)
    out = []
    for i, a in enumerate([0.30, 0.55, 0.80, 1.00]):
        f = A[i:i + 1] * (1 - 0.13 * (i + 1))
        f = f * (1 - a * m0) + a * m0
        f = 1 - (1 - f) * (1 - 0.75 * a * glow0)               # screen the glow
        out.append(f)
    for j, b in enumerate([1.00, 0.78, 0.52, 0.28, 0.10]):
        m = load_mask(mdir, j, W, H, S); g = gblur(m, 40 * S)
        f = B[j:j + 1] * (1 + 0.18 * b)
        f = f * (1 - b * m) + b * m
        f = 1 - (1 - f) * (1 - 0.6 * b * g)
        out.append(f)
    return torch.cat(out)

def hblur(x, L):
    L = int(L)
    if L < 2: return x
    c = torch.cumsum(F.pad(x, (L, 0, 0, 0), mode="replicate"), dim=3)
    return (c[..., L:] - c[..., :-L]) / L

def slide(A, B, d, S):
    W = A.shape[3]; n = 8
    p = [0.5 - 0.5 * np.cos(np.pi * (i + 0.5) / n) for i in range(n)]
    out = []
    for i in range(n):
        a = A[min(i, 3):min(i, 3) + 1]; b = B[max(i - 4, 0):max(i - 4, 0) + 1]
        sh = int(round(p[i] * W)); canvas = torch.zeros_like(a)
        if d > 0:   # content moves left
            canvas[..., :W - sh] = a[..., sh:]; canvas[..., W - sh:] = b[..., :sh]
        else:
            canvas[..., sh:] = a[..., :W - sh]; canvas[..., :sh] = b[..., W - sh:]
        v = (p[min(i + 1, n - 1)] - p[max(i - 1, 0)]) / 2 * W
        out.append(hblur(canvas, min(v * 0.9, W * 0.3)))
    return torch.cat(out)

def glitch(A, B, S, seed):
    g = torch.Generator(device="cpu").manual_seed(seed)
    W, H = A.shape[3], A.shape[2]
    plan = [(A[0], A[0], 0.35), (A[1], B[0], 0.9), (A[2], A[2], 1.0), (B[0], A[2], 1.0), (B[1], B[1], 0.6), (B[2], B[2], 0.25)]
    out = []
    for base, other, s in plan:
        f = base.clone()
        k = int(W * (0.004 + 0.016 * s))                       # RGB split, as a share of the width
        f[0] = torch.roll(base[0], k, dims=1); f[2] = torch.roll(base[2], -k, dims=1)
        nb = int(4 + 10 * s)
        for _ in range(nb):                                    # displaced bands, some taken from the other shot
            h = int((torch.rand(1, generator=g) * 0.08 + 0.01) * H); y = int(torch.rand(1, generator=g) * (H - h))
            dx = int((torch.rand(1, generator=g) - 0.5) * 2 * 0.25 * W * s)
            src = other if torch.rand(1, generator=g) < 0.4 else f
            f[:, y:y + h] = torch.roll(src[:, y:y + h], dx, dims=2)
        lines = (torch.arange(H, device=f.device) % max(2, H // 320) == 0).float().view(1, H, 1)
        f = f * (1 - 0.18 * s * lines)
        f = f * (1 + 0.25 * s * (torch.rand(1, generator=g).item() - 0.3))
        out.append(f[None])
    return torch.cat(out)

def make(kind, a_path, a_frames, b_path, W, H, S, fps, crf, preset, out, mdir=None, d=1, seed=0):
    ka, kb = K[kind]
    A = read_frames(a_path, a_frames - ka, ka, W, H); B = read_frames(b_path, 0, kb, W, H)
    with torch.inference_mode():
        if kind == "flash": T = flash(A, B, mdir, S)
        elif kind == "slide": T = slide(A, B, d, S)
        else: T = glitch(A, B, S, seed)
    write_frames(T, out, fps, crf, preset)
    return ka, kb
