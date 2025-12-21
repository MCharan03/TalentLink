import streamlit as st
from fpdf import FPDF
from ai_utils import generate_resume_analysis


def display_resume_builder():
    st.header("Resume Builder")

    with st.form("resume_form"):
        st.subheader("Personal Information")
        name = st.text_input("Full Name", key="name_input")
        email = st.text_input("Email", key="email_input")
        phone = st.text_input("Phone", key="phone_input")
        linkedin = st.text_input("LinkedIn Profile URL", key="linkedin_input")

        st.subheader("Summary")
        summary = st.text_area("Summary", key="summary_input")

        st.subheader("Work Experience")
        num_jobs = st.number_input(
            "Number of Job Experiences", min_value=1, value=1, key="num_jobs")
        jobs = []
        for i in range(num_jobs):
            st.markdown(f"---")
            st.markdown(f"### Job {i+1}")
            job_title = st.text_input(f"Job Title {i+1}", key=f"job_title_{i}")
            company = st.text_input(f"Company {i+1}", key=f"company_{i}")
            job_location = st.text_input(
                f"Location {i+1}", key=f"job_location_{i}")
            job_dates = st.text_input(
                f"Dates (e.g., Jan 2020 - Present) {i+1}", key=f"job_dates_{i}")
            job_desc = st.text_area(f"Description {i+1}", key=f"job_desc_{i}")
            jobs.append(
                (job_title, company, job_location, job_dates, job_desc))

        if st.form_submit_button("Get AI Suggestions"):
            with st.spinner("Generating suggestions..."):
                for i, job in enumerate(jobs):
                    suggestions = generate_resume_analysis(job[4])
                    if suggestions and suggestions.get('quantifiable_achievements_suggestions'):
                        st.info(f"AI Suggestions for Job {i+1}:")
                        for suggestion in suggestions.get('quantifiable_achievements_suggestions'):
                            st.write(suggestion)

        st.subheader("Education")
        num_edu = st.number_input(
            "Number of Educational Qualifications", min_value=1, value=1, key="num_edu")
        educations = []
        for i in range(num_edu):
            st.markdown(f"---")
            st.markdown(f"### Education {i+1}")
            degree = st.text_input(f"Degree {i+1}", key=f"degree_{i}")
            university = st.text_input(
                f"University {i+1}", key=f"university_{i}")
            edu_location = st.text_input(
                f"Location {i+1}", key=f"edu_location_{i}")
            edu_dates = st.text_input(
                f"Dates (e.g., Aug 2016 - May 2020) {i+1}", key=f"edu_dates_{i}")
            educations.append((degree, university, edu_location, edu_dates))

        st.subheader("Skills")
        skills = st.text_area("Skills (comma-separated)", key="skills_input")

        st.subheader("Projects")
        num_projects = st.number_input(
            "Number of Projects", min_value=1, value=1, key="num_projects")
        projects = []
        for i in range(num_projects):
            st.markdown(f"---")
            st.markdown(f"### Project {i+1}")
            project_name = st.text_input(
                f"Project Name {i+1}", key=f"project_name_{i}")
            project_desc = st.text_area(
                f"Project Description {i+1}", key=f"project_desc_{i}")
            projects.append((project_name, project_desc))

        submitted = st.form_submit_button(
            "Generate Resume", key="generate_resume_button")

        if submitted:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            # Personal Information
            pdf.cell(200, 10, txt=name, ln=True, align='C')
            pdf.cell(
                200, 10, txt=f"{email} | {phone} | {linkedin}", ln=True, align='C')

            # Summary
            pdf.ln(10)
            pdf.set_font("Arial", 'B', size=14)
            pdf.cell(200, 10, txt="Summary", ln=True)
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 5, txt=summary)

            # Work Experience
            pdf.ln(10)
            pdf.set_font("Arial", 'B', size=14)
            pdf.cell(200, 10, txt="Work Experience", ln=True)
            pdf.set_font("Arial", size=12)
            for job in jobs:
                pdf.set_font("Arial", 'B', size=12)
                pdf.cell(0, 10, txt=f"{job[0]} at {job[1]}", ln=True)
                pdf.set_font("Arial", size=12)
                pdf.cell(0, 5, txt=f"{job[2]} | {job[3]}", ln=True)
                pdf.multi_cell(0, 5, txt=job[4])
                pdf.ln(5)

            # Education
            pdf.ln(10)
            pdf.set_font("Arial", 'B', size=14)
            pdf.cell(200, 10, txt="Education", ln=True)
            pdf.set_font("Arial", size=12)
            for edu in educations:
                pdf.set_font("Arial", 'B', size=12)
                pdf.cell(0, 10, txt=f"{edu[0]} from {edu[1]}", ln=True)
                pdf.set_font("Arial", size=12)
                pdf.cell(0, 5, txt=f"{edu[2]} | {edu[3]}", ln=True)
                pdf.ln(5)

            # Skills
            pdf.ln(10)
            pdf.set_font("Arial", 'B', size=14)
            pdf.cell(200, 10, txt="Skills", ln=True)
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 5, txt=skills)

            # Projects
            pdf.ln(10)
            pdf.set_font("Arial", 'B', size=14)
            pdf.cell(200, 10, txt="Projects", ln=True)
            pdf.set_font("Arial", size=12)
            for proj in projects:
                pdf.set_font("Arial", 'B', size=12)
                pdf.cell(0, 10, txt=proj[0], ln=True)
                pdf.set_font("Arial", size=12)
                pdf.multi_cell(0, 5, txt=proj[1])
                pdf.ln(5)

            pdf_output = pdf.output(dest='S').encode('latin-1')
            st.download_button(
                label="Download Resume as PDF",
                data=pdf_output,
                file_name=f"{name.replace(' ', '_')}_Resume.pdf",
                mime="application/pdf",
            )
