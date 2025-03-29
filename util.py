import os
import streamlit as st
from glob import glob
from google import genai
from dotenv import load_dotenv
import base64

def show_html_page():
    html_file=st.session_state.htmls[-1]
    with open(html_file,'r',encoding='utf-8') as f:
        html_content=f.read()
    st.components.v1.html(html_content,height=600,width=800,scrolling=True)

#load_dotenv()  # Load environment variables from .env file
@st.cache_resource
def get_api_key():
    if "MY_API_KEY" in os.environ:
        try:
            return base64.b64decode(os.environ["MY_API_KEY"]).decode()
        except Exception as e:
            st.error(f"Error decoding API key: {e}")
            return None
    return None
#@st.cache_resource

def get_html_files(directory="."):
    """Get all HTML files in the specified directory"""
    return glob(os.path.join(directory, "*.html"))


def display_and_download_html_files():
    st.sidebar.title("DynamicStudy")
    st.title("📁 HTML File Manager")

    # Get all HTML files in current directory
    html_files = get_html_files()

    if not html_files:
        st.warning("No HTML files found in the current directory")
        return

    st.success(f"Found {len(html_files)} HTML files:")

    for idx, file_path in enumerate(html_files, 1):
        file_name = os.path.basename(file_path)
        if file_name not in st.session_state.htmls:
            st.session_state.htmls.append(file_name)
        #st.session_state.pages["Study pages"].append(st.Page(show_html_page,title=file_name))
        # Create columns for better layout
        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            st.write(f"{idx}. {file_name}")

        with col2:
            # Preview button
            if st.button(f"Preview", key=f"preview_{idx}"):
                if st.session_state.preview:
                    st.session_state.preview=None
                else:
                    st.session_state.preview=file_path


        with col3:
            # Download button
            with open(file_path, "rb") as f:
                st.download_button(
                    label="Download",
                    data=f,
                    file_name=file_name,
                    mime="text/html",
                    key=f"download_{idx}"
                )
    if st.session_state.preview:
        with open(st.session_state.preview, "r", encoding="utf-8") as f:
            html_content = f.read()
        st.components.v1.html(html_content,width=1000,scrolling=True,height=1000)


if __name__ == "__main__":
    display_and_download_html_files()
