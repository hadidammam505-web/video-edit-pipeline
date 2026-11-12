# Labelled contact sheets. usage: sheet.py out.jpg height cols step_seconds file[:start[:end]] [...]
# step <= 0 means: |step| evenly spaced samples per file.
import sys
import cv2, numpy as np

out, H, COLS, STEP = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4])
tiles = []
for arg in sys.argv[5:]:
    parts = arg.rsplit("|", 2) if "|" in arg else [arg]
    path = parts[0]
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    dur = cap.get(cv2.CAP_PROP_FRAME_COUNT) / fps
    a = float(parts[1]) if len(parts) > 1 else 0
    b = float(parts[2]) if len(parts) > 2 else dur
    step = STEP if STEP > 0 else (b - a) / -STEP
    name = path.replace("\\", "/").split("/")[-1].split("_")[-1].split(".")[0]
    t = a
    while t < b - 1e-3:
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ok, f = cap.read()
        if not ok:
            break
        f = cv2.resize(f, (int(f.shape[1] * H / f.shape[0]), H), interpolation=cv2.INTER_AREA)
        cv2.rectangle(f, (0, 0), (f.shape[1], 17), (0, 0, 0), -1)
        cv2.putText(f, "%s %.2f" % (name, t), (2, 13), cv2.FONT_HERSHEY_SIMPLEX, .42, (0, 255, 255), 1, cv2.LINE_AA)
        tiles.append(f)
        t += step
w = max(x.shape[1] for x in tiles)
tiles = [cv2.copyMakeBorder(x, 1, 1, 1, w - x.shape[1] + 1, cv2.BORDER_CONSTANT, value=(40, 40, 40)) for x in tiles]
blank = np.zeros_like(tiles[0])
rows = [np.hstack(tiles[i:i + COLS] + [blank] * (COLS - len(tiles[i:i + COLS]))) for i in range(0, len(tiles), COLS)]
cv2.imencode(".jpg", np.vstack(rows), [1, 82])[1].tofile(out)
print(out, len(tiles), "tiles")
