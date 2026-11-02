"""
Portrait generation backend coordinator.
Supports multi-provider synthesis (Google GenAI, OpenAI, Stability) and prompt export.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel

from portrait_generator.config import Config
from portrait_generator.profiler import SubjectProfile
from portrait_generator.prompt_engine import PromptEngine, CompiledPrompt


class GenerationResult(BaseModel):
    """Result of portrait generation or export."""

    subject_name: str
    style_id: str
    style_name: str
    provider: str
    output_files: List[str]
    prompt_used: str
    negative_prompt_used: str
    metadata: Dict[str, Any]
    success: bool
    message: str


class PortraitGenerator:
    """Coordinates image generation and prompt export across providers."""

    def __init__(self, prompt_engine: Optional[PromptEngine] = None):
        self.engine = prompt_engine or PromptEngine()

    def export_prompt_bundle(
        self,
        compiled: CompiledPrompt,
        profile: SubjectProfile,
        output_dir: Union[str, Path],
        reference_images: Optional[List[str]] = None,
    ) -> GenerationResult:
        """
        Exports generation-ready prompt bundles (JSON, TXT, Midjourney) for
        external generation tools (ComfyUI, Midjourney, Automatic1111).
        """
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        clean_name = re.sub(r"[^\w\-]", "_", profile.subject_name.lower()).strip("_")
        bundle_base = out_path / f"{clean_name}_{compiled.style_id}"

        # 1. Save standard text prompt
        txt_file = out_path / f"{bundle_base.name}.txt"
        txt_content = (
            f"=== POSITIVE PROMPT ===\n{compiled.positive_prompt}\n\n"
            f"=== NEGATIVE PROMPT ===\n{compiled.negative_prompt}\n\n"
            f"=== MIDJOURNEY COMMAND ===\n{compiled.to_midjourney_command()}\n"
        )
        txt_file.write_text(txt_content, encoding="utf-8")

        # 2. Save structured JSON metadata
        json_file = out_path / f"{bundle_base.name}.json"
        json_data = {
            "subject": profile.subject_name,
            "style": compiled.style_id,
            "style_name": compiled.style_name,
            "aspect_ratio": compiled.aspect_ratio,
            "cfg_scale": compiled.cfg_scale,
            "steps": compiled.steps,
            "positive_prompt": compiled.positive_prompt,
            "negative_prompt": compiled.negative_prompt,
            "midjourney_command": compiled.to_midjourney_command(),
            "reference_images": reference_images or profile.reference_crops,
        }
        json_file.write_text(json.dumps(json_data, indent=2), encoding="utf-8")

        return GenerationResult(
            subject_name=profile.subject_name,
            style_id=compiled.style_id,
            style_name=compiled.style_name,
            provider="export",
            output_files=[str(txt_file), str(json_file)],
            prompt_used=compiled.positive_prompt,
            negative_prompt_used=compiled.negative_prompt,
            metadata=json_data,
            success=True,
            message=f"Prompt bundle successfully exported to {out_path}",
        )

    def generate(
        self,
        style_id: str,
        profile: SubjectProfile,
        output_dir: Union[str, Path],
        provider: Optional[str] = None,
        reference_images: Optional[List[str]] = None,
    ) -> GenerationResult:
        """
        Generates portrait image using configured API or exports prompt bundle.
        """
        selected_provider = provider or Config.default_provider
        compiled = self.engine.compile(style_id=style_id, profile=profile)
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)

        if selected_provider == "openai" and Config.openai_api_key:
            return self._generate_openai(compiled, profile, out_path)
        elif selected_provider == "gemini" and Config.gemini_api_key:
            return self._generate_gemini(compiled, profile, out_path)
        else:
            # Default export bundle
            return self.export_prompt_bundle(
                compiled, profile, out_path, reference_images=reference_images
            )

    def _generate_openai(
        self, compiled: CompiledPrompt, profile: SubjectProfile, output_dir: Path
    ) -> GenerationResult:
        """Generates image via OpenAI DALL-E 3 API."""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=Config.openai_api_key)

            size_map = {
                "1:1": "1024x1024",
                "4:5": "1024x1792",
                "9:16": "1024x1792",
                "16:9": "1792x1024",
            }
            img_size = size_map.get(compiled.aspect_ratio, "1024x1024")

            response = client.images.generate(
                model="dall-e-3",
                prompt=compiled.positive_prompt,
                size=img_size,  # type: ignore
                quality="hd",
                n=1,
            )
            image_url = response.data[0].url

            # Download and save
            import requests
            img_data = requests.get(image_url).content
            out_file = output_dir / f"{profile.subject_name.lower()}_{compiled.style_id}.jpg"
            out_file.write_bytes(img_data)

            return GenerationResult(
                subject_name=profile.subject_name,
                style_id=compiled.style_id,
                style_name=compiled.style_name,
                provider="openai",
                output_files=[str(out_file)],
                prompt_used=compiled.positive_prompt,
                negative_prompt_used=compiled.negative_prompt,
                metadata={"url": image_url},
                success=True,
                message="Successfully generated portrait via OpenAI DALL-E 3",
            )
        except Exception as e:
            return GenerationResult(
                subject_name=profile.subject_name,
                style_id=compiled.style_id,
                style_name=compiled.style_name,
                provider="openai",
                output_files=[],
                prompt_used=compiled.positive_prompt,
                negative_prompt_used=compiled.negative_prompt,
                metadata={},
                success=False,
                message=f"OpenAI generation failed: {e}",
            )

    def _generate_gemini(
        self, compiled: CompiledPrompt, profile: SubjectProfile, output_dir: Path
    ) -> GenerationResult:
        """Generates image via Google GenAI / Imagen 3."""
        try:
            from google import genai
            client = genai.Client(api_key=Config.gemini_api_key)
            result = client.models.generate_images(
                model="imagen-3.0-generate-002",
                prompt=compiled.positive_prompt,
                config=dict(
                    number_of_images=1,
                    aspect_ratio=compiled.aspect_ratio if compiled.aspect_ratio in ("1:1", "4:3", "3:4", "16:9", "9:16") else "1:1",
                    person_generation="ALLOW_ADULT",
                ),
            )
            out_file = output_dir / f"{profile.subject_name.lower()}_{compiled.style_id}.jpg"
            for generated_image in result.generated_images:
                out_file.write_bytes(generated_image.image.image_bytes)
                break

            return GenerationResult(
                subject_name=profile.subject_name,
                style_id=compiled.style_id,
                style_name=compiled.style_name,
                provider="gemini",
                output_files=[str(out_file)],
                prompt_used=compiled.positive_prompt,
                negative_prompt_used=compiled.negative_prompt,
                metadata={},
                success=True,
                message="Successfully generated portrait via Google Imagen 3",
            )
        except Exception as e:
            return GenerationResult(
                subject_name=profile.subject_name,
                style_id=compiled.style_id,
                style_name=compiled.style_name,
                provider="gemini",
                output_files=[],
                prompt_used=compiled.positive_prompt,
                negative_prompt_used=compiled.negative_prompt,
                metadata={},
                success=False,
                message=f"Gemini generation failed: {e}",
            )
