"""Track one person (or object) through a shot with SAM 2.1 and write one PNG mask per frame. Run with the vision venv.

usage: sam2track.py <frames_dir> <out_dir> <points> [--neg <points>] [--frame N] [--model small|base_plus]
  frames_dir  JPEGs named 00000.jpg, 00001.jpg ... (ffmpeg -start_number 0 ... %05d.jpg)
  points      clicks on the subject in frame N, in pixels: "x,y;x,y;x,y" (torso, head, legs works well)
  --neg       clicks on things to leave out, such as a machine handle

Measured 2026-11-11 on a 39-frame 1600x900 shot (RTX 5060): 6 s, 1.1 GB GPU. It keeps the person
and leaves the machine out, where BiRefNet kept the lever arms, and it flickers about a third less.
Click on headphones or held objects too, or SAM leaves them out.
"""
import argparse, os, numpy as np, cv2, torch
from sam2.build_sam import build_sam2_video_predictor

MODELS = "C:/Users/ZGAMES/Documents/video-edit/tools/models"
CFG = {"small": ("configs/sam2.1/sam2.1_hiera_s.yaml", "sam2.1_hiera_small.pt"),
       "base_plus": ("configs/sam2.1/sam2.1_hiera_b+.yaml", "sam2.1_hiera_base_plus.pt")}

ap = argparse.ArgumentParser()
ap.add_argument("frames"); ap.add_argument("out"); ap.add_argument("points")
ap.add_argument("--neg", default=""); ap.add_argument("--frame", type=int, default=0); ap.add_argument("--model", default="small")
A = ap.parse_args()
parse = lambda s: [[float(v) for v in p.split(",")] for p in s.split(";") if p.strip()]
pos, neg = parse(A.points), parse(A.neg)
cfg, ck = CFG[A.model]
pred = build_sam2_video_predictor(cfg, os.path.join(MODELS, ck), device="cuda")
os.makedirs(A.out, exist_ok=True)
with torch.inference_mode(), torch.autocast("cuda", dtype=torch.bfloat16):
    st = pred.init_state(video_path=A.frames)
    pts = np.array(pos + neg, np.float32); lab = np.array([1] * len(pos) + [0] * len(neg), np.int32)
    pred.add_new_points_or_box(st, frame_idx=A.frame, obj_id=1, points=pts, labels=lab)
    n = 0
    for reverse in (False, True):          # forward from the clicked frame, then backward to the start
        for fi, _, logits in pred.propagate_in_video(st, start_frame_idx=A.frame, reverse=reverse):
            cv2.imwrite(os.path.join(A.out, "%05d.png" % fi), ((logits[0, 0] > 0).cpu().numpy() * 255).astype(np.uint8)); n += 1
print("masks written", A.out, n)
