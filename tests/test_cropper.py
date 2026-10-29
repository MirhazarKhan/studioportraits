"""
Unit tests for FaceCropper and aspect ratio calculations.
"""

import tempfile
import unittest
from pathlib import Path
from PIL import Image

from portrait_generator.cropper import FaceCropper, CropConfig


class TestFaceCropper(unittest.TestCase):
    def setUp(self):
        self.cropper = FaceCropper()

    def test_aspect_ratios_defined(self):
        self.assertIn("1:1", self.cropper.ASPECT_RATIOS)
        self.assertIn("4:5", self.cropper.ASPECT_RATIOS)
        self.assertIn("9:16", self.cropper.ASPECT_RATIOS)
        self.assertIn("passport_us", self.cropper.ASPECT_RATIOS)
        self.assertIn("passport_eu", self.cropper.ASPECT_RATIOS)

    def test_calculate_crop_box_square(self):
        left, top, right, bottom = self.cropper.calculate_crop_box(1000, 2000, None, "1:1")
        width = right - left
        height = bottom - top
        self.assertEqual(width, height)
        self.assertTrue(0 <= left <= right <= 1000)
        self.assertTrue(0 <= top <= bottom <= 2000)

    def test_calculate_crop_box_portrait_4_5(self):
        left, top, right, bottom = self.cropper.calculate_crop_box(1600, 2000, None, "4:5")
        width = right - left
        height = bottom - top
        ratio = width / height
        self.assertAlmostEqual(ratio, 4.0 / 5.0, places=2)

    def test_crop_single_execution(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            test_img = Image.new("RGB", (800, 1200), color=(100, 150, 200))
            test_file = tmp_path / "test_input.jpg"
            test_img.save(test_file)

            out_file = tmp_path / "test_output.jpg"
            config = CropConfig(aspect_ratio="1:1", detect_face=False)
            result = self.cropper.crop_single(test_file, out_file, config=config)

            self.assertTrue(result.success)
            self.assertTrue(out_file.exists())
            with Image.open(out_file) as saved:
                self.assertEqual(saved.size, (1024, 1024))



if __name__ == "__main__":
    unittest.main()
