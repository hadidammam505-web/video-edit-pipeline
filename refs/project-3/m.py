import cv2,numpy as np,sys,json
c=cv2.VideoCapture(sys.argv[1]);fps=c.get(5);pr=None;out=[];i=0;rows=None;L=[]
while True:
    ok,f=c.read()
    if not ok:break
    g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY)
    if rows is None:
        r=g.mean(1)>6;ys=np.where(r)[0]
    L.append(g)
    i+=1
all_=np.stack(L);r=all_.mean((0,2));ys=np.where(r>8)[0];y0,y1=ys[0],ys[-1]
print('fps',fps,'frames',len(L),'H',all_.shape[1],'W',all_.shape[2],'picture rows',y0,y1,'ratio',round(all_.shape[2]/(y1-y0+1),3))
pic=[cv2.resize(g[y0:y1],(90,64)).astype(np.float32) for g in L]
d=[0]+[float(np.abs(pic[k]-pic[k-1]).mean()) for k in range(1,len(pic))]
med=np.median(d)
cuts=[(k,round(k/fps,3),round(d[k],1)) for k in range(1,len(d)) if d[k]>max(6,4*med) and d[k]>=d[k-1] and (k+1==len(d) or d[k]>=d[k+1])]
print('median',round(med,2));print('cuts',cuts)
print('bright frames',[(k,round(k/fps,3),int((pic[k]>205).mean()*100)) for k in range(len(pic)) if (pic[k]>205).mean()>.04])
print('mean luma per .5s',[round(float(np.mean([pic[k].mean() for k in range(int(s*fps),min(len(pic),int((s+.5)*fps)))])),1) for s in np.arange(0,9.9,.5)])
