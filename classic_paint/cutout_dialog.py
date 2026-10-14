from .i18n import tr
"""Preview-first local cutout editor with explicit keep/remove correction tools."""
import numpy as np
import cv2
from PySide6.QtCore import Qt, QPointF, QRectF, Signal, QThread
from PySide6.QtGui import QPainter, QColor, QPen, QPixmap
from PySide6.QtWidgets import (QDialog,QWidget,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,
    QToolButton,QButtonGroup,QSlider,QSpinBox,QCheckBox,QDialogButtonBox,QProgressBar)
from .modern_widgets import ModernDialog as QDialog, ModernSpinBox as QSpinBox
from .cutout import (rgba_from_image,image_from_rgba,border_alpha,magic_region,grabcut_alpha,
                     compose,ai_alpha,model_path,download_model)

class SegmentationJob(QThread):
    result=Signal(object)
    failed=Signal(str)
    progress=Signal(int)
    def __init__(self,function,parent=None):super().__init__(parent);self.function=function
    def run(self):
        try:self.result.emit(self.function(self.progress.emit,self.isInterruptionRequested))
        except Exception as exc:self.failed.emit(str(exc))

class CutoutView(QWidget):
    stroke_started=Signal()
    stroke=Signal(object,object)
    magic_clicked=Signal(object)
    def __init__(self,dialog):
        super().__init__();self.dialog=dialog;self.setMinimumSize(360,300)
        self.mode='magic';self.last=None;self.cursor_pos=None;self.pan=QPointF();self.pan_anchor=None
        self.setMouseTracking(True);self.setCursor(Qt.CursorShape.CrossCursor)
        self.pixmap=QPixmap();self.original_pixmap=QPixmap.fromImage(image_from_rgba(dialog.rgba));self.bounds=QRectF();self.scale=1

    def set_image(self,image):self.pixmap=QPixmap.fromImage(image);self.update()

    def paintEvent(self,event):
        p=QPainter(self);p.fillRect(self.rect(),QColor('#191919' if self.dialog.dark else '#d9d9d9'))
        if self.pixmap.isNull():p.end();return
        fit=min((self.width()-24)/self.pixmap.width(),(self.height()-24)/self.pixmap.height())
        self.scale=1. if self.dialog.preview_zoom is None else fit*self.dialog.preview_zoom
        w,h=self.pixmap.width()*self.scale,self.pixmap.height()*self.scale
        self.bounds=QRectF((self.width()-w)/2+self.pan.x(),(self.height()-h)/2+self.pan.y(),w,h)
        p.save();p.setClipRect(self.bounds)
        bg=self.dialog.background
        if bg=='checker':
            visible=self.bounds.intersected(QRectF(self.rect()))
            for y in range(int(visible.top())//16*16,int(visible.bottom())+16,16):
                for x in range(int(visible.left())//16*16,int(visible.right())+16,16):
                    p.fillRect(QRectF(x,y,16,16),QColor('#777777' if (x//16+y//16)%2 else '#aaaaaa'))
        else:p.fillRect(self.bounds,QColor(bg))
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        if self.dialog.original_view.isChecked():
            p.drawPixmap(self.bounds,self.original_pixmap,QRectF(self.original_pixmap.rect()))
        else:p.drawPixmap(self.bounds,self.pixmap,QRectF(self.pixmap.rect()))
        if self.dialog.show_marks.isChecked() and not self.dialog.original_view.isChecked():
            p.drawImage(self.bounds,self.dialog.mark_image)
        p.restore()
        if self.cursor_pos is not None and self.mode!='magic' and not self.dialog.original_view.isChecked():
            r=self.dialog.brush.value()*self.scale/2
            p.setPen(QPen(QColor('#ffffff'),2));p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawEllipse(self.cursor_pos,max(2,r),max(2,r))
            p.setPen(QPen(QColor('#111111'),1));p.drawEllipse(self.cursor_pos,max(2,r)+2,max(2,r)+2)
        p.end()

    def image_point(self,pos):
        if not self.bounds.contains(pos):return None
        return (min(self.dialog.rgba.shape[1]-1,max(0,int((pos.x()-self.bounds.left())/self.scale))),
                min(self.dialog.rgba.shape[0]-1,max(0,int((pos.y()-self.bounds.top())/self.scale))))

    def mousePressEvent(self,event):
        if event.button()==Qt.MouseButton.MiddleButton:
            self.pan_anchor=event.position();return
        if event.button()!=Qt.MouseButton.LeftButton:return
        if self.dialog.original_view.isChecked():return
        point=self.image_point(event.position())
        if point is None:return
        if self.mode=='magic':self.magic_clicked.emit(point)
        else:self.stroke_started.emit();self.last=point;self.stroke.emit(point,point)

    def mouseMoveEvent(self,event):
        if self.pan_anchor is not None:
            self.pan+=event.position()-self.pan_anchor;self.pan_anchor=event.position();self.update();return
        self.cursor_pos=event.position();point=self.image_point(event.position())
        if self.last is not None and point is not None:
            self.stroke.emit(self.last,point);self.last=point
        self.update()

    def mouseReleaseEvent(self,event):
        if event.button()==Qt.MouseButton.MiddleButton:self.pan_anchor=None;return
        point=self.image_point(event.position())
        if self.last is not None and point is not None:self.stroke.emit(self.last,point)
        self.last=None

    def wheelEvent(self,event):
        fit=min((self.width()-24)/self.pixmap.width(),(self.height()-24)/self.pixmap.height())
        zoom=1/fit if self.dialog.preview_zoom is None else self.dialog.preview_zoom
        self.dialog.preview_zoom=max(.25,min(20,zoom*(1.2 if event.angleDelta().y()>0 else 1/1.2)))
        self.update();event.accept()

    def leaveEvent(self,event):self.cursor_pos=None;self.update()

class BackgroundDialog(QDialog):
    def __init__(self,image,parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr('Remover fundo'));self.resize(1100,800);self.setSizeGripEnabled(True)
        self.dark=getattr(parent,'dark_mode',True)
        self.rgba=rgba_from_image(image);h,w=self.rgba.shape[:2]
        self.alpha=np.full((h,w),255,np.uint8);self.keep=np.zeros((h,w),np.uint8);self.erase=self.keep.copy()
        self.history=[];self.history_bytes=0;self.worker=None;self._closing=False
        self.background='checker';self.preview_zoom=1.;self.output=None
        layout=QVBoxLayout(self);layout.setContentsMargins(16,16,16,16);layout.setSpacing(10)
        self.notice=QLabel(tr('1. Detecte o fundo ou clique nele com a seleção mágica.  2. Corrija com Manter / Apagar.  3. Revise e aplique.'))
        self.notice.setWordWrap(True);layout.addWidget(self.notice)
        actions=QHBoxLayout();layout.addLayout(actions)
        self.auto=QPushButton(tr('Detectar pelas bordas'));actions.addWidget(self.auto)
        self.ai=QPushButton(tr('Detectar com IA' if model_path().exists() else 'Baixar modelo IA'));actions.addWidget(self.ai)
        self.refine=QPushButton(tr('Refinar com marcações'));actions.addWidget(self.refine)
        self.undo=QPushButton(tr('Desfazer ajuste'));actions.addWidget(self.undo)
        self.reset=QPushButton(tr('Recomeçar'));actions.addWidget(self.reset)
        actions.addStretch()
        self.original_view=QCheckBox(tr('Ver original'));actions.addWidget(self.original_view)
        self.auto.clicked.connect(self.detect_border)
        self.ai.clicked.connect(self.detect_ai)
        self.refine.clicked.connect(self.refine_marked)
        self.undo.clicked.connect(self.undo_edit);self.reset.clicked.connect(self.reset_mask)
        tools=QHBoxLayout();layout.addLayout(tools)
        self.group=QButtonGroup(self);self.group.setExclusive(True)
        for mode,label in [('magic','Seleção mágica'),('keep','Manter'),('erase','Apagar')]:
            b=QToolButton();b.setText(tr(label));b.setCheckable(True);b.setChecked(mode=='magic');self.group.addButton(b)
            b.clicked.connect(lambda checked=False,m=mode:self.set_mode(m));tools.addWidget(b)
        tools.addSpacing(12);tools.addWidget(QLabel(tr('Tolerância')))
        self.tolerance=QSpinBox();self.tolerance.setRange(0,120);self.tolerance.setValue(24);tools.addWidget(self.tolerance)
        self.contiguous=QCheckBox(tr('Área conectada'));self.contiguous.setChecked(True);tools.addWidget(self.contiguous)
        tools.addSpacing(12);tools.addWidget(QLabel(tr('Pincel (px)')))
        self.brush=QSpinBox();self.brush.setRange(1,500);self.brush.setValue(30);tools.addWidget(self.brush)
        tools.addStretch();self.show_marks=QCheckBox(tr('Mostrar marcações'));self.show_marks.setChecked(True);tools.addWidget(self.show_marks)
        self.view=CutoutView(self);layout.addWidget(self.view,1)
        self.view.magic_clicked.connect(self.magic);self.view.stroke_started.connect(self.snapshot);self.view.stroke.connect(self.paint_mark)
        self.original_view.toggled.connect(self.original_toggled);self.show_marks.toggled.connect(lambda _:self.view.update())
        bottom=QHBoxLayout();layout.addLayout(bottom)
        for bg,label in [('checker','Transparência'),('#ffffff','Branco'),('#181818','Escuro')]:
            b=QPushButton(tr(label));b.clicked.connect(lambda checked=False,c=bg:self.set_background(c));bottom.addWidget(b)
        zoom=QPushButton(tr('Zoom 100% / Ajustar'));zoom.clicked.connect(self.toggle_zoom);bottom.addWidget(zoom)
        self.halo=QCheckBox(tr('Reduzir halo'));self.halo.setChecked(True);bottom.addWidget(self.halo)
        bottom.addStretch()
        edges=QHBoxLayout();layout.addLayout(edges);edges.addStretch();edges.addWidget(QLabel(tr('Suavizar borda')))
        self.feather=QSpinBox();self.feather.setRange(0,20);self.feather.setSuffix(' px');edges.addWidget(self.feather)
        edges.addSpacing(16);edges.addWidget(QLabel(tr('Expandir / retrair')))
        self.shift=QSpinBox();self.shift.setRange(-20,20);self.shift.setSuffix(' px');edges.addWidget(self.shift)
        self.feather.valueChanged.connect(self.refresh);self.shift.valueChanged.connect(self.refresh);self.halo.toggled.connect(self.refresh)
        self.status=QLabel(tr('A imagem original só será alterada ao clicar em Aplicar.'));self.status.setWordWrap(True);layout.addWidget(self.status)
        self.progress=QProgressBar();self.progress.hide();layout.addWidget(self.progress)
        self.buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel)
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setText(tr('Aplicar recorte'))
        self.buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(tr('Cancelar'))
        self.buttons.accepted.connect(self.accept);self.buttons.rejected.connect(self.reject);layout.addWidget(self.buttons)
        self.refresh()

    def snapshot(self):
        entry=(self.alpha.copy(),self.keep.copy(),self.erase.copy());size=sum(a.nbytes for a in entry)
        self.history.append(entry);self.history_bytes+=size
        while len(self.history)>1 and (len(self.history)>12 or self.history_bytes>128*1024*1024):
            self.history_bytes-=sum(a.nbytes for a in self.history.pop(0))
        self.undo.setEnabled(True)

    def undo_edit(self):
        if not self.history:return
        self.alpha,self.keep,self.erase=self.history.pop();self.history_bytes-=sum(a.nbytes for a in (self.alpha,self.keep,self.erase));self.refresh()

    def reset_mask(self):
        self.snapshot();self.alpha.fill(255);self.keep.fill(0);self.erase.fill(0);self.refresh()

    def original_toggled(self,checked):
        self.view.last=None
        self.view.setCursor(Qt.CursorShape.ArrowCursor if checked else Qt.CursorShape.CrossCursor)
        self.view.update()

    def set_mode(self,mode):
        self.original_view.setChecked(False)
        self.view.last=None;self.view.mode=mode
    def set_background(self,color):self.background=color;self.view.update()
    def toggle_zoom(self):
        self.preview_zoom=1 if self.preview_zoom is None else None
        self.view.pan=QPointF();self.view.update()

    def paint_mark(self,start,end):
        target,other=(self.keep,self.erase) if self.view.mode=='keep' else (self.erase,self.keep)
        width=self.brush.value()
        cv2.line(target,start,end,255,width);cv2.circle(target,end,width//2,255,-1)
        cv2.line(other,start,end,0,width);cv2.circle(other,end,width//2,0,-1)
        self.refresh()

    def magic(self,point):
        tolerance=self.tolerance.value();contiguous=self.contiguous.isChecked()
        self.start_job(lambda progress,cancel: ('magic',magic_region(self.rgba[:,:,:3],point,tolerance,contiguous)))

    def detect_border(self):
        tolerance=self.tolerance.value()
        self.start_job(lambda progress,cancel:border_alpha(self.rgba,tolerance))

    def refine_marked(self):
        alpha=self.alpha.copy();keep=self.keep.copy();erase=self.erase.copy()
        self.start_job(lambda progress,cancel:grabcut_alpha(self.rgba,alpha,keep,erase))

    def detect_ai(self):
        if not model_path().exists():
            self.status.setText(tr('Baixando modelo local (~220 MB). Depois do download, suas imagens são processadas neste computador.'))
            self.start_job(lambda progress,cancel:('model',download_model(progress,cancel)),download=True)
        else:self.start_job(lambda progress,cancel:ai_alpha(self.rgba))

    def start_job(self,function,download=False):
        if self.worker is not None:return
        self.original_view.setChecked(False)
        self.set_busy(True);self.worker=SegmentationJob(function,self)
        self.worker.result.connect(self.job_result);self.worker.failed.connect(self.job_error)
        self.worker.progress.connect(self.job_progress);self.worker.finished.connect(self.job_finished)
        if not download:self.status.setText(tr('Processando localmente… você pode cancelar sem alterar a imagem.'))
        self.worker.start()

    def set_busy(self,busy):
        for widget in (self.auto,self.ai,self.refine,self.reset,self.undo,self.view,self.feather,self.shift,self.halo,self.original_view):widget.setEnabled(not busy)
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(not busy)
        self.progress.setRange(0,0);self.progress.setVisible(busy)

    def job_progress(self,value):
        if value>=0:self.progress.setRange(0,100);self.progress.setValue(value)

    def job_result(self,value):
        if self._closing:return
        if isinstance(value,tuple) and value[0]=='model':
            self.ai.setText(tr('Detectar com IA'));self.status.setText(tr('Modelo pronto. Clique em Detectar com IA para criar a prévia.'));return
        self.snapshot()
        if isinstance(value,tuple):
            region=value[1];self.alpha[region]=0
        else:self.alpha=value
        self.refresh();self.status.setText(tr('Prévia pronta. Confira em fundo branco e escuro; marque Manter / Apagar para corrigir e use Refinar.'))

    def job_error(self,message):
        if not self._closing:self.status.setText(tr('Não foi possível concluir: '+message+' A imagem original foi preservada.'))

    def job_finished(self):
        worker=self.worker;self.worker=None
        if worker is not None:worker.deleteLater()
        self.set_busy(False);self.undo.setEnabled(bool(self.history))
        if self._closing:super().reject()

    def refresh(self,*args):
        result=compose(self.rgba,self.alpha,self.keep,self.erase,self.feather.value(),self.shift.value(),self.halo.isChecked())
        self.output=image_from_rgba(result);self.view.set_image(self.output)
        marks=np.zeros_like(self.rgba);marks[self.keep>0]=(70,220,130,95);marks[self.erase>0]=(240,80,100,95)
        self.mark_image=image_from_rgba(marks);self.undo.setEnabled(bool(self.history))

    def accept(self):
        if self.worker and self.worker.isRunning():return
        self.refresh();super().accept()

    def reject(self):
        if self.worker and self.worker.isRunning():
            self._closing=True;self.worker.requestInterruption();self.status.setText(tr('Cancelando… aguardando a tarefa local terminar.'));return
        super().reject()

    def closeEvent(self,event):
        if self.worker and self.worker.isRunning():event.ignore();self.reject()
        else:super().closeEvent(event)
