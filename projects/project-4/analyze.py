# Frame-level measurements of a reference. usage: analyze.py file.mp4
import sys
import cv2, numpy as np

cap = cv2.VideoCapture(sys.argv[1])
fps = cap.get(cv2.CAP_PROP_FPS)
frames = []
while True:
    ok, f = cap.read()
    if not ok:
        break
    frames.append(cv2.resize(f, (f.shape[1] // 2, f.shape[0] // 2), interpolation=cv2.INTER_AREA))
A = np.stack(frames).astype(np.float32)
n, h, w = A.shape[:3]
gray = A.mean(axis=3)

# picture bounds: rows/cols that are ever brighter than letterbox black
prow, pcol = gray.max(axis=0).max(axis=1), gray.max(axis=0).max(axis=0)
ys, xs = np.where(prow > 40)[0], np.where(pcol > 40)[0]
y0, y1, x0, x1 = ys[0], ys[-1] + 1, xs[0], xs[-1] + 1
print("size", w * 2, h * 2, "fps %.3f" % fps, "frames", n, "picture x", x0 * 2, x1 * 2, "y", y0 * 2, y1 * 2)

# per-frame picture bounds, to catch shots that use a different frame
rows = (gray.max(axis=2) > 30)
prev = None
for i in range(n):
    r = np.where(rows[i])[0]
    b = (int(r[0]) * 2, int(r[-1] + 1) * 2) if len(r) else None
    if b != prev and (b is None or prev is None or abs(b[0] - prev[0]) > 8 or abs(b[1] - prev[1]) > 8):
        print("  bounds change %.3f f%d -> %s" % (i / fps, i, b))
    prev = b

P = gray[:, y0:y1, x0:x1]
# ignore pixels near centre text by using a coarse grid of medians
small = np.stack([cv2.resize(p, (32, 18), interpolation=cv2.INTER_AREA) for p in P])
d = np.median(np.abs(small[1:] - small[:-1]), axis=(1, 2))
d2 = np.percentile(np.abs(small[1:] - small[:-1]), 75, axis=(1, 2))
base = np.median(d2)
cuts = [i + 1 for i in range(len(d2)) if d2[i] > max(9, 3.5 * base) and d2[i] >= d2[max(0, i - 1):i + 2].max()]
print("cuts:", " ".join("%.3f" % (c / fps) for c in cuts))
print("cut frames:", cuts)
mean = P.mean(axis=(1, 2))
print("white frames:", [("%.3f" % (i / fps), int(mean[i])) for i in range(n) if mean[i] > max(110, np.median(mean) * 2.4)])
print("dark frames:", [("%.3f" % (i / fps)) for i in range(n) if mean[i] < 3.5][:80])
# colour shift (glitch): big difference between channels
c = A[:, y0:y1, x0:x1]
chroma = np.abs(c[..., 0] - c[..., 1]).mean(axis=(1, 2))
print("chroma peaks:", [("%.3f" % (i / fps), int(chroma[i])) for i in range(n) if chroma[i] > np.median(chroma) * 2.5])
