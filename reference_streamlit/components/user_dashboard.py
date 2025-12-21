import streamlit as st
import pandas as pd


def display_user_dashboard(connection, cursor, user_id):
    st.subheader("Your Past Analyses")
    # Explicitly list columns to ensure correct order
    query = "SELECT ID, Name, Email_ID, ai_feedback, Timestamp, Page_no, Predicted_Field, User_level, Actual_skills, Recommended_skills, Recommended_courses, user_id FROM user_data WHERE user_id = %s"
    cursor.execute(query, (user_id,))
    user_analyses = cursor.fetchall()
    if user_analyses:
        # Use a matching and correct list of column names
        columns = ['ID', 'Name', 'Email_ID', 'ai_feedback', 'Timestamp', 'Page_no', 'Predicted_Field',
                   'User_level', 'Actual_skills', 'Recommended_skills', 'Recommended_courses', 'user_id']
        df = pd.DataFrame(user_analyses, columns=columns)
        st.dataframe(df)
    else:
        st.info("You have no past analyses.")
