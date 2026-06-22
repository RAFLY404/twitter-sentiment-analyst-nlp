"""Train a supervised Indonesian sentiment model on the labeled PPKM dataset."""

from __future__ import annotations

import argparse
import html
import pickle
import re
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import ComplementNB, MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "raw"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"

PPKM_DATASET = DATA_DIR / "ppkm_sentiment" / "INA_TweetsPPKM_Labeled_Pure.csv"
SLANG_DICTIONARY = DATA_DIR / "slang_dictionary.csv"

LABEL_MAP = {
    0: "positive",
    1: "neutral",
    2: "negative",
}

STOPWORDS_ID = {
    "ada",
    "adalah",
    "agar",
    "akan",
    "aku",
    "anda",
    "antara",
    "apa",
    "atau",
    "bagi",
    "bahwa",
    "dan",
    "dari",
    "dengan",
    "di",
    "dia",
    "ini",
    "itu",
    "jadi",
    "juga",
    "karena",
    "ke",
    "kita",
    "maka",
    "mereka",
    "oleh",
    "pada",
    "saat",
    "saya",
    "sebagai",
    "sebuah",
    "sehingga",
    "untuk",
    "yang",
}


def load_slang_dictionary(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    df = pd.read_csv(path)
    if not {"slang", "formal"}.issubset(df.columns):
        return {}

    pairs = df[["slang", "formal"]].dropna()
    return {
        str(row.slang).strip().lower(): str(row.formal).strip().lower()
        for row in pairs.itertuples(index=False)
        if str(row.slang).strip() and str(row.formal).strip()
    }


def normalize_tweet(text: object, slang_map: dict[str, str]) -> str:
    value = html.unescape(str(text).lower())
    value = re.sub(r"https?://\S+|www\.\S+", " ", value)
    value = re.sub(r"@\w+", " user ", value)
    value = re.sub(r"#", " ", value)
    value = re.sub(r"(.)\1{2,}", r"\1\1", value)
    value = re.sub(r"[^0-9a-zA-Z_]+", " ", value)
    tokens = [slang_map.get(token, token) for token in value.split()]
    return " ".join(tokens)


def load_ppkm_dataset(path: Path, slang_map: dict[str, str]) -> pd.DataFrame:
    df = pd.read_csv(path, sep="\t")
    required_columns = {"Tweet", "sentiment"}
    missing = required_columns.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns in {path}: {sorted(missing)}")

    dataset = df.dropna(subset=["Tweet", "sentiment"]).copy()
    dataset["sentiment"] = dataset["sentiment"].astype(int)
    dataset = dataset[dataset["sentiment"].isin(LABEL_MAP)].copy()
    dataset["label"] = dataset["sentiment"].map(LABEL_MAP)
    dataset["normalized_tweet"] = dataset["Tweet"].map(lambda text: normalize_tweet(text, slang_map))
    dataset = dataset[dataset["normalized_tweet"].str.strip().astype(bool)].copy()
    return dataset


def build_classifier_models(random_state: int) -> dict[str, object]:
    return {
        "logistic_regression": LogisticRegression(
            max_iter=1000,
            solver="lbfgs",
            class_weight="balanced",
            random_state=random_state,
        ),
        "linear_svc": LinearSVC(
            class_weight="balanced",
            random_state=random_state,
            max_iter=5000,
        ),
        "multinomial_nb": MultinomialNB(alpha=0.5),
        "complement_nb": ComplementNB(alpha=0.5),
    }


def build_model(max_features: int, classifier: object) -> Pipeline:
    return Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    min_df=2,
                    max_df=0.95,
                    max_features=max_features,
                    ngram_range=(1, 2),
                    sublinear_tf=True,
                    stop_words=list(STOPWORDS_ID),
                ),
            ),
            ("classifier", classifier),
        ]
    )


def plot_evaluation_metrics(metrics: dict[str, float], output_path: Path) -> None:
    labels = ["Accuracy", "Macro F1", "Weighted F1"]
    values = [metrics["accuracy"], metrics["macro_f1"], metrics["weighted_f1"]]

    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(labels, values, color=["#357ABD", "#2E8B57", "#C46A2B"])
    ax.set_title("PPKM Sentiment Evaluation Metrics")
    ax.set_ylabel("Score")
    ax.set_ylim(0, 1)
    ax.grid(axis="y", linestyle="--", alpha=0.35)

    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.02,
            f"{value:.4f}",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def plot_model_comparison(results: dict[str, dict[str, float]], output_path: Path) -> None:
    model_names = list(results)
    metric_names = ["accuracy", "macro_f1", "weighted_f1"]
    display_names = ["Accuracy", "Macro F1", "Weighted F1"]
    x_positions = range(len(model_names))
    bar_width = 0.25

    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ["#357ABD", "#2E8B57", "#C46A2B"]

    for index, (metric_name, display_name) in enumerate(zip(metric_names, display_names)):
        offset = (index - 1) * bar_width
        values = [results[model_name][metric_name] for model_name in model_names]
        bars = ax.bar(
            [position + offset for position in x_positions],
            values,
            width=bar_width,
            label=display_name,
            color=colors[index],
        )
        for bar, value in zip(bars, values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                value + 0.01,
                f"{value:.3f}",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    ax.set_title("PPKM Sentiment Model Comparison")
    ax.set_ylabel("Score")
    ax.set_ylim(0, 1)
    ax.set_xticks(list(x_positions))
    ax.set_xticklabels([name.replace("_", "\n") for name in model_names])
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    ax.legend()

    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def plot_confusion_matrix(matrix, labels: list[str], output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(6, 5))
    image = ax.imshow(matrix, cmap="Blues")
    fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)

    ax.set_title("PPKM Sentiment Confusion Matrix")
    ax.set_xlabel("Predicted label")
    ax.set_ylabel("True label")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels)

    threshold = matrix.max() / 2 if matrix.size else 0
    for row_index in range(matrix.shape[0]):
        for col_index in range(matrix.shape[1]):
            value = matrix[row_index, col_index]
            ax.text(
                col_index,
                row_index,
                str(value),
                ha="center",
                va="center",
                color="white" if value > threshold else "black",
            )

    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def format_project_path(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def evaluate_model(model: Pipeline, test_df: pd.DataFrame, labels: list[str]) -> dict:
    predictions = model.predict(test_df["normalized_tweet"])
    metrics = {
        "accuracy": accuracy_score(test_df["label"], predictions),
        "macro_f1": f1_score(test_df["label"], predictions, labels=labels, average="macro"),
        "weighted_f1": f1_score(test_df["label"], predictions, labels=labels, average="weighted"),
    }
    return {
        "metrics": metrics,
        "matrix": confusion_matrix(test_df["label"], predictions, labels=labels),
        "report": classification_report(
            test_df["label"],
            predictions,
            labels=labels,
            zero_division=0,
        ),
    }


def train(args: argparse.Namespace) -> dict:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    args.plots_dir = args.plots_dir.resolve()
    args.plots_dir.mkdir(parents=True, exist_ok=True)

    slang_map = load_slang_dictionary(args.slang_dictionary)
    dataset = load_ppkm_dataset(args.dataset, slang_map)

    train_df, test_df = train_test_split(
        dataset,
        test_size=args.test_size,
        random_state=args.random_state,
        stratify=dataset["label"],
    )

    labels = ["positive", "neutral", "negative"]
    trained_models = {}
    evaluations = {}

    for model_name, classifier in build_classifier_models(args.random_state).items():
        model = build_model(args.max_features, classifier)
        model.fit(train_df["normalized_tweet"], train_df["label"])
        trained_models[model_name] = model
        evaluations[model_name] = evaluate_model(model, test_df, labels)

    best_model_name = max(
        evaluations,
        key=lambda name: (
            evaluations[name]["metrics"]["macro_f1"],
            evaluations[name]["metrics"]["accuracy"],
        ),
    )
    best_evaluation = evaluations[best_model_name]
    best_model = trained_models[best_model_name]
    metrics_by_model = {
        model_name: evaluation["metrics"] for model_name, evaluation in evaluations.items()
    }

    metrics_plot = args.plots_dir / "evaluation_metrics.png"
    comparison_plot = args.plots_dir / "model_comparison.png"
    confusion_plot = args.plots_dir / "confusion_matrix.png"
    comparison_csv = args.plots_dir / "model_comparison.csv"

    plot_evaluation_metrics(best_evaluation["metrics"], metrics_plot)
    plot_model_comparison(metrics_by_model, comparison_plot)
    plot_confusion_matrix(best_evaluation["matrix"], labels, confusion_plot)
    pd.DataFrame.from_dict(metrics_by_model, orient="index").to_csv(
        comparison_csv,
        index_label="model",
    )

    artifact = {
        "model": best_model,
        "model_name": best_model_name,
        "label_map": LABEL_MAP,
        "slang_map": slang_map,
        "normalization": "src.train_sentiment.normalize_tweet",
        "metrics": best_evaluation["metrics"],
        "model_comparison": metrics_by_model,
        "plots": {
            "evaluation_metrics": str(metrics_plot),
            "model_comparison": str(comparison_plot),
            "confusion_matrix": str(confusion_plot),
        },
        "comparison_csv": str(comparison_csv),
    }
    with args.model_output.open("wb") as handle:
        pickle.dump(artifact, handle)

    print("Supervised PPKM Sentiment Evaluation")
    print("====================================")
    print(f"Dataset: {PPKM_DATASET.relative_to(PROJECT_ROOT)}")
    print("Label mapping: 0=positive, 1=neutral, 2=negative")
    print(f"Documents: {len(dataset)}")
    print(f"Test size: {args.test_size}")
    print(f"Random state: {args.random_state}")
    print(f"Max TF-IDF features: {args.max_features}")
    print("\nLabel distribution:")
    for label, count in dataset["label"].value_counts().reindex(labels, fill_value=0).items():
        print(f"- {label}: {int(count)}")
    print("\nModel comparison:")
    print(
        pd.DataFrame.from_dict(metrics_by_model, orient="index")
        .sort_values(["macro_f1", "accuracy"], ascending=False)
        .to_string(float_format=lambda value: f"{value:.4f}")
    )
    print(f"\nBest model: {best_model_name}")
    print(f"Accuracy: {best_evaluation['metrics']['accuracy']:.4f}")
    print(f"Macro F1: {best_evaluation['metrics']['macro_f1']:.4f}")
    print(f"Weighted F1: {best_evaluation['metrics']['weighted_f1']:.4f}")
    print(f"\nConfusion matrix, rows=true {labels}, cols=predicted:")
    print(best_evaluation["matrix"])
    print("\nSaved matplotlib plots:")
    print(f"- Best model metrics: {format_project_path(metrics_plot)}")
    print(f"- Model comparison: {format_project_path(comparison_plot)}")
    print(f"- Best model confusion matrix: {format_project_path(confusion_plot)}")
    print(f"- Model comparison CSV: {format_project_path(comparison_csv)}")
    print("\nClassification report:")
    print(best_evaluation["report"])

    return artifact


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=PPKM_DATASET)
    parser.add_argument("--slang-dictionary", type=Path, default=SLANG_DICTIONARY)
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument("--max-features", type=int, default=30000)
    parser.add_argument(
        "--model-output",
        type=Path,
        default=MODELS_DIR / "ppkm_sentiment_pipeline.pkl",
    )
    parser.add_argument(
        "--plots-dir",
        type=Path,
        default=REPORTS_DIR,
        help="Directory where matplotlib evaluation plots are saved.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    artifact = train(parse_args())
    metrics = artifact["metrics"]
    print(
        "\nSaved supervised PPKM model comparison "
        f"(best_model={artifact['model_name']}, "
        f"accuracy={metrics['accuracy']:.4f}, macro_f1={metrics['macro_f1']:.4f})"
    )
