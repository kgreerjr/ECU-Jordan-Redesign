# Recolor ECU's standard skull (BLA decal mask, sRGB-stored: R=trim/ECU/bandana, G=skull+bones, B=hat, none=line color)
# usage: python3 recolor_skull_logo.py MASK.png OUT.png TRIM SKULL HAT LINE   (hex colors)
import sys, numpy as np
from PIL import Image
def lin(c): return np.where(c<=0.04045, c/12.92, ((c+0.055)/1.055)**2.4)
def srgb(c): return np.where(c<=0.0031308, c*12.92, 1.055*np.clip(c,0,None)**(1/2.4)-0.055)
def hx(h): return lin(np.array([int(h[i:i+2],16) for i in (1,3,5)],float)/255)
def recolor(src, out, trim, skull, hat, line):
    a=np.array(Image.open(src).convert('RGBA')).astype(float)/255
    m=lin(a[...,:3]); R,G,B=m[...,0:1],m[...,1:2],m[...,2:3]
    s=np.clip(R+G+B,1,None); w=np.clip(R+G+B,0,1)
    rgb=(R*hx(trim)+G*hx(skull)+B*hx(hat))/s + (1-w)*hx(line)
    Image.fromarray(np.dstack([srgb(rgb)*255, a[...,3]*255]).clip(0,255).astype(np.uint8)).save(out)
if __name__=='__main__': recolor(*sys.argv[1:7])
