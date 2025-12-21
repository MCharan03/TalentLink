import streamlit as st


def display_job_board(connection, cursor, user_id):
    st.header("Available Job Opportunities")

    cursor.execute(
        "SELECT id, title, description, required_skills, min_experience_level FROM job_postings WHERE status = 'open'")
    jobs = cursor.fetchall()

    if not jobs:
        st.info(
            "No job opportunities available at the moment. Please check back later.")
        return

    for job in jobs:
        job_id, title, description, required_skills, min_experience_level = job
        with st.container():
            st.subheader(title)
            st.markdown(f"**Description:** {description}")
            st.markdown(f"**Required Skills:** {required_skills}")
            st.markdown(f"**Minimum Experience:** {min_experience_level}")

            # Check the user's application status for this job
            cursor.execute(
                "SELECT status FROM job_applications WHERE user_id = %s AND job_id = %s", (user_id, job_id))
            application = cursor.fetchone()

            if application:
                status = application[0]
                if status == 'mock_interview_pending':
                    st.info("You are eligible for a mock interview for this role!")
                    if st.button("Start Mock Interview", key=f"interview_{job_id}"):
                        st.session_state.start_mock_interview_for_job_id = job_id
                        st.rerun()
                else:
                    # Display other statuses like 'applied', 'not_eligible', 'mock_interview_passed', etc.
                    st.success(
                        f"Your application status: **{status.replace('_', ' ').title()}**")
            else:
                if st.button("Apply", key=f"apply_{job_id}"):
                    st.session_state.apply_for_job_id = job_id
                    st.rerun()
