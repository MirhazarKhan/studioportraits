"""
Configuration and Environment Settings for Portrait Generator.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Literal
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load local environment variables from .env if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseModel):
    """Global configuration settings for the pipeline."""

    base_dir: Path = Field(default=BASE_DIR)
    inputs_dir: Path = Field(default=BASE_DIR / "inputs")
    outputs_dir: Path = Field(default=BASE_DIR / "outputs")
    templates_dir: Path = Field(default=BASE_DIR / "templates")

    # API Keys (optional; pipeline can export prompts or run locally)
    gemini_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY"))
    openai_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    stability_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("STABILITY_API_KEY"))

    # Default backend provider
    default_provider: Literal["gemini", "openai", "stability", "export"] = Field(
        default_factory=lambda: os.getenv("PORTRAIT_PROVIDER", "export")  # type: ignore
    )

    # Image specs
    default_resolution: tuple[int, int] = (1024, 1024)
    save_format: Literal["JPEG", "PNG", "WEBP"] = "JPEG"
    jpeg_quality: int = 95

    class Config:
        arbitrary_types_allowed = True


# Singleton instance
Config = Settings()
