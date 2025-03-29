import streamlit as st
import os,base64
from google import genai
from google.genai import types
from dotenv import load_dotenv
from gemini import generate
from util import display_and_download_html_files,get_api_key

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
            p = generate(st.session_state.client, prompt)
        except AttributeError:
            st.error("Go to Api Manager and set API key First!")
            return
        if p:
            #st.session_state.pages['Study pages'].append(st.Page(lambda: show_html_page(p),title=p.title()[:-5]))
            with open(p,'r',encoding='utf-8') as c:
                st.code(c.read(), language='html')
                st.download_button(label="Download HTML",data=c, file_name=p)

if __name__=="__main__":
    if "pages" not in st.session_state:
        st.session_state.pages = {"Main pages": [st.Page(api_key_manager,title='Api Manager'),
                                                st.Page(sub, title="Prompt Page"),
                                                #st.Page(init2, title='Api Setter'),
                                                st.Page(display_and_download_html_files,title="Download Page")],
                                  "Study pages": []}
    if "client" not in st.session_state:
        st.session_state.client=None
    if "api_key" not in st.session_state:
        st.session_state.api_key=None
    if "htmls" not in st.session_state:
        st.session_state.htmls=[]
    if "preview" not in st.session_state:
        st.session_state.preview=None

    pg=st.navigation(st.session_state.pages)
    pg.run()