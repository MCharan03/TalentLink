import streamlit as st
import json

from components.resume_preview import display_resume_preview
from components.basic_info import display_basic_info
from components.skills import display_skills_and_recommendations
from components.ai_feedback import display_ai_feedback
from components.course_recommendations import display_course_recommendations
from components.download_buttons import display_download_buttons
from components.bonus_videos import display_bonus_videos
from components.user_dashboard import display_user_dashboard
from components.job_board import display_job_board
from components.past_interviews import display_past_interviews
from components.progress_charts import display_progress_charts
from components.notifications import display_notifications


def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def setup_page_config():
    st.set_page_config(
        page_title="Smart Resume Screener",
        layout="wide"
    )

    if 'theme' not in st.session_state:
        st.session_state.theme = "Dark"

    st.session_state.theme = st.sidebar.selectbox(
        "Theme", ["Dark", "Light"], index=0 if st.session_state.theme == "Dark" else 1)

    load_css("styles/streamlit_components.css")

    if st.session_state.theme == "Dark":
        load_css("styles/style.css")
    else:
        load_css("styles/light_style.css")
