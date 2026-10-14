from .i18n import tr
"""Local background segmentation, independent of the editor and GUI thread."""
from pathlib import Path
import hashlib
import os
import threading
import urllib.request
import numpy as np
import cv2
from PySide6.QtGui import QImage

MODEL_URL = "https://github.com/danielgatis/rembg/releases/download/v0.0.0/BiRefNet-general-bb_swin_v1_tiny-epoch_232.onnx"
MODEL_MD5 = "4fab47adc4ff364be1713e97b7e66334"
_SESSION = None
_LOCK = threading.Lock()

def rgba_from_image(image):
    image=image.convertToFormat(QImage.Format.Format_RGBA8888)
    data=np.frombuffer(image.constBits(),np.uint8).reshape(image.height(),image.bytesPerLine())
    return data[:,:image.width()*4].reshape(image.height(),image.width(),4).copy()

def image_from_rgba(array):
    array=np.ascontiguousarray(array,dtype=np.uint8)
    return QImage(array.data,array.shape[1],array.shape[0],array.strides[0],QImage.Format.Format_RGBA8888).copy()

def magic_region(rgb,seed,tolerance,contiguous=True):
    x,y=seed
    if not (0<=x<rgb.shape[1] and 0<=y<rgb.shape[0]):raise ValueError(tr('Clique dentro da imagem.'))
    tolerance=max(0,min(255,int(tolerance)))
    if not contiguous:
        distance=np.max(np.abs(rgb.astype(np.int16)-rgb[y,x].astype(np.int16)),axis=2)
        return distance<=tolerance
    mask=np.zeros((rgb.shape[0]+2,rgb.shape[1]+2),np.uint8)
    cv2.floodFill(np.ascontiguousarray(rgb),mask,(x,y),(0,0,0),
                 (tolerance,)*3,(tolerance,)*3,
                 4 | cv2.FLOODFILL_FIXED_RANGE | cv2.FLOODFILL_MASK_ONLY | (255<<8))
    return mask[1:-1,1:-1]>0

def border_alpha(rgba,tolerance=24):
    h,w=rgba.shape[:2]
    erased=np.zeros((h,w),bool)
    seeds=[(x,0) for x in np.linspace(0,w-1,5,dtype=int)]+[(x,h-1) for x in np.linspace(0,w-1,5,dtype=int)]
    seeds += [(0,y) for y in np.linspace(0,h-1,5,dtype=int)]+[(w-1,y) for y in np.linspace(0,h-1,5,dtype=int)]
    for x,y in seeds:
        if not erased[y,x]:erased |= magic_region(rgba[:,:,:3],(int(x),int(y)),tolerance)
    return np.where(erased,0,255).astype(np.uint8)

def grabcut_alpha(rgba,alpha=None,keep=None,erase=None):
    h,w=rgba.shape[:2]
    if min(h,w)<3:raise ValueError(tr('Imagem pequena demais para refinar.'))
    factor=min(1,1200/max(h,w));size=(max(3,round(w*factor)),max(3,round(h*factor)))
    rgb=cv2.resize(rgba[:,:,:3],size,interpolation=cv2.INTER_AREA)
    labels=np.full((size[1],size[0]),cv2.GC_PR_FGD,np.uint8)
    if alpha is None or np.all(alpha==255):
        border=border_alpha(np.dstack((rgb,np.full(labels.shape,255,np.uint8))))
        labels[border==0]=cv2.GC_PR_BGD
        labels[0,:]=labels[-1,:]=cv2.GC_BGD
        labels[:,0]=labels[:,-1]=cv2.GC_BGD
    else:
        a=cv2.resize(alpha,size,interpolation=cv2.INTER_LINEAR)
        labels[a<128]=cv2.GC_PR_BGD
        labels[a<5]=cv2.GC_BGD
        labels[a>250]=cv2.GC_FGD
    # Transparent input is definite background; never create opacity from it.
    labels[cv2.resize(rgba[:,:,3],size,interpolation=cv2.INTER_NEAREST)==0]=cv2.GC_BGD
    if keep is not None:labels[cv2.resize(keep.astype(np.uint8),size,interpolation=cv2.INTER_NEAREST)>0]=cv2.GC_FGD
    if erase is not None:labels[cv2.resize(erase.astype(np.uint8),size,interpolation=cv2.INTER_NEAREST)>0]=cv2.GC_BGD
    if not np.any((labels==cv2.GC_BGD)|(labels==cv2.GC_PR_BGD)) or not np.any((labels==cv2.GC_FGD)|(labels==cv2.GC_PR_FGD)):
        raise ValueError(tr('Marque pelo menos uma área para manter e outra para apagar.'))
    # Deterministic initialization and capped analysis size keep repeated previews stable.
    cv2.setRNGSeed(0)
    bg=np.zeros((1,65),np.float64);fg=np.zeros((1,65),np.float64)
    cv2.grabCut(cv2.cvtColor(rgb,cv2.COLOR_RGB2BGR),labels,None,bg,fg,5,cv2.GC_INIT_WITH_MASK)
    result=np.where((labels==cv2.GC_FGD)|(labels==cv2.GC_PR_FGD),255,0).astype(np.uint8)
    return cv2.resize(result,(w,h),interpolation=cv2.INTER_LINEAR)

def model_path():
    root=Path(os.environ.get('XDG_CACHE_HOME',Path.home()/'.cache'))/'LinuxPaint'/'models'
    return root/'birefnet-general-lite.onnx'

def download_model(progress=lambda value:None,cancel=lambda:False):
    path=model_path();path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():return path
    temp=path.with_name(path.name+f'.{os.getpid()}.download')
    try:
        digest=hashlib.md5()
        request=urllib.request.Request(MODEL_URL,headers={'User-Agent':'LinuxPaint/0.4'})
        with urllib.request.urlopen(request,timeout=60) as response,temp.open('wb') as stream:
            total=int(response.headers.get('Content-Length',0));count=0
            while True:
                if cancel():raise InterruptedError('Download cancelado.')
                chunk=response.read(1024*1024)
                if not chunk:break
                stream.write(chunk);digest.update(chunk);count+=len(chunk)
                progress(min(99,round(count*100/total)) if total else -1)
        if digest.hexdigest()!=MODEL_MD5:raise ValueError(tr('O modelo baixado falhou na verificação de integridade.'))
        temp.replace(path);progress(100);return path
    finally:temp.unlink(missing_ok=True)

def ai_alpha(rgba):
    global _SESSION
    if not model_path().exists():raise FileNotFoundError('Baixe o modelo local antes de usar a detecção IA.')
    import onnxruntime as ort
    ort.disable_telemetry_events()
    from PIL import Image
    with _LOCK:
        if _SESSION is None:
            options=ort.SessionOptions();options.intra_op_num_threads=max(1,min(4,os.cpu_count() or 1))
            _SESSION=ort.InferenceSession(str(model_path()),sess_options=options,providers=['CPUExecutionProvider'])
        rgb=rgba[:,:,:3].copy()
        # Composite transparent input on neutral grey for analysis only.
        a=rgba[:,:,3:4].astype(np.float32)/255
        rgb=np.clip(rgb*a+128*(1-a),0,255).astype(np.uint8)
        resized=np.asarray(Image.fromarray(rgb).resize((1024,1024),Image.Resampling.LANCZOS),dtype=np.float32)/255
        normalized=(resized-np.array([.485,.456,.406],np.float32))/np.array([.229,.224,.225],np.float32)
        tensor=np.transpose(normalized,(2,0,1))[None].astype(np.float32)
        logits=_SESSION.run(None,{_SESSION.get_inputs()[0].name:tensor})[0][0,0]
    probabilities=1/(1+np.exp(-np.clip(logits,-60,60)))
    low,high=float(probabilities.min()),float(probabilities.max())
    # Keep a constant model prediction constant instead of dividing by zero.
    if high-low>1e-6:probabilities=(probabilities-low)/(high-low)
    mask=Image.fromarray(np.clip(probabilities*255,0,255).astype(np.uint8))
    return np.asarray(mask.resize((rgba.shape[1],rgba.shape[0]),Image.Resampling.LANCZOS)).copy()

def reduce_color_halo(rgba,mask):
    """Unmix background color at soft edges; only originally opaque input is adjusted."""
    edges=(mask>8)&(mask<245)&(rgba[:,:,3]==255)
    background=mask<=8
    if not np.any(edges) or not np.any(background):return rgba[:,:,:3]
    # OpenCV PIXEL labels enumerate zero pixels in row order.
    _,labels=cv2.distanceTransformWithLabels((~background).astype(np.uint8),cv2.DIST_L2,5,labelType=cv2.DIST_LABEL_PIXEL)
    bg_colors=np.vstack((np.zeros((1,3),np.float32),rgba[:,:,:3][background].astype(np.float32)))
    nearest=bg_colors[labels[edges]]
    alpha=mask[edges,None].astype(np.float32)/255
    original=rgba[:,:,:3][edges].astype(np.float32)
    estimate=np.clip((original-(1-alpha)*nearest)/np.maximum(alpha,.04),0,255)
    rgb=rgba[:,:,:3].copy();rgb[edges]=estimate.astype(np.uint8)
    return rgb


def compose(rgba,alpha,keep=None,erase=None,feather=0,shift=0,decontaminate=False):
    mask=alpha.copy()
    if shift:
        kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*abs(shift)+1,)*2)
        mask=cv2.dilate(mask,kernel) if shift>0 else cv2.erode(mask,kernel)
    if feather>0:mask=cv2.GaussianBlur(mask,(2*feather+1,)*2,0)
    if keep is not None:mask[keep>0]=255
    if erase is not None:mask[erase>0]=0
    result=rgba.copy()
    if decontaminate:result[:,:,:3]=reduce_color_halo(rgba,mask)
    result[:,:,3]=((rgba[:,:,3].astype(np.uint16)*mask.astype(np.uint16)+127)//255).astype(np.uint8)
    return result
