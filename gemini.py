import base64
import os
from google import genai
from google.genai import types
import re
from dotenv import load_dotenv, find_dotenv


def extract_html_from_code_block(text):
    """
    Extracts HTML code from a text string, specifically from within '```html' and '```' code blocks.

    Args:
        text: The input text string.

    Returns:
        A list of HTML code strings found within the code blocks, or an empty list if none are found.
    """
    if not isinstance(text, str):
        return []

    pattern = r"```html(.*?)```"  # Non-greedy matching
    matches = re.findall(pattern, text, re.DOTALL)
    return matches
def init():
    env_path = find_dotenv()
    if env_path == "":
        with open('examples/.env', 'w') as f:
            pass
        env_path = find_dotenv()

    load_dotenv(find_dotenv(), override=True)

    # Check if API key is in environment variables
    api_key = os.getenv('GENERATIVE_AI_KEY')

    if api_key is None:
        # If API key is not set, ask the user for it
        api_key = input('Please enter your API key from https://ai.google.dev: ')

        # Store the API key in the .env file
        with open(find_dotenv(), 'a') as f:
            f.write(f'GENERATIVE_AI_KEY={api_key}\n')

        print("API key stored successfully!")
    load_dotenv()
    # genai.configure(api_key=os.environ["GENERATIVE_AI_KEY"])
    client = genai.Client(
        api_key=os.environ.get("GENERATIVE_AI_KEY"),
    )
    return client

def generate(client,prompt="page replacement techniques"):

    model = "gemini-2.0-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=f"""Create a html site to simulate {prompt}"""),
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
                client.models.generate_content_stream(model=model, contents=contents, config=generate_content_config))
    #st.markdown(a)
    html_list=extract_html_from_code_block(a)
    # Extract the first element (HTML content)
    html_content = html_list[0]
    fname=prompt if len(prompt.split())<=6 else " ".join(prompt.split()[:5])
    # Write to an HTML file
    with open(f'{fname}.html', 'w') as file:
        file.write(html_content)

    print(f"HTML file created successfully: '{fname}.html'")
    return f"{fname}.html"

if __name__ == "__main__":
    generate(init())
