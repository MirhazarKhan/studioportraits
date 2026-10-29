"""
Prompt synthesis engine and style preset compiler.
Translates biometric profile characteristics into calibrated generation prompts.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional, Any
from pydantic import BaseModel, Field

from portrait_generator.config import Config
from portrait_generator.profiler import SubjectProfile


class StylePreset(BaseModel):
    """Style configuration for a portrait archetype."""

    id: str = "custom"
    name: str
    description: str
    prompt_template: str
    negative_prompt: str = ""
    recommended_aspect_ratio: str = "1:1"
    cfg_scale: float = 7.0
    steps: int = 35


class CompiledPrompt(BaseModel):
    """Result of prompt compilation."""

    style_id: str
    style_name: str
    positive_prompt: str
    negative_prompt: str
    aspect_ratio: str
    cfg_scale: float
    steps: int

    def to_midjourney_command(self) -> str:
        """Formats prompt as a ready-to-use Midjourney command."""
        # Convert aspect ratio format (e.g. 4:5)
        ar = self.aspect_ratio.replace("_", ":")
        if ar in ("passport_us", "passport_eu"):
            ar = "1:1" if ar == "passport_us" else "4:5"
        return f"/imagine prompt: {self.positive_prompt} --ar {ar} --v 6.1 --style raw --c 5"

    def to_comfyui_dict(self) -> Dict[str, Any]:
        """Formats prompt metadata for ComfyUI / Stable Diffusion pipelines."""
        return {
            "positive": self.positive_prompt,
            "negative": self.negative_prompt,
            "cfg": self.cfg_scale,
            "steps": self.steps,
            "aspect_ratio": self.aspect_ratio,
        }


class PromptEngine:
    """Compiles prompts using presets and subject biometric profiles."""

    def __init__(self, presets_path: Optional[Path] = None):
        self.presets_path = presets_path or (Config.templates_dir / "style_presets.json")
        self.presets: Dict[str, StylePreset] = {}
        self.load_presets()

    def load_presets(self) -> None:
        """Loads presets from the JSON template or falls back to built-in presets."""
        if self.presets_path.exists():
            try:
                data = json.loads(self.presets_path.read_text(encoding="utf-8"))
                for pid, pdata in data.items():
                    self.presets[pid] = StylePreset(id=pid, **pdata)
                return
            except Exception:
                pass

        # Fallback default presets if file unavailable
        self.presets = {
            "tlou2": StylePreset(
                id="tlou2",
                name="The Last of Us Part II Survivalist",
                description="Cinematic post-pandemic chiaroscuro portrait with tactical jacket and dust lighting.",
                prompt_template="Hyper-realistic cinematic character portrait of {subject_name}, {biometric_description}. Setting inspired by The Last of Us Part II aesthetic, wearing weathered tactical jacket, chiaroscuro lighting, volumetric dust particles, 85mm lens, 8k.",
                negative_prompt="cartoon, 3d, airbrushed, plastic, lowres",
                recommended_aspect_ratio="4:5",
            ),
            "vinyl_toy_tan": StylePreset(
                id="vinyl_toy_tan",
                name="3D Minimalist Vinyl Toy Avatar",
                description="Designer collectible vinyl art toy with matte clay finish.",
                prompt_template="Designer 3D vinyl art toy collectible figurine of {subject_name}, {biometric_description}. Cute minimalist proportions, smooth matte tan finish, lightbox illumination, octane render, 8k.",
                negative_prompt="photorealistic human, uncanny valley, pores, real skin",
                recommended_aspect_ratio="1:1",
            ),
        }

    def list_styles(self) -> Dict[str, StylePreset]:
        """Returns all available style presets."""
        return self.presets

    def get_style(self, style_id: str) -> Optional[StylePreset]:
        """Retrieves a specific style preset by identifier."""
        return self.presets.get(style_id)

    def compile(
        self,
        style_id: str,
        profile: SubjectProfile,
        custom_negative: Optional[str] = None,
        custom_aspect_ratio: Optional[str] = None,
    ) -> CompiledPrompt:
        """
        Compiles a complete generation prompt using the specified style preset
        and subject biometric profile.
        """
        preset = self.get_style(style_id)
        if not preset:
            raise ValueError(f"Unknown style ID: '{style_id}'. Available: {list(self.presets.keys())}")

        biometric_desc = profile.to_compact_prompt_description()
        positive = preset.prompt_template.format(
            subject_name=profile.subject_name,
            biometric_description=biometric_desc,
        )

        negative = custom_negative or preset.negative_prompt
        ar = custom_aspect_ratio or preset.recommended_aspect_ratio

        return CompiledPrompt(
            style_id=preset.id,
            style_name=preset.name,
            positive_prompt=positive,
            negative_prompt=negative,
            aspect_ratio=ar,
            cfg_scale=preset.cfg_scale,
            steps=preset.steps,
        )
