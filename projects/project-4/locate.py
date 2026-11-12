import cv2, numpy as np, os, sys
SRC=os.path.expanduser("~")+"/Desktop/edting/storage/project 4/"
F={f.split("_")[-1][:4]:SRC+f for f in os.listdir(SRC) if f.upper().endswith(".MOV")}
L=[x.split("@") for x in sys.argv[3:]]; cols=int(sys.argv[2]); T=[]
for c,t in L:
    cap=cv2.VideoCapture(F[c]); cap.set(0,float(t)*1000); ok,f=cap.read()
    f=cv2.resize(f,(480,270),interpolation=cv2.INTER_AREA); h,w=f.shape[:2]
    for i in range(1,10):
        col=(0,255,255) if i==5 else (255,255,255)
        cv2.line(f,(i*w//10,0),(i*w//10,h),col,1); cv2.line(f,(0,i*h//10),(w,i*h//10),col,1)
        cv2.putText(f,"%d"%i,(i*w//10+1,10),0,.35,(0,255,0),1); cv2.putText(f,"%d"%i,(1,i*h//10-2),0,.35,(0,255,0),1)
    cv2.rectangle(f,(0,h-18),(w,h),(0,0,0),-1); cv2.putText(f,f"{c} {t}",(4,h-5),0,.5,(0,255,255),1); T.append(f)
while len(T)%cols: T.append(np.zeros_like(T[0]))
cv2.imencode(".jpg",np.vstack([np.hstack(T[i:i+cols]) for i in range(0,len(T),cols)]),[1,85])[1].tofile(sys.argv[1])
