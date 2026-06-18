import streamlit as st
import openai

st.set_page_config(
    page_title="TeachRec",
    page_icon="🎙️",
    layout="centered"
)

st.markdown("""
<style>
    .stApp { background-color: #080812; color: #f0f0f0; }
    #MainMenu, footer, header { visibility: hidden; }

    .hero {
        padding: 2rem 1rem 1.5rem;
        text-align: center;
    }
    .hero-tag {
        display: inline-block;
        background: #1a0533;
        color: #c084fc;
        font-size: 12px;
        font-weight: 600;
        padding: 5px 14px;
        border-radius: 20px;
        border: 1px solid #4c1d95;
        margin-bottom: 16px;
    }
    .hero h1 { font-size: 2.4rem; font-weight: 700; color: white; margin: 0 0 10px; }
    .hero h1 span { color: #a855f7; }
    .hero p { color: #6b7280; font-size: 14px; max-width: 420px; margin: 0 auto; line-height: 1.6; }

    .step-label {
        font-size: 11px; font-weight: 700; text-transform: uppercase;
        letter-spacing: 0.08em; color: #4b5563; margin: 1.8rem 0 0.8rem;
    }
    .step-label span { color: #a855f7; margin-right: 6px; }

    .stTabs [data-baseweb="tab-list"] {
        background: #0f0f1e; border: 1px solid #1f1f35; border-radius: 12px; padding: 4px; gap: 4px;
    }
    .stTabs [data-baseweb="tab"] { background: transparent; color: #6b7280; border-radius: 8px; font-weight: 600; }
    .stTabs [aria-selected="true"] { background: #7c3aed !important; color: white !important; }

    .stButton > button {
        background: linear-gradient(135deg, #6d28d9, #a855f7);
        color: white !important; border: none !important; border-radius: 10px;
        font-weight: 600; width: 100%; padding: 0.65rem; font-size: 14px;
    }
    .stButton > button:hover { opacity: 0.88; }

    .stDownloadButton > button {
        background: #0f0f1e !important; color: #a855f7 !important;
        border: 1px solid #4c1d95 !important; border-radius: 10px; font-weight: 600; width: 100%;
    }

    .stSelectbox label { color: #c084fc !important; font-weight: 600; }
    h2, h3 { color: #c084fc !important; }
    hr { border-color: #1f1f35; }

    .input-card {
        background: #0f0f1e; border: 1px solid #1f1f35; border-radius: 14px;
        padding: 1.2rem; margin-bottom: 0.5rem;
    }
    .input-card p { color: #6b7280; font-size: 13px; margin: 0 0 0.8rem; }

    .footer { text-align: center; color: #1f2937; font-size: 12px; margin-top: 2.5rem; padding-bottom: 1rem; }
</style>

<div class="hero">
    <div class="hero-tag">🎙️ TeachRec</div>
    <h1>Study smarter,<br><span>not harder</span></h1>
    <p>Record or upload any lecture and instantly get notes, flashcards, and quizzes</p>
</div>
""", unsafe_allow_html=True)

client = openai.OpenAI(
    api_key=st.secrets["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1"
)

st.markdown('<p class="step-label"><span>STEP 1</span> Choose your output format</p>', unsafe_allow_html=True)
format_option = st.selectbox(
    "",
    ["📝 Summary + Key Concepts", "🃏 Flashcards", "❓ Quiz Only", "📚 Full Study Pack (All of the above)"],
    label_visibility="collapsed"
)

prompts = {
    "📝 Summary + Key Concepts": """From this transcript generate:
1. A clean bullet-point summary
2. 5 key concepts explained simply""",
    "🃏 Flashcards": """From this transcript generate 8 flashcards in this format:
Q: [question]
A: [answer]
Make them concise and useful for revision.""",
    "❓ Quiz Only": """From this transcript generate 8 quiz questions with 4 multiple choice options each.
Mark the correct answer with ✅""",
    "📚 Full Study Pack (All of the above)": """From this transcript generate a complete study pack:
1. Bullet-point summary
2. 5 key concepts explained simply
3. 8 flashcards (Q: / A: format)
4. 5 quiz questions with multiple choice answers, mark correct with ✅"""
}

def generate_notes(text, format_option):
    with st.spinner("✨ Generating your notes..."):
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful study assistant."},
                {"role": "user", "content": f"{prompts[format_option]}\n\nTranscript: {text}"}
            ]
        )
        notes = response.choices[0].message.content
    st.success("🎉 Your notes are ready!")
    st.markdown("---")
    st.subheader("📚 Your Notes")
    st.write(notes)
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("⬇️ Download TXT", data=notes, file_name="teachrec_notes.txt", mime="text/plain")
    with col2:
        html_content = f"""<html><head><style>
        body {{ font-family: Arial; padding: 40px; line-height: 1.6; }}
        h1 {{ color: #7c3aed; }}
        </style></head><body><h1>TeachRec Notes</h1>
        <pre style="white-space: pre-wrap;">{notes}</pre></body></html>"""
        st.download_button("⬇️ Download HTML", data=html_content, file_name="teachrec_notes.html", mime="text/html")

st.markdown('<p class="step-label"><span>STEP 2</span> Record or upload your lecture</p>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🎤  Record Live", "📁  Upload File"])

with tab1:
    st.markdown('<div class="input-card"><p>Click the mic below to record your lecture</p></div>', unsafe_allow_html=True)
    audio_bytes = st.audio_input("Record your lecture", label_visibility="collapsed")
    if audio_bytes is not None:
        if st.button("✨ Generate Notes from Recording"):
            with st.spinner("🎧 Transcribing your audio..."):
                transcript = client.audio.transcriptions.create(
                    model="whisper-large-v3",
                    file=("audio.wav", audio_bytes, "audio/wav")
                )
                text = transcript.text
            st.markdown('<p class="step-label"><span>STEP 3</span> Your transcript & notes</p>', unsafe_allow_html=True)
            st.subheader("📝 Transcript")
            st.write(text)
            generate_notes(text, format_option)

with tab2:
    st.markdown('<div class="input-card"><p>Upload an MP3, WAV, M4A or MP4 file</p></div>', unsafe_allow_html=True)
    audio_file = st.file_uploader("Upload your lecture audio", type=["mp3", "mp4", "wav", "m4a"], label_visibility="collapsed")
    if audio_file is not None:
        st.audio(audio_file)
        if st.button("✨ Generate Notes from Upload"):
            with st.spinner("🎧 Transcribing your audio..."):
                transcript = client.audio.transcriptions.create(
                    model="whisper-large-v3",
                    file=audio_file
                )
                text = transcript.text
            st.markdown('<p class="step-label"><span>STEP 3</span> Your transcript & notes</p>', unsafe_allow_html=True)
            st.subheader("📝 Transcript")
            st.write(text)
            generate_notes(text, format_option)

st.markdown("<div class='footer'>Built with Nerolena using Streamlit & Groq AI</div>", unsafe_allow_html=True)
