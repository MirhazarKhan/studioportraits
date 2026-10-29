"""
Unit tests for PromptEngine and style presets.
"""

import unittest
from portrait_generator.profiler import SubjectProfile
from portrait_generator.prompt_engine import PromptEngine


class TestPromptEngine(unittest.TestCase):
    def setUp(self):
        self.engine = PromptEngine()

    def test_prompt_engine_loads_presets(self):
        styles = self.engine.list_styles()
        self.assertIn("tlou2", styles)
        self.assertIn("vinyl_toy_tan", styles)
        self.assertIn("studio_monochrome", styles)

    def test_compile_prompt(self):
        profile = SubjectProfile(subject_name="Jordan Cole")
        compiled = self.engine.compile("tlou2", profile)

        self.assertEqual(compiled.style_id, "tlou2")
        self.assertIn("Jordan Cole", compiled.positive_prompt)
        self.assertIn("The Last of Us Part II", compiled.positive_prompt)
        self.assertEqual(compiled.aspect_ratio, "4:5")
        self.assertEqual(compiled.cfg_scale, 7.5)

    def test_to_midjourney_command(self):
        profile = SubjectProfile(subject_name="Jordan Cole")
        compiled = self.engine.compile("vinyl_toy_tan", profile)

        mj_cmd = compiled.to_midjourney_command()
        self.assertTrue(mj_cmd.startswith("/imagine prompt:"))
        self.assertIn("--ar 1:1", mj_cmd)
        self.assertIn("--v 6.1", mj_cmd)

    def test_to_comfyui_dict(self):
        profile = SubjectProfile(subject_name="Jordan Cole")
        compiled = self.engine.compile("tlou2", profile)

        data = compiled.to_comfyui_dict()
        self.assertIn("positive", data)
        self.assertIn("negative", data)
        self.assertIn("cfg", data)
        self.assertIn("steps", data)


if __name__ == "__main__":
    unittest.main()
