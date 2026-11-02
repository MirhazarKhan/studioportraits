# Changelog

All notable changes to **Portrait Generator** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-29

### Added
- **Multi-Angle Face Cropping Engine**: Calibrated cropping with support for 1:1 Square, 4:5 Portrait, 9:16 Story, 3:2 Landscape, and US/EU Passport formats.
- **Biometric Profiler**: Standardized extraction and structured markdown reporting for cranial contours, eye geometry, facial hair, and Fitzpatrick skin tone typing.
- **Curated Style Presets**:
  - `tlou2`: The Last of Us Part II Gritty Chiaroscuro Survivalist.
  - `vinyl_toy_tan`: 3D Minimalist Vinyl Toy Avatar (Designer Tan Edition).
  - `vinyl_toy_porcelain`: 3D Minimalist Vinyl Toy Avatar (Porcelain Edition).
  - `studio_monochrome`: Cinematic Low-Key Monochrome Studio with Rembrandt split lighting.
  - `editorial_monochrome_knit`: Fine-Art Monochrome Studio (Waffle Knit & Folded Arms pose).
  - `street_monochrome_sunglasses`: High-Contrast Street Editorial (Sunglasses, Clasped Hands & Harrington Jacket).
  - `dualtone_crimson_cyan`: Cinematic Dual-Tone Studio with split crimson-red and cyan-blue rim lights.
  - `editorial_forbes`: Bespoke Executive / Forbes Editorial with high-rise architectural backdrop.
  - `executive_blue_suit`: Modern Executive / GQ Editorial (Royal Blue Suit, Open Collar & Steel Watch).
  - `corporate_executive_suit`: Classic Corporate Executive (Navy Suit, Light Blue Shirt, Silk Tie & Folded Arms).
  - `executive_windowpane_suit`: Bespoke Windowpane Check Executive (Charcoal Windowpane Suit, Open Collar & Dive Watch).
  - `fineart_chiaroscuro_slit`: Dramatic Fine-Art Chiaroscuro (Horizontal/Diagonal Slit Lighting across Eyes).
  - `cinestill_vintage`: Vintage 35mm Cinestill 800T Film with authentic halation.
  - `cyberpunk_neon`: Neo-Noir Cyberpunk with dual-tone anamorphic reflections.
  - `passport_biometric`: Official ICAO-compliant studio passport portraiture.
- **Multi-Platform Prompt Compiler**: One-click generation of Midjourney v6.1 commands and ComfyUI/SDXL prompt dictionaries.
- **Full CLI**: Command-line interface with `crop`, `profile`, `prompt`, `generate`, `list-styles`, and `check-env`.
- **Streamlit Web Studio**: Interactive browser UI for visual cropping, live profiling, and prompt generation.
- **Privacy Armor**: Strict `.gitignore` policy protecting all personal photo archives and subject data.
- **Full Test Suite**: Native unit tests covering cropping geometry, profile serialization, and prompt compilation.
