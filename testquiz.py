# pip install the below updated google genai module !! Also, you may need to pip install pydantic if you haven't done that already.
# pip install google-genai

import streamlit as st
import os
import json
from google import genai
from google.genai.types import GenerateContentConfig
from pydantic import BaseModel


class Packet(BaseModel):
    question: str
    choices: list[str]
    correct_answer: str
    explanation: str


def get_age():
    age = st.sidebar.slider("Select you AGE:", min_value=3, max_value=60, value=19, step=1, )
    st.session_state.age=age
    return age


def get_subject():
    subject = st.sidebar.text_input("Enter subject:")
    if st.sidebar.button("Select"):
        st.session_state.sub=subject
    return subject


def get_question():
    question = f"""a {st.session_state.age} year old is preparing for an exam. Generate only one random {st.session_state.sub} question for a {st.session_state.age} year old to help prepare for the exam.  
    provide four multiple choices for the correct answer. make sure that the correct answer is not always the first choice.\
     provide which is the correct answer separately and an explanation for the correct answer. \
    you must provide the response as a json format containing the keys and values for question, choices, correct_answer, explanation.\
        do not deviate from the instructions provided. make sure the keys are question, choices, correct_answer, explanation before you proceed.  keys and values must be in a CORRECT json format \
            where the keys are question, choices, correct answer, explanation. must come through as a string so that the json can be properly loaded."""

    response = st.session_state.client.models.generate_content(
        model="gemini-2.0-flash",
        contents=question,
        config=GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=Packet,
        ),
    )

    if 'question' and 'choices' and 'correct_answer' and 'explanation' in response.text:
        data = json.loads(response.text)
    else:
        Quiz()

    return data


def initialize_session_state():
    session_state = st.session_state
    session_state.form_count = 0
    session_state.quiz_data = ''


def Quiz():
    if "sub" not in st.session_state:
        st.session_state.sub=None
    if "form_count" not in st.session_state:
        st.session_state.form_count=0
    if "quiz_data" not in st.session_state:
        st.session_state.quiz_data=''
    if 'answers' not in st.session_state:
        st.session_state.answers = 0
    if 'age'not in st.session_state:
        st.session_state.age=19
    st.title('Quiz app')
    st.sidebar.title("Options")
    age = get_age()
    subject = st.sidebar.text_input("Enter subject:")
    if st.sidebar.button("Select"):
        st.session_state.sub = subject

    # if st.session_state.sub:
    #     if st.session_state.sub==None:
    #         get_subject()
    #         st.session_state.quiz_data = get_question()
    #     else:
    #         if st.session_state.quiz_data!= None:
    #             st.session_state.quiz_data = get_question()
    #         else:
    #             return
    #quiz_data = st.session_state.quiz_data
    st.write(st.session_state.sub)
    st.markdown(f"Question: {st.session_state.quiz_data['question']}")

    form = st.form(key=f"quiz_form_{st.session_state.form_count}")
    user_choice = form.radio("Choose an answer:", st.session_state.quiz_data['choices'])
    submitted = form.form_submit_button("Submit your answer")

    if submitted:
        if user_choice == st.session_state.quiz_data['correct_answer']:
            st.session_state.answers += 1
            st.success("Correct")
        else:
            st.error("Incorrect")
        st.markdown(f"Explanation: {st.session_state.quiz_data['explanation']}")
        st.sidebar.write(f"Correct answers so far: {st.session_state.answers}")

        # with st.spinner("Calling the model for the next question"):
        #     initialize_session_state()
        #quiz_data = st.session_state.quiz_data

        another_question = st.button("Another question")
        #
        if another_question:
            st.session_state.form_count += 1
        else:
            st.stop()


if __name__ == '__main__':
    api_key = os.environ.get('GENERATIVE_AI_KEY')
    client = genai.Client(api_key="YOUR-API-KEY")
    MODEL_ID = "gemini-2.0-flash-001"
    Quiz()