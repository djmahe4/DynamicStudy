# **DynamicStudy Tool**  

**DynamicStudy** is an AI-powered tool that generates interactive HTML pages for learning various topics. It uses **Generative AI** (Gemini) to create engaging educational content, which can be previewed live or downloaded as HTML code.  

## **Features**  
✅ **AI-Powered Content Generation** – Uses Gemini to create structured and interactive HTML learning modules.  
✅ **Live Preview** – See the generated content in real-time before downloading.  
✅ **Download HTML** – Save the generated HTML for offline use.  
✅ **Local Execution (`gemini.py`)** – Run the tool locally to generate HTML.  
✅ **Streamlit Web App** – User-friendly interface for easy prompt-based generation.  

---

## **🚀 Quick Start**  

### **Prerequisites**
***‼ Requires an API KEY created from https://ai.google.dev***

### **1. Running the Streamlit Web App (Recommended)**  
The Streamlit implementation allows live preview and easy HTML download.  

#### **Steps:**  
1. Install dependencies:  
   ```sh
   pip install -r requirements.txt
   ```
2. Clone the repo (if applicable) or ensure `app.py` is in your directory.  
3. Create a `.env` file with your **Gemini API key**:  
   ```sh
   echo "GEMINI_API_KEY=your_api_key_here" > .env
   ```
4. Run the Streamlit app:  
   ```sh
   streamlit run app.py
   ```
5. Enter a topic prompt (e.g., *"Explain Newton's Laws of Motion interactively"*), preview, and download the HTML!  

---

### **2. Running Locally (`gemini.py`)**  
If you prefer running the script directly without Streamlit:  

#### **Steps:**  
1. Install `google-generativeai`:  
   ```sh
   pip install google-generativeai python-dotenv
   ```
2. Set up `.env` with your Gemini API key (same as above).  
3. Run the script:  
   ```sh
   python gemini.py
   ```
4. Enter your learning topic when prompted.  
5. The script will generate an HTML file (e.g., `output.html`) in the same directory.  

---

### **3. Cloud Deployment**
The code is deployed in streamlit. 
So anyone can access it through the [link](https://dynamicstudy.streamlit.app/)

---

## **📂 File Structure**  
```
DynamicStudy/  
├── app.py            # Streamlit web app  
├── gemini.py         # Local script for HTML generation  
├── .env              # Stores Gemini API key  
├── README.md         # This guide  
├── uptil.py          # Codes to assist app.py 
└── examples/         # Sample generated HTML files  
```

---

## **🔧 Customization**  
- Modify `app.py` or `gemini.py` to change:  
  - **HTML styling** (edit the prompt in the code).  
  - **AI model parameters** (e.g., `temperature`, `max_tokens`).  
- Add more interactive elements (quizzes, diagrams) by refining the AI prompt.  

---

## **📜 License**  
MIT License – Free for personal and educational use.  

---

## **💡 Example Prompts**  
- *"Interactive HTML tutorial on Python lists."*  
- *"Quiz-style HTML page about World War II."*  
- *"Clickable HTML guide for machine learning basics."*  

---

### **🔗 Get Started Now!**  
👉 **Run locally:** `python gemini.py`  
👉 **Web version:** `streamlit run app.py` OR **https://dynamicstudy.streamlit.app/**  

Happy Learning! 🎓🚀  

---

**Contributions welcome!** Feel free to fork, improve, or suggest new features. 🛠️