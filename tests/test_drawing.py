import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import unittest
import numpy as np
from PySide6.QtCore import QPoint,Qt
from PySide6.QtGui import QColor
from PySide6.QtTest import QTest
from tests import test_dialog
APP=test_dialog.APP
from classic_paint.app import blank,SHAPE_TOOLS
from classic_paint.cutout import rgba_from_image

class DrawingTests(unittest.TestCase):
    setUp=test_dialog.DialogTests.setUp
    tearDown=test_dialog.DialogTests.tearDown
    def prepare(self,tool,width=12,hardness=100):
        c=self.w.canvas;c.image=blank(180,180,Qt.GlobalColor.transparent)
        c.before=c.image.copy();c.start=QPoint(45,45);c.primary=QColor('#ac2080')
        c.secondary=QColor('#2080ac');c.right_button=False;c.outline=True;c.fill=False
        c.stroke_width=width;c.hardness=hardness;c.tool=tool
        return c
    def test_pencil_uses_width_and_does_not_inherit_brush_shape(self):
        footprints=[]
        for width in (1,8,20):
            c=self.prepare('pencil',width);c.draw_stroke(QPoint(40,90),QPoint(130,90))
            alpha=rgba_from_image(c.image)[:,:,3];footprints.append(np.count_nonzero(alpha[:,90]))
        self.assertEqual(footprints,[1,8,20])
        images=[]
        for style in ('Round','Square','Airbrush'):
            c=self.prepare('pencil',12);c.brush_style=style
            c.draw_stroke(QPoint(90,90),QPoint(90,90));images.append(rgba_from_image(c.image))
        for image in images[1:]:np.testing.assert_array_equal(images[0],image)
    def test_one_pixel_pencil_also_obeys_hardness(self):
        results=[]
        for hardness in (100,0):
            c=self.prepare('pencil',1,hardness);c.draw_stroke(QPoint(90,90),QPoint(90,90))
            results.append(rgba_from_image(c.image)[:,:,3])
        self.assertEqual(results[0].max(),255);self.assertLess(results[1].max(),255)
        self.assertFalse(np.array_equal(*results))
    def test_pencil_and_all_shapes_obey_hardness(self):
        for tool in ('pencil',)+SHAPE_TOOLS+('trapezoid',):
            results=[]
            for hardness in (100,0):
                c=self.prepare(tool,12,hardness);c.antialias=False
                if tool=='pencil':c.draw_stroke(QPoint(45,90),QPoint(130,90))
                else:c.draw_shape(QPoint(130,130))
                results.append(rgba_from_image(c.image))
            with self.subTest(tool=tool):
                self.assertFalse(np.array_equal(*results))
                alpha=results[1][:,:,3]
                self.assertTrue(np.any((alpha>0)&(alpha<255)))
    def test_soft_shape_preserves_existing_pixels_and_paint_color(self):
        c=self.prepare('rectangle',12,0);c.image.setPixelColor(5,5,QColor('yellow'))
        c.before=c.image.copy();c.draw_shape(QPoint(130,130));pixels=rgba_from_image(c.image)
        self.assertEqual(c.image.pixelColor(5,5),QColor('yellow'))
        edge=pixels[40,90];self.assertGreater(edge[3],0);self.assertLess(edge[3],255)
        np.testing.assert_array_equal(edge[:3],[172,32,128])
        first=c.image.copy();c.draw_shape(QPoint(130,130));self.assertEqual(c.image,first)
    def test_feather_does_not_create_an_edge_at_canvas_boundary(self):
        c=self.prepare('rectangle',12,0);c.start=QPoint(-40,-40);c.fill=True;c.outline=False
        c.draw_shape(QPoint(220,220))
        self.assertEqual(c.image.pixelColor(0,0),c.secondary)
        self.assertEqual(c.image.pixelColor(179,179),c.secondary)
    def test_soft_shape_undo_and_redo_restore_exact_pixels(self):
        c=self.prepare('ellipse',12,0);original=c.image.copy()
        QTest.mousePress(c,Qt.MouseButton.LeftButton,pos=QPoint(40,40))
        QTest.mouseMove(c,QPoint(130,130))
        QTest.mouseRelease(c,Qt.MouseButton.LeftButton,pos=QPoint(130,130))
        drawn=c.image.copy();self.assertNotEqual(drawn,original)
        c.undo();self.assertEqual(c.image,original)
        c.redo();self.assertEqual(c.image,drawn)
    def test_airbrush_hardness_changes_falloff(self):
        import random
        results=[]
        for hardness in (100,0):
            random.seed(42);c=self.prepare('brush',12,hardness);c.brush_style='Airbrush'
            c.draw_stroke(QPoint(90,90),QPoint(90,90));results.append(rgba_from_image(c.image)[:,:,3])
        self.assertFalse(np.array_equal(*results));self.assertLess(results[1].sum(),results[0].sum())
    def test_right_button_swaps_outline_and_fill(self):
        c=self.prepare('rectangle');c.fill=True;c.right_button=True
        c.draw_shape(QPoint(130,130));self.assertEqual(c.image.pixelColor(90,90),c.primary)
        self.assertEqual(c.image.pixelColor(45,90),c.secondary)
    def test_keyboard_width_updates_ribbon_and_reaches_200(self):
        self.w.set_width(80)
        QTest.keyClick(self.w.canvas,Qt.Key.Key_BracketRight)
        self.assertEqual(self.w.canvas.stroke_width,81);self.assertEqual(self.w.size_spinbox.value(),81)
        self.assertEqual(self.w.size_slider.value(),81)
        QTest.keyClick(self.w.canvas,Qt.Key.Key_BracketLeft)
        self.assertEqual(self.w.size_spinbox.value(),80)
        self.w.set_width(200);self.w.canvas.change_width(1);self.assertEqual(self.w.size_slider.value(),200)

if __name__=='__main__':unittest.main()
