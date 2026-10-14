import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import time,unittest,tempfile
import numpy as np
from PySide6.QtWidgets import QApplication,QColorDialog,QMessageBox
from PySide6.QtCore import Qt,QPoint,QSettings
from PySide6.QtGui import QPalette
from PySide6.QtTest import QTest
from classic_paint.app import PaintWindow
from classic_paint.cutout import image_from_rgba,rgba_from_image
from classic_paint.cutout_dialog import BackgroundDialog

APP=QApplication.instance() or QApplication([])
APP.setStyle('Fusion')
CACHE=tempfile.TemporaryDirectory()
QSettings.setDefaultFormat(QSettings.Format.IniFormat)
QSettings.setPath(QSettings.Format.IniFormat,QSettings.Scope.UserScope,CACHE.name)
QSettings.setPath(QSettings.Format.NativeFormat,QSettings.Scope.UserScope,CACHE.name)

class DialogTests(unittest.TestCase):
    def setUp(self):
        self.w=PaintWindow();self.w.set_dark_mode(True);self.w.show();APP.processEvents()
    def tearDown(self):
        self.w.dirty=False;self.w.close();APP.processEvents()
    def wait_job(self,dialog):
        until=time.monotonic()+20
        while dialog.worker and dialog.worker.isRunning() and time.monotonic()<until:
            APP.processEvents();QTest.qWait(10)
        APP.processEvents()
        self.assertFalse(dialog.worker and dialog.worker.isRunning())
    def test_dark_palette_reaches_message_and_color_dialogs(self):
        for dialog in (QMessageBox(self.w),QColorDialog(self.w)):
            self.assertLess(dialog.palette().color(QPalette.ColorRole.Window).lightness(),100)
            self.assertGreater(dialog.palette().color(QPalette.ColorRole.Text).lightness(),150)
        self.w.set_dark_mode(False)
        self.assertGreater(QColorDialog(self.w).palette().color(QPalette.ColorRole.Window).lightness(),200)
    def test_theme_switch_repaints_every_ribbon_page(self):
        self.w.resize(1800,900)
        for dark in (False,True,False):
            self.w.set_dark_mode(dark)
            for tab in range(3):
                self.w.select_tab(tab);APP.processEvents()
                image=self.w.ribbon.grab().toImage()
                surface=image.pixelColor(image.width()-20,30).lightness()
                self.assertLess(surface,80) if dark else self.assertGreater(surface,210)
                text=self.w.rulers_checkbox.palette().color(QPalette.ColorRole.WindowText).lightness()
                self.assertGreater(text,180) if dark else self.assertLess(text,80)

    def test_open_starts_at_current_user_home(self):
        from pathlib import Path
        from unittest.mock import patch
        with patch('classic_paint.app.QFileDialog.getOpenFileName',return_value=('', '')) as chooser:
            self.w.open_file()
        self.assertEqual(chooser.call_args.args[2],str(Path.home()))

    def test_size_arrows_change_value_in_both_themes(self):
        for dark in (True,False):
            self.w.set_dark_mode(dark);self.w.set_width(12)
            spin=self.w.size_spinbox;spin.window().show();APP.processEvents()
            QTest.mouseClick(spin.increase,Qt.MouseButton.LeftButton)
            self.assertEqual(spin.value(),13)
            QTest.mouseClick(spin.decrease,Qt.MouseButton.LeftButton)
            self.assertEqual(spin.value(),12)
            spin.window().hide()

    def test_modern_alert_escape_preserves_unsaved_image(self):
        from classic_paint.modern_widgets import ModernAlert
        dialog=ModernAlert(self.w,'Unsaved image','Save changes?',
            QMessageBox.StandardButton.Save|QMessageBox.StandardButton.Discard|QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save)
        dialog.show();APP.processEvents()
        self.assertTrue(dialog.windowFlags() & Qt.WindowType.FramelessWindowHint)
        self.assertTrue(dialog.responses[QMessageBox.StandardButton.Save].isDefault())
        self.assertTrue(all(button.icon().isNull() for button in dialog.responses.values()))
        QTest.keyClick(dialog,Qt.Key.Key_Escape)
        self.assertEqual(dialog.response,QMessageBox.StandardButton.Cancel)

    def test_modern_alert_keeps_standard_responses(self):
        from classic_paint.modern_widgets import ModernAlert
        for response in (QMessageBox.StandardButton.Save,QMessageBox.StandardButton.Discard):
            dialog=ModernAlert(self.w,'Unsaved image','Save changes?',
                QMessageBox.StandardButton.Save|QMessageBox.StandardButton.Discard|QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save)
            dialog.show();APP.processEvents()
            QTest.mouseClick(dialog.responses[response],Qt.MouseButton.LeftButton)
            self.assertEqual(dialog.response,response)

    def test_cutout_header_is_added_once_and_action_is_highlighted(self):
        from PySide6.QtWidgets import QLabel,QDialogButtonBox
        dialog=BackgroundDialog(self.w.canvas.image,self.w)
        for _ in range(2):
            dialog.show();APP.processEvents();dialog.hide()
        self.assertEqual(len(dialog.findChildren(QLabel,'DialogHeading')),1)
        apply=dialog.buttons.button(QDialogButtonBox.StandardButton.Ok)
        self.assertTrue(apply.property('suggested'))
        self.assertTrue(apply.icon().isNull())
        self.assertGreaterEqual(dialog.feather.height(),36)
        dialog.reject()

    def test_numeric_buttons_respect_bounds_and_keyboard(self):
        from classic_paint.modern_widgets import ModernSpinBox
        spin=ModernSpinBox(self.w);spin.setRange(0,2);spin.show();APP.processEvents()
        self.assertFalse(spin.decrease.isEnabled())
        QTest.mouseClick(spin.increase,Qt.MouseButton.LeftButton)
        self.assertEqual(spin.value(),1)
        QTest.keyClick(spin,Qt.Key.Key_Up)
        self.assertEqual(spin.value(),2)
        self.assertFalse(spin.increase.isEnabled())
        spin.close()

    def test_distinct_brush_previews_and_eraser_options(self):
        seen=[]
        for style in ('Round','Square','Airbrush'):
            self.w.set_brush_style(style);APP.processEvents()
            im=self.w.tool_buttons['brush'].grab().toImage();seen.append(bytes(im.constBits()))
            self.assertEqual(self.w.canvas.tool,'brush')
        self.assertEqual(len(set(seen)),3)
        self.w.set_eraser_shape('square');self.assertEqual(self.w.canvas.tool,'eraser')
        self.assertEqual(self.w.canvas.eraser_shape,'square')
        self.w.set_width(180);self.assertEqual(self.w.size_slider.value(),180)
    def test_soft_eraser_has_alpha_falloff_and_width_matches_controls(self):
        from classic_paint.app import blank
        from PySide6.QtGui import QColor
        canvas=self.w.canvas;canvas.image=blank(100,100,QColor('red'))
        self.w.set_width(30);self.w.set_eraser_shape('round')
        canvas.hardness=0;canvas.right_button=True;canvas.draw_stroke(QPoint(50,50),QPoint(50,50))
        self.assertLess(canvas.image.pixelColor(50,50).alpha(),30)
        self.assertGreater(canvas.image.pixelColor(60,50).alpha(),100)
        self.assertEqual(canvas.image.pixelColor(70,50).alpha(),255)

    def test_resize_feedback_exists_outside_original_canvas(self):
        canvas=self.w.canvas;w,h=canvas.image.width(),canvas.image.height()
        QTest.mousePress(canvas,Qt.MouseButton.LeftButton,pos=QPoint(w+1,h+1))
        QTest.mouseMove(canvas,QPoint(w+70,h+45));APP.processEvents()
        self.assertTrue(self.w.scroll.resize_overlay.isVisible())
        self.assertEqual(self.w.scroll.resize_overlay.target,(w+69,h+44))
        QTest.mouseRelease(canvas,Qt.MouseButton.LeftButton,pos=QPoint(w+70,h+45))
        self.assertFalse(self.w.scroll.resize_overlay.isVisible())
        self.assertEqual(canvas.image.width(),w+69)
    def test_cutout_is_preview_only_until_accept_and_undo_restores_editor(self):
        array=np.full((100,140,4),255,np.uint8);array[20:80,40:100,:3]=(90,30,120)
        self.w.canvas.set_image(image_from_rgba(array),remember=False)
        before=self.w.canvas.image.copy()
        dialog=BackgroundDialog(before,self.w);dialog.show();APP.processEvents()
        dialog.magic((0,0));self.wait_job(dialog)
        self.assertEqual(rgba_from_image(dialog.output)[0,0,3],0)
        self.assertEqual(self.w.canvas.image,before)
        dialog.undo_edit();self.assertEqual(rgba_from_image(dialog.output)[0,0,3],255)
        dialog.magic((0,0));self.wait_job(dialog);dialog.accept()
        self.w.canvas.set_image(dialog.output)
        self.assertEqual(self.w.canvas.image.pixelColor(0,0).alpha(),0)
        self.w.canvas.undo();self.assertEqual(self.w.canvas.image,before)
    def test_original_comparison_before_and_after_detection_is_read_only(self):
        source=np.full((100,140,4),255,np.uint8);source[20:80,40:100,:3]=(90,30,120)
        dialog=BackgroundDialog(image_from_rgba(source),self.w);dialog.show();APP.processEvents()
        dialog.original_view.setChecked(True);APP.processEvents()
        point=dialog.view.bounds.topLeft()+QPoint(4,4)
        QTest.mouseClick(dialog.view,Qt.MouseButton.LeftButton,pos=point.toPoint())
        self.assertIsNone(dialog.worker)
        self.assertFalse(dialog.history)
        dialog.detect_border();self.wait_job(dialog)
        self.assertFalse(dialog.original_view.isChecked())
        preview=dialog.output.copy();dialog.original_view.setChecked(True);APP.processEvents()
        original=dialog.view.grab().toImage()
        dialog.original_view.setChecked(False);APP.processEvents()
        result=dialog.view.grab().toImage()
        self.assertNotEqual(original,result)
        self.assertEqual(dialog.output,preview)
        self.assertTrue(np.array_equal(dialog.rgba,source))
        dialog.reject()

    def test_magic_selection_feather_and_manual_corrections(self):
        source=np.full((100,140,4),255,np.uint8);source[20:80,40:100,:3]=(90,30,120)
        dialog=BackgroundDialog(image_from_rgba(source),self.w)
        dialog.magic((0,0));self.wait_job(dialog)
        dialog.feather.setValue(4)
        alpha=rgba_from_image(dialog.output)[:,:,3]
        self.assertTrue(np.any((alpha>0)&(alpha<255)))
        self.assertFalse(np.any(dialog.erase))
        dialog.set_mode('keep');dialog.brush.setValue(1);dialog.snapshot();dialog.paint_mark((2,2),(2,2))
        self.assertEqual(np.count_nonzero(dialog.keep),1)
        self.assertEqual(rgba_from_image(dialog.output)[2,2,3],255)
        dialog.set_mode('erase');dialog.snapshot();dialog.paint_mark((2,2),(2,2))
        self.assertEqual(dialog.keep[2,2],0)
        self.assertEqual(rgba_from_image(dialog.output)[2,2,3],0)
        dialog.undo_edit();self.assertEqual(dialog.keep[2,2],255)
        before=dialog.output.copy();dialog.reset_mask();dialog.undo_edit()
        self.assertEqual(dialog.output,before)
        dialog.reject()

    def test_job_failure_and_model_download_restore_controls_without_history(self):
        dialog=BackgroundDialog(self.w.canvas.image,self.w)
        before=dialog.output.copy()
        def failure(progress,cancel):raise RuntimeError('test failure')
        dialog.start_job(failure);self.wait_job(dialog)
        self.assertIn('test failure',dialog.status.text())
        self.assertEqual(dialog.output,before)
        self.assertFalse(dialog.history)
        self.assertTrue(dialog.auto.isEnabled())
        dialog.start_job(lambda progress,cancel:('model','test model'),download=True)
        self.wait_job(dialog)
        self.assertFalse(dialog.history)
        self.assertEqual(dialog.output,before)
        self.assertIsNone(dialog.worker)
        dialog.reject()

    def test_refine_marks_and_zoom_do_not_change_original(self):
        source=np.full((100,140,4),255,np.uint8);source[20:80,40:100,:3]=(90,30,120)
        dialog=BackgroundDialog(image_from_rgba(source),self.w);dialog.show();APP.processEvents()
        dialog.detect_border();self.wait_job(dialog)
        dialog.brush.setValue(5);dialog.set_mode('keep');dialog.snapshot();dialog.paint_mark((60,50),(65,50))
        dialog.set_mode('erase');dialog.snapshot();dialog.paint_mark((5,5),(10,5))
        dialog.refine_marked();self.wait_job(dialog)
        self.assertEqual(rgba_from_image(dialog.output)[50,60,3],255)
        self.assertEqual(rgba_from_image(dialog.output)[5,5,3],0)
        preview=dialog.output.copy();dialog.toggle_zoom();APP.processEvents()
        self.assertAlmostEqual(dialog.view.scale,1,places=4)
        dialog.preview_zoom=20;dialog.view.update();APP.processEvents()
        dialog.view.grab()
        self.assertEqual(dialog.output,preview)
        self.assertTrue(np.array_equal(dialog.rgba,source))
        dialog.reject()

    def test_cancel_during_job_never_changes_source(self):
        before=self.w.canvas.image.copy();dialog=BackgroundDialog(before,self.w);dialog.show()
        dialog.start_job(lambda progress,cancel:(time.sleep(.05),np.zeros((before.height(),before.width()),np.uint8))[1])
        dialog.reject();self.wait_job(dialog)
        self.assertEqual(dialog.result(),0);self.assertEqual(self.w.canvas.image,before)

if __name__=='__main__':unittest.main()
