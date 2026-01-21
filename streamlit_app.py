import re
import time
import streamlit as st
import pandas as pd

# ============================
# Page Config
# ============================
st.set_page_config(
    page_title="Fraud Review Detector",
    page_icon="🛒",
    layout="centered"
)

# ============================
# Session state init (IMPORTANT for sample buttons)
# ============================
if "review_text" not in st.session_state:
    st.session_state.review_text = ""

if "history" not in st.session_state:
    st.session_state.history = []

# ============================
# Premium Dark UI CSS
# ============================
st.markdown("""
<style>
/* ---- Hide/clean Streamlit top header space (fix covered top) ---- */
header[data-testid="stHeader"] {
    background: transparent;
}
div[data-testid="stToolbar"] {
    visibility: hidden;
    height: 0%;
    position: fixed;
}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* ---- Dark Gradient Background ---- */
.stApp {
    background: radial-gradient(circle at top left, rgba(99,102,241,0.24), transparent 52%),
                radial-gradient(circle at bottom right, rgba(236,72,153,0.18), transparent 55%),
                linear-gradient(135deg, rgba(15,23,42,1) 0%, rgba(2,6,23,1) 100%);
}

/* ---- Layout ---- */
.block-container {
    padding-top: 0.9rem;  /* reduced top padding */
    padding-bottom: 2.2rem;
    max-width: 860px;
}

/* ---- Minimal Header ---- */
.header-wrap {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-bottom: 12px;
}
.brand-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    width: fit-content;
    padding: 7px 12px;
    border-radius: 999px;
    border: 1px solid rgba(255,255,255,0.16);
    background: rgba(255,255,255,0.06);
    backdrop-filter: blur(10px);
    font-weight: 800;
    font-size: 0.9rem;
}
.main-title {
    font-size: 1.65rem;
    font-weight: 900;
    margin: 0;
    line-height: 1.15;
    letter-spacing: -0.4px;
}
.tagline {
    margin-top: -4px;
    color: rgba(255,255,255,0.72);
    font-size: 1.0rem;
}

/* ---- Glass Cards ---- */
.card {
    padding: 18px 18px;
    border-radius: 18px;
    border: 1px solid rgba(255,255,255,0.14);
    background: rgba(255,255,255,0.04);
    backdrop-filter: blur(12px);
    margin-top: 16px;
    transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
}
.card:hover {
    transform: scale(1.01);
    box-shadow: 0px 10px 30px rgba(0,0,0,0.35);
    border-color: rgba(255,255,255,0.22);
}

/* ---- Section titles ---- */
.section-title {
    font-size: 1.03rem;
    font-weight: 850;
    margin-bottom: 0.7rem;
}

/* ---- Muted ---- */
.muted {
    color: rgba(255,255,255,0.70);
    font-size: 0.95rem;
}

/* ---- Pills ---- */
.pill {
    display: inline-block;
    padding: 7px 12px;
    border-radius: 999px;
    font-size: 0.88rem;
    border: 1px solid rgba(255,255,255,0.14);
    background: rgba(255,255,255,0.06);
    margin-right: 10px;
    margin-top: 8px;
    transition: transform 0.15s ease;
}
.pill:hover { transform: scale(1.04); }

/* ---- Buttons (default) ---- */
div.stButton > button {
    border-radius: 14px !important;
    padding: 0.7rem 1rem !important;
    font-weight: 800 !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    background: rgba(255,255,255,0.08) !important;
    color: white !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
div.stButton > button:hover {
    transform: scale(1.03);
    box-shadow: 0px 8px 22px rgba(0,0,0,0.25);
}

/* ---- Make ONLY the Analyze button look special ---- */
div[data-testid="stVerticalBlock"] div:has(> div.stButton > button[kind="primary"]) button {
    background: linear-gradient(90deg, rgba(99,102,241,0.95), rgba(236,72,153,0.90)) !important;
    border: 1px solid rgba(255,255,255,0.14) !important;
}

/* ---- Inputs hover ---- */
textarea, input, select {
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
textarea:hover, input:hover, select:hover {
    transform: scale(1.01);
    box-shadow: 0px 10px 20px rgba(0,0,0,0.22);
}
</style>
""", unsafe_allow_html=True)

# ============================
# Demo signals logic (for UI)
# ============================
SUSPICIOUS_KEYWORDS = [
    "buy now", "must buy", "best product", "amazing", "100% recommended",
    "limited time", "click here", "free", "guaranteed", "life changing",
    "highly recommend", "worth every penny", "perfect", "awesome", "incredible",
]

def analyze_signals(text: str):
    txt = text.lower().strip()
    exclamations = txt.count("!")
    word_count = len(re.findall(r"\w+", txt))
    contains_link = ("http" in txt) or ("www" in txt)
    matches = [kw for kw in SUSPICIOUS_KEYWORDS if kw in txt]
    keyword_hits = len(matches)

    words = re.findall(r"\w+", txt)
    repetition_flag = False
    if len(words) > 0:
        unique_ratio = len(set(words)) / len(words)
        repetition_flag = unique_ratio < 0.55

    caps_ratio = 0.0
    if len(text) > 0:
        caps_ratio = sum(1 for c in text if c.isupper()) / max(1, len(text))

    return {
        "word_count": word_count,
        "exclamations": exclamations,
        "contains_link": contains_link,
        "keyword_hits": keyword_hits,
        "repetition_flag": repetition_flag,
        "caps_ratio": caps_ratio,
        "matched_phrases": matches[:5]
    }

# ============================
# Header (Minimalistic)
# ============================
st.markdown("""
<div class="header-wrap">
  <div class="brand-pill">🛡️ TrustShield AI</div>
  <div class="main-title">Fraud Review Detector</div>
  <div class="tagline">
    Detect fake or incentivized e-commerce reviews with authenticity scoring and transparent signals.
  </div>
</div>
""", unsafe_allow_html=True)

# ============================
# INPUT CARD (single layout)
# ============================
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>📝 Review Input</div>", unsafe_allow_html=True)

product_name = st.text_input("Product Name (optional)", placeholder="Wireless Earbuds")
rating = st.selectbox("Rating Given", [1, 2, 3, 4, 5], index=4)

st.text_area(
    "Review Text",
    height=170,
    key="review_text",
    placeholder="Example: BEST PRODUCT EVER!!! Must buy now!!! 100% recommended!!!"
)

st.markdown("<div class='muted'>Quick fill samples:</div>", unsafe_allow_html=True)
b1, b2, b3 = st.columns(3)

if b1.button("🚨 Fake Sample", use_container_width=True):
    st.session_state.review_text = "This product is AMAZING!!! Must buy now!!! Best product ever!!! 100% recommended!!!"

if b2.button("✅ Genuine Sample", use_container_width=True):
    st.session_state.review_text = "The quality is good for the price. Battery lasts around 5-6 hours. Delivery was on time."

if b3.button("🧹 Clear", use_container_width=True):
    st.session_state.review_text = ""

st.markdown("<br>", unsafe_allow_html=True)
analyze_btn = st.button("🔍 Analyze Review", type="primary", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

# ============================
# RESULT CARD
# ============================
if analyze_btn:
    text = st.session_state.review_text.strip()

    if not text:
        st.warning("Please enter a review text.")
    else:
        with st.spinner("Analyzing review..."):
            time.sleep(0.55)

        signals = analyze_signals(text)

        # Demo scoring (UI phase)
        suspicious_score = 0
        if rating == 5 and signals["word_count"] <= 8:
            suspicious_score += 2
        if signals["exclamations"] >= 3:
            suspicious_score += 2
        if signals["caps_ratio"] > 0.25:
            suspicious_score += 1
        if signals["keyword_hits"] >= 2:
            suspicious_score += 2
        if signals["repetition_flag"]:
            suspicious_score += 1
        if signals["contains_link"]:
            suspicious_score += 2

        label = "fake" if suspicious_score >= 4 else "genuine"
        confidence = min(0.95, 0.55 + (suspicious_score * 0.10))

        risk_score = int(confidence * 100) if label == "fake" else int((1 - confidence) * 100)
        authenticity_score = 100 - risk_score
        flagged = risk_score >= 60

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>✅ Detection Result</div>", unsafe_allow_html=True)

        if label == "fake":
            st.error("🚩 **Suspicious / Fake Review Detected**")
        else:
            st.success("✅ **Review Looks Genuine**")

        m1, m2, m3 = st.columns(3)
        m1.metric("Confidence", f"{round(confidence*100, 1)}%")
        m2.metric("Authenticity Score", f"{authenticity_score}/100")
        m3.metric("Flag Status", "FLAGGED 🚩" if flagged else "Not Flagged ✅")

        st.markdown("**Risk Meter**")
        st.progress(risk_score)

        st.markdown("<div class='section-title'>🔍 Rating Transparency</div>", unsafe_allow_html=True)
        st.markdown(f"<span class='pill'>⭐ Rating: {rating}</span>", unsafe_allow_html=True)
        st.markdown(f"<span class='pill'>🧾 Words: {signals['word_count']}</span>", unsafe_allow_html=True)
        st.markdown(f"<span class='pill'>❗ Exclamations: {signals['exclamations']}</span>", unsafe_allow_html=True)
        st.markdown(f"<span class='pill'>🏷️ Keyword Hits: {signals['keyword_hits']}</span>", unsafe_allow_html=True)
        st.markdown(
            f"<span class='pill'>🔗 Link: {'Found' if signals['contains_link'] else 'None'}</span>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<span class='pill'>🔁 Repetition: {'Yes' if signals['repetition_flag'] else 'No'}</span>",
            unsafe_allow_html=True
        )

        st.markdown("<div class='section-title'>🧠 Explanation</div>", unsafe_allow_html=True)
        explanation = []
        if rating == 5 and signals["word_count"] <= 8:
            explanation.append("Very short 5-star review")
        if signals["exclamations"] >= 3:
            explanation.append("Excessive punctuation")
        if signals["caps_ratio"] > 0.25:
            explanation.append("Too many capital letters")
        if signals["keyword_hits"] >= 2:
            explanation.append("Promotional keywords detected")
        if signals["repetition_flag"]:
            explanation.append("Unnatural repetition of words")
        if signals["contains_link"]:
            explanation.append("Contains suspicious link")
        if signals["matched_phrases"]:
            explanation.append("Matched phrases: " + ", ".join(signals["matched_phrases"]))

        if explanation:
            for r in explanation:
                st.write("•", r)
        else:
            st.write("No strong suspicious patterns detected.")

        st.markdown("<div class='section-title'>🧾 Review Snapshot</div>", unsafe_allow_html=True)
        st.code(text, language="text")

        # Save in session dashboard
        snippet = text.replace("\n", " ")
        snippet = snippet[:60] + "..." if len(snippet) > 60 else snippet

        st.session_state.history.insert(0, {
            "Product": product_name if product_name else "N/A",
            "Rating": rating,
            "Result": "Fake" if label == "fake" else "Genuine",
            "Authenticity": authenticity_score,
            "Flagged": "Yes" if flagged else "No",
            "Snippet": snippet
        })

        st.markdown("</div>", unsafe_allow_html=True)

# ============================
# MINI DASHBOARD
# ============================
if len(st.session_state.history) > 0:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>📊 Transparency Dashboard</div>", unsafe_allow_html=True)
    st.markdown("<div class='muted'>Recent detections in this session</div>", unsafe_allow_html=True)

    df = pd.DataFrame(st.session_state.history[:6])
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("</div>", unsafe_allow_html=True)