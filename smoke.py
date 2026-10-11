"""Verify Qt plugins, embedded artwork, and window initialization headlessly."""
import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from classic_paint.app import PaintWindow
app = QApplication([])
app.setStyle('Fusion')
window = PaintWindow()
window.show()
assert not window.canvas.image.isNull()
QTimer.singleShot(300, app.quit)
raise SystemExit(app.exec())
