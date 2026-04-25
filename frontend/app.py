import streamlit as st
import requests
import os

st.set_page_config(
    page_title="FinScope Earnings Analyzer",
    page_icon="📈",
    layout="wide"
)

SENTIMENT_CONFIG = {
    "Positive": {"icon": "🟢", "fn": st.success, "label": "Positive Outlook"},
    "Neutral":  {"icon": "🟡", "fn": st.info,    "label": "Neutral Outlook"},
    "Negative": {"icon": "🔴", "fn": st.error,   "label": "Negative Outlook"},
}

st.title("📈 FinScope Earnings Call Analyzer")
st.markdown("Powered by **Mistral via Ollama** · FastAPI backend · Streamlit frontend")
st.caption("For FinScope Capital — Investment Research Division")
st.divider()

# Sidebar
with st.sidebar:
    st.header("⚙️ Options")

    sample_path = os.path.join(
        os.path.dirname(__file__), "..", "data", "tesla_q4_2024.txt"
    )
    if st.button("📂 Load Tesla Q4 2024 Sample", use_container_width=True):
        try:
            with open(sample_path, "r") as f:
                st.session_state["sample_text"] = f.read()
            st.success("Sample loaded!")
        except FileNotFoundError:
            st.error("Sample file not found.")

    uploaded_file = st.file_uploader(
        "Or upload a .txt transcript:",
        type=["txt"],
        help="Upload a plain text earnings call transcript"
    )
    if uploaded_file:
        st.session_state["sample_text"] = uploaded_file.read().decode("utf-8")
        st.success(f"Loaded: {uploaded_file.name}")

    st.divider()
    st.subheader("📌 Output Sections")
    st.markdown("""
- 📝 **3-sentence summary**
- 📊 **Sentiment classification**
- 💡 **Financial insights:**
  - Revenue & Growth
  - Forward Guidance
  - Risk Factors
  - Strategic Signals
    """)

# Text input
default_text = st.session_state.get("sample_text", "")

call_text = st.text_area(
    "Paste earnings call transcript here:",
    value=default_text,
    height=300,
    placeholder="[CEO]: We had a strong quarter with revenue up 15%...",
)

if call_text.strip():
    wc = len(call_text.split())
    cc = len(call_text)
    st.caption(f"📊 Words: {wc:,} · Characters: {cc:,}")
    if cc > 60000:
        st.error("❌ Transcript exceeds 60,000 character limit. Please trim the text.")

col1, _ = st.columns([1, 5])
with col1:
    analyze_btn = st.button("🔍 Analyze Call", type="primary", use_container_width=True)

if analyze_btn:
    if not call_text.strip():
        st.warning("⚠️ Please paste or upload an earnings call transcript.")
    elif len(call_text) > 60000:
        st.error("❌ Document too large. Reduce to under 60,000 characters.")
    else:
        with st.spinner("Running 3 analysis tasks with Mistral..."):
            try:
                response = requests.post(
                    "http://localhost:8000/analyze/",
                    data={"text": call_text},
                    timeout=360
                )

                if response.status_code == 200:
                    output = response.json()

                    # Metadata
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Words Analyzed", f"{output.get('word_count', 0):,}")
                    m2.metric("Characters", f"{output.get('char_count', 0):,}")
                    sentiment_val = output.get("sentiment", "Neutral")
                    cfg = SENTIMENT_CONFIG.get(sentiment_val, SENTIMENT_CONFIG["Neutral"])
                    m3.metric("Sentiment", f"{cfg['icon']} {sentiment_val}")

                    st.divider()

                    # Sentiment banner
                    cfg["fn"](f"**Market Sentiment: {cfg['icon']} {cfg['label']}**")

                    st.divider()

                    # Results in tabs
                    tab1, tab2 = st.tabs(["📝 Summary & Sentiment", "💡 Financial Insights"])

                    with tab1:
                        st.subheader("📝 Earnings Call Summary")
                        st.markdown(output.get("summary", "No summary generated."))

                        st.subheader("📊 Sentiment Analysis")
                        cfg["fn"](f"**{cfg['icon']} {output.get('sentiment', 'N/A')}**")

                    with tab2:
                        st.subheader("💡 Key Financial Insights")
                        st.markdown(output.get("insights", "No insights extracted."))

                    st.divider()

                    # Full report download
                    report = (
                        f"FINSCOPE CAPITAL — EARNINGS CALL ANALYSIS\n"
                        f"{'=' * 60}\n\n"
                        f"SENTIMENT: {output.get('sentiment', 'N/A')}\n\n"
                        f"SUMMARY\n{'-' * 40}\n{output.get('summary', '')}\n\n"
                        f"KEY FINANCIAL INSIGHTS\n{'-' * 40}\n{output.get('insights', '')}\n"
                    )
                    st.download_button(
                        label="⬇️ Download Full Analysis Report (.txt)",
                        data=report,
                        file_name="finscope_earnings_analysis.txt",
                        mime="text/plain",
                        use_container_width=True
                    )

                elif response.status_code == 400:
                    st.error(f"❌ {response.json().get('detail', 'Bad request.')}")
                elif response.status_code == 413:
                    st.error("❌ Transcript too large. Please trim to under 60,000 characters.")
                elif response.status_code == 503:
                    st.error("❌ Ollama is not running. Start it with `ollama serve`.")
                else:
                    st.error(f"❌ Server error {response.status_code}: {response.text}")

            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot reach the backend. Run `uvicorn backend.main:app --reload`.")
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out. Long transcripts take time — try a shorter excerpt.")
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")

st.divider()
st.caption(
    "Ensure Ollama is running (`ollama serve`), Mistral is pulled (`ollama pull mistral`), "
    "and the backend is active (`uvicorn backend.main:app --reload`)."
)
