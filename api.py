from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib

# ---- INIT APP ----
app = Flask(__name__)
CORS(app)  # allow frontend requests

# ---- LOAD MODEL ----
model = joblib.load("fake_review_model.pkl")
vectorizer = joblib.load("tfidf_vectorizer.pkl")

# ---- PREDICTION FUNCTION ----
def predict_review(text):
    vec = vectorizer.transform([text])
    pred = model.predict(vec)[0]
    prob = model.predict_proba(vec)[0][pred]

    return {
        "prediction": "fake" if pred == 1 else "genuine",
        "confidence": round(float(prob) * 100, 2)
    }

# ---- API ROUTE ----
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()

    if not data or "review" not in data:
        return jsonify({"error": "Review text missing"}), 400

    result = predict_review(data["review"])
    return jsonify(result)

# ---- RUN SERVER ----
if __name__ == "__main__":
    app.run(debug=True)
