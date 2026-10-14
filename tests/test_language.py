import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import unittest
from PySide6.QtCore import QLocale
from tests import test_dialog
from classic_paint.app import PaintWindow
from classic_paint.cutout_dialog import BackgroundDialog
from classic_paint.i18n import tr

class LanguageTests(unittest.TestCase):
    def test_system_locale_controls_editor_and_cutout(self):
        previous=QLocale()
        try:
            for locale,open_label,opaque,cutout in [('en_US','Open…','Opaque','Remove background'),('pt_BR','Abrir…','Opaco','Remover fundo'),('de_DE','Open…','Opaque','Remove background')]:
                QLocale.setDefault(QLocale(locale));w=PaintWindow()
                self.assertEqual(w.actions['open'].text(),open_label)
                self.assertEqual(w.text_background['Opaque'].text(),opaque)
                dialog=BackgroundDialog(w.canvas.image,w)
                self.assertEqual(dialog.windowTitle(),cutout)
                w.set_tool('rectangle');w.set_fill_style(True)
                checked=[a.text() for a in w.fill_menu.actions() if a.isChecked()]
                self.assertEqual(checked,[tr('Solid color')])
                w.set_eraser_shape('square')
                self.assertEqual(w.canvas.eraser_shape,'square')
                dialog.reject();w.dirty=False;w.close()
        finally:QLocale.setDefault(previous)
if __name__=='__main__':unittest.main()
