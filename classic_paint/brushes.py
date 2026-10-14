"""Actual hardness falloff for round/square brushes and transparent erasing."""
import math
import numpy as np
from PySide6.QtCore import QPointF
from PySide6.QtGui import QImage,QPainter
_CACHE={}

def soft_stroke(painter,a,b,color,width,hardness,square=False):
    erase=color.alpha()==0
    if erase:painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationOut)
    else:painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
    key=(color.rgba(),round(width),round(hardness),square)
    if key not in _CACHE:
        size=max(3,math.ceil(width)+2);radius=max(1,width/2)
        coordinates=np.arange(size,dtype=np.float32)-(size-1)/2
        x,y=np.meshgrid(coordinates,coordinates)
        distance=np.maximum(np.abs(x),np.abs(y)) if square else np.hypot(x,y)
        coverage=np.clip((radius-distance)/max(.1,radius*(1-hardness/100)),0,1)
        if width<3:
            # Integrate coverage inside each pixel: a 1-pixel tip still responds
            # to hardness instead of sampling only a fully opaque center.
            coverage=np.zeros_like(distance)
            for dx in (-.375,-.125,.125,.375):
                for dy in (-.375,-.125,.125,.375):
                    d=np.maximum(np.abs(x+dx),np.abs(y+dy)) if square else np.hypot(x+dx,y+dy)
                    coverage+=np.clip((radius-d)/max(.1,radius*(1-hardness/100)),0,1)/16

        pixels=np.zeros((size,size,4),np.uint8)
        pixels[:,:,:3]=(color.red(),color.green(),color.blue())
        pixels[:,:,3]=np.round(coverage*(255 if erase else color.alpha())).astype(np.uint8)
        stamp=QImage(pixels.data,size,size,pixels.strides[0],QImage.Format.Format_RGBA8888).copy()
        if len(_CACHE)>=32:_CACHE.clear()
        _CACHE[key]=stamp
    stamp=_CACHE[key]
    length=math.hypot(b.x()-a.x(),b.y()-a.y());steps=max(1,math.ceil(length/max(1,width*.2)))
    # A click is one stamp. Repeated motion stamps intentionally accumulate paint.
    for i in range(1 if length==0 else steps+1):
        t=i/steps
        center=QPointF(a.x()+(b.x()-a.x())*t,a.y()+(b.y()-a.y())*t)
        painter.drawImage(center-QPointF(stamp.width()/2,stamp.height()/2),stamp)


def feather_shape(image,sigma):
    """Soften only the new shape, filtering premultiplied colors to avoid halos."""
    import cv2
    image=image.convertToFormat(QImage.Format.Format_RGBA8888)
    rgba=np.frombuffer(image.constBits(),np.uint8).reshape(image.height(),image.bytesPerLine())[:,:image.width()*4].reshape(image.height(),image.width(),4).astype(np.float32)/255
    rgba[:,:,:3]*=rgba[:,:,3:4]
    rgba=cv2.GaussianBlur(rgba,(0,0),sigmaX=sigma,sigmaY=sigma,borderType=cv2.BORDER_CONSTANT)
    alpha=rgba[:,:,3:4]
    rgba[:,:,:3]=np.divide(rgba[:,:,:3],alpha,out=np.zeros_like(rgba[:,:,:3]),where=alpha>0)
    pixels=np.round(np.clip(rgba,0,1)*255).astype(np.uint8)
    return QImage(pixels.data,image.width(),image.height(),pixels.strides[0],QImage.Format.Format_RGBA8888).copy()
