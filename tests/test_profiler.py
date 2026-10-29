"""
Unit tests for BiometricProfiler and SubjectProfile modeling.
"""

import tempfile
import unittest
from pathlib import Path
from portrait_generator.profiler import BiometricProfiler, SubjectProfile


class TestBiometricProfiler(unittest.TestCase):
    def test_subject_profile_defaults(self):
        profile = SubjectProfile(subject_name="Test Subject")
        self.assertEqual(profile.subject_name, "Test Subject")
        self.assertIn("contour", profile.face_shape.lower())
        self.assertIn("Type", profile.fitzpatrick_scale)

    def test_to_compact_prompt_description(self):
        profile = SubjectProfile(subject_name="Elena Vance", fitzpatrick_scale="Type III")
        desc = profile.to_compact_prompt_description()
        self.assertIn("Elena Vance", desc)
        self.assertIn("type iii", desc)
        self.assertIn("authentic facial likeness", desc)

    def test_markdown_save_and_load(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            profile = BiometricProfiler.create_profile(
                subject_name="Marcus Reed",
                custom_attributes={
                    "face_shape": "Angular square jaw with strong mandibular ramus",
                    "beard_style": "Heavy 5-day shadow stubble",
                    "fitzpatrick_scale": "Type II",
                },
                reference_crops=["frontal_01.jpg", "profile_02.jpg"],
            )

            out_file = tmp_path / "marcus_profile.md"
            saved_path = BiometricProfiler.save_markdown(profile, out_file)
            self.assertTrue(saved_path.exists())

            loaded = BiometricProfiler.load_markdown(saved_path)
            self.assertEqual(loaded.subject_name, "Marcus Reed")
            self.assertEqual(loaded.face_shape, "Angular square jaw with strong mandibular ramus")
            self.assertEqual(loaded.beard_style, "Heavy 5-day shadow stubble")
            self.assertEqual(loaded.fitzpatrick_scale, "Type II")
            self.assertIn("frontal_01.jpg", loaded.reference_crops)


if __name__ == "__main__":
    unittest.main()
