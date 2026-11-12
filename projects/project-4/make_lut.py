# A clean commercial look for bright gym footage: gentle film curve, natural skin, reds held back, soft teal shadows.
import colorsys, os
import numpy as np

N = 33
OUT = os.path.expanduser("~").replace("\\", "/") + "/Documents/video-edit/projects/project-4/extras/P4_Pro.cube"


def curve(x):
    x = np.clip(x, 0, 1) ** 1.10                          # settle mids a little, not dark
    s = x * x * (3 - 2 * x)
    y = x + .42 * (s - x)                                 # gentle contrast
    knee = .82
    return np.where(y > knee, knee + (1 - knee) * (1 - np.exp(-(y - knee) / (1 - knee))) / (1 - np.exp(-1)), y)


def grade(r, g, b):
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    deg = h * 360
    red = max(0, 1 - min(abs(deg - 355), abs(deg + 5), abs(deg - 360 + 5)) / 18) * min(1, s / .55)   # saturated machine red
    skin = max(0, 1 - abs(deg - 24) / 20) * (1 - max(0, s - .7) / .3)
    s2 = s * (1 + .08 * skin) * (1 - .24 * red)
    v2 = v * (1 - .12 * red)
    r2, g2, b2 = colorsys.hsv_to_rgb(h, min(s2, 1), v2)
    rgb = curve(np.array([r2, g2, b2]))
    luma = float(rgb @ [.2126, .7152, .0722])
    shadow, high = (1 - luma) ** 2, luma ** 2
    rgb = rgb + shadow * np.array([-.012, .004, .014]) + high * np.array([.012, .004, -.012])  # teal shadows, warm highs
    return np.clip(rgb, 0, 1)


with open(OUT, "w", encoding="ascii") as fh:
    fh.write('TITLE "P4 Pro"\nLUT_3D_SIZE %d\nDOMAIN_MIN 0 0 0\nDOMAIN_MAX 1 1 1\n' % N)
    for b in range(N):
        for g in range(N):
            for r in range(N):
                fh.write("%.6f %.6f %.6f\n" % tuple(grade(r / (N - 1), g / (N - 1), b / (N - 1))))
print("LUT written", OUT)
