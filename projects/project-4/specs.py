# Timelines for the five project-4 edits. Times are seconds measured from each reference.
WHITE, RED = (240, 240, 240), (34, 20, 190)   # BGR
IMPACT, BOD, BODB, BODC = "impact.ttf", "BOD_R.TTF", "BOD_B.TTF", "BOD_CB.TTF"
SCRIPT = "MISTRAL.TTF"
SANS = "arialbd.ttf"


def T(a, b, text, font=IMPACT, size=.1, color=WHITE, x=.5, y=.5, **kw):
    return dict(a=a, b=b, text=text, font=font, size=size, color=color, x=x, y=y, **kw)


# dark look with green-cream highlights, for a bright red gym
DARK = ("eq=contrast=1.28:gamma=0.72:saturation=0.9,"
        "curves=r='0/0 0.25/0.06 0.6/0.32 1/0.86':g='0/0 0.25/0.08 0.6/0.37 1/0.92':b='0/0 0.25/0.08 0.6/0.32 1/0.76',"
        "noise=alls=3:allf=t")
JOBS = {}

# ---- idea 3: quote on black gaps ---------------------------------------------
Q = "Nothing is more peaceful than destroying your body"
Q2 = "and getting the best version of yourself."
JOBS["r3"] = dict(
    canvas=(2160, 3840), pic=(0, 1128, 2160, 1584), dur=10.52, grade=DARK,
    shots=[
        dict(a=0, b=.9, c="C073", ss=33.0, s=.8, x=.55, y=.45, w=(.5, .5, .55, .7)),
        dict(a=.9, b=1.767, black=True),
        dict(a=1.767, b=2.633, c="C071", ss=25.3, s=1, x=.5, y=.3, w=(.5, .5, .7, .8)),
        dict(a=2.633, b=3.467, black=True),
        dict(a=3.467, b=4.4, c="C072", ss=12.4, s=1, x=.5, y=.62, w=(.5, .5, .6, .8)),
        dict(a=4.4, b=5.233, black=True),
        dict(a=5.233, b=6.233, c="C080", ss=62.0, s=.75, x=.68, y=.5, w=(.5, .5, .55, .8)),
        dict(a=6.233, b=7.167, c="C078", ss=56.0, s=.85, x=.5, y=.55, w=(.5, .5, .55, .8)),
        dict(a=7.167, b=8.1, c="C079", ss=40.0, s=.85, x=.5, y=.55, w=(.5, .5, .55, .8)),
        dict(a=8.1, b=8.833, c="C083", ss=20.0, s=.8, x=.45, y=.5, ph=1224, w=(.5, .5, .55, .8)),
        dict(a=8.833, b=9.7, c="C075", ss=14.0, s=.9, x=.5, y=.6, w=(.5, .5, .6, .8)),
        dict(a=9.7, b=9.833, c="C084", ss=24.0, s=.9, x=.5, y=.5, w=(.5, .5, .6, .8)),
        dict(a=9.833, b=10.0, c="C084", ss=24.13, s=.7, x=.5, y=.5, w=(.5, .5, .6, .8)),
        dict(a=10.0, b=10.52, c="C084", ss=24.3, s=.55, x=.5, y=.48, w=(.5, .5, .6, .8)),
    ],
    texts=[T(0, 10.52, Q, SANS, .0235, y=.48), T(0, 10.52, Q2, SANS, .0235, y=.525)],
)
