import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import streamlit as st

try:
    import pytesseract
    from PIL import Image
except Exception:  # noqa: BLE001
    pytesseract = None
    Image = None


DATA_PATH = Path(__file__).with_name("icd_reference.json")


@dataclass
class ICDMatch:
    code: str
    diagnosis: str
    score: float


def load_reference() -> Dict[str, List[str]]:
    with DATA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def tokenize(text: str) -> List[str]:
    return [token.strip(".,;:!?()[]{}\"'").lower() for token in text.split() if token.strip()]


def jaccard_similarity(a: str, b: str) -> float:
    set_a = set(tokenize(a))
    set_b = set(tokenize(b))
    if not set_a or not set_b:
        return 0.0
    return len(set_a.intersection(set_b)) / len(set_a.union(set_b))


def find_icd_matches(diagnosis_text: str, reference: Dict[str, List[str]], top_k: int = 5) -> List[ICDMatch]:
    matches: List[ICDMatch] = []
    for code, diagnoses in reference.items():
        best_score = 0.0
        best_diagnosis = ""
        for diagnosis in diagnoses:
            score = jaccard_similarity(diagnosis_text, diagnosis)
            if score > best_score:
                best_score = score
                best_diagnosis = diagnosis
        matches.append(ICDMatch(code=code, diagnosis=best_diagnosis, score=best_score))

    ranked = sorted(matches, key=lambda m: m.score, reverse=True)
    return ranked[:top_k]


def extract_text_from_image(uploaded_image) -> Tuple[str, str]:
    if pytesseract is None or Image is None:
        return "", "Install pytesseract and Pillow to enable OCR from handwritten images."

    try:
        image = Image.open(uploaded_image)
        text = pytesseract.image_to_string(image)
    except Exception as exc:  # noqa: BLE001
        return "", f"OCR failed: {exc}"

    if not text.strip():
        return "", "No text detected. Try a clearer image or use manual input."

    return text.strip(), ""


def main() -> None:
    st.set_page_config(page_title="Handwritten Diagnosis to ICD Code", layout="centered")
    st.title("Handwritten Diagnosis → ICD-10 Suggestion App")
    st.caption("Prototype workflow for RCM coding support. Verify all suggestions with a certified coder.")

    reference = load_reference()

    input_mode = st.radio("Choose input mode", ["Upload handwritten diagnosis image", "Paste diagnosis text"], index=0)

    extracted_text = ""
    if input_mode == "Upload handwritten diagnosis image":
        uploaded = st.file_uploader("Upload image", type=["png", "jpg", "jpeg"])
        if uploaded is not None:
            extracted_text, error = extract_text_from_image(uploaded)
            if error:
                st.warning(error)
            elif extracted_text:
                st.subheader("OCR Extracted Text")
                st.code(extracted_text)
    else:
        extracted_text = st.text_area("Diagnosis text", placeholder="e.g., uncontrolled type 2 diabetes with nephropathy")

    if st.button("Suggest ICD Codes", type="primary"):
        if not extracted_text.strip():
            st.error("Please provide or extract diagnosis text first.")
            return

        suggestions = find_icd_matches(extracted_text, reference)
        st.subheader("Top ICD-10 Suggestions")
        for item in suggestions:
            st.write(f"**{item.code}** — {item.diagnosis}")
            st.progress(min(max(item.score, 0.0), 1.0), text=f"Confidence (keyword overlap): {item.score:.0%}")

        st.info("These are keyword-based suggestions for triage only, not final billing codes.")


if __name__ == "__main__":
    main()
