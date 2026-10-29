"""
Portrait Generator - Open Source CLI Entrypoint.
A command-line tool for biometric face cropping, profile modeling, and AI portrait synthesis.
"""

from __future__ import annotations

import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional

from portrait_generator import __version__
from portrait_generator.config import Config
from portrait_generator.cropper import FaceCropper, CropConfig
from portrait_generator.profiler import BiometricProfiler, SubjectProfile
from portrait_generator.prompt_engine import PromptEngine
from portrait_generator.generator import PortraitGenerator


# Ensure UTF-8 output encoding where supported
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


# ANSI Terminal Colors
class Color:
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    MAGENTA = "\033[95m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"


def print_banner():
    banner = f"""{Color.CYAN}{Color.BOLD}+---------------------------------------------------------------------+
|                      AI PORTRAIT GENERATOR                          |
|               Biometric Calibration & Stylized Synthesis            |
|                            Version {__version__}                            |
+---------------------------------------------------------------------+{Color.RESET}"""
    print(banner)



def print_table(title: str, headers: List[str], rows: List[List[str]]):
    """Draws a clean, standard terminal table."""
    print(f"\n{Color.BOLD}{Color.CYAN}--- {title} ---{Color.RESET}")
    col_widths = [len(h) for h in headers]
    for row in rows:
        for idx, cell in enumerate(row):
            # strip color tags for length calculation
            clean_cell = cell.replace(Color.GREEN, "").replace(Color.RED, "").replace(Color.YELLOW, "").replace(Color.CYAN, "").replace(Color.RESET, "").replace(Color.BOLD, "").replace(Color.DIM, "")
            if len(clean_cell) > col_widths[idx]:
                col_widths[idx] = len(clean_cell)

    header_line = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    sep_line = "-+-".join("-" * col_widths[i] for i in range(len(headers)))

    print(f"{Color.BOLD}{header_line}{Color.RESET}")
    print(sep_line)
    for row in rows:
        formatted_cells = []
        for i, cell in enumerate(row):
            clean_cell = cell.replace(Color.GREEN, "").replace(Color.RED, "").replace(Color.YELLOW, "").replace(Color.CYAN, "").replace(Color.RESET, "").replace(Color.BOLD, "").replace(Color.DIM, "")
            pad = col_widths[i] - len(clean_cell)
            formatted_cells.append(cell + (" " * max(0, pad)))
        print(" | ".join(formatted_cells))
    print()


def cmd_list_styles(args):
    """Displays all configured style presets in a clean table."""
    engine = PromptEngine()
    styles = engine.list_styles()

    headers = ["Style ID", "Preset Name", "Ratio", "Description"]
    rows = []
    for sid, preset in styles.items():
        rows.append([
            f"{Color.GREEN}{sid}{Color.RESET}",
            f"{Color.BOLD}{preset.name}{Color.RESET}",
            f"{Color.YELLOW}{preset.recommended_aspect_ratio}{Color.RESET}",
            f"{Color.DIM}{preset.description[:55]}...{Color.RESET}" if len(preset.description) > 55 else preset.description,
        ])

    print_table("Available Portrait Style Presets", headers, rows)


def cmd_crop(args):
    """Crops an image or directory of images into calibrated aspect ratios."""
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"{Color.RED}Error: Input path '{input_path}' does not exist.{Color.RESET}")
        sys.exit(1)

    output_dir = Path(args.output or (Config.outputs_dir / "crops"))
    cropper = FaceCropper()
    config = CropConfig(
        aspect_ratio=args.aspect_ratio,
        padding_factor=args.padding,
        detect_face=not args.no_detect,
    )

    if input_path.is_file():
        image_files = [input_path]
    else:
        valid_exts = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"}
        image_files = [p for p in input_path.glob("*") if p.suffix.lower() in valid_exts]

    if not image_files:
        print(f"{Color.YELLOW}No supported images found in '{input_path}'.{Color.RESET}")
        return

    print(f"{Color.CYAN}Processing {len(image_files)} image(s) with aspect ratio '{args.aspect_ratio}'...{Color.RESET}")

    headers = ["Source Image", "Output Crop", "Status"]
    rows = []

    for idx, img_p in enumerate(image_files):
        out_file = output_dir / f"crop_{idx + 1:02d}_{img_p.stem}_{args.aspect_ratio.replace(':', 'x')}.jpg"
        res = cropper.crop_single(img_p, out_file, config=config, angle_label=f"view_{idx + 1}")
        status = f"{Color.GREEN}SUCCESS{Color.RESET}" if res.success else f"{Color.RED}{res.message}{Color.RESET}"
        rows.append([img_p.name, out_file.name, status])

    print_table("Cropping Results", headers, rows)
    print(f"{Color.BOLD}{Color.GREEN}Saved cropped outputs to: {output_dir}{Color.RESET}\n")


def cmd_profile(args):
    """Generates a structured biometric profile for a subject."""
    profile_out = Path(args.output or (Config.outputs_dir / f"{args.name.lower().replace(' ', '_')}_profile.md"))
    crops = []
    if args.crops_dir:
        crops_p = Path(args.crops_dir)
        if crops_p.exists():
            crops = [p.name for p in crops_p.glob("*.jpg")]

    profile = BiometricProfiler.create_profile(
        subject_name=args.name,
        reference_crops=crops,
    )
    saved = BiometricProfiler.save_markdown(profile, profile_out)
    print(f"\n{Color.CYAN}--- Biometric Profile: {args.name} ---{Color.RESET}")
    print(profile.to_markdown())
    print(f"{Color.BOLD}{Color.GREEN}Profile successfully saved to: {saved}{Color.RESET}\n")


def cmd_prompt(args):
    """Compiles stylized prompts for a given subject and style preset."""
    engine = PromptEngine()

    if args.profile and Path(args.profile).exists():
        profile = BiometricProfiler.load_markdown(args.profile)
    else:
        profile = SubjectProfile(subject_name=args.subject or "Subject")

    try:
        compiled = engine.compile(style_id=args.style, profile=profile)
    except ValueError as e:
        print(f"{Color.RED}{e}{Color.RESET}")
        sys.exit(1)

    print(f"\n{Color.GREEN}{Color.BOLD}Style Preset:{Color.RESET} {compiled.style_name}")
    print(f"{Color.GREEN}{Color.BOLD}Target Aspect Ratio:{Color.RESET} {compiled.aspect_ratio}")
    print(f"{Color.GREEN}{Color.BOLD}CFG Scale / Steps:{Color.RESET} {compiled.cfg_scale} / {compiled.steps}\n")

    print(f"{Color.CYAN}{Color.BOLD}=== POSITIVE PROMPT ==={Color.RESET}")
    print(compiled.positive_prompt)
    print()

    print(f"{Color.YELLOW}{Color.BOLD}=== NEGATIVE PROMPT ==={Color.RESET}")
    print(compiled.negative_prompt)
    print()

    print(f"{Color.MAGENTA}{Color.BOLD}=== MIDJOURNEY COMMAND ==={Color.RESET}")
    print(compiled.to_midjourney_command())
    print()


def cmd_generate(args):
    """Executes portrait generation or exports ready-to-run prompt bundles."""
    generator = PortraitGenerator()

    if args.profile and Path(args.profile).exists():
        profile = BiometricProfiler.load_markdown(args.profile)
    else:
        profile = SubjectProfile(subject_name=args.subject or "Subject")

    out_dir = Path(args.output or (Config.outputs_dir / profile.subject_name.lower().replace(" ", "_")))
    print(f"{Color.CYAN}Running generator for '{profile.subject_name}' in style '{args.style}' (Provider: {args.provider})...{Color.RESET}")

    res = generator.generate(
        style_id=args.style,
        profile=profile,
        output_dir=out_dir,
        provider=args.provider,
    )

    if res.success:
        print(f"{Color.BOLD}{Color.GREEN}{res.message}{Color.RESET}")
        for f in res.output_files:
            print(f"  • {f}")
    else:
        print(f"{Color.RED}{res.message}{Color.RESET}")


def cmd_check_env(args):
    """Checks dependencies, OpenCV, and API configuration."""
    headers = ["Component", "Status", "Details"]
    rows = []

    # Python version
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    rows.append(["Python", f"{Color.GREEN}OK{Color.RESET}", py_ver])

    # OpenCV
    try:
        import cv2
        rows.append(["OpenCV", f"{Color.GREEN}INSTALLED{Color.RESET}", cv2.__version__])
    except ImportError:
        rows.append(["OpenCV", f"{Color.YELLOW}NOT INSTALLED{Color.RESET}", "Fallback center-weighted cropping active"])

    # PIL
    try:
        from PIL import Image
        rows.append(["Pillow (PIL)", f"{Color.GREEN}INSTALLED{Color.RESET}", Image.__version__])
    except ImportError:
        rows.append(["Pillow (PIL)", f"{Color.RED}MISSING{Color.RESET}", "Required for image handling"])

    # API Keys
    rows.append([
        "Gemini API Key",
        f"{Color.GREEN}CONFIGURED{Color.RESET}" if Config.gemini_api_key else f"{Color.DIM}NOT SET{Color.RESET}",
        "Set GEMINI_API_KEY in .env (Optional)"
    ])
    rows.append([
        "OpenAI API Key",
        f"{Color.GREEN}CONFIGURED{Color.RESET}" if Config.openai_api_key else f"{Color.DIM}NOT SET{Color.RESET}",
        "Set OPENAI_API_KEY in .env (Optional)"
    ])
    rows.append([
        "Default Mode",
        f"{Color.CYAN}ACTIVE{Color.RESET}",
        f"Provider: '{Config.default_provider}'"
    ])

    print_table("Environment Diagnostic", headers, rows)


def main():
    parser = argparse.ArgumentParser(
        description="Portrait Generator - Biometric Face Calibration & Stylized AI Portrait Toolkit",
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # list-styles
    subparsers.add_parser("list-styles", help="List all available style presets")

    # check-env
    subparsers.add_parser("check-env", help="Check local environment, dependencies, and API keys")

    # crop
    crop_parser = subparsers.add_parser("crop", help="Crop faces to calibrated aspect ratios")
    crop_parser.add_argument("--input", "-i", required=True, help="Input image file or folder")
    crop_parser.add_argument("--output", "-o", help="Output directory")
    crop_parser.add_argument("--aspect-ratio", "-ar", default="1:1", choices=["1:1", "4:5", "9:16", "3:2", "passport_us", "passport_eu"])
    crop_parser.add_argument("--padding", "-p", type=float, default=0.5, help="Padding buffer factor (default: 0.5)")
    crop_parser.add_argument("--no-detect", action="store_true", help="Disable OpenCV face detection and use center crop")

    # profile
    prof_parser = subparsers.add_parser("profile", help="Generate or display a subject biometric profile")
    prof_parser.add_argument("--name", "-n", required=True, help="Name of the subject")
    prof_parser.add_argument("--crops-dir", help="Directory containing calibrated reference crops")
    prof_parser.add_argument("--output", "-o", help="Output markdown path")

    # prompt
    prompt_parser = subparsers.add_parser("prompt", help="Compile generation prompts for a subject and style")
    prompt_parser.add_argument("--style", "-s", required=True, help="Style preset identifier (e.g., tlou2, vinyl_toy_tan)")
    prompt_parser.add_argument("--profile", "-p", help="Path to subject profile markdown file")
    prompt_parser.add_argument("--subject", default="Subject", help="Subject name if no profile markdown provided")

    # generate
    gen_parser = subparsers.add_parser("generate", help="Synthesize portrait or export prompt bundles")
    gen_parser.add_argument("--style", "-s", required=True, help="Style preset ID")
    gen_parser.add_argument("--profile", "-p", help="Path to subject profile markdown file")
    gen_parser.add_argument("--subject", default="Subject", help="Subject name if no profile markdown provided")
    gen_parser.add_argument("--provider", choices=["export", "gemini", "openai", "stability"], default=Config.default_provider)
    gen_parser.add_argument("--output", "-o", help="Output directory")

    if len(sys.argv) == 1:
        print_banner()
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()
    print_banner()

    cmds = {
        "list-styles": cmd_list_styles,
        "check-env": cmd_check_env,
        "crop": cmd_crop,
        "profile": cmd_profile,
        "prompt": cmd_prompt,
        "generate": cmd_generate,
    }

    cmd_fn = cmds.get(args.command)
    if cmd_fn:
        cmd_fn(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
