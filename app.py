"""Streamlit interface for the Indonesian PPKM sentiment model."""

from pathlib import Path

import streamlit as st

from src.predict_sentiment import load_artifact, predict_texts


PROJECT_ROOT = Path(__file__).resolve().parent
MODEL_PATH = PROJECT_ROOT / "models" / "ppkm_sentiment_pipeline.pkl"

LABEL_DETAILS = {
    "positive": ("Positif", "Respons menunjukkan dukungan atau sentimen positif."),
    "neutral": ("Netral", "Respons tidak menunjukkan sentimen positif atau negatif yang kuat."),
    "negative": ("Negatif", "Respons menunjukkan penolakan atau sentimen negatif."),
}


@st.cache_resource
def get_model_artifact() -> dict:
    return load_artifact(MODEL_PATH)


def main() -> None:
    st.set_page_config(
        page_title="Analisis Sentimen PPKM",
        page_icon="💬",
        layout="centered",
    )

    st.title("Analisis Sentimen PPKM")
    st.caption("Klasifikasi teks Bahasa Indonesia dengan model TF-IDF.")

    text = st.text_area(
        "Masukkan teks",
        placeholder="Contoh: PPKM ini bikin masyarakat makin susah",
        height=150,
    )

    if not st.button("Analisis Sentimen", type="primary", use_container_width=True):
        return

    if not text.strip():
        st.warning("Masukkan teks terlebih dahulu.")
        return

    try:
        artifact = get_model_artifact()
        prediction = predict_texts([text.strip()], artifact).iloc[0]
    except (FileNotFoundError, ValueError) as error:
        st.error(str(error))
        return

    label = str(prediction["predicted_label"])
    display_label, description = LABEL_DETAILS.get(label, (label.title(), ""))

    st.subheader("Hasil")
    st.metric("Sentimen", display_label)
    if description:
        st.write(description)

    confidence = prediction.get("confidence")
    if confidence is not None:
        st.progress(float(confidence), text=f"Confidence: {float(confidence):.1%}")

    with st.expander("Detail prediksi"):
        st.write(f"Model: `{artifact.get('model_name', 'unknown')}`")
        st.write(f"Teks setelah normalisasi: `{prediction['normalized_text']}`")


if __name__ == "__main__":
    main()
