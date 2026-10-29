# Sample Subject Input Directory

Place your subject's raw reference photographs in this folder (or create a dedicated folder under `inputs/<subject_name>/`).

## Recommended Reference Photo Kit:
1. **0° Direct Frontal (`frontal.jpg`)**: Neutral lighting, straight-on gaze, no tilt, neutral or relaxed expression.
2. **45° Three-Quarter View (`threequarter.jpg`)**: Shows cheekbone definition, jawline taper, and temple contour.
3. **90° Side Profile (`profile.jpg`)**: Essential for nasal bridge angle, chin projection, and ear position.
4. **Dynamic Expression / Smile (`smile.jpg`)**: Natural smile displaying authentic teeth alignment and eye crinkling.
5. **Lighting Diversity (`ambient.jpg` / `outdoor.jpg`)**: Photos under daylight or warm indoor lighting to calibrate natural skin tone and undertone.

## Running the Pipeline:
```bash
# 1. Automatically crop and calibrate facial angles
python main.py crop --input inputs/sample_subject/ --output outputs/sample_subject/crops/

# 2. Generate a structured biometric profile
python main.py profile --name "Subject Name" --input outputs/sample_subject/crops/ --output outputs/sample_subject/facial_profile.md

# 3. Generate stylized portrait prompts
python main.py prompt --style tlou2 --profile outputs/sample_subject/facial_profile.md
```
> **Privacy Note**: Any images placed here remain 100% local on your machine and are excluded by `.gitignore`.
