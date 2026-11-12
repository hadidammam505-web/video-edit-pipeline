# Track the moving plates through each squat clip and list every rep. cutout venv (auto-rotates).
import os
import cv2, numpy as np

SRC = os.path.expanduser("~") + "/Desktop/edting/storage/project 4/"
F = {f.split("_")[-1][:4]: SRC + f for f in os.listdir(SRC) if f.upper().endswith(".MOV")}
# clip: start, end, template box, search box (fractions x0 x1 y0 y1)
C = {"C073": (50, 165, (.18, .33, .45, .75), (.03, .65, .15, 1)),
     "C075": (3, 97, (.05, .25, .6, .95), (0, .6, .3, 1)),
     "C077": (37, 149, (.17, .3, .33, .57), (.03, .55, .1, .85))}
STEP = 2


def track(c, a, b, tb, sb):
    path = f"scan/track_{c}.npz"
    if os.path.exists(path):
        d = np.load(path)
        return d["T"], d["P"]
    cap = cv2.VideoCapture(F[c])
    cap.set(cv2.CAP_PROP_POS_MSEC, a * 1000)
    tpl, P, T, i = None, [], [], 0
    fps = cap.get(cv2.CAP_PROP_FPS)
    while True:
        ok, f = cap.read()
        if not ok or a + i / fps > b:
            break
        if i % STEP == 0:
            g = cv2.cvtColor(cv2.resize(f, (960, 540), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY)
            if tpl is None:
                tpl = g[int(tb[2] * 540):int(tb[3] * 540), int(tb[0] * 960):int(tb[1] * 960)]
            y0, x0 = int(sb[2] * 540), int(sb[0] * 960)
            r = cv2.matchTemplate(g[y0:int(sb[3] * 540), x0:int(sb[1] * 960)], tpl, cv2.TM_CCOEFF_NORMED)
            _, score, _, loc = cv2.minMaxLoc(r)
            P.append((loc[0] + x0, loc[1] + y0, score))
            T.append(a + i / fps)
        i += 1
    P, T = np.array(P, np.float32), np.array(T)
    np.savez(path, T=T, P=P)
    return T, P


for c, (a, b, tb, sb) in C.items():
    T, P = track(c, a, b, tb, sb)
    good = P[:, 2] > .45
    xy = P[:, :2] - np.median(P[good, :2], axis=0)
    u = np.linalg.svd(xy[good], full_matrices=False)[2][0]
    s = np.convolve(xy @ u, np.ones(5) / 5, mode="same")
    th = .25 * (np.percentile(s[good], 97) - np.percentile(s[good], 3))
    # zigzag: alternate extremes separated by at least th
    ext, hi, lo, d = [], 0, 0, 0
    for i in range(1, len(s)):
        if d >= 0 and s[i] > s[hi]:
            hi = i
        if d <= 0 and s[i] < s[lo]:
            lo = i
        if d >= 0 and s[hi] - s[i] > th:
            ext.append(hi); d = -1; lo = i
        elif d <= 0 and s[i] - s[lo] > th:
            ext.append(lo); d = 1; hi = i
    print("==", c, "threshold px", round(float(th), 1), "good", round(float(good.mean()), 2), "legs", len(ext) - 1)
    print(" ".join("%.1f(%+.0f)" % (T[i], s[i]) for i in ext))
