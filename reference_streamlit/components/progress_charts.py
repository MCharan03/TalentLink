import streamlit as st
import pandas as pd
import plotly.express as px


def display_progress_charts(connection, cursor, user_id):
    st.subheader("Your Progress Over Time")

    query = "SELECT Timestamp, resume_score FROM user_data WHERE user_id = %s AND resume_score IS NOT NULL ORDER BY Timestamp ASC"
    cursor.execute(query, (user_id,))
    progress_data = cursor.fetchall()

    if len(progress_data) < 2:
        st.info("You need at least two resume analyses to see your progress.")
        return

    df = pd.DataFrame(progress_data, columns=["Timestamp", "Resume Score"])
    # Convert score to numeric, coercing errors
    df["Resume Score"] = pd.to_numeric(df["Resume Score"], errors='coerce')
    # Convert timestamp to datetime
    df["Timestamp"] = pd.to_datetime(
        df["Timestamp"], format='%Y-%m-%d_%H:%M:%S')
    df.dropna(inplace=True)  # Drop rows where score could not be converted

    if not df.empty:
        fig = px.line(
            df,
            x="Timestamp",
            y="Resume Score",
            title="Resume Score Over Time",
            markers=True
        )
        fig.update_layout(
            xaxis_title="Date of Analysis",
            yaxis_title="Resume Score (/100)",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No scorable resume analyses found.")
