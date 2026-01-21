import re
import time
import streamlit as st

# ----------------------------
# Page Config
# ----------------------------
st.set_page_config(
    page_title="Fraud Review Detector",
    page_icon="🛒",
    layout="centered",
)

# ----------------------------
# Premium Styling (CSS)
# ----------------------------
st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 900px;
    }
    .title {
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        color: rgba(255,255,255,0.75);
        margin-bottom: 1.2rem;
    }
    .card {
        padding: 18px;
        border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.12);
        background: rgba(255,255,255,0.03);
    }
    .mini {
        color: rgba(255,255,255,0.75);
        font-size: 0.95rem;
    }
    .pill {
        display: inline-block;
        padding: 6px 10px;
        border-radius: 999px;
        font-size: 0.85rem;
        border: 1px solid rgba(255,255,255,0.15);
        background: rgba(255,255,255,0.05);
        margin-right: 8px;
        margin-top: 6px;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Helpers (Rule-Based "Demo AI")
# ----------------------------
SUSPICIOUS_KEYWORDS = [
    "buy now", "must buy", "best product", "amazing", "100% recommended",
    "limited time", "click here", "free", "guaranteed", "life changing",
    "highly recommend", "worth every penny", "perfect", "awesome", "incredible",
]

def analyze_review_rule_based(text: str, rating: int):
    txt = text.lower().strip()

    # Basic signals
    exclamations = txt.count("!")
    caps_ratio = 0.0
    if len(text) > 0:
        caps_ratio = sum(1 for c in text if c.isupper()) / max(1, len(text))

    word_count = len(re.findall(r"\w+", txt))

    # Keyword matches
    matches = []
    for kw in SUSPICIOUS_KEYWORDS:
        if kw in txt:
            matches.append(kw)

    # Repetition check (simple)
    words = re.findall(r"\w+", txt)
    repetition_score = 0
    if len(words) > 0:
        unique_ratio = len(set(words)) / len(words)
        if unique_ratio < 0.55:
            repetition_score = 1

    # Scoring
    score = 0
    reasons = []

    if rating == 5 and word_count <= 8:
        score += 2
        reasons.append("Very short 5-star review (common fake pattern)")

    if exclamations >= 3:
        score += 2
        reasons.append("Excessive exclamation marks")

    if caps_ratio > 0.25:
        score += 1
        reasons.append("Too many capital letters (shouting tone)")

    if len(matches) >= 2:
        score += 2
        reasons.append("Promotional keywords detected")

    if repetition_score == 1:
        score += 1
        reasons.append("Unnatural repetition of words")

    if "http" in txt or "www" in txt:
        score += 2
        reasons.append("Contains links (often suspicious in reviews)")

    # Decide label
    if score >= 4:
        label = "fake"
    else:
        label = "genuine"

    # Confidence (fake: higher with score)
    confidence = min(0.95, 0.55 + (score * 0.10))

    # Add keyword pills
    if matches:
        reasons.append("Matched phrases: " + ", ".join(matches[:5]))

    return label, confidence, reasons

# ----------------------------
# Header
# ----------------------------
st.markdown('<div class="title">🛒 Fraud Review Detector</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Detect suspicious e-commerce reviews using AI-style signals (fast MVP). '
    'Connect ML later for final scoring.</div>',
    unsafe_allow_html=True
)

# ----------------------------
# Sidebar (Premium)
# ----------------------------
with st.sidebar:
    st.header("⚙️ Controls")
    mode = st.radio("Detection Mode", ["Demo AI (Rule-based)", "ML Model (Coming Soon)"], index=0)
    st.divider()

    st.markdown("### ✅ Hackathon Tips")
    st.markdown(
        "- Keep demo smooth\n"
        "- Show 2 examples (fake + genuine)\n"
        "- Explain features & impact\n"
    )

    st.divider()
    st.markdown("### 📌 Output")
    st.markdown("Label + Confidence + Reasons")

# ----------------------------
# Main Input Card
# ----------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)

col1, col2 = st.columns([2.2, 1])
with col1:
    review_text = st.text_area(
        "Review Text",
        height=160,
        placeholder="Example: BEST PRODUCT EVER!!! Buy now!!! Totally worth it!!!"
    )

with col2:
    rating = st.selectbox("Rating", [1, 2, 3, 4, 5], index=4)
    product = st.text_input("Product (optional)", placeholder="Wireless Earbuds")
    st.caption("Tip: Rating + text improves detection quality.")

st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------
# Sample Buttons
# ----------------------------
c1, c2, c3 = st.columns(3)

if c1.button("🚨 Try Fake Sample"):
    st.session_state["sample"] = "This product is AMAZING!!! Must buy now!!! Best product ever!!! 100% recommended!!!"

if c2.button("✅ Try Genuine Sample"):
    st.session_state["sample"] = "The quality is good for the price. Battery lasts around 5-6 hours. Delivery was on time."

if c3.button("🧹 Clear"):
    st.session_state["sample"] = ""

if "sample" in st.session_state and st.session_state["sample"] != "":
    review_text = st.session_state["sample"]

# ----------------------------
# Analyze
# ----------------------------
analyze = st.button("🔍 Analyze Review", type="primary")

if analyze:
    if not review_text.strip():
        st.warning("Please enter a review text.")
    else:
        with st.spinner("Analyzing..."):
            time.sleep(0.6)

        if mode == "Demo AI (Rule-based)":
            label, confidence, reasons = analyze_review_rule_based(review_text, rating)
        else:
            st.error("ML mode not connected yet. Use Demo AI for now ✅")
            st.stop()

        # ----------------------------
        # Results Card
        # ----------------------------
        st.markdown('<div class="card">', unsafe_allow_html=True)

        if label == "fake":
            st.error("🚨 Prediction: **Fake Review**")
        else:
            st.success("✅ Prediction: **Genuine Review**")

        m1, m2, m3 = st.columns(3)
        m1.metric("Confidence", f"{round(confidence*100, 1)}%")
        m2.metric("Rating", f"{rating} ⭐")
        m3.metric("Review Length", f"{len(review_text.split())} words")

        st.progress(int(confidence * 100))

        st.markdown("### 🧠 Reasons")
        if reasons:
            for r in reasons:
                st.write("•", r)
        else:
            st.write("No strong suspicious signals detected.")

        st.markdown("### 🧾 Review Snapshot")
        st.code(review_text, language="text")

        st.markdown('</div>', unsafe_allow_html=True)

        # ----------------------------
        # Future Scope
        # ----------------------------
        with st.expander("🚀 Future Scope (for judges)"):
            st.write("✅ Train TF-IDF + Logistic Regression model")
            st.write("✅ User-based signals: repeated posting patterns")
            st.write("✅ Product-level trust score dashboard")
            st.write("✅ Batch CSV upload + analytics")

# Footer
st.caption("Built for hackathon MVP ⚡ | Streamlit UI + explainable signals")
