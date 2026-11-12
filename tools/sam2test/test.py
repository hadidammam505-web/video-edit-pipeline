import sys, time, os, glob, numpy as np, cv2, torch
from sam2.build_sam import build_sam2_video_predictor
T = sys.argv[1]; E = "C:/Users/ZGAMES/Documents/video-edit/projects/project-4/extras/idea-2-ending"
ck = "C:/Users/ZGAMES/Documents/video-edit/tools/models/sam2.1_hiera_small.pt"
pred = build_sam2_video_predictor("configs/sam2.1/sam2.1_hiera_s.yaml", ck, device="cuda")
# BiRefNet masks for the same frames: out2 (10) then out (29)
bir = [cv2.imread(f, 0) for f in sorted(glob.glob(E + "/out2/*.png")) + sorted(glob.glob(E + "/out/*.png"))]
m0 = bir[0] > 127; ys, xs = np.nonzero(m0)
# three positive clicks inside the body (torso, head, thigh) chosen from the first mask
pts = []
for q in (0.25, 0.5, 0.8):
    y = int(np.quantile(ys, q)); row = xs[ys == y]; pts.append([int(np.median(row)), y])
t = time.time()
with torch.inference_mode(), torch.autocast("cuda", dtype=torch.bfloat16):
    st = pred.init_state(video_path=T + "/frames")
    pred.add_new_points_or_box(st, frame_idx=0, obj_id=1, points=np.array(pts, np.float32), labels=np.ones(len(pts), np.int32))
    out = {}
    for fi, ids, logits in pred.propagate_in_video(st):
        out[fi] = (logits[0, 0] > 0).cpu().numpy()
print("sam2 %d frames in %.1fs, peak GPU %.2f GB" % (len(out), time.time() - t, torch.cuda.max_memory_allocated() / 1e9))
iou = lambda a, b: (a & b).sum() / max((a | b).sum(), 1)
s_j = [1 - iou(out[i], out[i + 1]) for i in range(len(out) - 1)]
b = [x > 127 for x in bir[:len(out)]]
b_j = [1 - iou(b[i], b[i + 1]) for i in range(len(b) - 1)]
print("frame-to-frame change, lower is steadier: SAM2 mean %.4f max %.4f | BiRefNet mean %.4f max %.4f" % (np.mean(s_j), np.max(s_j), np.mean(b_j), np.max(b_j)))
print("SAM2 vs BiRefNet agreement IoU mean %.3f" % np.mean([iou(out[i], b[i]) for i in range(len(b))]))
os.makedirs(T + "/sam", exist_ok=True)
tiles = []
for i in (0, 9, 20, 38):
    im = cv2.imread(T + "/frames/%05d.jpg" % i)
    for m, col in ((out[i], (255, 0, 255)), (b[i], (0, 200, 255))):
        o = im.copy(); o[~m] = (o[~m] * .25 + np.array(col) * .75).astype(np.uint8); tiles.append(cv2.resize(o, (480, 270)))
g = np.vstack([np.hstack(tiles[k:k + 2]) for k in range(0, len(tiles), 2)])
cv2.imwrite(T + "/compare.jpg", g)
for i, m in out.items(): cv2.imwrite(T + "/sam/%05d.png" % i, (m * 255).astype(np.uint8))
