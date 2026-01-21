import re
import time
import streamlit as st

# ============================
# Page Config
# ============================
st.set_page_config(
    page_title="Fraud Review Detector",
    page_icon="🛒",
    layout="wide"
)

# ============================
# Premium CSS
# ============================
st.markdown("""
<style>
    .block-container {
        padding-top: 1.4rem;
        padding-bottom: 1.6rem;
    }

    /* Top header area */
    .topbar {
        padding: 18px 18px;
        border-radius: 18px;
        border: 1px solid rgba(255,255,255,0.12);
        background: rgba(255,255,255,0.03);
        margin-bottom: 18px;
    }

    .app-title {
        font-size: 1.8rem;
        font-weight: 900;
        margin: 0;
        padding: 0;
    }

    .app-subtitle {
        margin-top: 6px;
        color: rgba(255,255,255,0.72);
        font-size: 1rem;
    }

    .panel {
        padding: 18px;
        border-radius: 18px;
        border: 1px solid rgba(255,255,255,0.12);
        background: rgba(255,255,255,0.03);
    }

    .pill {
        display: inline-block;
        padding: 7px 12px;
        border-radius: 999px;
        font-size: 0.88rem;
        border: 1px solid rgba(255,255,255,0.14);
        background: rgba(255,255,255,0.05);
        margin-right: 10px;
        margin-top: 8px;
    }

    .muted {
        color: rgba(255,255,255,0.70);
        font-size: 0.95rem;
    }

    /* Make buttons look cleaner */
    div.stButton > button {
        border-radius: 14px !important;
        padding: 0.65rem 1rem !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================
# Demo AI Logic (Rule-based)
# ============================
SUSPICIOUS_KEYWORDS = [
    "buy now", "must buy", "best product", "amazing", "100% recommended",
    "limited time", "click here", "free", "guaranteed", "life changing",
    "highly recommend", "worth every penny", "perfect", "awesome", "incredible",
]

def analyze_review_rule_based(text: str, rating: int):
    txt = text.lower().strip()

    exclamations = txt.count("!")
    word_count = len(re.findall(r"\w+", txt))

    caps_ratio = 0.0
    if len(text) > 0:
        caps_ratio = sum(1 for c in text if c.isupper()) / max(1, len(text))

    matches = [kw for kw in SUSPICIOUS_KEYWORDS if kw in txt]

    # repetition: fewer unique words -> suspicious
    words = re.findall(r"\w+", txt)
    repetition_flag = False
    if len(words) > 0:
        unique_ratio = len(set(words)) / len(words)
        repetition_flag = unique_ratio < 0.55

    contains_link = ("http" in txt) or ("www" in txt)

    score = 0
    reasons = []

    if rating == 5 and word_count <= 8:
        score += 2
        reasons.append("Very short 5-star review")

    if exclamations >= 3:
        score += 2
        reasons.append("Excessive punctuation")

    if caps_ratio > 0.25:
        score += 1
        reasons.append("Too many capital letters")

    if len(matches) >= 2:
        score += 2
        reasons.append("Promotional keywords detected")

    if repetition_flag:
        score += 1
        reasons.append("Unnatural repetition of words")

    if contains_link:
        score += 2
        reasons.append("Contains suspicious link")

    label = "fake" if score >= 4 else "genuine"
    confidence = min(0.95, 0.55 + (score * 0.10))

    # add matched phrases (optional)
    if matches:
        reasons.append("Matched phrases: " + ", ".join(matches[:5]))

    # risk score: higher for fake, lower for genuine
    risk_score = int(confidence * 100) if label == "fake" else int((1 - confidence) * 100)
    trust_score = 100 - risk_score

    signals = {
        "exclamations": exclamations,
        "word_count": word_count,
        "caps_ratio": caps_ratio,
        "keyword_matches": len(matches),
        "contains_link": contains_link,
        "repetition_flag": repetition_flag
    }

    return label, confidence, risk_score, trust_score, reasons, signals

# ============================
# Header / Topbar
# ============================
st.markdown("""
<div class="topbar">
  <div class="app-title">🛒 Fraud Review Detector</div>
  <div class="app-subtitle">
    Analyze e-commerce reviews and detect suspicious patterns with explainable signals.
  </div>
</div>
""", unsafe_allow_html=True)

# ============================
# Layout: Input (Left) + Output (Right)
# ============================
left, right = st.columns([1.05, 1])

with left:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("Review Input")

    product = st.text_input("Product Name (optional)", placeholder="Wireless Earbuds")
    rating = st.selectbox("Rating", [1, 2, 3, 4, 5], index=4)

    review_text = st.text_area(
        "Review Text",
        height=180,
        placeholder="Example: BEST PRODUCT EVER!!! Buy now!!! Totally worth it!!!"
    )

    b1, b2, b3 = st.columns(3)

    if b1.button("🚨 Fake Sample"):
        review_text = "This product is AMAZING!!! Must buy now!!! Best product ever!!! 100% recommended!!!"

    if b2.button("✅ Genuine Sample"):
        review_text = "The quality is good for the price. Battery lasts around 5-6 hours. Delivery was on time."

    if b3.button("🧹 Clear"):
        review_text = ""

    analyze = st.button("🔍 Analyze", type="primary")

    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("Detection Result")
    st.markdown('<div class="muted">Submit a review from the left panel to see the analysis.</div>', unsafe_allow_html=True)

    if analyze:
        if not review_text.strip():
            st.warning("Please enter a review text.")
        else:
            with st.spinner("Analyzing review..."):
                time.sleep(0.55)

            label, confidence, risk, trust, reasons, signals = analyze_review_rule_based(review_text, rating)

            # Result Banner
            if label == "fake":
                st.error("🚨 **Fake Review Detected**")
            else:
                st.success("✅ **Review Looks Genuine**")

            # Metrics Row
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Confidence", f"{round(confidence * 100, 1)}%")
            c2.metric("Risk Score", f"{risk}/100")
            c3.metric("Trust Score", f"{trust}/100")
            c4.metric("Rating", f"{rating} ⭐")

            st.markdown("### Risk Meter")
            st.progress(risk)

            # Signals
            st.markdown("### Signals")
            st.markdown(f'<span class="pill">🧾 Words: {signals["word_count"]}</span>', unsafe_allow_html=True)
            st.markdown(f'<span class="pill">❗ Exclamations: {signals["exclamations"]}</span>', unsafe_allow_html=True)
            st.markdown(f'<span class="pill">🔠 Caps Ratio: {round(signals["caps_ratio"]*100, 1)}%</span>', unsafe_allow_html=True)
            st.markdown(f'<span class="pill">🏷️ Keyword Hits: {signals["keyword_matches"]}</span>', unsafe_allow_html=True)

            if signals["contains_link"]:
                st.markdown('<span class="pill">🔗 Link Found</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="pill">🔗 No Link</span>', unsafe_allow_html=True)

            if signals["repetition_flag"]:
                st.markdown('<span class="pill">🔁 Repetition Detected</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="pill">🔁 Normal Text</span>', unsafe_allow_html=True)

            # Reasons
            st.markdown("### Explanation")
            if reasons:
                for r in reasons:
                    st.write("•", r)
            else:
                st.write("No strong suspicious patterns detected.")

            # Snapshot
            st.markdown("### Review Snapshot")
            st.code(review_text, language="text")

            # Download report
            report = f"""
Fraud Review Detector Report
---------------------------
Product: {product if product else "N/A"}
Rating: {rating}
Prediction: {"Fake" if label == "fake" else "Genuine"}
Confidence: {round(confidence*100, 1)}%
Risk Score: {risk}/100
Trust Score: {trust}/100

Review Text:
{review_text}

Signals:
- Words: {signals["word_count"]}
- Exclamations: {signals["exclamations"]}
- Caps Ratio: {round(signals["caps_ratio"]*100, 1)}%
- Keyword Hits: {signals["keyword_matches"]}
- Link Found: {signals["contains_link"]}
- Repetition Detected: {signals["repetition_flag"]}

Explanation:
- {"; ".join(reasons) if reasons else "No suspicious patterns"}
""".strip()

            st.download_button(
                "📄 Download Report",
                data=report,
                file_name="fraud_review_report.txt",
                mime="text/plain"
            )

    st.markdown('</div>', unsafe_allow_html=True)
