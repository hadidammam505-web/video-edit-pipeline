"""BiRefNet masks limited to a box, keeping the largest blob. cutout venv.
usage: boxmask.py <frames_dir> <out_dir> <x0> <x1> <y0> <y1>   (box as fractions of the frame)
"""
import sys, os, glob
import numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import birefnet_mask as bm

src, dst = sys.argv[1], sys.argv[2]
x0, x1, y0, y1 = map(float, sys.argv[3:7])
os.makedirs(dst, exist_ok=True)
files = sorted(glob.glob(os.path.join(src, "*.jpg")))
sess = bm.session()
for f in files:
    out = os.path.join(dst, os.path.splitext(os.path.basename(f))[0] + ".png")
    if os.path.exists(out):
        continue
    img = cv2.imdecode(np.fromfile(f, np.uint8), 1)
    h, w = img.shape[:2]
    l, r, t, b = int(x0 * w), int(x1 * w), int(y0 * h), int(y1 * h)
    m = bm.mask(sess, img[t:b, l:r])
    full = np.zeros((h, w), np.float32)
    full[t:b, l:r] = m
    k, lab, st, _ = cv2.connectedComponentsWithStats((full > .5).astype(np.uint8))
    if k > 1:
        keep = cv2.dilate((lab == 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))).astype(np.uint8), np.ones((9, 9), np.uint8))
        full *= keep.astype(np.float32)
    cv2.imencode(".png", (full * 255).astype(np.uint8))[1].tofile(out)
print("masks done", len(files))
