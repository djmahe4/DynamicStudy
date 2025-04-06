import os
import time
import random
import streamlit as st
from streamlit import errors as errs
from google import genai
from google.genai import types
from dotenv import load_dotenv
from pylatexenc.latex2text import LatexNodes2Text
import pandas as pd

def markdown_to_df(markdown_table):
    """Convert Markdown table to pandas DataFrame"""
    lines = markdown_table.split('\n')
    # Extract headers
    headers = [h.strip() for h in lines[0].split('|')[1:-1]]
    # Extract rows
    data = []
    for line in lines[2:]:  # Skip header and separator lines
        cells = [c.strip() for c in line.split('|')[1:-1]]
        if cells:
            data.append(cells)
    return pd.DataFrame(data, columns=headers)
# Initialize Gemini client
def init_gemini():
    if "client" not in st.session_state:
        load_dotenv()
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        st.session_state.client = genai


# Cache Gemini responses
@st.cache_data(show_spinner=False)
def generate_content(_client, prompt, model_name="gemini-2.0-flash"):
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=f"""{prompt}"""),
            ],
        ),
    ]
    config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
        response_mime_type="text/plain"
    )
    response = _client.models.generate_content_stream(
        model=model_name,
        contents=contents,
        config=config
    )
    # formatted_response=LatexNodes2Text().latex_to_text("".join(item.text for item in response))
    # # Then in your display code:
    # if "|" in formatted_response and "-" in formatted_response:
    #     try:
    #         df = markdown_to_df(formatted_response)
    #         st.dataframe(df)  # Or st.table(df) for static display
    #     except:
    #         st.markdown(formatted_response)
    # else:
    #     st.write(formatted_response)
    return LatexNodes2Text().latex_to_text("".join(item.text for item in response))


# Study session steps
stages = {
        "preview": "📖 Preview",
        "questions": "❓ Questions",
        "study": "📚 Study Material",
        "summary": "📝 Summary",
        "test": "🧠 Knowledge Check"
    }
def study_session(material):

    if "current_stage" not in st.session_state:
        st.session_state.current_stage = "preview"

    current_idx = list(stages.keys()).index(st.session_state.current_stage)

    # Stage navigation
    cols = st.columns(len(stages))
    for idx, (key, label) in enumerate(stages.items()):
        # if key==st.session_state.current_stage:
        #     continue
        with cols[idx]:
            try:
                st.button(label,
                          key=f"stage_btn_{key}_{st.session_state.current_stage}",  # Unique key based on stage name
                          disabled=idx > current_idx,
                          on_click=lambda k=key: st.session_state.update({"current_stage": k}),
                          help="Complete previous stages to unlock" if idx > current_idx else "")
            except errs.DuplicateWidgetID:
                continue
    # Stage content
    with st.container():
        if st.session_state.current_stage == "preview":
            st.subheader("Preview Material")
            prompt = f"Key points and differences (comparisons if any within ```) about {material} by highlighting key concepts and real-world applications:"
            st.markdown(generate_content(st.session_state.client, prompt))

        elif st.session_state.current_stage == "questions":
            st.subheader("Essential Questions")
            prompt = f"Generate 5 critical thinking questions about {material} with answers:"
            st.markdown(generate_content(st.session_state.client, prompt))

        elif st.session_state.current_stage == "study":
            st.subheader("In-Depth Learning")
            prompt = f"Create a comprehensive lesson on {material} with examples and diagrams (describe visually):"
            st.markdown(generate_content(st.session_state.client, prompt))

        elif st.session_state.current_stage == "summary":
            st.subheader("Knowledge Synthesis")
            user_summary = st.text_area("Write your summary here (3-5 sentences):")
            if user_summary:
                prompt = f"Evaluate this summary: '{user_summary}'. Score/10 for {material} coverage. Highlight gaps:"
                st.markdown(generate_content(st.session_state.client, prompt))

        elif st.session_state.current_stage == "test":
            st.subheader("Self-Assessment")
            prompt = f"Create 3 test questions (mix of formats) about {material} with answers:"
            st.markdown(generate_content(st.session_state.client, prompt))


# Timer component
def timer(seconds, label):
    placeholder = st.empty()
    end_time = time.time() + seconds

    while time.time() < end_time:
        remaining = int(end_time - time.time())
        mins, secs = divmod(remaining, 60)
        placeholder.markdown(f"""
            <div style="border-radius:10px; padding:20px; background:#2e2e2e; text-align:center">
                <h3>{label}</h3>
                <h1>{mins:02d}:{secs:02d}</h1>
            </div>
        """, unsafe_allow_html=True)
        time.sleep(1)

        if st.session_state.get("skip"):
            placeholder.empty()
            st.session_state.skip = False
            return

    placeholder.empty()
    st.balloons()


# Main app flow
def pqrst():
    #init_gemini()

    st.title("AI-Powered Study Assistant")
    st.write("Boost your learning with smart pomodoro sessions")

    if "session_active" not in st.session_state:
        material = st.sidebar.text_input("📝 Enter your study topic:")
        if material:
            st.session_state.session_active = True
            st.session_state.material = material
            st.rerun()
        return

    # Session controls
    with st.expander("Session Controls", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("⏭️ Skip Phase"):
                st.session_state.skip = True
                try:
                    st.session_state.current_stage=list(stages.keys())[list(stages.keys()).index(st.session_state.current_stage)+1]
                except KeyError:
                    print(st.session_state.current_stage)
                    del st.session_state.session_active
        with col2:
            if st.button("🔄 Restart Session"):
                del st.session_state.session_active
                st.rerun()
        with col3:
            if st.button("⏹️ End Session"):
                del st.session_state.session_active
                #st.rerun()

    # Pomodoro phases
    phases = [
        ("focus", 2 * 60, "preview"),
        ("focus", 3 * 60, "questions"),
        ("focus", 12 * 60, "study"),
        ("focus", 3 * 60, "summary"),
        ("focus", 5 * 60, "test"),
        ("break", 5 * 60, "Short Break")
    ]

    for phase_type, duration, label in phases:
        if phase_type == "focus":
            st.session_state.current_state=label
            study_session(st.session_state.material)
        timer(duration, label)

    st.success("🎉 Session Complete! Ready for another round?")
    if st.button("Start New Session"):
        del st.session_state.session_active
        st.rerun()


if __name__ == "__main__":
    pqrst()