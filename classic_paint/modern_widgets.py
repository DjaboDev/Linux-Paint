"""Clean font previews and symbolic text options, independent of platform icons."""
from PySide6.QtCore import Qt,QRectF,QSize
from PySide6.QtGui import QFont,QPainter,QPen,QColor,QPixmap,QIcon,QPalette
from PySide6.QtWidgets import QStyledItemDelegate

class FontPreviewDelegate(QStyledItemDelegate):
    def sizeHint(self,option,index):return QSize(280,34)
    def paint(self,painter,option,index):
        from PySide6.QtWidgets import QStyle
        selected=bool(option.state & QStyle.StateFlag.State_Selected)
        painter.save()
        painter.fillRect(option.rect,option.palette.color(QPalette.ColorRole.Highlight if selected else QPalette.ColorRole.Base))
        painter.setPen(option.palette.color(QPalette.ColorRole.HighlightedText if selected else QPalette.ColorRole.Text))
        family=str(index.data(Qt.ItemDataRole.DisplayRole));font=QFont(family);font.setPixelSize(14);painter.setFont(font)
        painter.drawText(option.rect.adjusted(12,0,-12,0),Qt.AlignmentFlag.AlignVCenter,family)
        painter.restore()

def text_background_icon(opaque,dark):
    pix=QPixmap(18,18);pix.fill(Qt.GlobalColor.transparent);p=QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    fg=QColor('#eeeeec' if dark else '#303030')
    if opaque:p.fillRect(1,1,16,16,QColor('#eeeeec' if dark else '#303030'))
    else:
        p.setPen(QPen(fg,1,Qt.PenStyle.DotLine));p.drawRect(1,1,15,15)
    font=QFont();font.setPixelSize(13);font.setBold(True);p.setFont(font)
    p.setPen(QColor('#303030' if dark else '#eeeeec') if opaque else fg)
    p.drawText(QRectF(1,1,16,16),Qt.AlignmentFlag.AlignCenter,'A');p.end();return QIcon(pix)


from PySide6.QtWidgets import QProxyStyle,QStyle
class ModernStyle(QProxyStyle):
    def __init__(self):super().__init__('Fusion')
    def standardIcon(self,icon,option=None,widget=None):
        if icon in (QStyle.StandardPixmap.SP_MessageBoxInformation,QStyle.StandardPixmap.SP_MessageBoxQuestion,QStyle.StandardPixmap.SP_MessageBoxWarning,QStyle.StandardPixmap.SP_MessageBoxCritical):return QIcon(self.standardPixmap(icon,option,widget))
        return super().standardIcon(icon,option,widget)
    def standardPixmap(self,icon,option=None,widget=None):
        icons={QStyle.StandardPixmap.SP_MessageBoxInformation:('i','#3584e4'),QStyle.StandardPixmap.SP_MessageBoxQuestion:('?','#3584e4'),QStyle.StandardPixmap.SP_MessageBoxWarning:('!','#c88800'),QStyle.StandardPixmap.SP_MessageBoxCritical:('!','#c01c28')}
        if icon not in icons:return super().standardPixmap(icon,option,widget)
        symbol,color=icons[icon];pix=QPixmap(40,40);pix.fill(Qt.GlobalColor.transparent)
        p=QPainter(pix);p.setRenderHint(QPainter.RenderHint.Antialiasing);p.setPen(QPen(QColor(color),2));p.setBrush(Qt.BrushStyle.NoBrush);p.drawEllipse(QRectF(3,3,34,34))
        font=QFont();font.setPixelSize(25);font.setBold(True);p.setFont(font);p.drawText(QRectF(3,2,34,34),Qt.AlignmentFlag.AlignCenter,symbol);p.end();return pix
