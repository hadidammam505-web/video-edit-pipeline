import cv2, numpy as np, os
SRC=os.path.expanduser("~")+"/Desktop/edting/storage/project 4/"
F={f.split("_")[-1][:4]:SRC+f for f in os.listdir(SRC) if f.upper().endswith(".MOV")}
B={"C073":(55,110,.1,.75,.2,1),"C075":(4,40,.05,.85,0,1),"C078":(44,80,.3,.9,.1,.8),"C079":(28,62,.2,.85,.2,.8),"C080":(44,90,.55,.85,0,.6),
   "C081":(38,62,.1,.8,.3,.7),"C082":(26,52,.2,.9,.2,.8),"C083":(12,60,.2,.6,.3,.8),"C084":(14,48,.15,.8,.3,.8)}
for c,(a,b,x0,x1,y0,y1) in B.items():
    cap=cv2.VideoCapture(F[c]); cap.set(0,a*1000); prev=None; E=[]; n=int((b-a)*30)
    for i in range(n):
        ok,f=cap.read()
        if not ok: break
        if i%3: continue
        h,w=f.shape[:2]; g=cv2.cvtColor(cv2.resize(f[int(y0*h):int(y1*h),int(x0*w):int(x1*w)],(120,80)),cv2.COLOR_BGR2GRAY).astype(np.float32)
        if prev is not None: E.append(np.abs(g-prev).mean())
        prev=g
    E=np.convolve(E,np.ones(5)/5,mode="same"); pk=[i for i in range(2,len(E)-2) if E[i]==E[max(0,i-8):i+9].max() and E[i]>np.median(E)*1.2]
    print(c,"peaks",[round(a+.1*i+.1,1) for i in pk])
