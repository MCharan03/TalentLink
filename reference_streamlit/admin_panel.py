import streamlit as st
import pandas as pd
import json
from ai_utils import generate_job_description
from logger_config import logger
from database import create_notification


def handle_admin_panel(connection, cursor):
    st.title("Applicant Tracking & Job Management")

    # --- Create New Job Posting ---
    with st.expander("Create New Job Posting"):
        # Initialize session state for form fields if they don't exist
        if 'job_title' not in st.session_state:
            st.session_state.job_title = ""
        if 'job_description' not in st.session_state:
            st.session_state.job_description = ""
        if 'required_skills' not in st.session_state:
            st.session_state.required_skills = ""

        st.session_state.job_title = st.text_input(
            "Job Title", value=st.session_state.job_title)

        if st.button("Generate with AI"):
            if st.session_state.job_title:
                with st.spinner("Generating job description and skills..."):
                    generated_content = generate_job_description(
                        st.session_state.job_title)
                    if generated_content:
                        st.session_state.job_description = generated_content.get(
                            "description", "")
                        st.session_state.required_skills = generated_content.get(
                            "skills", "")
            else:
                st.warning("Please enter a job title first.")

        with st.form("new_job_form"):
            # The title is outside the form now, but we use its state
            st.text_area("Job Description", key="job_description")
            st.text_input("Required Skills (comma-separated)",
                          key="required_skills")

            allowed_experience = st.multiselect(
                "Allowed Experience Levels",
                ["All", "Fresher", "Intermediate",
                    "Experienced", "Senior", "Lead", "Principal"]
            )

            submitted = st.form_submit_button("Create Job Posting")
            if submitted:
                if "All" in allowed_experience:
                    experience_str = "All"
                else:
                    experience_str = ",".join(allowed_experience)
                try:
                    cursor.execute(
                        "INSERT INTO job_postings (title, description, required_skills, min_experience_level) VALUES (%s, %s, %s, %s)",
                        (st.session_state.job_title, st.session_state.job_description,
                         st.session_state.required_skills, experience_str)
                    )
                    connection.commit()
                    logger.info(
                        f"Admin created new job posting: {st.session_state.job_title}")
                    st.success("New job posting created successfully!")
                    # Clear form fields after submission
                    st.session_state.job_title = ""
                    st.session_state.job_description = ""
                    st.session_state.required_skills = ""
                except Exception as e:
                    logger.error(f"Error creating job posting: {e}")
                    st.error(f"Error creating job posting: {e}")

    st.markdown("---")

    # --- Manage Job Postings ---
    st.header("Manage Job Postings")

    # Pagination setup
    if 'job_page_number' not in st.session_state:
        st.session_state.job_page_number = 0

    jobs_per_page = 5

    # Get total number of jobs
    cursor.execute("SELECT COUNT(*) FROM job_postings")
    total_jobs = cursor.fetchone()[0]
    total_pages = (total_jobs // jobs_per_page) + \
        (1 if total_jobs % jobs_per_page > 0 else 0)

    # Fetch jobs for the current page
    offset = st.session_state.job_page_number * jobs_per_page
    cursor.execute(
        f"SELECT id, title, status FROM job_postings ORDER BY created_at ASC LIMIT {jobs_per_page} OFFSET {offset}")
    all_jobs = cursor.fetchall()

    if not all_jobs and st.session_state.job_page_number == 0:
        st.info("No job postings found. Create one above to get started.")
    else:
        for job in all_jobs:
            job_id, title, status = job
            st.subheader(f"#{job_id} - {title}")
            st.write(f"Status: **{status.title()}**")

            if status == 'open':
                if st.button("Close Job", key=f"close_{job_id}"):
                    try:
                        cursor.execute(
                            "UPDATE job_postings SET status = 'closed' WHERE id = %s", (job_id,))
                        connection.commit()
                        logger.info(f"Admin closed job_id: {job_id}")
                        st.rerun()
                    except Exception as e:
                        logger.error(f"Error closing job_id {job_id}: {e}")
                        st.error(f"Error closing job: {e}")
            else:
                if st.button("Re-open Job", key=f"reopen_{job_id}"):
                    try:
                        cursor.execute(
                            "UPDATE job_postings SET status = 'open' WHERE id = %s", (job_id,))
                        connection.commit()
                        logger.info(f"Admin re-opened job_id: {job_id}")
                        st.rerun()
                    except Exception as e:
                        logger.error(f"Error re-opening job_id {job_id}: {e}")
                        st.error(f"Error re-opening job: {e}")

            if st.button("Delete Job", key=f"delete_job_{job_id}"):
                st.session_state.confirm_delete_job_id = job_id

            # Confirmation for job delete
            if st.session_state.get('confirm_delete_job_id') == job_id:
                st.warning(
                    f"Are you sure you want to permanently delete this job posting and all its associated applications? This action cannot be undone.")
                if st.button("Confirm Delete Job", key=f"confirm_delete_job_{job_id}"):
                    try:
                        # First, delete all applications for this job
                        cursor.execute(
                            "DELETE FROM job_applications WHERE job_id = %s", (job_id,))
                        # Then, delete the job posting itself
                        cursor.execute(
                            "DELETE FROM job_postings WHERE id = %s", (job_id,))
                        connection.commit()
                        logger.info(
                            f"Admin deleted job_id: {job_id} and all associated applications.")
                        st.success(
                            "Job posting and all associated applications have been deleted.")
                        st.session_state.confirm_delete_job_id = None
                        st.rerun()
                    except Exception as e:
                        logger.error(f"Error deleting job_id {job_id}: {e}")
                        st.error(f"Error deleting job posting: {e}")

            st.markdown("---")

    # Pagination controls
    if total_pages > 1:
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("Previous Page", disabled=(st.session_state.job_page_number == 0)):
                st.session_state.job_page_number -= 1
                st.rerun()
        with col2:
            st.write(
                f"Page {st.session_state.job_page_number + 1} of {total_pages}")
        with col3:
            if st.button("Next Page", disabled=(st.session_state.job_page_number >= total_pages - 1)):
                st.session_state.job_page_number += 1
                st.rerun()

    # --- View Applicants ---
    st.header("View Applicants")

    cursor.execute(
        "SELECT id, title, status FROM job_postings ORDER BY created_at ASC")
    jobs_for_selectbox = cursor.fetchall()

    if not jobs_for_selectbox:
        return  # No need to show the applicant viewer if there are no jobs

    job_options = {
        job[0]: f"#{job[0]} - {job[1]} ({job[2]})" for job in jobs_for_selectbox}
    selected_job_id = st.selectbox("Select a Job Posting to View Applicants", options=list(
        job_options.keys()), format_func=lambda x: job_options[x])

    if selected_job_id:
        # --- Display Applicants for the Selected Job ---
        st.subheader(f"Applicants for {job_options[selected_job_id]}")

        # Pagination for applicants
        if 'app_page_number' not in st.session_state:
            st.session_state.app_page_number = 0

        apps_per_page = 5

        # Get total number of applicants for the selected job
        cursor.execute(
            "SELECT COUNT(*) FROM job_applications WHERE job_id = %s", (selected_job_id,))
        total_apps = cursor.fetchone()[0]
        total_app_pages = (total_apps // apps_per_page) + \
            (1 if total_apps % apps_per_page > 0 else 0)

        # Fetch applicants for the current page
        app_offset = st.session_state.app_page_number * apps_per_page
        query = f"""
            SELECT
                ja.id,
                u.username,
                ud.Name,
                ud.User_level,
                ud.resume_score,
                ja.status,
                ja.application_date,
                ud.ai_feedback,
                mi.overall_summary AS interview_summary,
                mi.interview_history,
                ja.user_id,
                u.username as email
            FROM
                job_applications ja
            JOIN
                users u ON ja.user_id = u.id
            LEFT JOIN
                (
                    SELECT *, ROW_NUMBER() OVER(PARTITION BY user_id ORDER BY Timestamp DESC) as rn
                    FROM user_data
                ) ud ON ja.user_id = ud.user_id AND ud.rn = 1
            LEFT JOIN
                (
                    SELECT *, ROW_NUMBER() OVER(PARTITION BY user_id ORDER BY timestamp DESC) as rn
                    FROM mock_interviews
                ) mi ON ja.user_id = mi.user_id AND mi.rn = 1
            WHERE
                ja.job_id = %s
            ORDER BY
                ja.application_date DESC
            LIMIT {apps_per_page} OFFSET {app_offset}
        """
        cursor.execute(query, (selected_job_id,))
        applicants = cursor.fetchall()

        if not applicants and st.session_state.app_page_number == 0:
            st.info("No applicants for this job posting yet.")
        else:
            for app in applicants:
                app_id, username, name, experience_level, resume_score, status, app_date, ai_summary, interview_summary, interview_history_json, user_id, email = app

                with st.expander(f"{name} ({username}) - Status: {status.replace('_', ' ').title()}"):
                    st.write(f"**Applied on:** {app_date}")
                    st.write(f"**Experience Level:** {experience_level}")
                    st.write(f"**Resume Score:** {resume_score}/100")

                    if ai_summary:
                        st.markdown("**AI Resume Summary:**")
                        st.info(ai_summary)

                    if interview_summary:
                        st.markdown("**Mock Interview Feedback:**")
                        st.success(f"**Overall Summary:** {interview_summary}")
                        if interview_history_json:
                            try:
                                history = json.loads(interview_history_json)
                                with st.expander("View Interview Transcript"):
                                    for item in history:
                                        st.text(f"Q: {item['question']}")
                                        st.text(f"A: {item['answer']}")
                            except (json.JSONDecodeError, TypeError):
                                pass  # Ignore if history is not valid JSON

                    st.markdown("---")
                    st.subheader("Manage this Applicant")

                    # Actions for this applicant
                    if status == 'mock_interview_passed':
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if st.button("Shortlist", key=f"shortlist_{app_id}"):
                                try:
                                    cursor.execute(
                                        "UPDATE job_applications SET status = 'shortlisted' WHERE id = %s", (app_id,))
                                    create_notification(
                                        connection, cursor, user_id, f"Congratulations! You have been shortlisted for the position: {job_options[selected_job_id]}.")
                                    send_email(email, f"Update on your application for {job_options[selected_job_id]}",
                                               "Congratulations! You have been shortlisted. We will contact you shortly with the next steps.")
                                    connection.commit()
                                    logger.info(
                                        f"Admin shortlisted application_id: {app_id}")
                                    st.success(
                                        "Applicant has been shortlisted.")
                                    st.rerun()
                                except Exception as e:
                                    logger.error(
                                        f"Error shortlisting application_id {app_id}: {e}")
                                    st.error(f"Error updating status: {e}")
                        with col2:
                            if st.button("Reject", key=f"reject_{app_id}"):
                                try:
                                    cursor.execute(
                                        "UPDATE job_applications SET status = 'rejected' WHERE id = %s", (app_id,))
                                    create_notification(
                                        connection, cursor, user_id, f"We regret to inform you that we will not be moving forward with your application for the position: {job_options[selected_job_id]}.")
                                    send_email(email, f"Update on your application for {job_options[selected_job_id]}",
                                               "We regret to inform you that we will not be moving forward with your application at this time. We appreciate your interest and encourage you to apply for other suitable positions in the future.")
                                    connection.commit()
                                    logger.info(
                                        f"Admin rejected application_id: {app_id}")
                                    st.warning("Applicant has been rejected.")
                                    st.rerun()
                                except Exception as e:
                                    logger.error(
                                        f"Error rejecting application_id {app_id}: {e}")
                                    st.error(f"Error updating status: {e}")
                        with col3:
                            if st.button("Delete", key=f"delete_{app_id}"):
                                st.session_state.confirm_delete_app_id = app_id
                    else:
                        st.write(
                            "No actions available for this applicant at this stage.")

                    # Confirmation for delete
                    if st.session_state.get('confirm_delete_app_id') == app_id:
                        st.warning(
                            f"Are you sure you want to permanently delete this application? This action cannot be undone.")
                        if st.button("Confirm Delete", key=f"confirm_delete_{app_id}"):
                            try:
                                cursor.execute(
                                    "DELETE FROM job_applications WHERE id = %s", (app_id,))
                                connection.commit()
                                logger.info(
                                    f"Admin deleted application_id: {app_id}")
                                st.success("Application has been deleted.")
                                st.session_state.confirm_delete_app_id = None
                                st.rerun()
                            except Exception as e:
                                logger.error(
                                    f"Error deleting application_id {app_id}: {e}")
                                st.error(f"Error deleting application: {e}")

        # Pagination controls for applicants
        if total_app_pages > 1:
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                if st.button("Previous Applicants", disabled=(st.session_state.app_page_number == 0)):
                    st.session_state.app_page_number -= 1
                    st.rerun()
            with col2:
                st.write(
                    f"Page {st.session_state.app_page_number + 1} of {total_app_pages}")
            with col3:
                if st.button("Next Applicants", disabled=(st.session_state.app_page_number >= total_app_pages - 1)):
                    st.session_state.app_page_number += 1
                    st.rerun()


def handle_user_management(connection, cursor):
    st.title("User Management")

    cursor.execute("SELECT id, username, role FROM users")
    users = cursor.fetchall()

    if not users:
        st.info("No users found.")
        return

    df = pd.DataFrame(users, columns=["ID", "Username", "Role"])
    st.dataframe(df)

    st.subheader("Delete User")
    user_to_delete = st.number_input("Enter User ID to delete", min_value=1)
    if st.button("Delete User"):
        try:
            # Delete from related tables first
            cursor.execute(
                "DELETE FROM user_data WHERE user_id = %s", (user_to_delete,))
            cursor.execute(
                "DELETE FROM mock_tests WHERE user_id = %s", (user_to_delete,))
            cursor.execute(
                "DELETE FROM mock_interviews WHERE user_id = %s", (user_to_delete,))
            cursor.execute(
                "DELETE FROM job_applications WHERE user_id = %s", (user_to_delete,))
            cursor.execute(
                "DELETE FROM notifications WHERE user_id = %s", (user_to_delete,))

            # Then delete the user
            cursor.execute("DELETE FROM users WHERE id = %s",
                           (user_to_delete,))

            connection.commit()
            logger.info(
                f"Admin deleted user_id: {user_to_delete} and all their associated data.")
            st.success(
                f"User with ID {user_to_delete} and all their associated data has been deleted.")
            st.rerun()
        except Exception as e:
            logger.error(f"Error deleting user_id {user_to_delete}: {e}")
            st.error(f"Error deleting user: {e}")
