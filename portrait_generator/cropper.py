"""
Face cropping and multi-angle calibration engine.
Extracts normalized crops with standard aspect ratios and automatic orientation.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Tuple, List, Union
from pydantic import BaseModel, Field
from PIL import Image, ImageOps

CV2_AVAILABLE = False
try:
    import numpy as np
    import cv2
    CV2_AVAILABLE = True
except BaseException:
    CV2_AVAILABLE = False



class CropConfig(BaseModel):
    """Configuration options for cropping."""

    aspect_ratio: str = "1:1"  # "1:1", "4:5", "9:16", "3:2", "passport_us", "passport_eu"
    padding_factor: float = 0.5  # Extra headroom and shoulder buffer around face
    output_size: Optional[Tuple[int, int]] = (1024, 1024)
    quality: int = 95
    detect_face: bool = True


class CropResult(BaseModel):
    """Result of a cropping operation."""

    source_path: str
    output_path: str
    angle_label: str
    crop_box: Tuple[int, int, int, int]  # (left, top, right, bottom)
    aspect_ratio: str
    success: bool
    message: str = "Success"


class FaceCropper:
    """Intelligent face detection and multi-angle reference cropper."""

    ASPECT_RATIOS = {
        "1:1": (1.0, 1.0),
        "4:5": (4.0, 5.0),
        "9:16": (9.0, 16.0),
        "3:2": (3.0, 2.0),
        "passport_us": (1.0, 1.0),       # 2x2 inches (600x600 px @ 300dpi)
        "passport_eu": (35.0, 45.0),     # 35x45 mm (413x531 px @ 300dpi)
    }

    def __init__(self):
        self._cascade_frontal = None
        self._cascade_profile = None
        if CV2_AVAILABLE:
            try:
                cv2_data = getattr(cv2, "data", None)
                if cv2_data and hasattr(cv2_data, "haarcascades"):
                    frontal_path = os.path.join(cv2_data.haarcascades, "haarcascade_frontalface_default.xml")
                    profile_path = os.path.join(cv2_data.haarcascades, "haarcascade_profileface.xml")
                    if os.path.exists(frontal_path):
                        self._cascade_frontal = cv2.CascadeClassifier(frontal_path)
                    if os.path.exists(profile_path):
                        self._cascade_profile = cv2.CascadeClassifier(profile_path)
            except Exception:
                pass

    @staticmethod
    def load_normalized_image(image_path: Union[str, Path]) -> Image.Image:
        """Loads an image with proper EXIF orientation applied."""
        img = Image.open(image_path)
        img = ImageOps.exif_transpose(img)
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        return img

    def detect_face_box(self, img: Image.Image) -> Optional[Tuple[int, int, int, int]]:
        """
        Detects primary face bounding box (x, y, w, h).
        Returns None if not detected or OpenCV not available.
        """
        if not CV2_AVAILABLE or self._cascade_frontal is None:
            return None

        try:
            cv_img = np.array(img.convert("RGB"))
            gray = cv2.cvtColor(cv_img, cv2.COLOR_RGB2GRAY)

            # Try frontal cascade first
            faces = self._cascade_frontal.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60)
            )

            # If frontal fails, try profile cascade
            if len(faces) == 0 and self._cascade_profile is not None:
                faces = self._cascade_profile.detectMultiScale(
                    gray, scaleFactor=1.1, minNeighbors=4, minSize=(60, 60)
                )

            if len(faces) > 0:
                # Return the largest detected face
                largest = max(faces, key=lambda b: b[2] * b[3])
                return tuple(int(v) for v in largest)  # (x, y, w, h)
        except Exception:
            return None
        return None

    def calculate_crop_box(
        self,
        img_width: int,
        img_height: int,
        face_box: Optional[Tuple[int, int, int, int]] = None,
        aspect_ratio_str: str = "1:1",
        padding_factor: float = 0.5,
    ) -> Tuple[int, int, int, int]:
        """
        Calculates the bounding box (left, top, right, bottom) for cropping
        around the face with target aspect ratio and safety padding.
        """
        ratio_w, ratio_h = self.ASPECT_RATIOS.get(aspect_ratio_str, (1.0, 1.0))
        target_ratio = ratio_w / ratio_h

        if face_box:
            fx, fy, fw, fh = face_box
            cx = fx + fw / 2.0
            cy = fy + fh * 0.45  # Align eyes slightly above vertical center

            # Calculate base bounding size with padding
            base_dim = max(fw, fh) * (1.0 + padding_factor * 2.0)
            if target_ratio >= 1.0:
                crop_w = base_dim * target_ratio
                crop_h = base_dim
            else:
                crop_w = base_dim
                crop_h = base_dim / target_ratio
        else:
            # Center crop fallback
            cx = img_width / 2.0
            cy = img_height * 0.45  # Golden ratio portrait focus

            if (img_width / img_height) > target_ratio:
                crop_h = img_height * 0.9
                crop_w = crop_h * target_ratio
            else:
                crop_w = img_width * 0.9
                crop_h = crop_w / target_ratio

        # Clamp crop dimensions to image bounds
        if crop_w > img_width:
            crop_w = img_width
            crop_h = crop_w / target_ratio
        if crop_h > img_height:
            crop_h = img_height
            crop_w = crop_h * target_ratio

        left = int(max(0, cx - crop_w / 2.0))
        top = int(max(0, cy - crop_h / 2.0))
        right = int(min(img_width, left + crop_w))
        bottom = int(min(img_height, top + crop_h))

        # Adjust bounds if clamped on one side
        actual_w = right - left
        actual_h = bottom - top
        if actual_w < crop_w and left > 0:
            left = int(max(0, right - crop_w))
        if actual_h < crop_h and top > 0:
            top = int(max(0, bottom - crop_h))

        return (left, top, right, bottom)

    def crop_single(
        self,
        image_path: Union[str, Path],
        output_path: Union[str, Path],
        config: Optional[CropConfig] = None,
        angle_label: str = "frontal",
    ) -> CropResult:
        """
        Crops an image file according to the configuration and saves the output.
        """
        config = config or CropConfig()
        src_path = Path(image_path)
        dst_path = Path(output_path)
        dst_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            img = self.load_normalized_image(src_path)
            w, h = img.size

            face_box = self.detect_face_box(img) if config.detect_face else None
            box = self.calculate_crop_box(
                w, h, face_box, config.aspect_ratio, config.padding_factor
            )

            cropped = img.crop(box)

            if config.output_size:
                cropped = cropped.resize(config.output_size, Image.Resampling.LANCZOS)

            cropped.save(dst_path, quality=config.quality)

            return CropResult(
                source_path=str(src_path),
                output_path=str(dst_path),
                angle_label=angle_label,
                crop_box=box,
                aspect_ratio=config.aspect_ratio,
                success=True,
                message="Successfully cropped",
            )
        except Exception as e:
            return CropResult(
                source_path=str(src_path),
                output_path=str(dst_path),
                angle_label=angle_label,
                crop_box=(0, 0, 0, 0),
                aspect_ratio=config.aspect_ratio,
                success=False,
                message=str(e),
            )

    def crop_batch(
        self,
        image_paths: List[Union[str, Path]],
        output_dir: Union[str, Path],
        config: Optional[CropConfig] = None,
    ) -> List[CropResult]:
        """Processes multiple images in batch."""
        results = []
        out_dir = Path(output_dir)
        for idx, p in enumerate(image_paths):
            path_obj = Path(p)
            out_file = out_dir / f"crop_{idx + 1:02d}_{path_obj.stem}.jpg"
            result = self.crop_single(path_obj, out_file, config=config, angle_label=f"view_{idx + 1}")
            results.append(result)
        return results
