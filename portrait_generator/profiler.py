"""
Biometric facial feature extraction and structured profiling engine.
Produces standardized cranial, facial, and chromatic profiles for accurate AI reproduction.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class SubjectProfile(BaseModel):
    """Complete biometric and facial profile of a portrait subject."""

    subject_name: str = "Subject"
    face_shape: str = "Oval-to-oblong contour with balanced facial thirds"
    jaw_chin: str = "Structured mandibular line with rounded-square chin"
    forehead_temples: str = "Broad forehead with smooth brow line and gentle temple taper"
    cheekbones: str = "Softly defined zygomatic structure providing natural mid-face depth"
    eye_geometry: str = "Almond-shaped, deep-set, dark brown irises with calm direct gaze"
    eyebrows: str = "Well-defined natural arch with medium density tapering at temples"
    orbital_features: str = "Clean upper eyelid crease with natural lower orbital shading"
    nasal_profile: str = "Straight dorsal bridge with distinct masculine prominence"
    nasal_tip: str = "Proportional rounded tip with balanced alar width"
    lips: str = "Full proportional lips with defined vermilion borders and subtle cupid's bow"
    smile_teeth: str = "Authentic warm smile displaying clean upper dental alignment"
    neutral_expression: str = "Poised, calm, confident, and direct"
    beard_style: str = "Tailored short-boxed beard (~3-5mm) covering jaw and chin"
    mustache: str = "Neatly trimmed mustache connecting softly to beard line"
    hair: str = "Jet black, textured short crop with faded/tapered sides and back"
    fitzpatrick_scale: str = "Type IV-V (Warm golden-olive South Asian skin tone)"
    surface_quality: str = "Healthy natural skin texture with subtle specular highlights"
    reference_crops: List[str] = Field(default_factory=list)

    def to_compact_prompt_description(self) -> str:
        """Compiles key facial attributes into a concise prompt token for generation."""
        tokens = [
            f"{self.subject_name}",
            f"{self.face_shape.lower()}",
            f"{self.eye_geometry.lower()}",
            f"{self.hair.lower()}",
            f"{self.beard_style.lower()}" if self.beard_style else "",
            f"{self.fitzpatrick_scale.lower()}",
            "authentic facial likeness and natural facial proportions",
        ]
        return ", ".join(t for t in tokens if t)

    def to_markdown(self) -> str:
        """Formats the profile into a high-fidelity markdown report."""
        crops_section = ""
        if self.reference_crops:
            crops_list = "\n".join(f"- `{crop}`" for crop in self.reference_crops)
            crops_section = f"\n---\n\n## Calibrated Reference Crops Prepared\n{crops_list}\n"

        return f"""# {self.subject_name} - Biometric & Facial Feature Extraction Profile

## 1. Craniofacial & Head Geometry
- **Face Shape**: {self.face_shape}
- **Jaw & Chin**: {self.jaw_chin}
- **Forehead & Temples**: {self.forehead_temples}
- **Cheekbones**: {self.cheekbones}

## 2. Eyes & Brows
- **Eye Geometry**: {self.eye_geometry}
- **Eyebrows**: {self.eyebrows}
- **Orbital Features**: {self.orbital_features}

## 3. Nose Architecture
- **Nasal Profile**: {self.nasal_profile}
- **Tip & Base**: {self.nasal_tip}

## 4. Mouth, Lips & Expression
- **Lips**: {self.lips}
- **Smile & Teeth**: {self.smile_teeth}
- **Neutral Expression**: {self.neutral_expression}

## 5. Facial Hair & Grooming
- **Beard Style**: {self.beard_style}
- **Mustache**: {self.mustache}
- **Hair**: {self.hair}

## 6. Complexion & Tone
- **Fitzpatrick Type**: {self.fitzpatrick_scale}
- **Surface Quality**: {self.surface_quality}
{crops_section}"""


class BiometricProfiler:
    """Manages creation, parsing, and export of subject facial profiles."""

    @classmethod
    def create_profile(
        cls,
        subject_name: str,
        custom_attributes: Optional[Dict[str, str]] = None,
        reference_crops: Optional[List[str]] = None,
    ) -> SubjectProfile:
        """Creates a new SubjectProfile with optional attribute overrides."""
        attrs = custom_attributes or {}
        profile = SubjectProfile(
            subject_name=subject_name,
            reference_crops=reference_crops or [],
            **attrs,
        )
        return profile

    @classmethod
    def save_markdown(cls, profile: SubjectProfile, output_path: Union[str, Path]) -> Path:
        """Saves a profile to a markdown file."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(profile.to_markdown(), encoding="utf-8")
        return path

    @classmethod
    def load_markdown(cls, input_path: Union[str, Path]) -> SubjectProfile:
        """Parses a saved markdown profile back into a SubjectProfile object."""
        path = Path(input_path)
        content = path.read_text(encoding="utf-8")

        # Extract subject name
        title_match = re.search(r"^#\s+(.+?)\s+-\s+Biometric", content, re.MULTILINE)
        subject_name = title_match.group(1).strip() if title_match else path.stem

        # Extract key-value pairs
        data: Dict[str, str] = {}
        mappings = {
            "Face Shape": "face_shape",
            "Jaw & Chin": "jaw_chin",
            "Forehead & Temples": "forehead_temples",
            "Cheekbones": "cheekbones",
            "Eye Geometry": "eye_geometry",
            "Eyebrows": "eyebrows",
            "Orbital Features": "orbital_features",
            "Nasal Profile": "nasal_profile",
            "Tip & Base": "nasal_tip",
            "Lips": "lips",
            "Smile & Teeth": "smile_teeth",
            "Neutral Expression": "neutral_expression",
            "Beard Style": "beard_style",
            "Mustache": "mustache",
            "Hair": "hair",
            "Fitzpatrick Type": "fitzpatrick_scale",
            "Surface Quality": "surface_quality",
        }

        for label, attr_name in mappings.items():
            pattern = rf"-\s+\*\*{re.escape(label)}\*\*:\s*(.+)$"
            match = re.search(pattern, content, re.MULTILINE)
            if match:
                data[attr_name] = match.group(1).strip()

        # Extract reference crops
        crops = []
        crop_matches = re.findall(r"^-\s+`([^`]+)`", content, re.MULTILINE)
        if crop_matches:
            crops = crop_matches

        return SubjectProfile(
            subject_name=subject_name,
            reference_crops=crops,
            **data,
        )
