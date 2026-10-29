"""
AI Portrait Generator - Interactive Streamlit Web Studio
Launch with: streamlit run app.py
"""

from __future__ import annotations

import io
import json
from pathlib import Path
from PIL import Image
import streamlit as st

from portrait_generator import __version__
from portrait_generator.config import Config
from portrait_generator.cropper import FaceCropper, CropConfig
from portrait_generator.profiler import BiometricProfiler, SubjectProfile
from portrait_generator.prompt_engine import PromptEngine
from portrait_generator.generator import PortraitGenerator

# Page Configuration
st.set_page_config(
    page_title="AI Portrait Generator Studio",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #94a3b8;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    .card {
        background-color: #1e293b;
        padding: 1.2rem;
        border-radius: 12px;
        border: 1px solid #334155;
        margin-bottom: 1rem;
    }
    .badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        background-color: #0f172a;
        color: #38bdf8;
        font-weight: 600;
        font-size: 0.85rem;
        border: 1px solid #0284c7;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar
st.sidebar.markdown(f"### 🎨 Portrait Studio v{__version__}")
st.sidebar.caption("Biometric Calibration & Stylized AI Portrait Toolkit")

tab_choice = st.sidebar.radio(
    "Studio Navigation",
    [
        "📐 Angle & Face Cropper",
        "🧬 Biometric Profiler",
        "✨ Style Presets & Prompt Studio",
        "🚀 Generator & Export Bundle",
        "📖 User Guide & Best Practices",
    ],
)

# Initialize engines
engine = PromptEngine()
cropper = FaceCropper()
generator = PortraitGenerator(engine)

# ==========================================
# 1. ANGLE & FACE CROPPER
# ==========================================
if tab_choice == "📐 Angle & Face Cropper":
    st.markdown('<div class="main-header">Multi-Angle Reference Calibration</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Crop and normalize reference photographs for multi-angle AI training & generation.</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        uploaded_file = st.file_uploader(
            "Upload Reference Photo",
            type=["jpg", "jpeg", "png", "webp", "tif"],
            help="Upload a portrait photo to calibrate framing and aspect ratios.",
        )

        aspect_ratio = st.selectbox(
            "Target Aspect Ratio",
            options=["1:1", "4:5", "9:16", "3:2", "passport_us", "passport_eu"],
            index=0,
            format_func=lambda x: {
                "1:1": "1:1 Square (Studio / Avatar)",
                "4:5": "4:5 Portrait (Instagram / Editorial)",
                "9:16": "9:16 Story (Vertical Wallpaper)",
                "3:2": "3:2 Landscape (Classic 35mm)",
                "passport_us": "Passport US (2x2 inches / 600x600)",
                "passport_eu": "Passport Schengen/UK (35x45mm)",
            }[x],
        )

        padding = st.slider("Headroom & Padding Factor", min_value=0.1, max_value=1.0, value=0.5, step=0.05)
        auto_detect = st.checkbox("Auto-detect Face Center", value=True)

    with col2:
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Original Upload", use_container_width=True)

            if st.button("✂️ Generate Calibrated Crop", type="primary"):
                w, h = image.size
                config = CropConfig(aspect_ratio=aspect_ratio, padding_factor=padding, detect_face=auto_detect)
                box = cropper.calculate_crop_box(w, h, None, aspect_ratio, padding)
                cropped = image.crop(box)

                st.success("Successfully cropped!")
                st.image(cropped, caption=f"Result ({aspect_ratio})", use_container_width=True)

                buf = io.BytesIO()
                cropped.save(buf, format="JPEG", quality=95)
                st.download_button(
                    label="💾 Download Crop",
                    data=buf.getvalue(),
                    file_name=f"crop_{aspect_ratio.replace(':', 'x')}.jpg",
                    mime="image/jpeg",
                )
        else:
            st.info("Upload an image on the left to begin calibration.")

# ==========================================
# 2. BIOMETRIC PROFILER
# ==========================================
elif tab_choice == "🧬 Biometric Profiler":
    st.markdown('<div class="main-header">Biometric Facial Profiler</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Extract cranial geometry, gaze, grooming, and skin tone into a structured markdown profile.</div>', unsafe_allow_html=True)

    with st.form("profiler_form"):
        col1, col2 = st.columns(2)

        with col1:
            subject_name = st.text_input("Subject Name", value="Alex Rivera")
            face_shape = st.text_input("Face Shape & Contour", value="Oval-to-oblong contour with balanced facial thirds")
            jaw_chin = st.text_input("Jaw & Chin Definition", value="Structured mandibular line with rounded-square chin")
            forehead = st.text_input("Forehead & Temples", value="Broad forehead with smooth brow line and gentle temple taper")
            eye_geom = st.text_input("Eye Geometry & Color", value="Almond-shaped, deep-set, dark brown irises with calm direct gaze")
            eyebrows = st.text_input("Eyebrows", value="Well-defined natural arch with medium density tapering at temples")

        with col2:
            beard_style = st.text_input("Facial Hair & Beard", value="Tailored short-boxed beard (~3-5mm) covering jaw and chin")
            mustache = st.text_input("Mustache", value="Neatly trimmed mustache connecting softly to beard line")
            hair = st.text_input("Hairstyle & Color", value="Jet black, textured short crop with faded/tapered sides and back")
            fitzpatrick = st.selectbox(
                "Fitzpatrick Skin Type",
                [
                    "Type I (Pale white, highly sensitive)",
                    "Type II (Fair white, sensitive)",
                    "Type III (Medium / Light olive)",
                    "Type IV-V (Warm golden-olive South Asian / Mediterranean / Latin)",
                    "Type VI (Deep richly pigmented dark brown / black)",
                ],
                index=3,
            )
            expression = st.text_input("Default Expression", value="Poised, calm, confident, and direct")

        submitted = st.form_submit_button("📝 Build Biometric Profile", type="primary")

    profile = SubjectProfile(
        subject_name=subject_name,
        face_shape=face_shape,
        jaw_chin=jaw_chin,
        forehead_temples=forehead,
        eye_geometry=eye_geom,
        eyebrows=eyebrows,
        beard_style=beard_style,
        mustache=mustache,
        hair=hair,
        fitzpatrick_scale=fitzpatrick,
        neutral_expression=expression,
    )

    md_output = profile.to_markdown()
    st.markdown("### Generated Markdown Profile")
    st.code(md_output, language="markdown")

    st.download_button(
        label="💾 Download facial_profile.md",
        data=md_output,
        file_name=f"{subject_name.lower().replace(' ', '_')}_profile.md",
        mime="text/markdown",
    )

# ==========================================
# 3. STYLE PRESETS & PROMPT STUDIO
# ==========================================
elif tab_choice == "✨ Style Presets & Prompt Studio":
    st.markdown('<div class="main-header">Style Synthesis & Prompt Studio</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Select curated cinematic, 3D toy, and editorial archetypes to compile production-ready prompts.</div>', unsafe_allow_html=True)

    styles = engine.list_styles()
    style_ids = list(styles.keys())

    col1, col2 = st.columns([1, 2])

    with col1:
        chosen_style = st.selectbox(
            "Select Portrait Style",
            options=style_ids,
            format_func=lambda s: f"{styles[s].name} ({styles[s].recommended_aspect_ratio})",
        )
        subject_input = st.text_input("Subject Name", value="Alex Rivera")
        custom_aspect = st.selectbox("Aspect Ratio Override (Optional)", options=["Default", "1:1", "4:5", "9:16", "16:9", "3:2"], index=0)

        preset = styles[chosen_style]
        st.info(f"**Description:** {preset.description}")

    with col2:
        profile_demo = SubjectProfile(subject_name=subject_input)
        ar = None if custom_aspect == "Default" else custom_aspect
        compiled = engine.compile(style_id=chosen_style, profile=profile_demo, custom_aspect_ratio=ar)

        st.markdown(f"### Compiled Prompt: {preset.name}")

        st.markdown("**Positive Prompt:**")
        st.code(compiled.positive_prompt, language="text")

        st.markdown("**Negative Prompt:**")
        st.code(compiled.negative_prompt, language="text")

        st.markdown("**Midjourney v6.1 Command:**")
        st.code(compiled.to_midjourney_command(), language="bash")

# ==========================================
# 4. GENERATOR & EXPORT BUNDLE
# ==========================================
elif tab_choice == "🚀 Generator & Export Bundle":
    st.markdown('<div class="main-header">Generation Studio & Export Bundle</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Export bundles for Midjourney, ComfyUI, SDXL, or call Gemini / OpenAI APIs.</div>', unsafe_allow_html=True)

    styles = engine.list_styles()
    col1, col2 = st.columns(2)

    with col1:
        subject = st.text_input("Subject Name", value="Alex Rivera", key="gen_subj")
        selected_style = st.selectbox("Style Preset", options=list(styles.keys()), format_func=lambda s: styles[s].name, key="gen_style")
        backend = st.selectbox("Backend Provider", options=["export (Ready-to-run bundle)", "gemini", "openai"], index=0)

    with col2:
        st.markdown("### Provider Configuration")
        if "gemini" in backend:
            key_status = "✅ Configured" if Config.gemini_api_key else "⚠️ Not configured (Set GEMINI_API_KEY in .env)"
            st.write(f"**Gemini API Key:** {key_status}")
        elif "openai" in backend:
            key_status = "✅ Configured" if Config.openai_api_key else "⚠️ Not configured (Set OPENAI_API_KEY in .env)"
            st.write(f"**OpenAI API Key:** {key_status}")
        else:
            st.write("**Export Mode:** Generates formatted JSON, TXT prompts, and ComfyUI configurations locally.")

    if st.button("🚀 Run / Export Bundle", type="primary"):
        profile_obj = SubjectProfile(subject_name=subject)
        compiled_res = engine.compile(style_id=selected_style, profile=profile_obj)

        bundle_dict = compiled_res.to_comfyui_dict()
        bundle_json = json.dumps(bundle_dict, indent=2)

        st.success("Bundle compiled successfully!")
        st.json(bundle_dict)

        st.download_button(
            label="💾 Download Prompt Bundle (JSON)",
            data=bundle_json,
            file_name=f"{subject.lower()}_{selected_style}_bundle.json",
            mime="application/json",
        )

# ==========================================
# 5. USER GUIDE
# ==========================================
else:
    st.markdown('<div class="main-header">Portrait Generator Pipeline Guide</div>', unsafe_allow_html=True)
    st.markdown(
        """
        ### The 4-Step Professional Portrait Workflow

        1. **Reference Photography**:
           - Capture 3-5 images with neutral expressions, sharp focus on irises, and clean lighting.
           - Recommended kit: 0° Frontal, 45° Three-Quarter, 90° Profile, Dynamic Smile, Natural Daylight.

        2. **Angle Calibration & Cropping**:
           - Use the **Angle Cropper** or `python main.py crop` to normalize portraits into standard 1:1, 4:5, and passport frames.

        3. **Biometric Feature Extraction**:
           - Use the **Biometric Profiler** to document facial thirds, mandibular contours, eye geometry, and skin undertones into `facial_profile.md`.

        4. **Style Synthesis**:
           - Match your subject with battle-tested presets:
             - **The Last of Us Part II**: Cinematic post-apocalyptic survivalist aesthetic.
             - **3D Minimalist Vinyl Toy**: Cute collectible designer figurines.
             - **Cinematic Monochrome Studio**: Fine art Rembrandt lighting.
             - **Forbes Executive**: Bespoke corporate tailoring.

        ---
        ### 🔒 Privacy & Open-Source Ethics
        All raw personal photos, subject archives, and credentials stay **100% local** on your machine.
        The included `.gitignore` guarantees that private photos are never tracked by Git.
        """
    )
