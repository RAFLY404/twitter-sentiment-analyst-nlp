# Indonesian Sentiment Analyst

This project builds lightweight Indonesian NLP baselines for:

- Supervised PPKM tweet sentiment classification.
- Extractive summarization examples with LexRank and TextRank.

## Current Sentiment Models

The sentiment experiment compares four supervised classifiers with the same
preprocessing, train/test split, and TF-IDF features:

- Labeled PPKM Twitter sentiment data.
- Slang normalization with `new_kamusalay.csv`.
- TF-IDF word and bigram features.
- A stratified 80/20 train/test split.
- Logistic Regression with balanced class weights.
- Linear SVC with balanced class weights.
- Multinomial Naive Bayes.
- Complement Naive Bayes.

Label mapping:

- `0 = positive`
- `1 = neutral`
- `2 = negative`

The training script selects the best model by Macro F1, using Accuracy as a
tiebreaker, and saves that best pipeline for prediction.

Latest comparison:

| Model | Accuracy | Macro F1 | Weighted F1 |
| --- | ---: | ---: | ---: |
| Logistic Regression | `0.8414` | `0.7373` | `0.8499` |
| Linear SVC | `0.8579` | `0.7337` | `0.8568` |
| Multinomial Naive Bayes | `0.8450` | `0.6597` | `0.8319` |
| Complement Naive Bayes | `0.7919` | `0.6716` | `0.8048` |

The selected best model is Logistic Regression because it has the highest Macro
F1 score.

## Dataset References

Used for sentiment training:

- Local file: `data/raw/ppkm_sentiment/INA_TweetsPPKM_Labeled_Pure.csv`
- Source: [Indonesian Twitter Sentiment Analysis Dataset - PPKM](https://www.kaggle.com/datasets/anggapurnama/twitter-dataset-ppkm)

Used for slang normalization:

- Local file: `data/raw/slang_dictionary.csv`
- Source: [new_kamusalay.csv from Ibrohim and Budi's Indonesian hate speech dataset](https://github.com/okkyibrohim/id-multi-label-hate-speech-and-abusive-language-detection)
- Note: the local file is the same as `new_kamusalay.csv`, with the header `slang,formal` added.

Used for summarization examples:

- Local files:
  - `data/raw/indosum_train_00.jsonl`
  - `data/raw/indosum_dev_00.jsonl`
  - `data/raw/indosum_test_00.jsonl`
- Source: [IndoSum](https://github.com/kata-ai/indosum)

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

## Train

Run the supervised sentiment comparison:

```bash
python src/train_sentiment.py
```

The terminal output includes a side-by-side model comparison. The saved training
artifact contains the best model from the comparison:

- `models/ppkm_sentiment_pipeline.pkl`

Matplotlib evaluation plots are saved to:

- `reports/evaluation_metrics.png`
- `reports/model_comparison.png`
- `reports/confusion_matrix.png`

The model comparison table is saved to:

- `reports/model_comparison.csv`

## Predict

Predict one text:

```bash
python src/predict_sentiment.py "PPKM ini bikin masyarakat makin susah"
```

Predict a CSV file:

```bash
python src/predict_sentiment.py --csv-input input.csv --text-column Tweet --output predictions.csv
```

## Streamlit App

Run the web interface locally:

```bash
streamlit run app.py
```

The app loads `models/ppkm_sentiment_pipeline.pkl` and provides one text input
with the predicted sentiment, confidence score, and normalized text as output.

For Streamlit Community Cloud, deploy this repository with `app.py` as the main
file. Keep the trained model artifact inside the `models` directory.

## Notebook

Open `main.ipynb` and run all cells to reproduce the supervised sentiment
experiment and the LexRank/TextRank summarization examples. Evaluation results,
matplotlib metric plots, prediction previews, and summary examples are displayed
inside the notebook.

## Presentation

Presentation-ready materials:

- `presentation/indonesian-sentiment-analyst.pptx`
- `presentation/presentation-material.md`
- `presentation/speaker-notes.md`
