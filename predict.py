import joblib

# ---- LOAD SAVED OBJECTS ----
model = joblib.load("fake_review_model.pkl")
vectorizer = joblib.load("tfidf_vectorizer.pkl")

print("Model and vectorizer loaded successfully")
def predict_review(text):
    text_vec = vectorizer.transform([text])
    pred = model.predict(text_vec)[0]
    prob = model.predict_proba(text_vec)[0][pred]

    if pred == 1:
        return f"⚠️ Fake Review (confidence: {prob:.2f})"
    else:
        return f"✅ Genuine Review (confidence: {prob:.2f})"
# ---- TEST ----
print(predict_review("This product quality is good and worth the price"))
print(predict_review("Buy now buy now limited offer best product"))
