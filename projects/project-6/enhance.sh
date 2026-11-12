#!/bin/bash
# Enhance the landscape (morning + kitchen) shots for project 6. Each job: name clip start dur [crop]
PY=/c/Users/ZGAMES/Documents/video-edit/tools/vision/Scripts/python.exe
T=/c/Users/ZGAMES/Documents/video-edit/tools/esrgan.py
ST="/c/Users/ZGAMES/Desktop/edting/storage"; O=/c/Users/ZGAMES/Documents/video-edit/projects/project-6/enh
job() { [ -f "$O/$1.mov" ] && return; "$PY" "$T" "$2" "$O/$1.mov" --ss $3 --t $4 --fps 30 --pre 1 --denoise 0.5 --vf "hqdn3d=0:0:6:6" --w 2028 ${5:+--crop $5}; }
job sleep  "$ST/project 6/A001_08300235_C035.MOV" 0.0 3.4
job stir   "$ST/project 6/A001_08300235_C035.MOV" 3.8 2.0
job throw  "$ST/project 6/A001_08300235_C035.MOV" 7.9 1.0
job wake   "$ST/project 6/A001_08300239_C037.MOV" 4.7 1.4
job stretch "$ST/project 6/A001_08300239_C037.MOV" 31.6 1.8
job getup  "$ST/project 6/A001_08300239_C037.MOV" 45.0 1.6
job hanger "$ST/project 6/A001_08300228_C032.MOV" 2.2 1.8
job walk   "$ST/project 6/A001_08300225_C031.MOV" 0.3 2.5
job towel  "$ST/project 6/A001_08300224_C030.MOV" 3.3 2.5
job pour   "$ST/project 5/100E8BE3-D509-4B0F-BCFD-F8C9E03A9F53.MP4" 2.9 3.4 1440:810:0:875
job mix    "$ST/project 5/100E8BE3-D509-4B0F-BCFD-F8C9E03A9F53.MP4" 9.1 1.8 1440:810:0:875
job sauce  "$ST/project 5/100E8BE3-D509-4B0F-BCFD-F8C9E03A9F53.MP4" 11.8 3.4 1440:810:0:875
echo "rev1 done"
# revision 2 (2026-11-12): second wake-up, shower entry, plating
job wake2  "$ST/project 6/A001_08300241_C038.MOV" 2.8 2.7
job enter  "$ST/project 6/A001_08300225_C031.MOV" 2.6 2.2
job plate  "$ST/project 5/100E8BE3-D509-4B0F-BCFD-F8C9E03A9F53.MP4" 14.6 2.6 1440:810:0:875
echo REV2 DONE
