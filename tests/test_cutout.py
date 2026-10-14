import unittest
import numpy as np
import cv2
from classic_paint.cutout import (magic_region,border_alpha,grabcut_alpha,compose,
                                 image_from_rgba,rgba_from_image)

class CutoutTests(unittest.TestCase):
    def setUp(self):
        self.rgba=np.full((120,160,4),255,np.uint8)
        cv2.rectangle(self.rgba,(45,25),(115,95),(90,40,140,255),-1)
        cv2.circle(self.rgba,(80,60),10,(255,255,255,255),-1)

    def test_connected_magic_preserves_disconnected_same_color(self):
        region=magic_region(self.rgba[:,:,:3],(0,0),0)
        self.assertTrue(region[0,0]);self.assertFalse(region[60,80])
        self.assertTrue(magic_region(self.rgba[:,:,:3],(0,0),0,False)[60,80])

    def test_edges_keep_subject_and_enclosed_detail(self):
        alpha=border_alpha(self.rgba,12)
        self.assertEqual(alpha[0,0],0);self.assertEqual(alpha[30,50],255)
        self.assertEqual(alpha[60,80],255)
        self.assertTrue(np.array_equal(compose(self.rgba,alpha)[:,:,:3],self.rgba[:,:,:3]))

    def test_existing_transparency_and_soft_alpha_never_become_opaque(self):
        self.rgba[0,0,3]=0;self.rgba[1,1,3]=70
        alpha=np.full(self.rgba.shape[:2],128,np.uint8)
        keep=np.zeros(alpha.shape,np.uint8);keep[0,0]=keep[1,1]=255
        result=compose(self.rgba,alpha,keep)
        self.assertEqual(result[0,0,3],0);self.assertEqual(result[1,1,3],70)
        self.assertEqual(result[5,5,3],128)

    def test_manual_corrections_override_feather_and_are_reversible(self):
        alpha=border_alpha(self.rgba,12);keep=np.zeros(alpha.shape,np.uint8);erase=keep.copy()
        keep[2,2]=255;erase[30,50]=255
        result=compose(self.rgba,alpha,keep,erase,feather=3,shift=2)
        self.assertEqual(result[2,2,3],255);self.assertEqual(result[30,50,3],0)
        self.assertTrue(np.any((result[:,:,3]>0)&(result[:,:,3]<255)))

    def test_grabcut_respects_keep_and_erase_marks(self):
        alpha=border_alpha(self.rgba,12);keep=np.zeros(alpha.shape,np.uint8);erase=keep.copy()
        keep[60,80]=255;erase[0:5,:]=255
        refined=grabcut_alpha(self.rgba,alpha,keep,erase)
        self.assertEqual(refined[60,80],255);self.assertEqual(refined[1,1],0)
        self.assertGreater(np.mean(refined[30:90,50:110]>128),.95)

    def test_qimage_roundtrip_preserves_rgba_and_odd_width_stride(self):
        array=self.rgba[:,:157].copy();array[0,0]=(10,20,30,40)
        self.assertTrue(np.array_equal(rgba_from_image(image_from_rgba(array)),array))

    def test_halo_removal_keeps_rgb_interior_and_transparent_input(self):
        source=np.full((5,5,4),255,np.uint8)
        source[2,2,:3]=(177,127,127)  # red subject blended 50% against white
        mask=np.zeros((5,5),np.uint8);mask[2,2]=128
        result=compose(source,mask,decontaminate=True)
        self.assertLess(int(result[2,2,1]),5)
        self.assertLess(int(result[2,2,2]),5)
        self.assertGreater(int(result[2,2,0]),95)
        source[2,2,3]=128
        result=compose(source,mask,decontaminate=True)
        self.assertTrue(np.array_equal(result[2,2,:3],source[2,2,:3]))

    def test_edges_preserve_subject_touching_the_image_boundary(self):
        source=np.full((120,160,4),255,np.uint8)
        source[:90,60:100,:3]=(90,40,140)
        alpha=border_alpha(source,12)
        self.assertEqual(alpha[0,80],255)
        self.assertEqual(alpha[60,80],255)
        self.assertEqual(alpha[0,0],0)

    def test_transparent_border_never_removes_opaque_subject(self):
        source=np.zeros((60,80,4),np.uint8)
        source[10:50,20:60]=(100,30,150,255)
        alpha=border_alpha(source,12)
        self.assertEqual(alpha[30,40],255)
        self.assertEqual(compose(source,alpha)[0,0,3],0)

    def test_shift_expands_and_contracts_in_the_expected_direction(self):
        alpha=np.zeros((30,30),np.uint8);alpha[10:20,10:20]=255
        source=np.full((30,30,4),255,np.uint8)
        area=lambda shift:np.count_nonzero(compose(source,alpha,shift=shift)[:,:,3])
        self.assertLess(area(-2),area(0));self.assertGreater(area(2),area(0))

    def test_invalid_click_has_clear_error(self):
        with self.assertRaises(ValueError):magic_region(self.rgba[:,:,:3],(-1,4),20)

if __name__=='__main__':unittest.main()
