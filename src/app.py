import streamlit as st
from io import BytesIO

# === App Configuration ===
st.set_page_config(
    page_title="FitCV - AI Resume Optimizer",
    page_icon="📄",
    layout="wide"
)

# === Header Section ===
col1, col2 = st.columns([1, 6])

with col1:
    st.image("assets/logo.png", width=40)  # Replace with your own logo

with col2:
    st.markdown(
        "<h1 style='font-size: 32px; display: inline;'>FitCV</h1><br>"
        "<span style='font-size:16px; color: gray;'>Your AI-Powered Resume Optimizer</span>",
        unsafe_allow_html=True
    )

st.markdown("---")

# === Input Section ===
st.header("🔍 Optimize Your Resume for the Job You Want")

uploaded_cv = st.file_uploader("📄 Upload Your CV (PDF only)", type=["pdf"])

github_username = st.text_input("🐙 Enter Your GitHub Username")

job_mode = st.radio("What job info do you have?", ["Job Title", "Full Job Posting"])

if job_mode == "Job Title":
    job_input = st.text_input("💼 Enter the Job Title (e.g., Data Scientist at Google)")
else:
    job_input = st.text_area("💬 Paste the Full Job Posting")

# === Button ===
if st.button("✨ Optimize Resume"):
    if not uploaded_cv or not github_username or not job_input.strip():
        st.warning("Please fill in all fields and upload a valid resume.")
    else:
        with st.spinner("Analyzing your GitHub, resume, and job requirements..."):

            # === Placeholder: Call to your main pipeline logic ===
            from src.pipeline.recommend import refine_resume  # Adjust path accordingly

            # Simulate reading bytes
            resume_bytes = uploaded_cv.read()

            result = refine_resume(
                resume_pdf_bytes=resume_bytes,
                github_username=github_username,
                job_input=job_input
            )

        # === Output Section ===
        st.success("✅ Resume optimization complete!")

        st.subheader("📝 Refined Professional Summary")
        st.write(result["summary"])

        st.subheader("🧠 Recommended Skills for This Role")
        st.write(", ".join(result["skills"]))

        st.subheader("🚀 GitHub Projects to Highlight")
        for proj in result["projects"]:
            st.markdown(f"- **[{proj['name']}]({proj['url']})**: {proj['description']}")

        st.markdown("---")
        st.info("These suggestions are tailored to the job you provided. You can now update your CV accordingly!")