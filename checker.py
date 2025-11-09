# ==========================================================
# 📄 ATS Resume Expert - Professional Edition
# Author: Nhowmitha Suresh
# Built with Streamlit + Google Gemini
# ==========================================================

import os
import io
import base64
from dotenv import load_dotenv
import streamlit as st
from PIL import Image
from fpdf import FPDF

# Try importing dependencies
try:
    import pdf2image
    import google.generativeai as genai
except ImportError:
    st.error("⚠️ Missing dependencies. Please run:\n\npip install fpdf2 streamlit python-dotenv google-generativeai pdf2image pillow")
    st.stop()

# ==========================================================
# 🔧 CONFIGURATION
# ==========================================================
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    st.error("❌ GOOGLE_API_KEY not found in .env file. Add it as:\nGOOGLE_API_KEY=your_key_here")
    st.stop()

genai.configure(api_key=API_KEY)
MODEL_NAME = "gemini-2.5-flash"

# ==========================================================
# 🎨 PAGE SETUP
# ==========================================================
st.set_page_config(page_title="ATS Resume Expert", page_icon="💼", layout="wide")

# Theme switcher
theme = st.sidebar.radio("🎨 Theme Mode", ["Light", "Dark"], horizontal=True)

if theme == "Dark":
    bg_color = "#0E1117"
    text_color = "#F1F1F1"
    card_bg = "#1C1F26"
    accent = "#4E9EFF"
else:
    bg_color = "#F8F9FB"
    text_color = "#111"
    card_bg = "#FFFFFF"
    accent = "#0078FF"

st.markdown(f"""
<style>
    html, body, [class*="st-"] {{
        background-color: {bg_color};
        color: {text_color};
        font-family: "Inter", sans-serif;
    }}
    .title {{
        color: {accent};
        text-align: center;
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0.3rem;
    }}
    .subtitle {{
        text-align: center;
        color: gray;
        margin-bottom: 2rem;
        font-size: 1rem;
    }}
    .card {{
        background-color: {card_bg};
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-top: 1rem;
    }}
    div.stButton > button {{
        width: 100%;
        background-color: {accent};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.7rem;
        font-weight: 600;
        transition: all 0.3s;
    }}
    div.stButton > button:hover {{
        transform: scale(1.05);
        background-color: #005ad9;
    }}
</style>
""", unsafe_allow_html=True)

# ==========================================================
# 🧭 SIDEBAR
# ==========================================================
with st.sidebar:
    st.header("📘 About")
    st.write("""
    **ATS Resume Expert** uses **Google Gemini AI** to:
    - Analyze resumes for ATS compatibility  
    - Suggest skill improvements  
    - Calculate job match percentage  
    - Generate tailored resumes  
    """)
    st.divider()
    st.markdown("👩‍💻 **Developer:** Nhowmitha Suresh")
    st.markdown("[🌐 GitHub](https://github.com/Nhowmitha-suresh) | [✉️ Email](mailto:nhowmithasuresh@gmail.com)")

# ==========================================================
# 🧠 HELPER FUNCTIONS
# ==========================================================
def gemini_response(input_text, pdf_content, prompt):
    """Generate response using Gemini model with resume data."""
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content([input_text, pdf_content[0], prompt])
        return response.text
    except Exception as e:
        return f"⚠️ Error generating response: {str(e)}"


def gemini_text_response(input_text, prompt):
    """Generate response using text only."""
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content([input_text, prompt])
        return response.text
    except Exception as e:
        return f"⚠️ Error generating response: {str(e)}"


def pdf_to_image(uploaded_file):
    """Convert first page of PDF to image for AI analysis."""
    try:
        images = pdf2image.convert_from_bytes(uploaded_file.read())
        img_byte_arr = io.BytesIO()
        images[0].save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()
        return [{"mime_type": "image/jpeg", "data": base64.b64encode(img_byte_arr).decode()}]
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        st.stop()

def save_as_pdf(title, text):
    """Save AI response as PDF."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    safe_text = text.encode("latin-1", "replace").decode("latin-1")
    pdf.multi_cell(0, 10, safe_text)
    filename = f"{title.replace(' ', '_')}.pdf"
    pdf.output(filename)
    return filename

# ==========================================================
# 🖥️ MAIN UI
# ==========================================================
st.markdown("<div class='title'>ATS Resume Expert</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>AI-Powered Resume Analyzer & Optimizer using Google Gemini</div>", unsafe_allow_html=True)
st.divider()

input_text = st.text_area("🧾 Enter Job Description", height=150, placeholder="Paste the full job description here...")
uploaded_file = st.file_uploader("📂 Upload your Resume (PDF only)", type=["pdf"])

if uploaded_file:
    st.success("✅ Resume uploaded successfully!")

# ==========================================================
# 🎯 BUTTONS
# ==========================================================
st.markdown("### ⚙️ Choose an Action")
col1, col2, col3, col4, col5 = st.columns(5)
btns = {
    "About Resume": col1.button("📄 About"),
    "Skill Improvement": col2.button("💡 Improve"),
    "Match %": col3.button("📊 Match"),
    "Tailor Resume": col4.button("🧵 Tailor"),
    "Generate Resume": col5.button("🧠 Generate"),
}

# ==========================================================
# 💬 PROMPTS
# ==========================================================
prompts = {
    "About Resume": "Analyze resume strengths, weaknesses, and fit for the given job.",
    "Skill Improvement": "Suggest skill improvements and missing keywords to enhance job relevance.",
    "Match %": "Provide ATS compatibility score, missing skills, and final remarks.",
    "Tailor Resume": "Rewrite and tailor resume content to perfectly match the job description.",
    "Generate Resume": "Generate a new professional ATS-optimized resume for this job description."
}

# ==========================================================
# 🚀 PROCESS LOGIC
# ==========================================================
for label, pressed in btns.items():
    if pressed:
        with st.spinner("🤖 Gemini AI is analyzing your resume... Please wait."):
            if label == "Generate Resume":
                response = gemini_text_response(input_text, prompts[label])
            elif uploaded_file:
                pdf_content = pdf_to_image(uploaded_file)
                response = gemini_response(input_text, pdf_content, prompts[label])
            else:
                st.warning("⚠️ Please upload your resume first.")
                st.stop()

        if response:
            st.markdown(f"<div class='card'><h4>{label}</h4><p>{response}</p></div>", unsafe_allow_html=True)
            pdf_file = save_as_pdf(label, response)

            with open(pdf_file, "rb") as file:
                st.download_button(
                    f"💾 Download {label} (PDF)",
                    data=file,
                    file_name=pdf_file,
                    mime="application/pdf"
                )

# ==========================================================
# 🧾 FOOTER
# ==========================================================
st.divider()
st.markdown(
    "<p style='text-align:center;color:gray;'>© 2025 ATS Resume Expert | Developed by <b>Nhowmitha Suresh</b> 💼</p>",
    unsafe_allow_html=True
)
