# Tileable topographic contour pattern for the Jolly Roger fabric layer (material colorTexture).
# White = full charcoal, darker lines = tonal "sublimated" contours (material tint multiplies).
import numpy as np, sys
from PIL import Image
# usage: make_topo_pattern.py OUTDIR [NAME LINE WIDTH]   pants (default): ECU_JR_Topo_col 0.2 4.5 ; jersey: ECU_JR_Topo_Jersey_col 0.08 6.0
OUT=sys.argv[1]; NAME=sys.argv[2] if len(sys.argv)>2 else 'ECU_JR_Topo_col'
N=1024; LINE=float(sys.argv[3]) if len(sys.argv)>3 else 0.2; W=float(sys.argv[4]) if len(sys.argv)>4 else 4.5
y,x=np.mgrid[0:N,0:N]/N*2*np.pi
rng=np.random.default_rng(1928)
h=np.zeros((N,N))
for fx,fy,a in [(1,0,1),(0,1,1),(1,1,.8),(1,-1,.8),(2,1,.45),(1,2,.45),(2,-1,.4),(3,1,.22),(1,3,.22),(3,-2,.15),(2,3,.15)]:
    h+=a*np.sin(fx*x+fy*y+rng.uniform(0,2*np.pi))      # integer freqs -> seamless tile
h=(h-h.min())/(h.max()-h.min())
k=11; f=h*k; d=np.abs(f-np.round(f))                   # distance to nearest contour
g=np.hypot(*np.gradient(f))+1e-9; px=d/g               # ~pixel distance -> even line width
w=W; line=np.clip(1-(px-w)/1.2,0,1)*np.clip((g-0.004)/0.004,0,1)   # no dots at peaks
v=1-(1-LINE)*line
img=(np.clip(v,0,1)*255).astype(np.uint8)
Image.fromarray(np.dstack([img,img,img,np.full_like(img,255)]),'RGBA').save(OUT+'/'+NAME+'.png')
# preview: 2x2 tiles on charcoal #404044 (linear multiply), gold "0" not included
lin=lambda c:((c/255+0.055)/1.055)**2.4; srgb=lambda l:np.where(l<=0.0031308,12.92*l,1.055*l**(1/2.4)-0.055)
t=np.tile(v,(2,2)); prev=np.dstack([srgb(lin(c)*t) for c in (0x4A,0x4A,0x4F)])
Image.fromarray((prev*255).astype(np.uint8)).resize((1024,1024)).save(OUT+'/preview_'+NAME+'.png')
print('ok')
