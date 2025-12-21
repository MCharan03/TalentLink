import streamlit as st
import streamlit.components.v1 as components
from ai_utils import generate_mock_test, generate_next_interview_question, get_interview_feedback
from database import save_mock_test_results, save_mock_interview_results
from logger_config import logger
import pyttsx3
import speech_recognition as sr

engine = pyttsx3.init()


def speak(text):
    engine.say(text)
    engine.runAndWait()


def handle_interview_prep(connection, cursor, job_id=None):
    st.write("Interview Prep section is active!")
    if job_id:
        st.title(f"Mock Interview for Job Application #{job_id}")
        handle_mock_interview(connection, cursor, job_id=job_id)
    else:
        st.title("Interview Prep")
        prep_type = st.selectbox("Select Interview Prep Type", [
                                 "Mock Test", "Mock Interview"], key="prep_type_selector")
        if prep_type == "Mock Test":
            handle_mock_test(connection, cursor)
        elif prep_type == "Mock Interview":
            handle_mock_interview(connection, cursor)


def handle_mock_test(connection, cursor):
    logger.info("Entering handle_mock_test function.")
    st.header("Mock Test")
    if 'user_id' not in st.session_state or st.session_state.user_id is None:
        st.warning(
            "User not logged in. Please log in to access mock test features.")
        logger.warning("handle_mock_test: User not logged in.")
        return

    if 'analysis' not in st.session_state or st.session_state.analysis is None:
        st.warning("Please analyze your resume first to generate a mock test.")
        logger.warning(
            "handle_mock_test: Resume analysis not found in session state.")
        return

    predicted_field = st.session_state.analysis.get('predicted_field', 'N/A')
    experience_level = st.session_state.analysis.get('experience_level', 'N/A')
    logger.info(
        f"handle_mock_test: Predicted Field: {predicted_field}, Experience Level: {experience_level}")

    if st.button("Generate Mock Test"):
        with st.spinner("Generating mock test..."):
            mock_test = generate_mock_test(predicted_field, experience_level)
            logger.info(
                f"handle_mock_test: Result of generate_mock_test: {mock_test}")
            if mock_test:
                st.session_state.mock_test = mock_test
                st.session_state.user_answers = [
                    None] * len(mock_test['questions'])
                logger.info(
                    "handle_mock_test: Mock test generated successfully.")
            else:
                st.error("Failed to generate mock test.")
                logger.error("handle_mock_test: Failed to generate mock test.")

    if 'mock_test' in st.session_state:
        mock_test = st.session_state.mock_test
        questions = mock_test['questions']
        user_answers = st.session_state.user_answers

        for i, q in enumerate(questions):
            st.subheader(f"Question {i+1}: {q['question']}")
            options = q['options']
            user_answers[i] = st.radio("Options", options, key=f"q{i}")

        if st.button("Submit Test"):
            score = 0
            test_history = []
            for i, q in enumerate(questions):
                correct_answer = q['answer']
                user_answer = user_answers[i]
                is_correct = user_answer == correct_answer
                if is_correct:
                    score += 1
                test_history.append({
                    'question': q['question'],
                    'user_answer': user_answer,
                    'correct_answer': correct_answer,
                    'is_correct': is_correct,
                    'explanation': q['explanation']
                })

            st.session_state.test_results = {
                'score': score,
                'total_questions': len(questions),
                'test_history': test_history
            }
            st.rerun()

    if 'test_results' in st.session_state:
        results = st.session_state.test_results
        st.subheader("Test Results")
        st.write(
            f"Your score: {results['score']} / {results['total_questions']}")

        for i, record in enumerate(results['test_history']):
            with st.expander(f"Question {i+1}: {record['question']}"):
                st.write(f"Your answer: {record['user_answer']}")
                st.write(f"Correct answer: {record['correct_answer']}")
                if record['is_correct']:
                    st.success("Correct!")
                else:
                    st.error("Incorrect!")
                st.write("Explanation:", record['explanation'])

        if st.button("Save Test Results"):
            save_mock_test_results(connection, cursor, st.session_state.user_id,
                                   f"{results['score']} / {results['total_questions']}", "N/A", results['test_history'])
            st.success("Test results saved successfully!")


def handle_mock_interview(connection, cursor, job_id=None):
    logger.info("Entering handle_mock_interview function.")
    st.header("Mock Interview")

    if 'user_id' not in st.session_state or st.session_state.user_id is None:
        st.warning(
            "User not logged in. Please log in to access mock interview features.")
        logger.warning("handle_mock_interview: User not logged in.")
        return

    # Initialize session state
    if 'interview_phase' not in st.session_state:
        st.session_state.interview_phase = 'not_started'
    if 'interview_history' not in st.session_state:
        st.session_state.interview_history = []
    if 'current_interview_question' not in st.session_state:
        st.session_state.current_interview_question = None
    if 'interview_feedback' not in st.session_state:
        st.session_state.interview_feedback = None

    # Get user's predicted field and experience level from the latest analysis
    predicted_field = None
    experience_level = None

    if 'analysis' in st.session_state and st.session_state.analysis is not None:
        predicted_field = st.session_state.analysis.get('predicted_field')
        experience_level = st.session_state.analysis.get('experience_level')
        logger.info(
            f"handle_mock_interview: Retrieved from session state - Predicted Field: {predicted_field}, Experience Level: {experience_level}")

    if not predicted_field or not experience_level or predicted_field == 'N/A' or experience_level == 'N/A':
        # Try to fetch the latest analysis from the database if not in session state or is N/A
        cursor.execute(
            "SELECT Predicted_Field, User_level FROM user_data WHERE user_id = %s ORDER BY Timestamp DESC LIMIT 1", (st.session_state.user_id,))
        latest_analysis = cursor.fetchone()
        if latest_analysis:
            predicted_field = latest_analysis[0]
            experience_level = latest_analysis[1]
            logger.info(
                f"handle_mock_interview: Retrieved from database - Predicted Field: {predicted_field}, Experience Level: {experience_level}")
        else:
            st.warning("Please analyze your resume first to start a mock interview. Your resume analysis helps us tailor the interview questions to your predicted field and experience level.")
            logger.warning(
                "handle_mock_interview: Resume analysis not found in session state or database.")
            return

    if st.session_state.interview_phase == 'not_started':
        st.info(
            "This is a conversational mock interview. Your answers will be recorded and evaluated at the end.")
        if st.button("Start Interview"):
            st.session_state.interview_phase = 'in_progress'
            st.session_state.current_interview_question = generate_next_interview_question(
                [], predicted_field, experience_level)
            if st.session_state.current_interview_question and st.session_state.current_interview_question.get('status') == 'in_progress':
                speak(st.session_state.current_interview_question['question'])
            logger.info(
                f"handle_mock_interview: Initial interview question generated: {st.session_state.current_interview_question}")
            st.rerun()

    elif st.session_state.interview_phase == 'in_progress':
        q = st.session_state.current_interview_question
        if q and q.get('status') == 'in_progress':
            with open('proctoring_component.html', 'r') as f:
                html_code = f.read()
                components.html(html_code, height=0)

            col1, col2 = st.columns([1, 2])

            with col1:
                # Add the camera input widget here
                st.camera_input("Your Camera View")

            with col2:
                st.subheader(q['question'])
                user_answer = st.text_area(
                    "Your Answer", key=f"interview_q_{len(st.session_state.interview_history)}")

                if st.button("Record Answer"):
                    r = sr.Recognizer()
                    with sr.Microphone() as source:
                        st.info("Listening...")
                        audio = r.listen(source)
                    try:
                        user_answer = r.recognize_google(audio)
                        st.session_state[f"interview_q_{len(st.session_state.interview_history)}"] = user_answer
                    except sr.UnknownValueError:
                        st.warning("Could not understand audio")
                    except sr.RequestError as e:
                        st.error(
                            f"Could not request results from Google Speech Recognition service; {e}")

                if st.button("Submit Answer"):
                    st.session_state.interview_history.append(
                        {'question': q['question'], 'answer': user_answer})
                    st.session_state.current_interview_question = generate_next_interview_question(
                        st.session_state.interview_history, predicted_field, experience_level)
                    if st.session_state.current_interview_question and st.session_state.current_interview_question.get('status') == 'in_progress':
                        speak(
                            st.session_state.current_interview_question['question'])
                    logger.info(
                        f"handle_mock_interview: Next interview question generated: {st.session_state.current_interview_question}")
                    st.rerun()
        else:
            st.session_state.interview_phase = 'completed'
            with st.spinner("Generating feedback..."):
                st.session_state.interview_feedback = get_interview_feedback(
                    st.session_state.interview_history)
            logger.info(
                f"handle_mock_interview: Interview feedback generated: {st.session_state.interview_feedback}")
            st.rerun()

    elif st.session_state.interview_phase == 'completed':
        feedback = st.session_state.interview_feedback
        st.subheader("Interview Feedback")

        if feedback:
            st.write("Overall Summary:", feedback.get(
                'overall_summary', 'N/A'))
            st.write("Recommendation:", feedback.get('recommendation', 'N/A'))
            st.write("Justification:", feedback.get('justification', 'N/A'))

            # Save the interview results to the database
            save_mock_interview_results(connection, cursor, st.session_state.user_id, feedback.get(
                'overall_summary', 'N/A'), st.session_state.interview_history)
            logger.info(
                "handle_mock_interview: Interview results saved to database.")

            # Pass/Fail logic and database update (only for job application interviews)
            if job_id:
                recommendation = feedback.get('recommendation', '').lower()
                if "hire" in recommendation:  # Catches "Hire" and "Strong Hire"
                    new_status = 'mock_interview_passed'
                    st.success(
                        "Congratulations! You have passed the mock interview. The admin has been notified.")
                else:
                    new_status = 'mock_interview_failed'
                    st.error("Thank you for completing the mock interview. Unfortunately, based on the feedback, you did not pass this time. Please review the summary and justification for more details.")

                try:
                    cursor.execute("UPDATE job_applications SET status = %s WHERE user_id = %s AND job_id = %s", (
                        new_status, st.session_state.user_id, job_id))
                    connection.commit()
                    logger.info(
                        f"handle_mock_interview: Job application status updated to {new_status} for job_id {job_id}.")
                except Exception as e:
                    st.error(f"Error updating application status: {e}")
                    logger.error(
                        f"handle_mock_interview: Error updating application status: {e}")

        else:
            st.error("Failed to get feedback for the interview.")
            logger.error(
                "handle_mock_interview: Failed to get feedback for the interview.")

        if st.button("Back to Dashboard"):
            # Reset all relevant session state variables
            st.session_state.start_mock_interview_for_job_id = None
            st.session_state.interview_phase = 'not_started'
            st.session_state.interview_history = []
            st.session_state.current_interview_question = None
            st.session_state.interview_feedback = None
            st.rerun()
