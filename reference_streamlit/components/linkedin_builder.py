import streamlit as st
from ai_utils import generate_resume_analysis


def display_linkedin_builder():
    st.header("LinkedIn Profile Builder")

    with st.form("linkedin_form"):
        st.subheader("Personal Information")
        name = st.text_input("Full Name", key="linkedin_name_input")
        email = st.text_input("Email", key="linkedin_email_input")
        phone = st.text_input("Phone", key="linkedin_phone_input")
        linkedin = st.text_input(
            "LinkedIn Profile URL", key="linkedin_linkedin_input")

        st.subheader("Summary / About Section")
        summary = st.text_area("Summary", key="linkedin_summary_input")

        st.subheader("Work Experience")
        num_jobs = st.number_input(
            "Number of Job Experiences", min_value=1, value=1, key="linkedin_num_jobs")
        jobs = []
        for i in range(num_jobs):
            st.markdown(f"---")
            st.markdown(f"### Job {i+1}")
            job_title = st.text_input(
                f"Job Title {i+1}", key=f"linkedin_job_title_{i}")
            company = st.text_input(
                f"Company {i+1}", key=f"linkedin_company_{i}")
            job_location = st.text_input(
                f"Location {i+1}", key=f"linkedin_job_location_{i}")
            job_dates = st.text_input(
                f"Dates (e.g., Jan 2020 - Present) {i+1}", key=f"linkedin_job_dates_{i}")
            job_desc = st.text_area(
                f"Description {i+1}", key=f"linkedin_job_desc_{i}")
            jobs.append(
                (job_title, company, job_location, job_dates, job_desc))

        if st.form_submit_button("Get AI Suggestions for LinkedIn"):
            with st.spinner("Generating suggestions..."):
                for i, job in enumerate(jobs):
                    suggestions = generate_resume_analysis(
                        job[4])  # Assuming this is generic enough
                    if suggestions and suggestions.get('quantifiable_achievements_suggestions'):
                        st.info(f"AI Suggestions for Job {i+1}:")
                        for suggestion in suggestions.get('quantifiable_achievements_suggestions'):
                            st.write(suggestion)

        st.subheader("Education")
        num_edu = st.number_input(
            "Number of Educational Qualifications", min_value=1, value=1, key="linkedin_num_edu")
        educations = []
        for i in range(num_edu):
            st.markdown(f"---")
            st.markdown(f"### Education {i+1}")
            degree = st.text_input(f"Degree {i+1}", key=f"linkedin_degree_{i}")
            university = st.text_input(
                f"University {i+1}", key=f"linkedin_university_{i}")
            edu_location = st.text_input(
                f"Location {i+1}", key=f"linkedin_edu_location_{i}")
            edu_dates = st.text_input(
                f"Dates (e.g., Aug 2016 - May 2020) {i+1}", key=f"linkedin_edu_dates_{i}")
            educations.append((degree, university, edu_location, edu_dates))

        st.subheader("Skills")
        skills = st.text_area(
            "Skills (comma-separated, top skills first)", key="linkedin_skills_input")

        st.subheader("Projects")
        num_projects = st.number_input(
            "Number of Projects", min_value=1, value=1, key="linkedin_num_projects")
        projects = []
        for i in range(num_projects):
            st.markdown(f"---")
            st.markdown(f"### Project {i+1}")
            project_name = st.text_input(
                f"Project Name {i+1}", key=f"linkedin_project_name_{i}")
            project_desc = st.text_area(
                f"Project Description {i+1}", key=f"linkedin_project_desc_{i}")
            projects.append((project_name, project_desc))

        submitted = st.form_submit_button(
            "Generate LinkedIn Profile Text", key="generate_linkedin_button")

        if submitted:
            profile_text = ""

            # Summary
            profile_text += "### About Section ###\n"
            profile_text += "=====================\n"
            profile_text += summary + "\n\n"

            # Work Experience
            profile_text += "### Work Experience ###\n"
            profile_text += "=======================\n\n"
            for job in jobs:
                profile_text += f"**Title:** {job[0]}\n"
                profile_text += f"**Company:** {job[1]}\n"
                profile_text += f"**Dates:** {job[3]}\n"
                profile_text += f"**Location:** {job[2]}\n"
                profile_text += f"**Description:**\n{job[4]}\n\n"

            # Education
            profile_text += "### Education ###\n"
            profile_text += "=================\n\n"
            for edu in educations:
                profile_text += f"**School:** {edu[1]}\n"
                profile_text += f"**Degree:** {edu[0]}\n"
                profile_text += f"**Dates:** {edu[3]}\n\n"

            # Skills
            profile_text += "### Skills ###\n"
            profile_text += "==============\n"
            profile_text += skills + "\n\n"

            # Projects
            profile_text += "### Projects ###\n"
            profile_text += "================\n\n"
            for proj in projects:
                profile_text += f"**Project Name:** {proj[0]}\n"
                profile_text += f"**Description:**\n{proj[1]}\n\n"

            st.download_button(
                label="Download LinkedIn Profile as Text File",
                data=profile_text,
                file_name=f"{name.replace(' ', '_')}_LinkedIn_Profile.txt",
                mime="text/plain",
            )
