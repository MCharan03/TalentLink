import streamlit as st
import json


def display_past_interviews(connection, cursor, user_id):
    st.subheader("Your Past Mock Interviews")
    cursor.execute(
        "SELECT timestamp, overall_summary, interview_history FROM mock_interviews WHERE user_id = %s ORDER BY timestamp DESC", (user_id,))
    past_interviews = cursor.fetchall()

    if not past_interviews:
        st.info("You have no past mock interview results.")
        return

    for i, interview in enumerate(past_interviews):
        timestamp, overall_summary, interview_history_json = interview
        with st.expander(f"Interview on {timestamp}"):
            st.markdown("**Overall Summary:**")
            st.write(overall_summary)

            try:
                interview_history = json.loads(interview_history_json)
                st.markdown("**Interview Transcript:**")
                for item in interview_history:
                    st.text(f"Q: {item['question']}")
                    st.text(f"A: {item['answer']}")
                    st.markdown("---")
            except (json.JSONDecodeError, TypeError):
                st.warning("Could not load interview transcript.")
