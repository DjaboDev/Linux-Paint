import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import tempfile,unittest
from pathlib import Path
from PySide6.QtCore import QSettings
from tests import test_dialog
from classic_paint.app import PaintWindow,blank

class PersistenceTests(unittest.TestCase):
    def test_normal_and_maximized_state_survive_reopen(self):
        settings=QSettings('ClassicPaint','ClassicPaint');settings.remove('geometry');settings.remove('window/maximized')
        w=PaintWindow();w.show();w.showNormal();w.resize(820,480);test_dialog.APP.processEvents()
        size=w.size();w.dirty=False;w.close()
        reopened=PaintWindow();reopened.show();test_dialog.APP.processEvents()
        self.assertFalse(reopened.isMaximized());self.assertEqual(reopened.size(),size)
        reopened.showMaximized();test_dialog.APP.processEvents();reopened.dirty=False;reopened.close()
        maximized=PaintWindow();maximized.show();test_dialog.APP.processEvents();self.assertTrue(maximized.isMaximized())
        maximized.showNormal();maximized.dirty=False;maximized.close()
    def test_open_directory_remembers_successful_file_and_falls_back(self):
        settings=QSettings('ClassicPaint','ClassicPaint');settings.remove('files/open_directory')
        w=PaintWindow();self.assertEqual(w.open_directory(),Path.home())
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'sample.png';blank(20,20).save(str(path))
            self.assertTrue(w.load_file_from_path(path));w.dirty=False;w.close()
            w=PaintWindow();self.assertEqual(w.open_directory(),Path(folder))
            self.assertFalse(w.load_file_from_path(Path(folder)/'missing.png'))
            self.assertEqual(w.open_directory(),Path(folder))
        self.assertEqual(w.open_directory(),Path.home());w.dirty=False;w.close()
if __name__=='__main__':unittest.main()
