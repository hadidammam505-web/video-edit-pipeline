"""BiRefNet person mask on the GPU (DirectML), with CPU fallback.

Usage (cutout venv, it has onnxruntime-directml):
  tools\\cutout\\Scripts\\python.exe birefnet_mask.py <in.jpg|folder> <out_dir> [--check]

Writes <name>.png masks (white = person) at the input's size.
--check also writes <name>_check.jpg: the person on magenta, to inspect edges.
"""
import sys, os, glob, time
import numpy as np, cv2, onnxruntime as ort

MODEL = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "models", "BiRefNet-general-epoch_244.onnx")
SIZE = 1024
MEAN = np.array([0.485, 0.456, 0.406], np.float32)
STD = np.array([0.229, 0.224, 0.225], np.float32)


def session(gpu=True):
    if not gpu:
        return ort.InferenceSession(MODEL, providers=["CPUExecutionProvider"])
    # DirectML's graph fusion breaks one of BiRefNet's nodes, so turn fusion off.
    so = ort.SessionOptions()
    so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_DISABLE_ALL
    so.enable_mem_pattern = False
    return ort.InferenceSession(MODEL, so, providers=["DmlExecutionProvider", "CPUExecutionProvider"])


def mask(sess, bgr):
    h, w = bgr.shape[:2]
    x = cv2.resize(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB), (SIZE, SIZE), interpolation=cv2.INTER_AREA)
    x = ((x.astype(np.float32) / 255 - MEAN) / STD).transpose(2, 0, 1)[None]
    out = sess.run(None, {sess.get_inputs()[0].name: x})[-1][0, 0]
    out = 1 / (1 + np.exp(-out))  # logits -> 0..1
    return cv2.resize(out, (w, h), interpolation=cv2.INTER_LINEAR)


def main():
    src, dst = sys.argv[1], sys.argv[2]
    check = "--check" in sys.argv
    os.makedirs(dst, exist_ok=True)
    files = sorted(glob.glob(os.path.join(src, "*.jpg"))) if os.path.isdir(src) else [src]
    sess = session()
    try:
        mask(sess, cv2.imread(files[0]))
    except Exception as e:
        print("GPU failed, using CPU:", str(e)[:120])
        sess = session(gpu=False)
    print("provider:", sess.get_providers()[0])
    t0 = time.time()
    for f in files:
        img = cv2.imread(f)
        m = mask(sess, img)
        name = os.path.splitext(os.path.basename(f))[0]
        cv2.imwrite(os.path.join(dst, name + ".png"), (m * 255).astype(np.uint8))
        if check:
            mag = np.zeros_like(img); mag[:] = (255, 0, 255)
            comp = (img * m[..., None] + mag * (1 - m[..., None])).astype(np.uint8)
            cv2.imwrite(os.path.join(dst, name + "_check.jpg"), comp)
    print("%d frames, %.2fs per frame" % (len(files), (time.time() - t0) / max(1, len(files))))


if __name__ == "__main__":
    main()
