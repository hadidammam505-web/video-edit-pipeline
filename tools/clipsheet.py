"""Timed contact sheet of one clip: clipsheet.py <clip> <out.jpg> <start> <end> <fps> [height]. Run with the vision venv."""
import sys, subprocess, os, tempfile, glob
from PIL import Image, ImageDraw
clip, out, a, b, fps = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])
h = int(sys.argv[6]) if len(sys.argv) > 6 else 220
d = tempfile.mkdtemp()
subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", str(a), "-t", str(b - a), "-i", clip,
                "-vf", f"fps={fps},scale=-2:{h}", os.path.join(d, "%04d.jpg")], check=True)
fs = sorted(glob.glob(os.path.join(d, "*.jpg"))); w = Image.open(fs[0]).width
cols = max(1, min(len(fs), 2000 // w)); rows = (len(fs) + cols - 1) // cols
s = Image.new("RGB", (cols * w, rows * h), "black")
for i, f in enumerate(fs):
    im = Image.open(f); x, y = (i % cols) * w, (i // cols) * h; s.paste(im, (x, y))
    ImageDraw.Draw(s).text((x + 3, y + 3), "%.2f" % (a + i / fps), fill="yellow")
s.save(out, quality=82); print(out, len(fs))
