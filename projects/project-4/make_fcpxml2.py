# Idea 2 for grading in Resolve: one ungraded clip per shot, editable titles (my own words) with positions, ungraded body layers on top.
import os
from urllib.parse import quote
from xml.sax.saxutils import escape
from PIL import ImageFont
import specs4

HOME = os.path.expanduser("~").replace("\\", "/")
W = HOME + "/Documents/video-edit/projects/project-4"
VIDEO = W + "/extras/idea-2-neutral.mp4"
LDIR = W + "/extras/idea-2-body-layers-neutral"
LAYERS = [("body-from-07.43s.mov", 223, 27), ("body-from-08.33s.mov", 250, 58), ("body-from-22.30s.mov", 669, 28)]
NAMES = {"impact.ttf": "Impact", "MISTRAL.TTF": "Mistral"}
J = specs4.JOBS["r2"]
CW, CH = J["canvas"]
TOTAL = 818
f = lambda t: int(round(t * 30))
t_ = lambda n: f"{n}/30s"
url = lambda p: "file:///" + quote(p)

texts = sorted(J["texts"], key=lambda t: (t["a"], t["y"]))
lanes, rows = [], []
for T in texts:
    a, b = f(T["a"]), f(T["b"])
    lane = next((i for i, end in enumerate(lanes) if end <= a), None)
    if lane is None:
        lanes.append(b)
        lane = len(lanes) - 1
    else:
        lanes[lane] = b
    px = int(T["size"] * CH)
    width = ImageFont.truetype("C:/Windows/Fonts/" + T["font"], px).getlength(T["text"])
    x = T["x"] * CW
    cx = x + width / 2 if T.get("anchor") == "l" else x - width / 2 if T.get("anchor") == "r" else x
    rows.append((T, a, b, lane + 1, px, cx - CW / 2, CH / 2 - T["y"] * CH))
top = len(lanes) + 1
shots = [(f(s["a"]), f(s["b"])) for s in J["shots"]]

children = {i: [] for i in range(len(shots))}
owner = lambda a: next(i for i, (x, y) in enumerate(shots) if x <= a < y)
for k, (T, a, b, lane, px, tx, ty) in enumerate(rows):
    r, g, bl = (c / 255 for c in T["color"][::-1])
    children[owner(a)] += [
        f'<title name="{escape(T["text"])}" lane="{lane}" ref="r9" offset="{t_(a)}" start="0s" duration="{t_(b - a)}">',
        f'<text><text-style ref="ts{k}">{escape(T["text"])}</text-style></text>',
        f'<text-style-def id="ts{k}"><text-style font="{NAMES[T["font"]]}" fontSize="{px / 2:.0f}" fontColor="{r:.3f} {g:.3f} {bl:.3f} 1" alignment="center"/></text-style-def>',
        f'<adjust-transform position="{tx / CH * 100:.3f} {ty / CH * 100:.3f}"/>', "</title>"]
for i, (n, a, d) in enumerate(LAYERS):
    children[owner(a)].append(f'<asset-clip name="{n}" ref="r{3 + i}" lane="{top}" offset="{t_(a)}" start="0s" duration="{t_(d)}" format="r1"/>')

out = ['<?xml version="1.0" encoding="UTF-8"?>', "<!DOCTYPE fcpxml>", '<fcpxml version="1.9">', "<resources>",
       f'<format id="r1" name="FFVideoFormat3840x2160p30" frameDuration="1/30s" width="{CW}" height="{CH}"/>',
       f'<asset id="r2" name="idea-2-neutral" src="{url(VIDEO)}" start="0s" duration="{t_(TOTAL)}" hasVideo="1" hasAudio="1" format="r1" audioSources="1" audioChannels="2"/>']
for i, (n, _, d) in enumerate(LAYERS):
    out.append(f'<asset id="r{3 + i}" name="{n}" src="{url(LDIR + "/" + n)}" start="0s" duration="{t_(d)}" hasVideo="1" format="r1"/>')
out.append('<effect id="r9" name="Basic Title" uid=".../Titles.localized/Bumper:Opener.localized/Basic Title.localized/Basic Title.moti"/>')
out += ["</resources>", "<library>", '<event name="Idea 2">', '<project name="Idea 2 Graded">',
        f'<sequence format="r1" duration="{t_(TOTAL)}" tcStart="0s" tcFormat="NDF" audioLayout="stereo" audioRate="48k">', "<spine>"]
for i, (a, b) in enumerate(shots):
    out.append(f'<asset-clip name="idea-2-neutral" ref="r2" offset="{t_(a)}" start="{t_(a)}" duration="{t_(b - a)}" format="r1" audioRole="dialogue">')
    out += children[i]
    out.append("</asset-clip>")
out += ["</spine>", "</sequence>", "</project>", "</event>", "</library>", "</fcpxml>"]
with open(f"{W}/extras/idea-2-graded.fcpxml", "w", encoding="utf-8") as fh:
    fh.write("\n".join(out))
print("shots", len(shots), "titles", len(rows), "layer lane", top)
