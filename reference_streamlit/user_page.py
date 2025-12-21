import streamlit as st
import os
import time
import datetime
from file_utils import get_pdf_text
from ai_utils import generate_resume_analysis, generate_next_question, generate_updated_analysis
from database import insert_data
from ui import display_resume_preview, display_basic_info, display_skills_and_recommendations, display_course_recommendations, display_ai_feedback, display_bonus_videos, display_download_buttons, display_user_dashboard, display_job_board, display_past_interviews, display_progress_charts
from interview_prep import handle_interview_prep
from logger_config import logger
from components.quantifiable_achievements import display_quantifiable_achievements
from components.formatting_analysis import display_formatting_analysis


def handle_normal_user(connection, cursor):
    if st.button("Logout"):
        st.session_state.user_id = None
        st.session_state.analysis = None
        st.session_state.save_path = None
        st.session_state.page_count = None
        st.rerun()
    # Check for mock interview trigger
    if st.session_state.get('start_mock_interview_for_job_id'):
        job_id = st.session_state.start_mock_interview_for_job_id
        logger.info(
            f"User {st.session_state.user_id} starting mock interview for job_id: {job_id}")
        # Directly call the interview prep page for the specific job
        handle_interview_prep(connection, cursor, job_id=job_id)
    else:
        # If not in a mock interview, show the normal navigation
        st.title("Smart Resume Screener & Analyzer")
        tab1, tab2, tab3 = st.tabs(
            ["Resume Analysis", "My Dashboard", "Interview Prep"])

        with tab1:
            if 'analysis' not in st.session_state:
                st.session_state.analysis = None

            if st.session_state.analysis is None:
                st.info(
                    "💡 **Upload your resume to get smart recommendations and an instant analysis!**")
                pdf_file = st.file_uploader(
                    "📥 **Upload Your Resume (PDF)**", type=["pdf"])
                job_description_input = st.text_area(
                    "Optional: Paste a Job Description for tailored analysis", height=150)

                if pdf_file is not None:
                    with st.spinner('Analyzing your Resume...'):
                        save_path = os.path.join(
                            "./Uploaded_Resumes", pdf_file.name)
                        os.makedirs(os.path.dirname(save_path), exist_ok=True)
                        with open(save_path, "wb") as f:
                            f.write(pdf_file.getbuffer())
                        logger.info(
                            f"User {st.session_state.user_id} uploaded resume: {pdf_file.name}")

                        text, page_count = get_pdf_text(save_path)
                        analysis = generate_resume_analysis(
                            text, job_description_input)
                        if analysis is None:
                            logger.error(
                                f"Resume analysis failed for user {st.session_state.user_id}")
                            st.error(
                                "Error analyzing the resume. Please try again.")
                            return

                        # Insert data only once, right after analysis
                        ts = datetime.datetime.fromtimestamp(
                            time.time()).strftime('%Y-%m-%d_%H:%M:%S')
                        name = analysis.get('name', 'N/A')
                        email = analysis.get('email', 'N/A')
                        ai_summary = analysis.get('ai_summary', 'N/A')
                        resume_score = analysis.get('resume_score', 'N/A')
                        predicted_field = analysis.get(
                            'predicted_field', 'N/A')
                        experience_level = analysis.get(
                            'experience_level', 'N/A')
                        actual_skills = analysis.get('actual_skills', [])
                        recommended_skills = analysis.get(
                            'recommended_skills', [])
                        recommended_courses = analysis.get(
                            'recommended_courses', [])
                        quantifiable_achievements_suggestions = analysis.get(
                            'quantifiable_achievements_suggestions', [])
                        formatting_analysis = analysis.get(
                            'formatting_analysis', '')
                        insert_data(connection, cursor, st.session_state.user_id, name, email, ai_summary, resume_score, ts, str(page_count), predicted_field, experience_level, str(
                            actual_skills), str(recommended_skills), str(recommended_courses), str(quantifiable_achievements_suggestions), formatting_analysis)

                        st.session_state.analysis = analysis
                        st.session_state.save_path = save_path
                        st.session_state.page_count = page_count
                        st.rerun()
                else:
                    st.info("👆 Please upload a PDF resume to get started!")
            else:
                st.success("Resume uploaded and analyzed successfully! 🎉")

                if st.button("Upload another resume"):
                    logger.info(
                        f"User {st.session_state.user_id} clearing analysis to upload another resume.")
                    st.session_state.analysis = None
                    st.session_state.save_path = None
                    st.session_state.page_count = None
                    st.rerun()

                analysis = st.session_state.analysis
                save_path = st.session_state.save_path
                page_count = st.session_state.page_count

                display_resume_preview(save_path)

                if analysis:
                    name = analysis.get('name', 'N/A')
                    email = analysis.get('email', 'N/A')
                    contact_number = analysis.get('contact_number', 'N/A')
                    experience_level = analysis.get('experience_level', 'N/A')

                    resume_score = analysis.get('resume_score', 'N/A')

                    cand_level, no_of_pages = display_basic_info(
                        name, email, contact_number, experience_level, page_count)

                    predicted_field = analysis.get('predicted_field', 'N/A')
                    actual_skills = analysis.get('actual_skills', [])
                    recommended_skills = analysis.get('recommended_skills', [])
                    recommended_courses = analysis.get(
                        'recommended_courses', [])
                    ai_summary = analysis.get('ai_summary', 'N/A')

                    display_skills_and_recommendations(
                        predicted_field, actual_skills, recommended_skills)
                    display_course_recommendations(
                        recommended_courses, resume_score)
                    display_ai_feedback(ai_summary)
                    display_quantifiable_achievements(analysis.get(
                        'quantifiable_achievements_suggestions', []))
                    display_formatting_analysis(
                        analysis.get('formatting_analysis', ''))

                    ts = datetime.datetime.fromtimestamp(
                        time.time()).strftime('%Y-%m-%d_%H:%M:%S')

                    resume_data = {'name': name, 'email': email,
                                   'ai_feedback': ai_summary}

                    resume_vid_url, interview_vid_url = display_bonus_videos()
                    display_download_buttons(resume_data, ts, no_of_pages, predicted_field, cand_level,
                                             actual_skills, recommended_skills, recommended_courses, resume_vid_url, interview_vid_url)

                    # --- Conversational Assessment Section ---
                    with st.container():
                        st.header("Get to Know You More")

                        # Initialize session state variables for the assessment
                        if 'assessment_phase' not in st.session_state:
                            st.session_state.assessment_phase = 'not_started'
                        if 'conversation_history' not in st.session_state:
                            st.session_state.conversation_history = []
                        if 'current_question' not in st.session_state:
                            st.session_state.current_question = None
                        if 'updated_analysis' not in st.session_state:
                            st.session_state.updated_analysis = None

                        # Display the updated analysis if the assessment is complete
                        if st.session_state.updated_analysis:
                            st.subheader("Updated Analysis")
                            st.markdown(
                                st.session_state.updated_analysis['ai_summary'])
                            st.markdown(st.session_state.updated_analysis.get(
                                'how_to_improve', 'No specific improvement suggestions available.'))

                        # Main assessment logic
                        if st.session_state.assessment_phase == 'not_started':
                            st.info(
                                "Take a short assessment to get a more detailed analysis of your skills.")
                            if st.button("Start Assessment"):
                                logger.info(
                                    f"User {st.session_state.user_id} starting conversational assessment.")
                                st.session_state.assessment_phase = 'in_progress'
                                # Get the first question
                                st.session_state.current_question = generate_next_question(
                                    [], predicted_field, experience_level)
                                st.rerun()

                        elif st.session_state.assessment_phase == 'in_progress':
                            if st.session_state.current_question and st.session_state.current_question.get('status') == 'in_progress':
                                q = st.session_state.current_question
                                st.subheader(q['question'])
                                user_answer = st.radio(
                                    "Choose your answer:", q['options'], key=f"q_{len(st.session_state.conversation_history)}")

                                if st.button("Submit Answer"):
                                    # Record the answer
                                    st.session_state.conversation_history.append(
                                        {'question': q['question'], 'answer': user_answer})

                                    # Get the next question
                                    st.session_state.current_question = generate_next_question(
                                        st.session_state.conversation_history, predicted_field, experience_level)
                                    st.rerun()
                            else:
                                # Assessment is complete
                                logger.info(
                                    f"User {st.session_state.user_id} completed conversational assessment.")
                                st.session_state.assessment_phase = 'completed'
                                with st.spinner("Generating updated analysis..."):
                                    st.session_state.updated_analysis = generate_updated_analysis(
                                        analysis, st.session_state.conversation_history)
                                st.rerun()

                        elif st.session_state.assessment_phase == 'completed':
                            st.success(
                                "Assessment completed! See your updated analysis above.")
                            if st.button("Retake Assessment"):
                                # Reset the assessment state
                                st.session_state.assessment_phase = 'not_started'
                                st.session_state.conversation_history = []
                                st.session_state.current_question = None
                                st.session_state.updated_analysis = None
                                st.rerun()

        with tab2:
            st.header("My Dashboard")

            # Handle job application logic
            if 'apply_for_job_id' in st.session_state and st.session_state.apply_for_job_id is not None:
                job_id = st.session_state.apply_for_job_id
                try:
                    # Insert application into the database
                    cursor.execute("INSERT INTO job_applications (user_id, job_id, status) VALUES (%s, %s, %s)", (
                        st.session_state.user_id, job_id, 'applied'))
                    connection.commit()
                    logger.info(
                        f"User {st.session_state.user_id} applied for job_id: {job_id}")

                    # --- Eligibility Check ---
                    # Fetch job requirements
                    cursor.execute(
                        "SELECT required_skills, min_experience_level FROM job_postings WHERE id = %s", (job_id,))
                    job_requirements = cursor.fetchone()

                    # Fetch user's latest analysis
                    cursor.execute(
                        "SELECT Actual_skills, User_level FROM user_data WHERE user_id = %s ORDER BY Timestamp DESC LIMIT 1", (st.session_state.user_id,))
                    user_data = cursor.fetchone()

                    if job_requirements and user_data:
                        required_skills = job_requirements[0].lower().split(
                            ',')
                        user_skills = user_data[0].lower()
                        user_level = user_data[1]

                        # Simple eligibility check
                        skills_match = all(
                            skill.strip() in user_skills for skill in required_skills)

                        # Experience level check
                        allowed_experience = job_requirements[1].lower()
                        if allowed_experience == 'all':
                            level_match = True
                        else:
                            allowed_experience_list = allowed_experience.split(
                                ',')
                            level_match = user_level.lower() in allowed_experience_list

                        if skills_match and level_match:
                            # Eligible for mock interview
                            cursor.execute("UPDATE job_applications SET status = %s WHERE user_id = %s AND job_id = %s", (
                                'mock_interview_pending', st.session_state.user_id, job_id))
                            connection.commit()
                            logger.info(
                                f"User {st.session_state.user_id} is eligible for mock interview for job_id: {job_id}")
                            st.success(
                                "Application submitted! You are eligible for the next step: a mock interview. You can find it in your dashboard.")
                        else:
                            # Not eligible
                            cursor.execute("UPDATE job_applications SET status = %s WHERE user_id = %s AND job_id = %s", (
                                'not_eligible', st.session_state.user_id, job_id))
                            connection.commit()
                            logger.warning(
                                f"User {st.session_state.user_id} is not eligible for job_id: {job_id}")
                            st.warning(
                                "Application submitted. However, your profile does not meet the minimum requirements for this job. We encourage you to use our analysis tools to improve your resume.")

                except Exception as e:
                    logger.error(
                        f"Error during job application for user {st.session_state.user_id}, job_id {job_id}: {e}")
                    st.error(f"Error applying for the job: {e}")
                finally:
                    # Reset the session state variable
                    st.session_state.apply_for_job_id = None

            dashboard_tab1, dashboard_tab2, dashboard_tab3, dashboard_tab4, dashboard_tab5, dashboard_tab6 = st.tabs(
                ["Past Analyses", "Job Opportunities", "My Progress", "Past Interview Analysis", "Resume Builder", "LinkedIn Builder"])

            with dashboard_tab1:
                display_user_dashboard(
                    connection, cursor, st.session_state.user_id)

            with dashboard_tab2:
                display_job_board(connection, cursor, st.session_state.user_id)

            with dashboard_tab3:
                display_progress_charts(
                    connection, cursor, st.session_state.user_id)

            with dashboard_tab4:
                display_past_interviews(
                    connection, cursor, st.session_state.user_id)

            with dashboard_tab5:
                from components.resume_builder import display_resume_builder
                display_resume_builder()

            with dashboard_tab6:
                from components.linkedin_builder import display_linkedin_builder
                display_linkedin_builder()

        with tab3:
            # General interview prep, not for a specific job
            handle_interview_prep(connection, cursor)
