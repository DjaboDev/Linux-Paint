from .i18n import tr
"""Original symbolic ribbon artwork and Linux desktop identity."""
from pathlib import Path
import math
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPen, QPolygonF, QConicalGradient, QPalette
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QApplication, QWidget

APP_ID = "io.github.DjaboDev.LinuxPaint"

def application_icon():
    return QIcon(str(Path(__file__).parent / "assets" / "linux-paint.png"))

# Hand-authored symbolic SVG paths: no captured Windows artwork.
GLYPHS = {
    "brush_round": '<path d="M10 14L18 3q3-2 3 1l-8 12z"/><path d="M10 14q-6 1-6 7q8 1 9-5z" fill="currentColor"/>',
    "brush_square": '<path d="M10 14L18 3q3-2 3 1l-8 12z"/><path d="M10 13l5 4-4 5-6-5z" fill="currentColor"/>',
    "brush_airbrush": '<path d="M8 9h9v5H8z M13 9V5h4 M11 14v7h4v-7 M17 11h4"/><circle cx="4" cy="8" r=".7"/><circle cx="3" cy="12" r=".7"/><circle cx="4" cy="16" r=".7"/><circle cx="1" cy="10" r=".5"/><circle cx="1" cy="14" r=".5"/>',
    "background": '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M4 17l6-7 5 5 4-4 M6 3v3 M3 6h3 M17 18l4 3 M21 18l-4 3"/>',

    "save": '<rect x="4" y="3" width="16" height="18" rx="1"/><path d="M8 3v6h8V3 M8 21v-7h8v7"/>',
    "undo": '<path d="M8 4L3 9l5 5 M3 9h9q9 0 9 10"/>',
    "redo": '<path d="M16 4l5 5-5 5 M21 9h-9q-9 0-9 10"/>',
    "new": '<path d="M6 3h8l4 4v14H6z M14 3v5h4"/>',
    "open": '<path d="M3 7h7l3 3h8l-3 10H3z M3 7V4h7l3 3h7v3"/>',

    "document": '<path d="M6 3h8l4 4v14H6z M14 3v5h4"/>',
    "paste": '<rect x="5" y="5" width="14" height="16" rx="1"/><rect x="9" y="3" width="6" height="4" rx="1"/>',
    "copy": '<rect x="8" y="7" width="11" height="14" rx="1"/><path d="M15 7V3H4v14h4"/>',
    "cut": '<circle cx="6" cy="17" r="3"/><circle cx="18" cy="17" r="3"/><path d="M7 14L18 3 M17 14L6 3"/>',
    "crop": '<path d="M7 3v14h14 M3 7h14v14 M4 20L20 4"/>',
    "resize": '<rect x="4" y="4" width="16" height="16" rx="1"/><path d="M8 16L16 8 M10 8h6v6"/>',
    "rotate": '<path d="M6 8a8 8 0 1 1-1 9 M6 3v5H1"/>',
    "pencil": '<path d="M4 16L16 4l4 4L8 20H4z M13 7l4 4"/>',
    "bucket": '<path d="M4 13l9-9 8 8-9 9z M7 3l9 9 M3 14h17 M21 16q-4 5 0 5q4 0 0-5"/>',
    "eraser": '<path d="M3 14L13 4l8 8-9 9H9z M8 9l8 8 M12 21h10"/>',
    "picker": '<path d="M5 15L15 5l4 4L9 19l-5 1z M13 4l7 7 M16 3l5 5"/>',
    "magnifier": '<circle cx="10" cy="10" r="6"/><path d="M15 15l6 6"/>',
    "brush": '<path d="M10 14L18 3q3-2 3 1l-8 12z"/><path d="M10 14q-6 1-6 7q8 1 9-5z" fill="currentColor"/>',
    "outline": '<path d="M4 16L16 4l4 4L8 20H4z M13 7l4 4 M3 22h18"/>',
    "fill": '<path d="M4 13l9-9 8 8-9 9z M7 3l9 9 M3 14h17"/>',
    "line": '<path d="M3 21L21 3"/>',
    "curve": '<path d="M2 17C8 0 14 24 22 7"/>',
    "ellipse": '<ellipse cx="12" cy="12" rx="10" ry="7"/>',
    "rectangle": '<rect x="3" y="5" width="18" height="14"/>',
    "rounded": '<rect x="3" y="5" width="18" height="14" rx="4"/>',
    "triangle": '<path d="M12 2L22 21H2z"/>',
    "righttriangle": '<path d="M3 3L21 21H3z"/>',
    "diamond": '<path d="M12 2L22 12 12 22 2 12z"/>',
    "polygon": '<path d="M3 19V7l8 3 3-7 7 16z"/>',
    "speech": '<path d="M3 4h18v13h-8l-6 5v-5H3z"/>',
    "ovalspeech": '<path d="M8 19C-2 15 1 3 12 3s14 12 4 16l-8 3z"/>',
    "cloud": '<path d="M5 18C-1 15 2 9 6 9C5 2 15 1 17 7C24 5 25 16 20 18z"/>',
    "size": '<path d="M3 4h18 M3 9h18"/><path d="M3 15h18" stroke-width="3"/><path d="M3 21h18" stroke-width="4"/>',
    "gallery_up": '<path d="M7 15l5-5 5 5"/>',
    "gallery_down": '<path d="M7 10l5 5 5-5"/>',
    "gallery_more": '<path d="M7 8l5 5 5-5 M7 13l5 5 5-5"/>',
}

def glyph(painter, key, rect, color):
    if key == 'text':
        painter.save(); painter.setPen(QColor(color)); f=QFont('Cantarell'); f.setPixelSize(round(rect.height())); painter.setFont(f)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, tr('A')); painter.restore(); return
    body = GLYPHS.get(key)
    if key.startswith('arrow'):
        body='<path d="M2 8h12V3l8 9-8 9v-5H2z"/>'
        degrees={'arrow':0,'arrowleft':180,'arrowup':-90,'arrowdown':90}.get(key,0)
        body=f'<g transform="rotate({degrees} 12 12)">{body}</g>'
    if key in ('pentagon','hexagon','star4','star','star6'):
        n={'pentagon':5,'hexagon':6,'star4':4,'star':5,'star6':6}[key]
        star=key.startswith('star'); count=n*2 if star else n
        pts=[]
        for i in range(count):
            a=i*2*math.pi/count-math.pi/2; r=10 if not star or i%2==0 else 4.5
            pts.append(f'{12+r*math.cos(a):.2f},{12+r*math.sin(a):.2f}')
        body='<polygon points="'+' '.join(pts)+'"/>'
    if not body: body=GLYPHS['brush']
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><g fill="none" color="{color}" stroke="{color}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{body}</g></svg>'
    QSvgRenderer(svg.encode()).render(painter, rect)

LABELS={'paste':'Colar','cut':'Recortar','copy':'Copiar','select':'Selecionar','crop':'Crop','resize':'Redimensionar','rotate':'Girar','brush':'','outline':'Contorno','fill':'Preenchimento','size':'','color1':'Cor 1','color2':'Cor 2','colors':'Editar\ncores','background':'Remover\nfundo'}

def paint_button(button):
    p=QPainter(button); p.setRenderHint(QPainter.RenderHint.Antialiasing)
    dark=getattr(button.window(),'dark_mode',True)
    fg='#eeeeec' if dark else '#303030'
    key=getattr(button,'icon_key',button.text().lower())
    if key=='brush': key=getattr(button,'active_icon_key','brush_round')
    if hasattr(button,'twin'): key=getattr(button.twin,'icon_key',key)
    if not button.isEnabled(): p.setOpacity(.35)
    selected=button.isCheckable() and button.isChecked()
    if selected and key not in ('color1','color2') or button.isDown() or button.underMouse():
        p.setPen(QPen(QColor('#3584e4' if selected else '#505050'),1))
        p.setBrush(QColor(('#28558b' if dark else '#d3e5fa') if selected else ('#383838' if dark else '#e3e3e3')))
        p.drawRoundedRect(QRectF(button.rect()).adjusted(1,1,-1,-1),5,5)
    f=QFont('Cantarell'); f.setPixelSize(11);p.setFont(f);p.setPen(QColor(fg))
    w,h=button.width(),button.height()
    if button.color is not None or key in ('color1','color2'):
        r=QRectF(2,2,w-4,h-4) if key.startswith('swatch') else QRectF((w-32)/2,7,32,32)
        c=button.color or QColor('black' if key=='color1' else 'white')
        # Alpha colors show a small checkerboard rather than a fake white paint chip.
        p.save();p.setClipRect(r)
        for y in range(int(r.top()),int(r.bottom())+1,6):
            for x in range(int(r.left()),int(r.right())+1,6):
                p.fillRect(QRectF(x,y,6,6),QColor('#aaaaaa' if (x//6+y//6)%2 else '#eeeeee'))
        p.fillRect(r,c);p.restore();p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(QColor('#3584e4' if selected else '#777777'),2 if selected else 1));p.drawRoundedRect(r,2,2)
        if not key.startswith('swatch'):
            p.setPen(QColor(fg));p.drawText(QRectF(0,44,w,20),Qt.AlignmentFlag.AlignCenter,tr(LABELS[key]))
    elif key=='colors':
        grad=QConicalGradient(QPointF(w/2,23),0)
        for pos,col in [(0,'#ed5575'),(.17,'#e7be51'),(.34,'#68b977'),(.51,'#55c3bc'),(.68,'#727ee4'),(.85,'#be7bdc'),(1,'#ed5575')]:grad.setColorAt(pos,QColor(col))
        p.setPen(Qt.PenStyle.NoPen);p.setBrush(grad);p.drawEllipse(QRectF(w/2-15,8,30,30));p.setPen(QColor(fg))
        p.drawText(QRectF(0,42,w,32),Qt.AlignmentFlag.AlignCenter,tr(LABELS[key]))
    else:
        large=h>55; tiny=w<=30
        size=30 if large else (19 if tiny else 16)
        r=QRectF((w-size)/2,8 if large else (h-size)/2,size,size) if large or tiny else QRectF(5,(h-size)/2,size,size)
        if key=='select':
            p.setPen(QPen(QColor('#62a8ef'),1.5,Qt.PenStyle.DashLine));p.setBrush(Qt.BrushStyle.NoBrush);p.drawRect(r.adjusted(2,2,-2,-2))
        else: glyph(p,key,r,fg)
        if key in LABELS and LABELS[key]:
            p.setPen(QColor(fg))
            label_rect=QRectF(0,42,w,34) if large and '\n' in LABELS[key] else QRectF(0,44,w,18) if large else QRectF(26,0,w-27,h)
            p.drawText(label_rect,Qt.AlignmentFlag.AlignCenter if large else Qt.AlignmentFlag.AlignVCenter,tr(LABELS[key]))
        if button.menu() is not None and not key.startswith('gallery'):
            cy=h-10 if large else (h-4 if tiny else h/2);cx=w/2 if large else w-5
            p.setPen(QPen(QColor(fg),1.3));p.drawPolyline(QPolygonF([QPointF(cx-3,cy-2),QPointF(cx,cy+1),QPointF(cx+3,cy-2)]))
    if button.hasFocus():
        p.setPen(QPen(QColor('#62a8ef'),1,Qt.PenStyle.DotLine));p.setBrush(Qt.BrushStyle.NoBrush);p.drawRoundedRect(QRectF(button.rect()).adjusted(2,2,-2,-2),4,4)
    p.end()

def paint_groups(widget,groups):
    p=QPainter(widget); dark=getattr(widget.window(),'dark_mode',True)
    p.fillRect(widget.rect(),QColor('#282828' if dark else '#f0f0f0'))
    p.setPen(QColor('#414141' if dark else '#d0d0d0'))
    f=QFont('Cantarell');f.setPixelSize(11);p.setFont(f)
    for start,end,label in groups:
        p.setPen(QColor('#414141' if dark else '#d0d0d0'))
        if start:p.drawLine(start,8,start,widget.height()-8)
        p.setPen(QColor('#b8b8b8' if dark else '#626262'))
        p.drawText(QRectF(start,86,end-start,18),Qt.AlignmentFlag.AlignCenter,tr(label))
    p.setPen(QColor('#383838' if dark else '#d0d0d0'));p.drawLine(0,widget.height()-1,widget.width(),widget.height()-1);p.end()

HOME_GROUPS=[(0,123,'Área de transferência'),(123,298,'Imagem'),(298,389,'Ferramentas'),(389,452,'Pincéis'),(452,768,'Formas'),(768,830,'Espessura'),(830,1263,'Cores'),(1263,1350,'Recorte')]


def apply_palette(dark):
    """Keep native Qt dialogs and disabled text consistent with the window theme."""
    palette=QPalette()
    colors={'Window':'#282828','WindowText':'#eeeeec','Base':'#202020','AlternateBase':'#303030',
            'Text':'#eeeeec','Button':'#353535','ButtonText':'#eeeeec','Highlight':'#3584e4',
            'HighlightedText':'#ffffff','ToolTipBase':'#353535','ToolTipText':'#ffffff','Link':'#78aeed'} if dark else {
            'Window':'#f5f5f5','WindowText':'#303030','Base':'#ffffff','AlternateBase':'#eeeeee',
            'Text':'#303030','Button':'#e8e8e8','ButtonText':'#303030','Highlight':'#3584e4',
            'HighlightedText':'#ffffff','ToolTipBase':'#ffffff','ToolTipText':'#303030','Link':'#1c71d8'}
    for name,color in colors.items():palette.setColor(getattr(QPalette.ColorRole,name),QColor(color))
    for role in (QPalette.ColorRole.Text,QPalette.ColorRole.WindowText,QPalette.ColorRole.ButtonText):
        palette.setColor(QPalette.ColorGroup.Disabled,role,QColor('#929292' if dark else '#888888'))
    QApplication.instance().setPalette(palette)


class ResizeOverlay(QWidget):
    """Viewport overlay: canvas growth feedback must not be clipped by the canvas."""
    def __init__(self,workspace):
        super().__init__(workspace.viewport());self.workspace=workspace;self.target=None
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.hide()

    def set_target(self,target):
        self.target=target
        self.setGeometry(self.parentWidget().rect());self.setVisible(target is not None)
        self.raise_();self.update()

    def paintEvent(self,event):
        if self.target is None:return
        canvas=self.workspace.canvas
        origin=canvas.mapTo(self.parentWidget(),canvas.rect().topLeft())
        w,h=self.target
        rect=QRectF(origin.x(),origin.y(),w*canvas.zoom,h*canvas.zoom)
        p=QPainter(self);p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(QColor('#111111'),3));p.drawRect(rect)
        p.setPen(QPen(QColor('#8fc7ff'),1.5,Qt.PenStyle.DashLine));p.drawRect(rect)
        x=max(4,min(rect.right()-140,self.width()-150));y=max(4,min(rect.bottom()+8,self.height()-30))
        label=QRectF(x,y,140,24);p.fillRect(label,QColor('#28558b'))
        p.setPen(QColor('#ffffff'));p.drawText(label,Qt.AlignmentFlag.AlignCenter,tr(f'{w} × {h} px'));p.end()
