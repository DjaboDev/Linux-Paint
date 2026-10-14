"""Clean font previews and symbolic text options, independent of platform icons."""
from PySide6.QtCore import Qt,QRectF,QSize,QObject,QEvent
from PySide6.QtGui import QFont,QPainter,QPen,QColor,QPixmap,QIcon,QPalette
from PySide6.QtWidgets import (QStyledItemDelegate, QDialog, QMessageBox,
    QSpinBox, QAbstractSpinBox, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QToolButton, QDialogButtonBox, QColorDialog)
from .i18n import tr


class NumericSteppers(QObject):
    """Shared steppers for application fields and Qt's built-in color fields."""
    def __init__(self, spin):
        super().__init__(spin)
        self.spin = spin
        spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        spin.setMinimumSize(124, 36)
        spin.setProperty('modernSpin', True)
        self.decrease = QToolButton(spin)
        self.increase = QToolButton(spin)
        for button, text, step, label in (
                (self.decrease, '−', -1, tr('Diminuir valor')),
                (self.increase, '+', 1, tr('Aumentar valor'))):
            button.setText(text)
            button.setAccessibleName(label)
            button.setToolTip(label)
            button.setObjectName('NumericStepper')
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            button.setAutoRepeat(True)
            button.clicked.connect(lambda checked=False, s=step: spin.stepBy(s))
        spin.valueChanged.connect(self.update_steps)
        spin.installEventFilter(self)

    def update_steps(self, *args):
        steps = self.spin.stepEnabled()
        self.decrease.setEnabled(bool(steps & QAbstractSpinBox.StepEnabledFlag.StepDownEnabled))
        self.increase.setEnabled(bool(steps & QAbstractSpinBox.StepEnabledFlag.StepUpEnabled))

    def eventFilter(self, watched, event):
        if event.type() in (QEvent.Type.Resize, QEvent.Type.Show):
            self.decrease.setGeometry(self.spin.width()-60, 3, 28, self.spin.height()-6)
            self.increase.setGeometry(self.spin.width()-31, 3, 28, self.spin.height()-6)
            self.update_steps()
        return False


class ModernSpinBox(QSpinBox):
    """Readable horizontal steppers, preserving Qt's numeric/keyboard behavior."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.steppers = NumericSteppers(self)
        self.decrease = self.steppers.decrease
        self.increase = self.steppers.increase


class ModernDialog(QDialog):
    """Action dialog with an internal header and application-owned controls."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setModal(True)
        self.setObjectName('ModernDialog')
        self._header_added = False

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and event.position().y() < 76:
            if self.windowHandle() and self.windowHandle().startSystemMove():
                event.accept()
                return
        QDialog.mousePressEvent(self, event)

    def prepare_header(self):
        if not self._header_added and self.layout() is not None:
            layout = self.layout()
            layout.setContentsMargins(24, 20, 24, 24)
            layout.setSpacing(16)
            header = QHBoxLayout()
            heading = QLabel(self.windowTitle())
            heading.setObjectName('DialogHeading')
            heading.setWordWrap(True)
            header.addWidget(heading, 1)
            buttons = self.findChildren(QDialogButtonBox)
            if buttons:
                box = buttons[-1]
                box.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
                for button in box.buttons():
                    button.setIcon(QIcon())
                    button.setMinimumHeight(36)
                    if box.buttonRole(button) in (QDialogButtonBox.ButtonRole.AcceptRole, QDialogButtonBox.ButtonRole.YesRole):
                        button.setProperty('suggested', True)
                    button.style().unpolish(button)
                    button.style().polish(button)
                layout.removeWidget(box)
                header.addWidget(box)
            else:
                close = QToolButton()
                close.setText('×')
                close.setAccessibleName(tr('Fechar janela'))
                close.clicked.connect(self.reject)
                header.addWidget(close)
            if isinstance(layout, QVBoxLayout):
                layout.insertLayout(0, header)
            else:
                # Form dialogs reserve the first spanning row for their header.
                layout.insertRow(0, header)
            self._header_added = True

    def showEvent(self, event):
        self.prepare_header()
        super().showEvent(event)


class ModernColorDialog(QColorDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.steppers = [NumericSteppers(spin) for spin in self.findChildren(QSpinBox)]
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setObjectName('ModernDialog')
        self._header_added = False

    def showEvent(self, event):
        ModernDialog.prepare_header(self)
        super().showEvent(event)

    def mousePressEvent(self, event):
        ModernDialog.mousePressEvent(self, event)

    @staticmethod
    def getColor(initial=QColor('white'), parent=None, title='', options=QColorDialog.ColorDialogOption.DontUseNativeDialog):
        dialog = ModernColorDialog(parent)
        dialog.setOptions(options | QColorDialog.ColorDialogOption.DontUseNativeDialog)
        dialog.setCurrentColor(initial)
        dialog.setWindowTitle(tr(title))
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.selectedColor()
        return QColor()


class ModernAlert(QDialog):
    """Modal alert with explicit safe dismissal and unchanged standard responses."""
    def __init__(self, parent, title, text, buttons, default):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setWindowTitle(title)
        self.setObjectName('ModernDialog')
        self.setModal(True)
        self.response = QMessageBox.StandardButton.Cancel if buttons & QMessageBox.StandardButton.Cancel else QMessageBox.StandardButton.NoButton
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 24)
        layout.setSpacing(20)
        heading = QLabel(title)
        heading.setObjectName('DialogHeading')
        heading.setWordWrap(True)
        heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(heading)
        body = QLabel(text)
        body.setWordWrap(True)
        body.setOpenExternalLinks(True)
        body.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(body)
        row = QHBoxLayout()
        row.setSpacing(10)
        layout.addLayout(row)
        labels = ((QMessageBox.StandardButton.Discard, 'Descartar alterações'),
                  (QMessageBox.StandardButton.No, 'Não'),
                  (QMessageBox.StandardButton.Cancel, 'Cancelar'),
                  (QMessageBox.StandardButton.Yes, 'Continuar'),
                  (QMessageBox.StandardButton.Save, 'Salvar'),
                  (QMessageBox.StandardButton.Ok, 'OK'))
        self.responses = {}
        for response, label in labels:
            if buttons & response:
                button = QPushButton(tr(label))
                button.setMinimumHeight(40)
                button.setProperty('destructive', response == QMessageBox.StandardButton.Discard)
                button.setProperty('suggested', response == default and response != QMessageBox.StandardButton.Cancel)
                button.setAutoDefault(False)
                button.setDefault(response == default)
                button.clicked.connect(lambda checked=False, r=response: self.choose(r))
                row.addWidget(button)
                self.responses[response] = button
        self.setFixedWidth(460 if len(self.responses) >= 3 else 420)

    def choose(self, response):
        self.response = response
        self.accept()


class ModernMessageBox:
    StandardButton = QMessageBox.StandardButton

    @staticmethod
    def question(parent, title, text, buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                 defaultButton=QMessageBox.StandardButton.No):
        dialog = ModernAlert(parent, title, text, buttons, defaultButton)
        dialog.exec()
        return dialog.response

    @staticmethod
    def warning(parent, title, text):
        return ModernMessageBox.question(parent, title, text, QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Ok)

    @staticmethod
    def about(parent, title, text):
        return ModernMessageBox.warning(parent, title, text)

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
    def styleHint(self, hint, option=None, widget=None, returnData=None):
        if hint == QStyle.StyleHint.SH_DialogButtonBox_ButtonsHaveIcons:
            return 0
        return super().styleHint(hint, option, widget, returnData)
    def standardIcon(self,icon,option=None,widget=None):
        if icon in (QStyle.StandardPixmap.SP_MessageBoxInformation,QStyle.StandardPixmap.SP_MessageBoxQuestion,QStyle.StandardPixmap.SP_MessageBoxWarning,QStyle.StandardPixmap.SP_MessageBoxCritical):return QIcon(self.standardPixmap(icon,option,widget))
        return super().standardIcon(icon,option,widget)
    def standardPixmap(self,icon,option=None,widget=None):
        icons={QStyle.StandardPixmap.SP_MessageBoxInformation:('i','#3584e4'),QStyle.StandardPixmap.SP_MessageBoxQuestion:('?','#3584e4'),QStyle.StandardPixmap.SP_MessageBoxWarning:('!','#c88800'),QStyle.StandardPixmap.SP_MessageBoxCritical:('!','#c01c28')}
        if icon not in icons:return super().standardPixmap(icon,option,widget)
        symbol,color=icons[icon];pix=QPixmap(40,40);pix.fill(Qt.GlobalColor.transparent)
        p=QPainter(pix);p.setRenderHint(QPainter.RenderHint.Antialiasing);p.setPen(QPen(QColor(color),2));p.setBrush(Qt.BrushStyle.NoBrush);p.drawEllipse(QRectF(3,3,34,34))
        font=QFont();font.setPixelSize(25);font.setBold(True);p.setFont(font);p.drawText(QRectF(3,2,34,34),Qt.AlignmentFlag.AlignCenter,symbol);p.end();return pix
