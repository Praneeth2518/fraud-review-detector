import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV

import joblib
import random

# ---- DATA GENERATION ----

genuine_templates = [
    "The product quality is very good and works as expected",
    "I am satisfied with this purchase and delivery was on time",
    "Build quality feels solid and worth the price",
    "Customer support was helpful and resolved my issue",
    "Using this product daily and it performs well",
    "Value for money and easy to use",
    "Product matches the description and packaging was good",
    "Decent performance for this price range",
    "Overall experience has been positive",
    "Would recommend this product to others"
]

fake_templates = [
    "Buy now buy now best product",
    "Limited time offer buy fast",
    "Best product ever must buy now",
    "Excellent excellent excellent excellent",
    "Highly recommended highly recommended",
    "Best price best quality best deal",
    "No one can beat this product",
    "Five stars five stars five stars",
    "Amazing amazing amazing deal deal",
    "100 percent genuine buy now"
]

reviews = []
labels = []

# Generate genuine reviews
for _ in range(500):
    review = random.choice(genuine_templates)
    reviews.append(review)
    labels.append(0)

# Generate fake reviews
for _ in range(500):
    review = random.choice(fake_templates)
    reviews.append(review)
    labels.append(1)

# Shuffle dataset
combined = list(zip(reviews, labels))
random.shuffle(combined)

reviews, labels = zip(*combined)

df = pd.DataFrame({
    "review": reviews,
    "label": labels
})

print("Total reviews:", len(df))
print(df.head())

from sklearn.feature_extraction.text import TfidfVectorizer

# ---- TEXT TO NUMBERS ----
vectorizer = TfidfVectorizer(
    stop_words="english",
    ngram_range=(1, 2),   # unigrams + bigrams
    max_features=1000,
    min_df=1
)


X = vectorizer.fit_transform(df["review"])
y = df["label"]

# ---- TRAIN TEST SPLIT ----
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42
)


print("TF-IDF shape:", X.shape)
from sklearn.linear_model import LogisticRegression

# ---- MODEL TRAINING ----
# ---- HYPERPARAMETER TUNING ----
param_grid = {
    "C": [0.01, 0.1, 1, 10, 100],
    "penalty": ["l2"],
    "solver": ["lbfgs"]
}

grid = GridSearchCV(
    LogisticRegression(max_iter=1000),
    param_grid,
    cv=5,
    scoring="accuracy",
    n_jobs=-1
)

grid.fit(X_train, y_train)

best_model = grid.best_estimator_

print("Best Parameters:", grid.best_params_)



print("Model training completed")
from sklearn.metrics import accuracy_score


# ---- MODEL EVALUATION (TEST DATA ONLY) ----
from sklearn.metrics import accuracy_score, confusion_matrix

# ---- EVALUATION ON TEST DATA ----
predictions = best_model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)
print("Test Accuracy after tuning:", accuracy)

cm = confusion_matrix(y_test, predictions)
print("Confusion Matrix:")
print(cm)




# ---- PREDICT NEW REVIEW ----
def predict_review(text):
    text_vec = vectorizer.transform([text])
    pred = best_model.predict(text_vec)[0]
    prob = best_model.predict_proba(text_vec)[0][pred]

    if pred == 1:
        return f"⚠️ Fake Review (confidence: {prob:.2f})"
    else:
        return f"✅ Genuine Review (confidence: {prob:.2f})"


# Test examples
print(predict_review("This product is really good and worth the money"))
print(predict_review("Buy now buy now best offer limited time"))
# ---- SAVE MODEL & VECTORIZER ----
joblib.dump(best_model, "fake_review_model.pkl")
joblib.dump(vectorizer, "tfidf_vectorizer.pkl")

print("Model and vectorizer saved successfully")
