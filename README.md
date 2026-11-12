# Video Edit Pipeline 🎞️

> The real build scripts behind six gym / lifestyle video edits — a code-first editing pipeline using **Python, ffmpeg, OpenCV, SAM 2, BiRefNet, Real-ESRGAN** and **DaVinci Resolve (FCPXML)**.

**[العربية](#بالعربي)** · **English below**

Instead of dragging clips on a timeline, every edit here is a script: the timeline is a Python list, transitions are functions, and one command renders the whole 4K video. Each project folder is one finished (or in-progress) edit.

## Projects

| Folder | Highlights |
|---|---|
| `projects/project-1` | First edit, pure bash + ffmpeg: shots as a list of crop/zoom specs, slow push-ins, an eased zoom-out that reveals the full rep, dark cinematic grade, cuts on the words of the song. |
| `projects/project-2` | Landscape 4K edit: ISNet silhouette **body flash**, **glitch**, fast zoom, red word behind the athlete, two-stage dark grade. |
| `projects/project-3` | Vertical letterboxed edit: "stack" opening (person stays, gym flickers behind), **plates appear on the beat**. |
| `projects/project-4` | One renderer (`engine.py`) driving five edits from timeline specs (`specs*.py`); plate tracking to find heavy reps (`squats.py`); **FCPXML export to DaVinci Resolve** (`make_fcpxml2.py`); LUT generation; "word fills the body → flash → person vanishes" ending (`ending2.py`). |
| `projects/project-5` | Text-card edit, bilingual English/Arabic words (Arabic rendered through headless Edge), **words tracked to the moving weight** with SAM 2 centroids. |
| `projects/project-6` | Landscape-to-vertical morning routine with sliding bars, Real-ESRGAN upscaling of old clips, beat-locked gym cuts, and a GPU transitions module (`trans6.py`: body flash, whip slide, glitch). |

## Tools

| File | What it does |
|---|---|
| `tools/sam2track.py` | Track a person/object through a shot with **SAM 2.1** from a few clicks; writes one PNG mask per frame. |
| `tools/birefnet_mask.py` | High-detail person cutout with **BiRefNet** on the GPU, with a magenta `--check` preview. |
| `tools/esrgan.py` | **Real-ESRGAN** upscale/denoise for soft, dark, old clips (supports region crops). |
| `tools/boxmask.py` | Restrict a mask to a box around the subject. |
| `tools/clipsheet.py` | Contact sheet of a clip for checking by eye. |
| `fonts/specimen.py` | Renders a font specimen sheet. |
| `refs/project-3/*.py` | Small helpers for measuring a reference edit. |

## Stack

`Python` · `ffmpeg` · `OpenCV` · `NumPy` · `Pillow` · `onnxruntime` · `PyTorch` · `SAM 2` · `BiRefNet` · `Real-ESRGAN` · `librosa` · `DaVinci Resolve`

## Notes

- Footage, songs, models and renders are **not** included (several GB, and personal).
- Paths at the top of each script point to the author's Windows folders; change `SRC`, `OUT`, `DATA` and `BIN` to run them yourself.
- Companion Claude Code skill: [gym-luxury-edit](https://github.com/hadidammam505-web/gym-luxury-edit).

---

## بالعربي

هذي السكربتات الحقيقية اللي انبنت فيها ست مقاطع مونتاج للجيم والروتين اليومي. بدل ما تسحب المقاطع على تايملاين، كل مونتاج عبارة عن سكربت بايثون: التايملاين قائمة، والانتقالات دوال، وأمر واحد يطلّع الفيديو بدقة 4K.

فيها: تتبع الشخص بـ SAM 2، قص الشخص بـ BiRefNet، تحسين المقاطع القديمة بـ Real-ESRGAN، انتقالات فلاش وقلتش وسلايد، كلمات عربية وإنجليزية تتحرك مع الوزن، وتصدير إلى دافنشي ريزولف.

## License

MIT — see [LICENSE](LICENSE).
