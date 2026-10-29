# Contributing to Portrait Generator

Thank you for your interest in contributing to **Portrait Generator**! We welcome contributions from developers, designers, prompt engineers, and photographers.

## How Can You Contribute?
- **Add New Style Presets**: Submit refined prompt templates in `templates/style_presets.json`.
- **Improve Face Detection & Landmarks**: Enhance multi-angle detection and facial feature mapping in `cropper.py` and `profiler.py`.
- **New Backends**: Add support for local models (e.g., ComfyUI WebSocket API, Automatic1111 WebUI, Ollama / FLUX).
- **Web App Enhancements**: Improve the Streamlit interface in `app.py`.
- **Documentation & Recipes**: Add prompt engineering guides and camera lighting recipes to `README.md`.

## Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/MirhazarKhan/studioportraits.git
   cd studioportraits
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux / macOS:
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Run tests**:
   ```bash
   python -m unittest discover tests/
   ```

## Pull Request Guidelines
1. Create a descriptive feature branch (`git checkout -b feature/my-new-style`).
2. Ensure all tests pass (`python -m unittest discover tests/`).
3. Never commit raw personal photos or credentials. Keep inputs and subject images strictly local.
4. Submit a clear Pull Request explaining your changes and motivation.
