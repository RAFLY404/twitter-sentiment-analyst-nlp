"""Predict Indonesian PPKM sentiment from text or a CSV file."""

from __future__ import annotations

import argparse
import pickle
from pathlib import Path

import pandas as pd

try:
    from .train_sentiment import MODELS_DIR, normalize_tweet
except ImportError:
    from train_sentiment import MODELS_DIR, normalize_tweet


DEFAULT_MODEL = MODELS_DIR / "ppkm_sentiment_pipeline.pkl"


def load_artifact(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(
            f"Model not found: {path}. Run `python src/train_sentiment.py` first."
        )
    with path.open("rb") as handle:
        artifact = pickle.load(handle)
    if "model" not in artifact or "slang_map" not in artifact:
        raise ValueError(f"Unexpected model artifact format: {path}")
    return artifact


def predict_texts(texts: list[str], artifact: dict) -> pd.DataFrame:
    model = artifact["model"]
    slang_map = artifact["slang_map"]
    normalized = [normalize_tweet(text, slang_map) for text in texts]
    labels = model.predict(normalized)

    result = pd.DataFrame(
        {
            "text": texts,
            "normalized_text": normalized,
            "predicted_label": labels,
        }
    )

    if hasattr(model.named_steps["classifier"], "predict_proba"):
        probabilities = model.predict_proba(normalized)
        result["confidence"] = probabilities.max(axis=1)
        for label, values in zip(model.named_steps["classifier"].classes_, probabilities.T):
            result[f"probability_{label}"] = values

    return result


def predict_csv(args: argparse.Namespace, artifact: dict) -> pd.DataFrame:
    df = pd.read_csv(args.csv_input)
    if args.text_column not in df.columns:
        raise ValueError(
            f"Column {args.text_column!r} not found in {args.csv_input}. "
            f"Available columns: {list(df.columns)}"
        )

    predictions = predict_texts(df[args.text_column].fillna("").astype(str).tolist(), artifact)
    output = pd.concat([df.reset_index(drop=True), predictions.drop(columns=["text"])], axis=1)
    output.to_csv(args.output, index=False)
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "text",
        nargs="*",
        help="Text to classify. Use quotes for a sentence.",
    )
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--csv-input", type=Path, help="CSV file containing texts to classify.")
    parser.add_argument("--text-column", default="Tweet", help="Text column for --csv-input.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("predictions.csv"),
        help="Output path for CSV predictions.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    artifact = load_artifact(args.model)

    if args.csv_input:
        output = predict_csv(args, artifact)
        print(f"Saved {len(output)} predictions to {args.output}")
        return

    text = " ".join(args.text).strip()
    if not text:
        raise SystemExit("Provide text to classify, or use --csv-input.")

    result = predict_texts([text], artifact)
    row = result.iloc[0]
    confidence = row.get("confidence")
    if confidence is None:
        print(row["predicted_label"])
    else:
        print(f"{row['predicted_label']} ({confidence:.4f})")


if __name__ == "__main__":
    main()
