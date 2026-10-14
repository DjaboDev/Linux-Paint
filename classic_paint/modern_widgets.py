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
