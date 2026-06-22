# Indonesian Sentiment Analysis Experiment Explanation

## 1. Project Objective

This experiment builds an Indonesian sentiment analysis model for PPKM-related tweets.

The goal is to classify each tweet into one of three sentiment classes:

- `positive`
- `neutral`
- `negative`

The complete workflow is:

```text
load data -> preprocess text -> extract TF-IDF features -> train model -> evaluate model -> predict new text
```

This workflow is used because sentiment analysis is a supervised text classification problem. The model needs labeled text examples, a way to convert text into numerical features, and an algorithm that can learn the relationship between text patterns and sentiment labels.

## 2. Dataset Loading

The main dataset used in this experiment is:

```text
data/raw/ppkm_sentiment/INA_TweetsPPKM_Labeled_Pure.csv
```

This dataset contains Indonesian tweets about PPKM and their sentiment labels.

The dataset has:

```text
23,644 tweets
```

The sentiment label mapping is:

```text
0 = positive
1 = neutral
2 = negative
```

The label distribution is:

| Label | Meaning | Count |
|---|---:|---:|
| 0 | Positive | 1,958 |
| 1 | Neutral | 17,706 |
| 2 | Negative | 3,980 |

The project also loads:

```text
data/raw/slang_dictionary.csv
```

This file contains informal Indonesian words and their formal equivalents. It is used during preprocessing to normalize slang words.

### Concept Used: Supervised Learning

This experiment uses **supervised learning** because the dataset already contains input text and target labels.

In supervised learning, the model learns from examples like:

```text
tweet text -> sentiment label
```

This concept is used because the task is not only to group tweets, but to predict a known category: positive, neutral, or negative.

## 3. Text Preprocessing

Tweets are noisy because they often contain URLs, mentions, hashtags, informal spelling, repeated letters, and slang. Preprocessing is used to make the text cleaner and more consistent before it enters the model.

The preprocessing function is implemented in:

```text
src/train_sentiment.py
```

The main preprocessing steps are:

### 3.1 Lowercasing

All text is converted to lowercase.

Example:

```text
PPKM
```

becomes:

```text
ppkm
```

This is used so the model treats `PPKM`, `Ppkm`, and `ppkm` as the same word.

### 3.2 HTML Unescaping

Some tweets contain HTML entities such as:

```text
&amp;
```

HTML unescaping converts them into their normal form.

This is used because tweets may be collected from web sources where characters are encoded.

### 3.3 URL Removal

URLs are removed from the text.

Example:

```text
https://t.co/abc123
```

is removed.

This is used because URLs usually do not directly represent sentiment and can add noise to the model.

### 3.4 Mention Replacement

Mentions such as:

```text
@username
```

are replaced with:

```text
user
```

This is used because the specific username is usually not important, but the existence of a mention may still be useful.

### 3.5 Hashtag Processing

The hashtag symbol `#` is removed, but the hashtag word is kept.

Example:

```text
#PPKM
```

becomes:

```text
ppkm
```

This is used because hashtag words often contain meaningful topic or sentiment information.

### 3.6 Repeated Character Normalization

Repeated characters are shortened.

Example:

```text
bangettttt
```

becomes:

```text
bangett
```

This is used because informal tweets often exaggerate spelling. Normalizing repeated characters helps reduce unnecessary word variations.

### 3.7 Symbol Removal

Unnecessary symbols and punctuation are removed.

This is used to keep the model focused on words and numbers instead of noisy characters.

### 3.8 Slang Normalization

The slang dictionary is used to replace informal words with formal words.

Example:

```text
yg -> yang
gak -> tidak
loe -> kamu
```

This is used because Indonesian tweets often contain informal language. Slang normalization helps different forms of the same meaning become more consistent.

### Preprocessing Example

Raw tweet:

```text
@user PPKM ini nyusahin bangettt https://t.co/abc
```

After preprocessing:

```text
user ppkm ini menyusahkan bangett
```

## 4. Feature Extraction With TF-IDF

Machine learning models cannot directly understand raw text. The text must first be converted into numerical features.

This experiment uses **TF-IDF**, which stands for **Term Frequency-Inverse Document Frequency**.

### Concept Used: TF-IDF

TF-IDF gives weight to words based on two ideas:

1. **Term Frequency**
   - How often a word appears in a document.

2. **Inverse Document Frequency**
   - How rare or common a word is across all documents.

A word gets a higher TF-IDF value if it appears often in one tweet but is not too common across all tweets.

This is useful for sentiment analysis because words such as:

```text
susah
senang
beban
baik
longgar
```

may help distinguish positive, neutral, and negative sentiment.

The TF-IDF configuration uses:

```text
min_df = 2
max_df = 0.95
max_features = 30000
ngram_range = (1, 2)
sublinear_tf = True
```

### Why These Settings Are Used

| Setting | Meaning | Why It Is Used |
|---|---|---|
| `min_df=2` | Ignore terms that appear in only one document | Reduces rare noise |
| `max_df=0.95` | Ignore terms that appear in more than 95% of documents | Removes overly common terms |
| `max_features=30000` | Keep the top 30,000 features | Limits feature size |
| `ngram_range=(1,2)` | Use single words and two-word phrases | Captures more context than single words only |
| `sublinear_tf=True` | Reduces the effect of repeated terms | Prevents repeated words from dominating |

### Concept Used: N-Grams

The model uses:

- unigrams: single words
- bigrams: two-word phrases

Example:

```text
ppkm susah
masyarakat kecil
tidak setuju
```

Bigrams are used because sentiment can depend on word combinations, not only individual words.

## 5. Model Training

The model used in this experiment is **Logistic Regression**.

The model is trained using the TF-IDF features and the sentiment labels.

### Concept Used: Logistic Regression

Logistic Regression is a supervised classification algorithm. For this project, it learns how text features relate to sentiment classes.

It predicts one of:

```text
positive
neutral
negative
```

### Why Logistic Regression Is Used

Logistic Regression is used because:

- it works well for text classification baselines
- it is fast to train
- it is easier to explain than deep learning models
- it works well with TF-IDF features
- it is suitable for academic experiments and presentations

The model configuration uses:

```text
max_iter = 1000
solver = lbfgs
class_weight = balanced
random_state = 42
```

### Concept Used: Class Weighting

The dataset is imbalanced because most tweets are neutral.

Class distribution:

```text
positive: 1,958
neutral: 17,706
negative: 3,980
```

If the model ignores this imbalance, it may predict `neutral` too often.

The parameter:

```text
class_weight = balanced
```

is used so the model gives more attention to smaller classes such as positive and negative.

## 6. Train/Test Split

The dataset is split into training and testing data.

The split uses:

```text
80% training data
20% testing data
```

The project uses a **stratified split**.

### Concept Used: Stratified Train/Test Split

A stratified split keeps the label distribution similar in both the training and testing data.

This is important because the dataset is imbalanced. Without stratification, the test set might not represent the original label distribution properly.

The split uses:

```text
test_size = 0.2
random_state = 42
stratify = labels
```

`random_state=42` is used to make the experiment reproducible. This means the same split can be generated again.

## 7. Model Evaluation

The model is evaluated on the test set.

The evaluation metrics are:

- Accuracy
- Macro F1
- Weighted F1
- Confusion matrix
- Classification report

### 7.1 Accuracy

Accuracy measures the percentage of predictions that are correct.

```text
accuracy = correct predictions / total predictions
```

Accuracy is easy to understand, but it can be misleading when the dataset is imbalanced.

### 7.2 Precision

Precision measures how many predictions for a class are actually correct.

Example question:

```text
When the model predicts negative, how often is it truly negative?
```

### 7.3 Recall

Recall measures how many actual examples of a class the model successfully finds.

Example question:

```text
Of all actual negative tweets, how many did the model detect?
```

### 7.4 F1-Score

F1-score combines precision and recall.

It is useful when we need a balance between precision and recall.

### 7.5 Macro F1

Macro F1 calculates F1 for each class and then averages them equally.

This is important for this project because the dataset is imbalanced. Macro F1 gives equal importance to positive, neutral, and negative classes.

### 7.6 Weighted F1

Weighted F1 also averages class F1 scores, but it considers the number of examples in each class.

This gives a performance score that reflects the actual class distribution.

### 7.7 Confusion Matrix

A confusion matrix shows how many examples from each true class were predicted as each class.

It helps identify which classes are confused by the model.

## 8. Experiment Results

The experiment result is:

```text
Accuracy: 0.8422
Macro F1: 0.7384
Weighted F1: 0.8506
```

The confusion matrix is:

```text
Rows = true labels
Columns = predicted labels

              predicted_positive  predicted_neutral  predicted_negative
true_positive        263                 70                  59
true_neutral         215               3062                 264
true_negative         56                 82                 658
```

The classification report is:

| Class | Precision | Recall | F1-Score | Support |
|---|---:|---:|---:|---:|
| Positive | 0.49 | 0.67 | 0.57 | 392 |
| Neutral | 0.95 | 0.86 | 0.91 | 3541 |
| Negative | 0.67 | 0.83 | 0.74 | 796 |
| Accuracy |  |  | 0.84 | 4729 |
| Macro Avg | 0.71 | 0.79 | 0.74 | 4729 |
| Weighted Avg | 0.87 | 0.84 | 0.85 | 4729 |

## 9. Result Interpretation

The model achieves strong overall performance with an accuracy of `0.8422`.

The neutral class has the highest F1-score:

```text
neutral F1-score = 0.91
```

This happens because neutral tweets are the largest class in the dataset, giving the model more examples to learn from.

The positive class has the lowest F1-score:

```text
positive F1-score = 0.57
```

This happens because the positive class has fewer examples than the neutral class. Positive tweets may also be harder to distinguish because some positive tweets can look informational or neutral.

The negative class performs reasonably well:

```text
negative F1-score = 0.74
```

This shows that the model is able to detect many negative tweets, although some confusion still exists between negative and neutral sentiment.

## 10. Prediction Usage

After training, the model is saved as:

```text
models/ppkm_sentiment_pipeline.pkl
```

To train the model:

```bash
python src/train_sentiment.py
```

To predict one sentence:

```bash
python src/predict_sentiment.py "PPKM ini bikin masyarakat makin susah"
```

Example output:

```text
negative (0.7358)
```

This means the model predicts the sentence as negative with a confidence score of `0.7358`.

## 11. Summary

This experiment demonstrates a complete Indonesian sentiment analysis pipeline.

The main concepts used are:

- **Supervised learning**, because the dataset has sentiment labels.
- **Text preprocessing**, because tweet text is noisy and informal.
- **Slang normalization**, because Indonesian tweets often contain informal words.
- **TF-IDF**, because machine learning models need numerical text features.
- **N-grams**, because word combinations can carry sentiment meaning.
- **Logistic Regression**, because it is an effective and interpretable baseline for text classification.
- **Class weighting**, because the dataset is imbalanced.
- **Stratified train/test split**, because the label distribution should be preserved during evaluation.
- **Macro F1 and weighted F1**, because accuracy alone is not enough for imbalanced classification.

The final result shows that the model performs well overall, especially on the neutral class, while the positive class remains the most challenging class.
