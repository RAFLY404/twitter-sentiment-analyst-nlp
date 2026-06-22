# Indonesian Sentiment Analyst - Presentation Material

## Opening

This project is an Indonesian NLP project that focuses on sentiment analysis for PPKM-related tweets. The goal is to classify each tweet into one of three sentiment classes: positive, neutral, or negative.

## What The Project Does

The project processes Indonesian tweets, cleans the text, converts the text into numerical features, trains a machine learning model, evaluates the model, and allows new text to be predicted from the command line.

The main sentiment labels are:

- `0 = positive`
- `1 = neutral`
- `2 = negative`

The project also includes simple extractive summarization examples using LexRank and TextRank with the IndoSum dataset.

## Why The Project Is Useful

Social media contains public opinion in informal language. During events like PPKM, tweets can show support, criticism, or neutral information. Sentiment analysis helps convert large amounts of tweet text into structured information that is easier to analyze.

This project is useful for an NLP presentation because it demonstrates a complete pipeline:

```text
dataset -> preprocessing -> feature extraction -> model training -> evaluation -> prediction
```

## Dataset

The sentiment model uses the labeled PPKM Twitter dataset:

```text
data/raw/ppkm_sentiment/INA_TweetsPPKM_Labeled_Pure.csv
```

The dataset contains `23,644` labeled tweets.

The project also uses:

```text
data/raw/slang_dictionary.csv
```

This slang dictionary helps normalize informal Indonesian words into more formal versions.

## Preprocessing

The preprocessing step prepares noisy tweet text before it enters the model.

It performs:

- lowercasing
- HTML unescaping
- URL removal
- mention replacement
- hashtag symbol removal while keeping the hashtag word
- repeated-character normalization
- symbol removal
- slang normalization

Example:

```text
@user PPKM ini nyusahin bangettt https://t.co/abc
```

becomes:

```text
user ppkm ini menyusahkan bangett
```

## Model

The model uses TF-IDF and Logistic Regression.

TF-IDF converts text into numerical features. It gives more importance to words or phrases that are useful for distinguishing documents.

The TF-IDF setup uses:

- single words
- two-word phrases
- maximum 30,000 features
- Indonesian stopword removal

Logistic Regression is used as the classifier because it is fast, interpretable, and effective for text-classification baselines.

The model predicts:

```text
positive / neutral / negative
```

## Evaluation

The model is evaluated using a stratified train/test split.

Current results:

```text
Accuracy: 0.8422
Macro F1: 0.7384
Weighted F1: 0.8506
```

Macro F1 is important because the dataset is imbalanced. Neutral tweets appear much more often than positive tweets, so accuracy alone does not fully describe the model quality.

## How To Run

Train the model:

```bash
python src/train_sentiment.py
```

Predict one sentence:

```bash
python src/predict_sentiment.py "PPKM ini bikin masyarakat makin susah"
```

Example output:

```text
negative (0.7358)
```

## Limitations

The model is a strong baseline, but it has limitations:

- It is trained on PPKM-related tweets, so its domain is specific.
- The dataset is imbalanced.
- TF-IDF does not deeply understand sarcasm or context.
- LexRank and TextRank summarization are extractive baselines.

## Closing

The project demonstrates a complete and reproducible Indonesian sentiment-analysis workflow. It starts from raw tweet data, applies preprocessing, trains a supervised model, evaluates the results, and supports prediction for new text.
