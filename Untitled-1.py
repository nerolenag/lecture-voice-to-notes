import streamlit as st
import openai

st.set_page_config(
    page_title="Lecture Voice-to-Notes",
    page_icon="🎙️",
    layout="centered"
)

st.markdown("""
<style>
    .stApp {
        background-color: #0e0e1a;
        color: #f0f0f0;
    }
    h1 { color: #a855f7 !important; text-align: center; font-size: 2.5rem !important; }
    h2, h3 { color: #c084fc !important; }
    .stSelectbox label { color: #c084fc !important; font-weight: 600; }
    .stTabs [data-baseweb="tab"] { background-color: #1a1a2e; color: #a855f7; border-radius: 8px 8px 0 0; font-weight: 600; }
    .stTabs [aria-selected="true"] { background-color: #a855f7 !important; color: white !important; }
    .stButton > button { background: linear-gradient(135deg, #7c3aed, #a855f7); color: white; border: none; border-radius: 10px; padding: 0.5rem 2rem; font-weight: 600; width: 100%; }
    .stButton > button:hover { background: linear-gradient(135deg, #a855f7, #c084fc); }
    .stDownloadButton > button { background: linear-gradient(135deg, #1a1a2e, #2d2d4e); color: #a855f7 !important; border: 1px solid #a855f7 !important; border-radius: 10px; font-weight: 600; width: 100%; }
    hr { border-color: #7c3aed; }
</style>
""", unsafe_allow_html=True)

client = openai.OpenAI(
    api_key=st.secrets["GROQ_API_KEY"],
   
    base_url="https://api.groq.com/openai/v1"
)

st.title("🎙️ Lecture Voice-to-Notes")
st.markdown("<p style='text-align:center; color:#9ca3af;'>Turn your lectures into smart study notes instantly using AI</p>", unsafe_allow_html=True)
st.markdown("---")

st.subheader("📋 Choose Output Format")
format_option = st.selectbox(
    "What do you want to generate?",
    ["📝 Summary + Key Concepts", "🃏 Flashcards", "❓ Quiz Only", "📚 Full Study Pack (All of the above)"]
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
    st.markdown("---")
    st.subheader("📚 Your Notes")
    st.write(notes)
    st.markdown("---")
    st.download_button(
        label="⬇️ Download Notes as TXT",
        data=notes,
        file_name="lecture_notes.txt",
        mime="text/plain"
    )

tab1, tab2 = st.tabs(["🎤 Record Live", "📁 Upload File"])

with tab1:
    st.markdown("<p style='color:#9ca3af;'>Click the mic below to record your lecture</p>", unsafe_allow_html=True)
    audio_bytes = st.audio_input("Record your lecture")
    if audio_bytes is not None:
        if st.button("Generate Notes from Recording"):
            with st.spinner("🎧 Transcribing your audio..."):
                transcript = client.audio.transcriptions.create(
                    model="whisper-large-v3",
                    file=("audio.wav", audio_bytes, "audio/wav")
                )
                text = transcript.text
            st.subheader("📝 Transcript")
            st.write(text)
            generate_notes(text, format_option)

with tab2:
    st.markdown("<p style='color:#9ca3af;'>Upload an MP3, WAV, M4A or MP4 file</p>", unsafe_allow_html=True)
    audio_file = st.file_uploader("Upload your lecture audio", type=["mp3", "mp4", "wav", "m4a"])
    if audio_file is not None:
        st.audio(audio_file)
        if st.button("Generate Notes from Upload"):
            with st.spinner("🎧 Transcribing your audio..."):
                transcript = client.audio.transcriptions.create(
                    model="whisper-large-v3",
                    file=audio_file
                )
                text = transcript.text
            st.subheader("📝 Transcript")
            st.write(text)
            generate_notes(text, format_option)

st.markdown("---")
st.markdown("<p style='text-align:center; color:#6b7280; font-size:0.8rem;'>Built with ❤️ using Streamlit & Groq AI</p>", unsafe_allow_html=True)