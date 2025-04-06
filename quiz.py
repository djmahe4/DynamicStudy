import streamlit as st
import time  # Changed from 'import time' and 'from time import sleep'
import datetime
import re
import os
import random
from icecream import ic
from dotenv import load_dotenv, find_dotenv
import google.genai as genai  # Fixed import
from google.genai import types# Updated config import
import base64
import ast


def get_api_key():
    if "MY_API_KEY" in os.environ:
        try:
            return base64.b64decode(os.environ["MY_API_KEY"]).decode()
        except Exception as e:
            st.error(f"Error decoding API key: {e}")
            return None
    return None

# ... (existing get_api_key remains the same) ...

# Initialize Gemini
def init_gemini():
    with st.form("api_key_form"):
        api_key = st.text_input("Enter your API key from aistudio.google.com:", type="password", value="")
        submitted = st.form_submit_button("Save API Key")

        if submitted and api_key:
            try:
                # Configure Gemini directly
                genai.configure(api_key=api_key)
                st.success("API key configured successfully!")
                return True
            except Exception as e:
                st.error(f"Error configuring Gemini: {str(e)}")
                return False
        return False


def timer2(seconds):
    placeholder = st.empty()
    end_time = time.time() + seconds

    while time.time() < end_time:
        remaining = int(end_time - time.time())
        mins, secs = divmod(remaining, 60)
        placeholder.markdown(f"""
                <div style="border-radius:10px; padding:20px; background:#2e2e2e; text-align:center">
                    <h1>{mins:02d}:{secs:02d}</h1>
                </div>
            """, unsafe_allow_html=True)
        time.sleep(1)

        # if st.session_state.get("skip"):
        #     placeholder.empty()
        #     st.session_state.skip = False
        #     return

    placeholder.empty()
def timer3(seconds):

    end_time = time.time() + seconds

    while time.time() < end_time:
        remaining = int(end_time - time.time())
        mins, secs = divmod(remaining, 60)
        tstring=f"{mins:02d}:{secs:02d}"+"\r"
        st.write(tstring)
        time.sleep(1)

# ... (existing timer function remains the same) ...

def generate_questions(query):
    if "quiz_data" not in st.session_state:
        with st.spinner('Generating quiz questions...'):
            try:

                # Improved prompt with strict formatting

                prompt = f"""Generate 10 MCQ questions about {query} with 4 options each.
                                Return ONLY a Python list of dictionaries in this EXACT format:

                                [
                                    {{
                                        "question": "What is the capital of France?",
                                        "options": [
                                            "a) London",
                                            "b) Paris",
                                            "c) Berlin",
                                            "d) Madrid"
                                        ],
                                        "answer": "b"
                                    }},
                                    {{
                                        "question": "Which planet is known as the Red Planet?",
                                        "options": [
                                            "a) Venus",
                                            "b) Mars",
                                            "c) Jupiter",
                                            "d) Saturn"
                                        ],
                                        "answer": "b"
                                    }}
                                ]

                                Important guidelines:
                                1. Use double quotes for all strings
                                2. Include exactly 10 questions
                                3. Answer should be just the letter (a/b/c/d)
                                4. No additional text before or after the list"""
                model = "gemini-2.0-flash"
                contents = [
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_text(text=f"""{prompt}"""),
                        ],
                    ),
                ]
                generate_content_config = types.GenerateContentConfig(
                    temperature=1,
                    top_p=0.95,
                    top_k=40,
                    max_output_tokens=8192,
                    response_mime_type="text/plain",
                )
                a = "".join(item.text for item in
                            st.session_state.client.models.generate_content_stream(model=model, contents=contents,
                                                                  config=generate_content_config))
                st.code(a)
                if a:
                    raw_text=re.findall(r"```python(.*?)```", a, re.DOTALL)[0]
                # Step 2: Convert to dict
                if raw_text:
                    try:
                        python_dict = ast.literal_eval(raw_text)
                        print(type(python_dict), python_dict)
                        st.session_state.quiz_data = python_dict
                    except (SyntaxError, ValueError) as e:
                        print(f"Error: {e}")
                        st.session_state.quiz_data = []

                #st.session_state.quiz_data = parse_questions(raw_text)

            except Exception as e:
                st.error(f"Error generating questions: {str(e)}")
                st.session_state.quiz_data = []


def parse_questions(raw_text):
    questions = []
    current_q = None
    st.write(raw_text)
    lines = [line.strip() for line in raw_text.split("""'""") if line.strip()]
    st.code(lines)
    for line in lines:
        # Detect question start
        if re.match(r'^\d+\.', line):
            if current_q:
                questions.append(current_q)
            current_q = {
                'question': line,
                'options': [],
                'answer': ''
            }
        # Detect options
        elif re.match(r'^[a-d]\)', line):
            if current_q:
                current_q['options'].append(line)
        # Detect answer
        elif line.lower().startswith('answer:'):
            if current_q:
                current_q['answer'] = line.split(':')[1].strip().lower()
                questions.append(current_q)
                current_q = None
        # Continue question text
        elif current_q and not current_q['answer']:
            current_q['question'] += ' ' + line

    # Cleanup any remaining question
    if current_q and current_q['answer']:
        questions.append(current_q)

    return questions


def quiz():
    st.title("Mini Quiz Master")

    if not genai.get_api_key():
        if not init_gemini():
            return

    prompt = st.text_input("Enter topic:")

    if not st.session_state.get("quiz_started"):
        if prompt and st.button("Start New Quiz"):
            st.session_state.quiz_started = True
            st.session_state.score = 0
            st.session_state.current_topic = prompt
            generate_questions(prompt)

    if not st.session_state.get("quiz_data"):
        return

    # ... (rest of quiz rendering remains the same) ...


if __name__ == "__main__":
    # st.set_page_config(page_title="Quiz Master")
    # quiz()
    timer3(5)