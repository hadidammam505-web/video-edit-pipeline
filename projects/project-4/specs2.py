# All five timelines, framed for the real 2160x1214 landscape footage.
from specs import *

JOBS["r3"]["shots"] = [
    dict(a=0, b=.9, c="C073", ss=73.4, s=.85, x=.42, y=.5, w=(.45, .5, .6, .9)),
    dict(a=.9, b=1.767, black=True),
    dict(a=1.767, b=2.633, c="C080", ss=64.6, s=.7, x=.43, y=.42, w=(.5, .45, .45, .8)),
    dict(a=2.633, b=3.467, black=True),
    dict(a=3.467, b=4.4, c="C075", ss=10.5, s=1, x=.42, y=.5, floor=.5, w=(.35, .45, .7, .9)),
    dict(a=4.4, b=5.233, black=True),
    dict(a=5.233, b=6.233, c="C081", ss=50.3, s=.8, x=.42, y=.5, w=(.4, .5, .55, .9)),
    dict(a=6.233, b=7.167, c="C078", ss=59.0, s=.8, x=.55, y=.45, w=(.5, .45, .5, .8)),
    dict(a=7.167, b=8.1, c="C079", ss=40.4, s=.9, x=.52, y=.5, w=(.55, .5, .55, .8)),
    dict(a=8.1, b=8.833, c="C083", ss=19.2, s=.8, x=.46, y=.55, ph=1224, w=(.5, .5, .5, .8)),
    dict(a=8.833, b=9.7, c="C082", ss=32.5, s=.9, x=.56, y=.5, w=(.55, .5, .55, .9)),
    dict(a=9.7, b=9.833, c="C084", ss=24.5, s=.9, x=.53, y=.5, w=(.55, .5, .55, .8)),
    dict(a=9.833, b=10.0, c="C084", ss=24.63, s=.7, x=.53, y=.48, w=(.55, .5, .55, .8)),
    dict(a=10.0, b=10.52, c="C084", ss=24.8, s=.55, x=.53, y=.46, w=(.5, .5, .55, .8)),
]

# ---- idea 1: word-by-word type, stack opening, glitch ----
W1 = [(BOD, 1.0), (IMPACT, .95), (BODB, 1.15), (IMPACT, 1.5), (BOD, 1.0), (BODC, 1.3)]
BG1 = [("C079", 50, .9, .6, .5), ("C075", 14, 1, .5, .5), ("C083", 20, .9, .4, .5), ("C081", 52, .9, .4, .5), ("C082", 33, .9, .56, .5),
       ("C084", 26, 1, .5, .5), ("C078", 56, .9, .6, .5), ("C084", 31, 1, .5, .5), ("C073", 70, 1, .5, .5), ("C079", 43, 1, .55, .5),
       ("C078", 63, 1, .55, .5), ("C080", 71.5, .8, .42, .5)]


def WD(a, b, t, red=False, **k):
    k.setdefault("size", .115)
    return T(a, b, t, k.pop("font", IMPACT), color=RED if red else WHITE, **k)


JOBS["r1"] = dict(
    canvas=(2160, 3840), pic=(0, 1284, 2160, 1272), dur=12.03, grade=DARK,
    shots=[
        dict(a=0, b=.751, c="C080", ss=64.2, s=.7, x=.42, y=.4, mask=True, box=(.25, .75, 0, 1), every=2, bgs=BG1),
        dict(a=.751, b=.792, c="C078", ss=55.6, s=.75, x=.55, y=.4, fx=[dict(a=.7, b=.8, k="white")]),
        dict(a=.792, b=2.336, c="C078", ss=55.6, s=.75, x=.55, y=.4, w=(.5, .45, .5, .8), z=(1, 1.03)),
        dict(a=2.336, b=4.129, c="C079", ss=38.3, s=.8, x=.5, y=.5, w=(.55, .5, .55, .85),
             fx=[dict(a=3.87, b=4.13, k="pixel", block=14, tints=[(1.3, .7, 1.4), (1, 1, 1), (1.4, .6, 1.3)])]),
        dict(a=4.129, b=6.131, c="C075", ss=13.8, s=.95, x=.47, y=.5, w=(.45, .5, .6, .9),
             fx=[dict(a=4.12, b=4.45, k="pixel", block=20, tints=[(.8, 1.35, .8), (1, 1, 1), (1.3, .7, 1.3)])]),
        dict(a=6.131, b=9.176, c="C084", ss=24.3, s=.62, x=.52, y=.47, w=(.5, .5, .55, .8), z=(1, 1.05), fx=[dict(a=6, b=10, k="blur", r=.004)]),
        dict(a=9.176, b=12.03, c="C082", ss=26.4, s=.72, x=.56, y=.48, w=(.55, .5, .5, .85)),
    ],
    texts=[
        WD(0, .2, "WHEN", cycle=W1, every=3), WD(.2, .5, "THEY", cycle=W1, every=3), WD(.5, .751, "REST", cycle=W1, every=3),
        WD(.792, 1.4, "I'M", font=BOD), WD(1.4, 1.6, "STILL", True, font=BOD), WD(1.6, 1.9, "LIFT", font=BOD), WD(1.9, 2.336, "LIFTING", font=BOD),
        WD(2.336, 3.4, "HEAVY", True, font=BOD), WD(3.4, 3.7, "EACH", font=BOD), WD(3.7, 3.9, "SINGLE", font=BOD), WD(3.9, 4.4, "DAY", True, font=BOD),
        WD(4.4, 4.9, "SO", font=BOD), WD(4.9, 5.2, "TELL", font=BOD), WD(5.2, 5.4, "ME", font=BOD), WD(5.4, 6.131, "NOW", True, font=BOD),
        WD(6.131, 6.4, "WHO", font=BOD), WD(6.4, 6.9, "BEATS", font=BOD), WD(6.9, 9.176, "ME", cycle=W1, every=7, size=.14),
        WD(9.176, 9.5, "WHO", True, font=BOD), WD(9.5, 10.4, "BEATS", font=BOD), WD(10.4, 12.03, "ME", font=BOD),
    ],
    sfx=[(.751, "hit"), (3.9, "glitch"), (4.13, "glitch")],
)

# ---- idea 4: same reference as project 3 ----
BG4 = [("C079", 50, 1, .6, .5), ("C075", 14, 1, .5, .5), ("C083", 20, 1, .4, .5), ("C081", 52, 1, .4, .5), ("C082", 33, 1, .56, .5), ("C084", 26, 1, .5, .5),
       ("C078", 56, 1, .6, .5), ("C073", 70, 1, .5, .5), ("C080", 71.5, 1, .45, .5), ("C078", 63, 1, .55, .5), ("C079", 33, .7, .6, .5), ("C083", 27.5, .7, .46, .55),
       ("C082", 45, .7, .6, .5), ("C075", 22, .7, .4, .55), ("C081", 40, .7, .4, .5), ("C078", 62, .7, .6, .4), ("C084", 31, .7, .55, .5)]
CREAM = (200, 240, 230)
JOBS["r4"] = dict(
    canvas=(2160, 3840), pic=(0, 1152, 2160, 1536), dur=9.94, grade=DARK,
    shots=[
        dict(a=0, b=1.376, c="C085", ss=33.6, s=.62, x=.56, y=.42, mask=True, box=(.2, .85, 0, 1), every=2, bgs=BG4),
        dict(a=1.376, b=1.501, c="C073", ss=74.9, s=.85, x=.45, y=.5, w=(.5, .5, .6, .9)),
        dict(a=1.501, b=1.668, c="C079", ss=40.5, s=.9, x=.52, y=.5, w=(.55, .5, .55, .9)),
        dict(a=1.668, b=2.294, c="C078", ss=59.0, s=.8, x=.55, y=.45, w=(.5, .45, .5, .85)),
        dict(a=2.294, b=2.794, c="C078", ss=59.6, s=.6, x=.55, y=.4, w=(.5, .5, .6, .9)),
        dict(a=2.794, b=3.295, c="C075", ss=14.2, s=.95, x=.45, y=.5, w=(.45, .5, .6, .9), fx=[dict(a=3.21, b=3.3, k="sil", color=CREAM)]),
        dict(a=3.295, b=3.67, c="C080", ss=64.6, s=.7, x=.42, y=.38, mask="first", box=(.25, .75, 0, 1), w=(.5, .45, .45, .85)),
        dict(a=3.67, b=4.129, c="C081", ss=41.8, s=.9, x=.45, y=.5, w=(.4, .5, .55, .9)),
        dict(a=4.129, b=5.047, c="C082", ss=32.4, s=.9, x=.56, y=.5, w=(.6, .5, .5, .9)),
        dict(a=5.047, b=5.505, c="C083", ss=19.5, s=.6, x=.46, y=.55, w=(.5, .5, .55, .9)),
        dict(a=5.505, b=5.756, c="C084", ss=25.0, s=1, x=.5, y=.5, w=(.6, .5, .5, .9)),
        dict(a=5.756, b=6.381, c="C084", ss=25.25, s=.62, x=.54, y=.48, w=(.5, .5, .55, .9)),
        dict(a=6.381, b=7.132, c="C073", ss=75.9, s=.75, x=.4, y=.55, w=(.45, .5, .6, .9), fx=[dict(a=7.05, b=7.14, k="sil", color=CREAM)]),
        dict(a=7.132, b=8.717, c="C081", ss=50.8, s=.85, x=.42, y=.5, mask="first", box=(0, .85, 0, 1), w=(.42, .5, .55, .9),
             fx=[dict(a=7.96, b=8.06, k="dim", v=1.6)], z=(1, 1.04)),
        dict(a=8.717, b=9.94, c="C085", ss=39.0, s=.62, x=.56, y=.42, z=(1, 1.07), w=(.5, .45, .5, .85)),
    ],
    texts=[],
    sfx=[(3.295, "hit"), (7.132, "hit")],
)

# ---- idea 2: landscape, big type behind the lifter ----
L, R = "l", "r"
WH = (255, 255, 255)
JOBS["r2"] = dict(
    canvas=(3840, 2160), pic=(0, 0, 3840, 2160), dur=27.28, grade=DARK,
    shots=[
        dict(a=0, b=.17, black=True),
        dict(a=.17, b=5.467, c="C078", ss=58.6, s=.72, x=.66, y=.45, w=(.45, .5, .5, .9)),
        dict(a=5.467, b=6.9, c="C081", ss=51.0, s=.85, x=.45, y=.5, w=(.35, .5, .5, .9)),
        dict(a=6.9, b=7.433, c="C082", ss=28.4, s=.85, x=.56, y=.5, w=(.55, .5, .55, .9)),
        dict(a=7.433, b=8.333, c="C080", ss=64.4, s=.72, x=.42, y=.34, mask=True, box=(.25, .75, 0, 1), w=(.5, .5, .5, .9)),
        dict(a=8.333, b=10.267, c="C080", ss=65.3, s=.72, x=.42, y=.34, mask=True, box=(.25, .75, 0, 1), w=(.5, .5, .5, .9)),
        dict(a=10.267, b=12.5, c="C075", ss=15.2, s=.9, x=.5, y=.5, w=(.55, .5, .6, .9)),
        dict(a=12.5, b=13.4, c="C084", ss=31.0, s=.75, x=.52, y=.5, w=(.52, .5, .55, .9)),
        dict(a=13.4, b=15.867, c="C075", ss=17.9, s=.9, x=.55, y=.5, w=(.55, .5, .6, .9)),
        dict(a=15.867, b=18.933, c="C073", ss=75.0, s=1, x=.5, y=.5, w=(.45, .55, .6, .9)),
        dict(a=18.933, b=22.3, c="C083", ss=26.2, s=.9, x=.568, y=.55, w=(.38, .55, .5, .9)),
        dict(a=22.3, b=23.3, c="C085", ss=39.0, s=.9, x=.56, y=.42, mask=True, box=(.25, .8, 0, 1), w=(.5, .5, .55, .95),
             fx=[dict(a=23.22, b=23.31, k="sil", color=WH)]),
        dict(a=23.3, b=24.85, c="C082", ss=38.0, s=.62, x=.653, y=.48, mask="first", box=(0, .75, 0, 1), w=(.35, .5, .5, .9)),
        dict(a=24.85, b=26.0, c="C079", ss=41.0, s=.9, x=.52, y=.5, w=(.55, .5, .55, .9), fx=[dict(a=25.89, b=26.01, k="sil", color=WH)]),
        dict(a=26.0, b=26.47, c="C081", ss=53.4, s=.85, x=.45, y=.5, mask="first", box=(0, .85, 0, 1), w=(.4, .5, .55, .9), fx=[dict(a=26.15, b=26.47, k="fadeout")]),
        dict(a=26.47, b=27.28, black=True),
    ],
    texts=[
        T(2.5, 5.467, "I", size=.2, x=.505, y=.32, anchor=L), T(2.75, 5.467, "TOLD", size=.2, color=RED, x=.57, y=.32, anchor=L),
        T(3.0, 5.467, "MY MIND", size=.2, x=.505, y=.55, anchor=L), T(4.0, 5.467, "to", SCRIPT, .14, RED, x=.875, y=.53, anchor=L),
        T(4.75, 5.467, "KEEP ON", size=.1, x=.7, y=.7, anchor=L),
        T(5.467, 6.9, "GOING", size=.43, x=.96, y=.38, anchor=R),
        T(7.433, 8.333, "PUSHING", size=.44, x=.5, y=.3, behind=True),
        T(8.333, 10.267, "FORWARD", size=.42, color=RED, x=.5, y=.38, behind=True),
        T(10.267, 12.5, "I PROMISED", size=.2, x=.08, y=.24, anchor=L), T(11.25, 12.5, "MY SELF", size=.2, color=RED, x=.08, y=.5, anchor=L),
        T(12.0, 12.5, "that", SCRIPT, .15, x=.3, y=.74, anchor=L),
        T(12.5, 13.0, "THE DOUBT", size=.3, color=RED, x=.55, y=.28), T(13.0, 13.4, "doubt", SCRIPT, .32, RED, x=.55, y=.38),
        T(13.4, 15.867, "WOULD NOT", size=.2, x=.08, y=.24, anchor=L), T(14.25, 15.867, "STOP", size=.2, x=.08, y=.5, anchor=L),
        T(15.0, 15.867, "ME", size=.2, color=RED, x=.36, y=.5, anchor=L),
        T(17.0, 17.6, "no", SCRIPT, .55, RED, x=.42, y=.55),
        T(18.25, 22.3, "SO I", size=.2, x=.93, y=.24, anchor=R), T(20.25, 22.3, "STAYED", size=.2, color=RED, x=.93, y=.5, anchor=R),
        T(21.5, 22.3, "TILL THE", size=.15, x=.62, y=.75, anchor=L), T(22.0, 22.3, "end", SCRIPT, .15, RED, x=.875, y=.74, anchor=L),
        T(22.3, 23.3, "PAIN", size=.78, color=RED, x=.46, y=.32, behind=True),
        T(23.45, 24.85, "BUT THIS", size=.21, x=.95, y=.25, anchor=R), T(24.25, 24.85, "IS MINE", size=.21, color=RED, x=.95, y=.5, anchor=R),
    ] + [T(24.85, 26.0, "MINE", size=.075 + .03 * k, color=RED, x=.48, y=.12 + .135 * k) for k in range(5)]
      + [T(24.85, 26.0, "MINE", size=.2, color=RED, x=.48, y=.86)],
    sfx=[(23.3, "hit"), (26.0, "hit")],
)

# ---- idea 5: square, very dark, high-key flickers ----
D5 = DARK + ",eq=gamma=.72:brightness=-.02"


def DIM(v):
    return [dict(a=0, b=99, k="dim", v=v)]


JOBS["r5"] = dict(
    canvas=(2160, 2160), pic=(0, 0, 2160, 2160), dur=9.05, grade=D5, floor=.2,
    shots=[
        dict(a=0, b=1.633, c="C082", ss=26.4, s=.56, x=.56, y=.5, z=(1.32, 1), ease=1, w=(.5, .5, .6, .8)),
        dict(a=1.633, b=1.767, black=True),
        dict(a=1.767, b=2.567, c="C084", ss=25.0, s=.56, x=.52, y=.5, w=(.5, .5, .55, .8), fx=DIM(.65)),
        dict(a=2.567, b=2.667, black=True),
        dict(a=2.667, b=3.033, c="C083", ss=19.6, s=.56, x=.46, y=.5, w=(.5, .5, .55, .8), fx=DIM(.55)),
        dict(a=3.033, b=3.133, black=True),
        dict(a=3.133, b=3.533, c="C079", ss=43.0, s=.56, x=.55, y=.5, w=(.5, .5, .55, .8),
             fx=DIM(.55) + [dict(a=3.26, b=3.3, k="high"), dict(a=3.33, b=3.4, k="high"), dict(a=3.43, b=3.465, k="high"), dict(a=3.5, b=3.54, k="high")]),
        dict(a=3.533, b=4.433, c="C073", ss=75.0, s=.56, x=.38, y=.5, z=(1.15, 1), ease=1, w=(.45, .5, .7, .9),
             fx=[dict(a=3.5, b=3.9, k="blur", r=.03), dict(a=3.5, b=4.1, k="dim", v=.55), dict(a=4.4, b=4.44, k="band", x0=0, x1=.5)]),
        dict(a=4.433, b=5.333, c="C081", ss=50.2, s=.62, x=.38, y=.52, w=(.5, .5, .55, .85),
             fx=[dict(a=4.43, b=4.47, k="band", x0=.5, x1=.8), dict(a=5.27, b=5.34, k="dim", v=2.2)]),
        dict(a=5.333, b=6.2, c="C080", ss=72.0, s=.55, x=.42, y=.5, w=(.5, .5, .6, .8), fx=DIM(.18)),
        dict(a=6.2, b=6.267, c="C080", ss=72.87, s=.55, x=.42, y=.5, w=(.5, .5, .6, .8), fx=[dict(a=6, b=7, k="high", gain=5, floor=170)]),
        dict(a=6.267, b=7.067, c="C085", ss=39.0, s=.45, x=.56, y=.4, grade=DARK, floor=.5, w=(.5, .45, .6, .9),
             fx=[dict(a=6.66, b=6.7, k="dim", v=1.5), dict(a=6.86, b=6.97, k="dim", v=1.55)]),
        dict(a=7.067, b=7.1, c="C085", ss=39.8, s=.45, x=.56, y=.4, grade=DARK, fx=[dict(a=7, b=8, k="hblur", amount=.25)]),
        dict(a=7.1, b=8.867, c="C080", ss=66.0, s=.55, x=.41, y=.4, z=(1, 1.04), grade=DARK, floor=.42, w=(.5, .5, .6, .95), fx=DIM(.9)),
        dict(a=8.867, b=9.05, black=True),
    ],
    texts=[T(0, 3.533, "THE GOAL IS SIMPLE", SANS, .024, track=.14), T(3.533, 8.867, "BE BETTER THAN YESTERDAY", SANS, .024, track=.14)],
    sfx=[(3.26, "glitch"), (4.4, "hit"), (6.2, "hit"), (7.067, "hit")],
)
