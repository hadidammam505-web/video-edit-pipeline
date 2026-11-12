# Balanced version: about 40% heavy squats, 60% other lifts. Idea 4 stays as it is in specs3.
from specs3 import *
from specs3 import up, Q73, Q75, Q77


def O(c, ss, s, x, y, w, **k):
    return dict(c=c, ss=ss, s=s, x=x, y=y, w=w, floor=.32, **k)


# idea 1: squats at 4.13 and the long final grind
up("r1", .792, **O("C078", 59.0, .75, .55, .4, (.5, .45, .5, .8)))
up("r1", 2.336, **O("C080", 64.4, .7, .43, .4, (.5, .45, .5, .85)))
up("r1", 6.131, **O("C084", 24.3, .62, .52, .47, (.5, .5, .55, .8)), fx=[dict(a=6, b=10, k="blur", r=.004)], z=(1, 1.05))

# idea 3
up("r3", 3.467, **O("C081", 50.3, .8, .42, .5, (.4, .5, .55, .9)))
up("r3", 5.233, **O("C080", 64.6, .7, .43, .42, (.5, .45, .45, .8)))
up("r3", 6.233, **O("C078", 59.0, .8, .55, .45, (.5, .45, .5, .8)))
up("r3", 8.1, **Q73(104.1, .733))
up("r3", 8.833, **O("C082", 32.5, .9, .56, .5, (.55, .5, .55, .9)))

# idea 2
up("r2", 5.467, **O("C081", 51.0, .85, .45, .5, (.35, .5, .5, .9)))
up("r2", 7.433, **O("C080", 64.4, .72, .42, .34, (.5, .5, .5, .9)))
up("r2", 8.333, **O("C080", 65.3, .72, .42, .34, (.5, .5, .5, .9)))
up("r2", 13.4, **O("C078", 59.6, .72, .66, .45, (.45, .5, .5, .9)))
up("r2", 24.85, **O("C079", 41.0, .9, .52, .5, (.55, .5, .55, .9)))

# idea 5
up("r5", 2.667, **O("C084", 25.4, .56, .52, .5, (.5, .5, .55, .8)))
up("r5", 3.133, **O("C079", 43.0, .56, .55, .5, (.5, .5, .55, .8)))
up("r5", 7.1, **O("C080", 66.0, .55, .41, .4, (.5, .5, .6, .95)), floor2=None)
for s in JOBS["r5"]["shots"]:
    if abs(s["a"] - 7.1) < 1e-3:
        s["floor"] = .42
        s.pop("floor2")

up("r2", 7.433, mask=True)
up("r2", 8.333, mask=True)

if __name__ == "__main__":
    SQ = ("C073", "C075", "C077")
    for k, J in JOBS.items():
        total = sum(s["b"] - s["a"] for s in J["shots"] if not s.get("black"))
        sq = sum(s["b"] - s["a"] for s in J["shots"] if s.get("c") in SQ and not s.get("bgs"))
        print(k, "squat %.1fs of %.1fs = %.0f%%" % (sq, total, sq / total * 100))
