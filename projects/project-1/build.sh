set -e
export PATH="/c/Users/ZGAMES/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0.2-full_build/bin:$PATH"
SCR="$(cd "$(dirname "$0")" && pwd)"
SRC="/c/Users/ZGAMES/Desktop/edting/storage/project 1"
W="$HOME/Documents/video-edit/projects/project-1"; mkdir -p "$W/shots"
OUTDIR="/c/Users/ZGAMES/Desktop/edting/results/project 1"; mkdir -p "$OUTDIR"
V="${1:-1}"

# dark cinematic grade: lower exposure, crush highlights, cool shadows, keep the reds, vignette, light grain
GRADE="eq=brightness=-0.06:contrast=1.25:saturation=0.80:gamma=0.78,curves=all='0/0 0.30/0.13 0.65/0.42 1/0.78',colorbalance=rs=-0.04:bs=0.07:rm=-0.02:bm=0.03,vignette=angle=PI/3.2,noise=alls=7:allf=t"
FIT="scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1,fps=30"

# file | start | duration | crop size | crop x | crop y   (fractions of the frame; cuts land on the words of the song)
# last field: 1 = slow push-in during the shot
# TRY x4 on the leg extension, each closer: wide -> closer -> closer -> face with head back at peak strain
# then legs close-up (technique), chest, bicep, back, chest
L="A001_11041651_C018.mov"
SHOTS=(
  "$L|22.7|0.70|0.80|0.05|0.08|1"
  "$L|27.4|1.10|0.58|0.17|0.15|1"
  "$L|30.8|0.68|0.42|0.29|0.20|1"
  "$L|34.0|0.90|0.28|0.39|0.22|1"
  "$L|41.6|2.10|0.85|0.02|0.08|2"
  "A001_11041715_C022.MOV|20.0|1.72|1|0|0|0"
  "A001_11041753_C024.MOV|32.0|1.00|1|0|0|0"
  "A001_11041749_C023.MOV|72.5|1.78|1|0|0|0"
  "A001_11041715_C022.MOV|48.1|1.28|0.80|0.04|0.0|1"
)
: > "$W/shots/list.txt"
i=0
for s in "${SHOTS[@]}"; do
  IFS='|' read -r f st du cw cx cy push <<< "$s"; i=$((i+1))
  CROP="crop=trunc(iw*$cw/2)*2:trunc(ih*$cw/2)*2:iw*$cx:ih*$cy,unsharp=5:5:0.6"
  PUSH=""
  [ "$push" = 1 ] && PUSH=",zoompan=z='1+0.08*on/($du*30)':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s=1920x1080:fps=30"
  # 2 = zoom out: starts close, ends wide (eased) so the full rep is revealed
  [ "$push" = 2 ] && PUSH=",zoompan=z='1+0.6*pow(1-min(1,on/($du*30*0.8)),2)':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s=1920x1080:fps=30"
  ffmpeg -v error -y -ss "$st" -t "$du" -i "$SRC/$f" -an -vf "$CROP,$FIT$PUSH,$GRADE" \
    -c:v libx264 -preset medium -crf 14 -pix_fmt yuv420p "$W/shots/s$i.mp4"
  echo "file 's$i.mp4'" >> "$W/shots/list.txt"
done
cp "$SCR/song.wav" "$W/song.wav"

# lyric text: handwritten font, pops in big then settles (like the reference)
cd /c/Windows/Fonts
FONT="Inkfree.ttf"; [ -f "$FONT" ] || FONT="segoepr.ttf"
pop(){ # text start end size colour y
  echo "drawtext=fontfile=$FONT:text='$1':enable='between(t,$2,$3)':fontsize='$4*(1+0.35*max(0,1-(t-$2)*7))':fontcolor=$5:x=(w-text_w)/2+3*sin(t*37):y=$6-text_h/2+2*cos(t*41):shadowcolor=black@0.7:shadowx=3:shadowy=3"
}
WHITE="0xE8E8E8"; RED="0xD0201E"; YEL="0xD8B23A"
T=(
  "$(pop 'TRY' 0.00 0.66 110 $WHITE 540)"
  "$(pop 'TRY' 0.70 1.76 150 $WHITE 540)"
  "$(pop 'TRY' 1.80 2.44 190 $WHITE 540)"
  "$(pop 'TRY' 2.48 3.36 240 $WHITE 540)"
  "$(pop 'TO THINK OF SOMETHING' 3.38 5.46 80 $WHITE 470)"
  "$(pop 'DIFFERENT' 4.54 5.46 80 $YEL 580)"
  "$(pop 'OH' 5.48 6.00 120 $WHITE 540)"
  "$(pop 'MY' 6.02 7.18 150 $WHITE 540)"
  "$(pop 'GOD' 7.20 8.18 300 $WHITE 540)"
  "$(pop 'KEEP' 8.20 8.76 120 $WHITE 470)"
  "$(pop 'ME FROM GOING' 8.76 9.96 100 $WHITE 600)"
  "$(pop 'LUNATIC' 9.98 11.26 190 $RED 540)"
)
VF="$(IFS=,; echo "${T[*]}")"
OUT="$OUTDIR/project-1-v$V.mp4"
ffmpeg -v error -y -f concat -safe 0 -i "$(cygpath -m "$W/shots/list.txt")" -i "$(cygpath -m "$W/song.wav")" \
  -vf "$VF" -map 0:v -map 1:a -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -c:a aac -b:a 256k -shortest -movflags +faststart "$(cygpath -m "$OUT")"
ffprobe -v error -show_entries format=duration -of csv=p=0 "$(cygpath -m "$OUT")"
# contact sheet: one frame per 0.5s
ffmpeg -v error -y -i "$(cygpath -m "$OUT")" -vf "fps=2,scale=480:-2,tile=6x4" -frames:v 1 "$(cygpath -m "$SCR/v$V-sheet.jpg")"
echo "OUT=$(cygpath -w "$OUT")"
