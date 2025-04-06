import streamlit as st
import os,base64
from google import genai
from google.genai import types
from dotenv import load_dotenv
from gemini import generate
from util import display_and_download_html_files,get_api_key
from mindmap import *
from _pqrst import *
#from quiz import *
from testquiz import *

def pqrst_time():
    st.sidebar.title("DynamicStudy")
    if st.session_state.client == None:
        st.error("Set api key first!")
        st.page_link(st.Page(api_key_manager, title="Set API"))
    else:
        st.info("Enter Prompt..")
        # timer = PomodoroTimer()
        # timer.run()
        pqrst()
def quiz_main():
    if st.session_state.client == None:
        st.error("Set api key first!")
        st.page_link(st.Page(api_key_manager, title="Set API"))
    else:
        if "sub" not in st.session_state:
            st.session_state.sub = None
        if "form_count" not in st.session_state:
            st.session_state.form_count = 0
        if "quiz_data" not in st.session_state:
            st.session_state.quiz_data = ''
        if 'answers' not in st.session_state:
            st.session_state.answers = 0
        st.title('Quiz app')
        st.sidebar.title("Options")
        age = get_age()
        subject = st.sidebar.text_input("Enter subject:")
        if st.sidebar.button("Select"):
            st.session_state.sub = subject

            if not st.session_state.quiz_data:
                st.session_state.quiz_data = get_question()

            quiz_data = st.session_state.quiz_data
            st.markdown(f"Question: {quiz_data['question']}")

            form = st.form(key=f"quiz_form_{st.session_state.form_count}")
            user_choice = form.radio("Choose an answer:", quiz_data['choices'])
            submitted = form.form_submit_button("Submit your answer")

            if submitted:
                if user_choice == quiz_data['correct_answer']:
                    st.session_state.answers += 1
                    st.success("Correct")
                else:
                    st.error("Incorrect")
                st.markdown(f"Explanation: {quiz_data['explanation']}")
                st.sidebar.write(f"Correct answers so far: {st.session_state.answers}")

                #with st.spinner("Calling the model for the next question"):
                    #initialize_session_state()
                quiz_data = st.session_state.quiz_data

                another_question = st.button("Another question")

                if another_question:
                    st.session_state.form_count += 1
                else:
                    st.stop()

def show_html_page(html_file):
    with open(html_file,'r',encoding='utf-8') as f:
        html_content=f.read()
    st.components.v1.html(html_content,height=600,width=800,scrolling=True)

def api_key_manager():
    st.sidebar.title("DynamicStudy")
    st.title("🔑 API Key Manager")

    with st.form("api_key_form"):
        api_key = st.text_input("Enter your API key from aistudio.google.com:", type="password", value="")
        submitted = st.form_submit_button("Save API Key")

        if submitted:
            if api_key:
                # Encode and store in environment variable (for current session)
                encoded_key = base64.b64encode(api_key.encode()).decode()
                os.environ["MY_API_KEY"] = encoded_key
                st.success("API key saved for this session!")
                st.session_state.client = genai.Client(
                    api_key=get_api_key(),
                )
                if st.session_state.client:
                    st.success("Initialized client!")
                    st.page_link(st.Page(sub,title="Prompt here.."))
            else:
                st.warning("Please enter an API key")

    # Retrieve the key when needed
    if "MY_API_KEY" in os.environ:
        st.info("An API key is stored for this session")
        if st.button("Clear API Key"):
            del os.environ["MY_API_KEY"]
            st.rerun()

        return base64.b64decode(os.environ["MY_API_KEY"]).decode()
    return None
def sub():
    st.sidebar.title("DynamicStudy")
    if st.session_state.client==None:
        st.error("Set api key first!")
        st.page_link(st.Page(api_key_manager, title="Set API"))
    else:
        st.info("Enter Prompt in the sidebar..")
    prompt = st.sidebar.text_input("Enter topic:")
    if prompt:
        try:
            with st.spinner("Generating..."):
                p = generate(st.session_state.client, prompt)
        except AttributeError:
            st.error("Go to Api Manager and set API key First!")
            return
        if p:
            #st.session_state.pages['Study pages'].append(st.Page(lambda: show_html_page(p),title=p.title()[:-5]))
            with open(p,'r',encoding='utf-8') as c:
                st.code(c.read(), language='html')
                st.download_button(label="Download HTML",data=c, file_name=p)
def mind():
    """Main function to run the Streamlit app."""
    st.sidebar.title("DynamicStudy")
    if st.session_state.client == None:
        st.error("Set api key first!")
        st.page_link(st.Page(api_key_manager, title="Set API"))
    else:
        st.info("Enter Prompt in the sidebar..")
    st.title("Gemini Mind Map Generator")
    query = st.text_input("Enter topic:")
    if st.button("Generate Mind Map"):
        if not query:
            st.warning("Please enter a topic")
        else:
            fig = generate_mind_text(st.session_state.client, query)
            if fig:
                #st.pyplot(fig)
                st.success("Mind map generated successfully!")

                st.download_button(fig)
            else:
                st.error("Failed to generate mind map. Please check your API key and try again.")

if __name__=="__main__":
    if "pages" not in st.session_state:
        st.session_state.pages = {"Main pages": [st.Page(api_key_manager,title='Api Manager'),
                                                st.Page(sub, title="Prompt Page"),
                                                #st.Page(init2, title='Api Setter'),
                                                st.Page(display_and_download_html_files,title="Download Page")],
                                  "Study pages": [st.Page(mind,title='Mindmap Maker'),
                                                  st.Page(pqrst_time,title="PQRST Timer"),
                                                  #st.Page(testq, title="test"),
                                                  st.Page(quiz_main,title="Quiz App")
                                                  ]}
    if "client" not in st.session_state:
        st.session_state.client=None
    if "api_key" not in st.session_state:
        st.session_state.api_key=None
    if "htmls" not in st.session_state:
        st.session_state.htmls=[]
    if "preview" not in st.session_state:
        st.session_state.preview=None
    if "quiz_started" not in st.session_state:
        st.session_state.quiz_started = False
    if "score" not in st.session_state:
        st.session_state.score = 0
    if "prompt" not in st.session_state:
        st.session_state.current_topic = None
    if "quiz_data" not in st.session_state:
        st.session_state.quiz_data=[]

    pg=st.navigation(st.session_state.pages)
    pg.run()