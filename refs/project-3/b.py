import librosa,numpy as np,sys
y,sr=librosa.load(sys.argv[1],sr=22050,mono=True);env=librosa.onset.onset_strength(y=y,sr=sr,hop_length=256)
on=librosa.onset.onset_detect(onset_envelope=env,sr=sr,hop_length=256,units='time');t,b=librosa.beat.beat_track(y=y,sr=sr,units='time')
print('dur',round(len(y)/sr,2),'tempo',np.round(t,1));print('beats',np.round(b,2).tolist());print('onsets',np.round(on,2).tolist())
S=np.abs(librosa.stft(y,hop_length=256));f=librosa.fft_frequencies(sr=sr);fr=librosa.frames_to_time(np.arange(S.shape[1]),sr=sr,hop_length=256)
for a,c,n in ((0,150,'low'),(2000,11000,'high')):
    e=S[(f>=a)&(f<c)].sum(0);print(n,[int(20*np.log10(e[(fr>=x)&(fr<x+.5)].mean()+1e-6)) for x in np.arange(0,10,.5)])
