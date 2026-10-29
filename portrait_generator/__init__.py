"""
Portrait Generator
==================
An open-source AI portrait generation pipeline and biometric calibration toolkit.
Extract multi-angle facial crops, build biometric profiles, and synthesize
stunning cinematic, editorial, and stylized portraits.
"""

__version__ = "1.0.0"
__author__ = "Portrait Generator Open Source Contributors"
__license__ = "MIT"

from portrait_generator.config import Config, Settings
from portrait_generator.cropper import FaceCropper, CropConfig, CropResult
from portrait_generator.profiler import BiometricProfiler, SubjectProfile
from portrait_generator.prompt_engine import PromptEngine, StylePreset
from portrait_generator.generator import PortraitGenerator

__all__ = [
    "Config",
    "Settings",
    "FaceCropper",
    "CropConfig",
    "CropResult",
    "BiometricProfiler",
    "SubjectProfile",
    "PromptEngine",
    "StylePreset",
    "PortraitGenerator",
]
