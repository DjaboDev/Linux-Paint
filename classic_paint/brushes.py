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
