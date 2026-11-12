"""Clean up soft, noisy footage with Real-ESRGAN general-x4v3 (BSD-3, weights only, no third-party code).
Run with the vision venv. The network is SRVGGNetCompact, written here from the published architecture.

usage: esrgan.py <in> <out.mov> --ss S --t T [--pre 0.5] [--denoise 0.5] [--w 2160]
  --pre      scale the input first (0.5 = half size; the 4x net then returns 2x the original)
  --denoise  0 = weak-denoise model only (keeps more grain/detail), 1 = full denoise model
  --w        output width; the result is resized to this with lanczos
  --vf       ffmpeg filters run first. Tested 2026-11-12: "hqdn3d=0:0:6:6" (temporal only) + --pre 1 --denoise 0.5
             was the best mix on the dark bedroom clips: the net sharpens, hqdn3d stops the per-frame shimmer.
             --pre 0.5 looked painted (plastic skin), so keep --pre 1. About 1.2 s per 2160x1214 frame on the RTX 5060.
Output is ProRes 422 HQ so nothing is lost before the final edit.
"""
import argparse, subprocess, json, numpy as np, torch, torch.nn as nn, torch.nn.functional as F

M = "C:/Users/ZGAMES/Documents/video-edit/tools/models/realesrgan/"

class SRVGG(nn.Module):
    def __init__(s, feat=64, conv=32, up=4):
        super().__init__(); s.up = up
        b = [nn.Conv2d(3, feat, 3, 1, 1), nn.PReLU(feat)]
        for _ in range(conv): b += [nn.Conv2d(feat, feat, 3, 1, 1), nn.PReLU(feat)]
        b += [nn.Conv2d(feat, 3 * up * up, 3, 1, 1)]
        s.body = nn.ModuleList(b); s.ps = nn.PixelShuffle(up)
    def forward(s, x):
        y = x
        for m in s.body: y = m(y)
        return s.ps(y) + F.interpolate(x, scale_factor=s.up, mode="nearest")

def load(dn):
    a = torch.load(M + "realesr-general-x4v3.pth", map_location="cpu", weights_only=True)["params"]
    b = torch.load(M + "realesr-general-wdn-x4v3.pth", map_location="cpu", weights_only=True)["params"]
    net = SRVGG(); net.load_state_dict({k: dn * a[k] + (1 - dn) * b[k] for k in a})
    return net.eval().cuda().half()

ap = argparse.ArgumentParser()
ap.add_argument("inp"); ap.add_argument("out")
ap.add_argument("--ss", type=float, default=0); ap.add_argument("--t", type=float, default=0)
ap.add_argument("--pre", type=float, default=0.5); ap.add_argument("--denoise", type=float, default=0.5)
ap.add_argument("--w", type=int, default=2160)
ap.add_argument("--crop", default="", help="w:h:x:y in display pixels, applied before --pre")
ap.add_argument("--fps", default="", help="output frame rate, e.g. 30 (drops frames from a 60 fps source)")
ap.add_argument("--vf", default="", help="ffmpeg filters before the net, e.g. hqdn3d=0:0:6:6 for temporal denoise")
A = ap.parse_args()

pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
     "stream=width,height,r_frame_rate:stream_side_data=rotation", "-of", "json", A.inp], capture_output=True, text=True).stdout)["streams"][0]
W, H = pr["width"], pr["height"]
if any(abs(d.get("rotation", 0)) == 90 for d in pr.get("side_data_list", [])): W, H = H, W
if A.crop: W, H = [int(v) for v in A.crop.split(":")[:2]]
iw, ih = int(W * A.pre) // 2 * 2, int(H * A.pre) // 2 * 2
ow = A.w; oh = int(round(ow * ih / iw / 2)) * 2
dec = ["ffmpeg", "-nostdin", "-v", "error", "-ss", str(A.ss)] + (["-t", str(A.t)] if A.t else []) + \
      ["-i", A.inp, "-vf", ",".join(x for x in [f"fps={A.fps}" if A.fps else "", f"crop={A.crop}" if A.crop else "", A.vf, f"scale={iw}:{ih}:flags=area"] if x), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
enc = ["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb48le", "-s", f"{iw*4}x{ih*4}",
       "-r", A.fps or pr["r_frame_rate"], "-i", "-", "-vf", f"scale={ow}:{oh}:flags=lanczos", "-c:v", "prores_ks", "-profile:v", "3",
       "-pix_fmt", "yuv422p10le", A.out]
net = load(A.denoise)
d = subprocess.Popen(dec, stdout=subprocess.PIPE); e = subprocess.Popen(enc, stdin=subprocess.PIPE)
n = 0
with torch.inference_mode():
    while True:
        buf = d.stdout.read(iw * ih * 3)
        if len(buf) < iw * ih * 3: break
        x = torch.frombuffer(bytearray(buf), dtype=torch.uint8).view(ih, iw, 3).cuda().permute(2, 0, 1)[None].half() / 255
        y = net(x).clamp(0, 1)[0].permute(1, 2, 0).float().mul(65535).round().to(torch.int32).cpu().numpy().astype("<u2")
        e.stdin.write(y.tobytes()); n += 1
e.stdin.close(); e.wait(); d.wait()
print("frames", n, "->", A.out, f"{ow}x{oh}")
