import streamlit as st
import pdfplumber
import difflib
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from fpdf import FPDF
import re

# ==========================================================
# PAGE CONFIG
# ==========================================================
st.set_page_config(
    page_title="ATS Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

# ==========================================================
# SESSION STATE
# ==========================================================
if "theme" not in st.session_state:
    st.session_state.theme = "Dark"

if "versions" not in st.session_state:
    st.session_state.versions = []

# ==========================================================
# THEME
# ==========================================================
bg = "#0E1117" if st.session_state.theme == "Dark" else "#FFFFFF"
fg = "#F1F1F1" if st.session_state.theme == "Dark" else "#111"

st.markdown(f"""
<style>
body {{
    background-color: {bg};
    color: {fg};
}}
.stButton button {{
    width: 100%;
}}
</style>
""", unsafe_allow_html=True)

# ==========================================================
# SIDEBAR
# ==========================================================
st.sidebar.title("⚙️ Settings")
st.session_state.theme = st.sidebar.radio(
    "Theme",
    ["Dark", "Light"],
    index=0 if st.session_state.theme == "Dark" else 1
)

target_role = st.sidebar.selectbox(
    "Target Role",
    ["Data Scientist", "ML Engineer", "Software Engineer", "Analyst"]
)

experience = st.sidebar.selectbox(
    "Experience Level",
    ["Fresher", "1–3 Years", "3–5 Years", "5+ Years"]
)

country = st.sidebar.selectbox(
    "Resume Region",
    ["India", "US", "Europe"]
)

# ==========================================================
# HELPERS
# ==========================================================
def extract_text(pdf):
    text = ""
    with pdfplumber.open(pdf) as p:
        for page in p.pages:
            text += page.extract_text() or ""
    return text.lower()

def find_sections(text):
    sections = ["education", "skills", "projects", "experience", "certifications"]
    found = [s for s in sections if s in text]
    return found

def keyword_coverage(resume, jd):
    jd_words = set(re.findall(r"\b[a-z]{3,}\b", jd))
    resume_words = set(re.findall(r"\b[a-z]{3,}\b", resume))
    matched = jd_words & resume_words
    return len(matched), len(jd_words)

def action_verb_check(text):
    weak = ["worked", "helped", "responsible"]
    return [w for w in weak if w in text]

def resume_score(resume, jd):
    score = 0
    score += 25 if len(resume.split()) < 700 else 10
    score += 25 if len(find_sections(resume)) >= 4 else 10
    m, t = keyword_coverage(resume, jd)
    score += min(30, int((m / max(t, 1)) * 30))
    score += 20 if not action_verb_check(resume) else 10
    return score

def save_pdf(title, content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(0, 8, content.encode("latin-1", "replace").decode())
    file = f"{title}.pdf"
    pdf.output(file)
    return file

# ==========================================================
# MAIN UI
# ==========================================================
st.title("📄 ATS Resume Analyzer (Offline Edition)")
st.caption("No API Keys • Rule-Based • Recruiter Friendly")

jd = st.text_area("📋 Paste Job Description")
resume_pdf = st.file_uploader("📂 Upload Resume (PDF)", type="pdf")

if resume_pdf:
    resume_text = extract_text(resume_pdf)
    st.session_state.versions.append(resume_text)
    st.success("Resume uploaded and processed")

# ==========================================================
# KEYWORD CLOUD
# ==========================================================
if jd:
    st.subheader("☁️ Job Description Keyword Cloud")
    wc = WordCloud(width=800, height=300, background_color="black").generate(jd)
    fig, ax = plt.subplots()
    ax.imshow(wc)
    ax.axis("off")
    st.pyplot(fig)

# ==========================================================
# ANALYSIS
# ==========================================================
if resume_pdf and jd:
    st.subheader("📊 ATS Analysis")

    score = resume_score(resume_text, jd)
    matched, total = keyword_coverage(resume_text, jd)
    weak_verbs = action_verb_check(resume_text)
    sections = find_sections(resume_text)

    st.metric("ATS Readiness Score", f"{score}/100")
    st.progress(score / 100)

    st.write("### ✅ Section Check")
    for s in ["education", "skills", "projects", "experience"]:
        st.write("✔️" if s in sections else "❌", s.title())

    st.write("### 🔑 Keyword Coverage")
    st.write(f"Matched {matched} of {total} keywords")

    st.write("### ⚠️ Weak Action Verbs")
    if weak_verbs:
        st.write(", ".join(weak_verbs))
    else:
        st.write("None found")

    report = f"""
ATS RESUME AUDIT REPORT

Target Role: {target_role}
Experience Level: {experience}
Region: {country}

ATS Score: {score}/100
Keyword Coverage: {matched}/{total}
Missing Sections: {', '.join(set(['education','skills','projects','experience']) - set(sections))}
Weak Verbs: {', '.join(weak_verbs) if weak_verbs else 'None'}
"""

    pdf_file = save_pdf("Resume_Audit_Report", report)
    with open(pdf_file, "rb") as f:
        st.download_button("⬇️ Download Audit Report (PDF)", f, file_name=pdf_file)

# ==========================================================
# VERSION DIFF
# ==========================================================
st.subheader("🗂 Resume Versions & Comparison")

if len(st.session_state.versions) >= 2:
    diff = difflib.unified_diff(
        st.session_state.versions[-2].splitlines(),
        st.session_state.versions[-1].splitlines(),
        lineterm=""
    )
    st.code("\n".join(diff))
else:
    st.info("Upload more than one resume to compare versions")

# ==========================================================
# FOOTER
# ==========================================================
st.markdown("---")
st.caption("© 2025 ATS Resume Analyzer | Built without APIs")
