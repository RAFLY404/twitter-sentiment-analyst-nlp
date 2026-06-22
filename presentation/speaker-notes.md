# Indonesian Sentiment Analyst - Speaker Notes

## Slide 1 - Project Summary
Introduce the project as an Indonesian sentiment-analysis system for PPKM tweets. Explain that the model predicts positive, neutral, or negative sentiment from tweet text.

## Slide 2 - What The Project Uses
Explain the main dataset: 23,644 labeled PPKM tweets. Mention that the slang dictionary helps normalize informal Indonesian language before training.

## Slide 3 - Why Preprocessing Matters
Tweets are noisy because they contain links, mentions, hashtags, repeated letters, and slang. The preprocessing step makes the text more consistent so the model can learn useful patterns.

## Slide 4 - How The Model Works
Explain the model pipeline. Cleaned text is converted into TF-IDF features. Logistic Regression then learns how those features relate to positive, neutral, and negative labels.

## Slide 5 - Model Evaluation
Present the main results: accuracy 0.8422, macro F1 0.7384, weighted F1 0.8506. Explain that macro F1 is important because the dataset is imbalanced.

## Slide 6 - How To Use It
Show the two usage paths. The notebook is useful for explaining the full workflow. The command line is useful for quickly training the model or predicting new text.

## Slide 7 - Project Scope
Explain the boundaries of the system. It is focused on PPKM tweet sentiment. It is a good baseline, but TF-IDF may miss sarcasm or deeper context.

## Slide 8 - Conclusion
Close by summarizing the complete workflow: data loading, preprocessing, TF-IDF feature extraction, Logistic Regression training, evaluation, and prediction.
