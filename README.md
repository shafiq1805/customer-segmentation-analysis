# customer-segmentation-analysis

This repository originally contains analysis assets for retail customer segmentation.

## Added: Handwritten Diagnosis to ICD-10 Suggestion App

I added a small Streamlit application (`app.py`) that can:

- Accept a handwritten diagnosis image upload and run OCR (via `pytesseract` + `Pillow`), or
- Accept diagnosis text manually,
- Suggest top ICD-10 matches using keyword-overlap scoring against a local reference file (`icd_reference.json`).

> This is a prototype for RCM coding support. It is **not** a replacement for certified coding review.

### Run locally

```bash
pip install streamlit pytesseract pillow
streamlit run app.py
```

If OCR does not work on your machine, install the Tesseract engine:

- Ubuntu/Debian: `sudo apt-get install tesseract-ocr`
- macOS (Homebrew): `brew install tesseract`

### Notes on your request

I cannot directly connect to your ChatGPT profile or private "RCM automation project" from this environment. The app here is implemented locally in this repository and can be integrated with your external automation stack once you share API/project details.
