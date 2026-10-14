"""Functional regression and QHD render of the actual Qt application."""
import os
import tempfile
os.environ['QT_QPA_PLATFORM']='offscreen'
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QPoint, Qt, QSettings
from PySide6.QtTest import QTest
from classic_paint.app import PaintWindow
from classic_paint.modern_ui import APP_ID, application_icon

app=QApplication([])
app.setApplicationName('LinuxPaint');app.setDesktopFileName(APP_ID)
app.setStyle('Fusion');app.setWindowIcon(application_icon())
# Isolate saved geometry/theme from the user's preferences.
settings_dir=tempfile.TemporaryDirectory()
QSettings.setDefaultFormat(QSettings.Format.IniFormat)
QSettings.setPath(QSettings.Format.IniFormat,QSettings.Scope.UserScope,settings_dir.name)
QSettings.setPath(QSettings.Format.NativeFormat,QSettings.Scope.UserScope,settings_dir.name)
w=PaintWindow();assert w.dark_mode
w.resize(2560,1440);w.show();app.processEvents()
assert w.header_bar.title_box.geometry().center().x() == w.header_bar.width()//2-1
assert w.ribbon_controls['colors'].geometry().right()<1280
assert not w.windowIcon().isNull()
assert app.desktopFileName()==APP_ID
# Choose pencil via ribbon, draw, undo, redo via unified header.
QTest.mouseClick(w.tool_buttons['pencil'],Qt.MouseButton.LeftButton)
assert w.canvas.tool=='pencil'
before=w.canvas.image.copy()
QTest.mousePress(w.canvas,Qt.MouseButton.LeftButton,pos=QPoint(40,40))
QTest.mouseMove(w.canvas,QPoint(80,80))
QTest.mouseRelease(w.canvas,Qt.MouseButton.LeftButton,pos=QPoint(80,80))
assert w.canvas.image!=before
painted=w.canvas.image.copy()
QTest.mouseClick(w.header_bar.undo_btn,Qt.MouseButton.LeftButton)
assert w.canvas.image==before
QTest.mouseClick(w.header_bar.redo_btn,Qt.MouseButton.LeftButton)
assert w.canvas.image==painted
assert w.header_bar.undo_btn.icon().cacheKey()==w.actions['undo'].icon().cacheKey()
# Color palette and all shape buttons still select real drawing tools.
QTest.mouseClick(w.ribbon_controls['swatch3'],Qt.MouseButton.LeftButton)
assert w.canvas.primary==w.ribbon_controls['swatch3'].color
for key in ('ellipse','rectangle','star','arrow','brush'):
    QTest.mouseClick(w.tool_buttons[key],Qt.MouseButton.LeftButton,pos=QPoint(10,10))
    assert w.canvas.tool==key
w.set_dark_mode(False);app.processEvents();assert not w.dark_mode
w.set_dark_mode(True)
w.select_tab(1);app.processEvents();assert w.ribbon.currentIndex()==1
w.select_tab(2);app.processEvents();assert w.ribbon.currentIndex()==2
w.select_tab(0);w.canvas.set_image(before);w.set_tool('brush')
for width in (820,1360,2560):
    w.resize(width,1440 if width==2560 else 720);app.processEvents()
    assert w.header_bar.close_btn.geometry().right()<w.header_bar.width()
    assert w.ribbon_scroll.height()>=108
w.grab().save(str(Path(__file__).parent/'screenshots'/'linux-paint-modern-qhd.png'))
print('PASS: drawing, undo/redo, colors, shapes, themes, tabs, 820/1360/2560 layouts, app identity and QHD render')
