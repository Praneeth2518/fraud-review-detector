import streamlit as st
import joblib
import re

# ----------------------------
# Load Model
# ----------------------------
model = joblib.load("fake_review_model.pkl")
vectorizer = joblib.load("tfidf_vectorizer.pkl")

# ----------------------------
# Page Config
# ----------------------------
st.set_page_config(
    page_title="Fraud Review Detector",
    page_icon="🕵️",
    layout="wide"
)

# ----------------------------
# Custom CSS (Premium++)
# ----------------------------
st.markdown("""
<style>
body { background-color: #0e1117; }
.card {
    background-color: #161b22;
    padding: 25px;
    border-radius: 16px;
    box-shadow: 0 0 30px rgba(0,0,0,0.4);
}
.pill {
    display: inline-block;
    background-color: #2a2f3a;
    color: #facc15;
    padding: 6px 12px;
    margin: 4px;
    border-radius: 20px;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Title
# ----------------------------
st.markdown("<h1 style='text-align:center;'>🕵️ AI Fraud Review Detector</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:gray;'>High-tech AI system for detecting fake & suspicious reviews</p>", unsafe_allow_html=True)
st.divider()

# ----------------------------
# Inputs
# ----------------------------
col1, col2 = st.columns(2)

with col1:
    product = st.text_input("📦 Product Name (optional)")
    rating = st.slider("⭐ Rating Given", 1, 5, 5)

with col2:
    review_text = st.text_area(
        "📝 Paste Review Text",
        height=160,
        placeholder="Example: This product is amazing, best deal ever, buy now!"
    )

# ----------------------------
# Helper: Suspicious Signals
# ----------------------------
def detect_signals(text):
    reasons = []
    text_lower = text.lower()

    if len(text.split()) < 6:
        reasons.append("Very short review (low information content)")

    if len(re.findall(r"(buy now|limited offer|best product)", text_lower)) > 0:
        reasons.append("Promotional / urgency keywords detected")

    if len(set(text_lower.split())) < len(text_lower.split()) * 0.6:
        reasons.append("High word repetition (spam-like pattern)")

    if sum(1 for c in text if c.isupper()) > 10:
        reasons.append("Excessive capital letters")

    return reasons


# ----------------------------
# Automated Abnormal Activity Flags
# ----------------------------
def abnormal_activity_flag(label, risk_score, reasons, rating):
    flags = []

    if label == "fake" and risk_score > 70:
        flags.append("High-risk fake review detected")

    if len(reasons) >= 2:
        flags.append("Multiple suspicious linguistic signals")

    if rating >= 4 and label == "fake":
        flags.append("Rating–content mismatch (high rating, fake text)")

    if rating == 5 and any("Promotional" in r for r in reasons):
        flags.append("Possible incentivized or paid review")

    return flags




# ----------------------------
# Predict Button
# ----------------------------
if st.button("🔍 Analyze Review", use_container_width=True):
    if review_text.strip() == "":
        st.warning("⚠️ Please enter a review.")
    else:
        vec = vectorizer.transform([review_text])
        pred = model.predict(vec)[0]
        confidence = model.predict_proba(vec)[0][pred]

        label = "fake" if pred == 1 else "genuine"
        reasons = detect_signals(review_text)


        # ----------------------------
        # Results Card (Premium++)
        # ----------------------------
        st.markdown('<div class="card">', unsafe_allow_html=True)

        # Risk & Trust Scores
        risk_score = int(confidence * 100) if label == "fake" else int((1 - confidence) * 100)

# Boost risk if suspicious signals exist
        risk_score += min(len(reasons) * 5, 20)
        risk_score = min(risk_score, 100)

        trust_score = 100 - risk_score

# Get automated flags
        flags = abnormal_activity_flag(label, risk_score, reasons, rating)


        if label == "fake":
            st.error("🚨 Prediction: **Fake Review**")
        else:
            st.success("✅ Prediction: **Genuine Review**")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Confidence", f"{round(confidence*100, 1)}%")
        m2.metric("Risk Score", f"{risk_score}/100")
        m3.metric("Trust Score", f"{trust_score}/100")
        m4.metric("Rating", f"{rating} ⭐")

        st.markdown("### 📊 Risk Meter")
        st.progress(risk_score)

        st.markdown("### 🚩 Automated Flags")

        if flags:
            for f in flags:
                st.warning(f"⚠️ {f}")
        else:
            st.success("✅ No abnormal review activity detected")

        if reasons:
            for r in reasons:
                st.markdown(f'<span class="pill">⚠️ {r}</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="pill">✅ No suspicious signals</span>', unsafe_allow_html=True)

        st.markdown("### 📝 Explanation")
        if reasons:
            for r in reasons:
                st.write("•", r)
        else:
            st.write("No strong suspicious signals detected.")

        st.markdown("### 🧾 Review Snapshot")
        st.code(review_text, language="text")

        # ----------------------------
        # Download Report
        # ----------------------------
        report = f"""
Fraud Review Detector Report
---------------------------
Product: {product if product else "N/A"}
Rating: {rating}
Prediction: {"Fake" if label == "fake" else "Genuine"}
Confidence: {round(confidence*100, 1)}%
Risk Score: {risk_score}/100
Trust Score: {trust_score}/100

Review:
{review_text}

Reasons:
- {"; ".join(reasons) if reasons else "No suspicious signals detected"}
""".strip()

        st.download_button(
            label="📄 Download Report",
            data=report,
            file_name="fraud_review_report.txt",
            mime="text/plain"
        )

        st.markdown('</div>', unsafe_allow_html=True)

        # ----------------------------
        # Future Scope
        # ----------------------------
        with st.expander("🚀 Future Scope (for judges)"):
            st.write("✅ Train TF-IDF + Logistic Regression model for real ML predictions")
            st.write("✅ User-behavior signals & burst review detection")
            st.write("✅ Product-level trust analytics dashboard")
            st.write("✅ Batch CSV upload & trend analysis")
