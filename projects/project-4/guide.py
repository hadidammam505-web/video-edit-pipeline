# Timing tables for adding text by hand. The word column is left empty for the user.
import csv, os
import specs2 as specs

OUT = os.path.expanduser("~").replace("\\", "/") + "/Desktop/edting/results/project 4"
NAMES = {"impact.ttf": "Impact", "BOD_R.TTF": "Bodoni MT", "BOD_B.TTF": "Bodoni MT Bold", "BOD_CB.TTF": "Bodoni MT Condensed Bold",
         "MISTRAL.TTF": "Mistral", "arialbd.ttf": "Arial Bold"}
HEAD = ["رقم", "من ثانية", "إلى ثانية", "الكلمة (اكتبها أنت)", "الخط", "اللون", "المكان أفقي %", "المكان عمودي %", "المحاذاة", "ارتفاع الحروف % من الشاشة", "ملاحظة"]
for name in ("r1", "r2"):
    J = specs.JOBS[name]
    CW, CH = J["canvas"]
    PX, PY, PW, PH = J["pic"]
    rows = []
    for i, T in enumerate(sorted(J["texts"], key=lambda t: (t["a"], t["y"])), 1):
        notes = []
        if T.get("behind"):
            notes.append("خلف الجسم: حط طبقة الجسم فوق الكتابة")
        font = NAMES[T["font"]]
        if "cycle" in T:
            font = " / ".join(dict.fromkeys(NAMES[c[0]] for c in T["cycle"]))
            notes.append("الخط يتبدل كل %d فريم" % T.get("every", 3))
        col = "أحمر #BE1422" if T["color"] == specs.RED else "أبيض #F0F0F0"
        anc = {"l": "يسار", "r": "يمين"}.get(T.get("anchor", "m"), "وسط")
        rows.append([i, round(T["a"], 2), round(T["b"], 2), "", font, col, round((PX + T["x"] * PW) / CW * 100, 1), round((PY + T["y"] * PH) / CH * 100, 1),
                     anc, round(T["size"] * PH * .72 / CH * 100, 1), "، ".join(notes)])
    path = f"{OUT}/idea-{name[1:]}-text-timing.csv"
    with open(path, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(HEAD)
        w.writerows(rows)
    print(path, len(rows), "rows")
