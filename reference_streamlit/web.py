import streamlit as st
import nltk
import os
import datetime
import time
from logger_config import logger

from auth import register_user, login_user, display_login_form, display_registration_form
from file_utils import format_as_bullet_list, fetch_yt_video_title, get_pdf_text, create_user_pdf, create_doc, create_admin_pdf, show_pdf
from ai_utils import generate_resume_analysis
from user_page import handle_normal_user
from database import create_secrets_file_if_not_exists, setup_database, insert_data
from ui import setup_page_config, display_resume_preview, display_basic_info, display_skills_and_recommendations, display_ai_feedback, display_course_recommendations, display_download_buttons, display_bonus_videos, display_user_dashboard, display_notifications
from admin_page import handle_admin_user


def main():
    logger.info("Application started.")
    create_secrets_file_if_not_exists()
    setup_page_config()
    connection, cursor = setup_database()
    logger.info("Database setup complete.")

    st.sidebar.title("Role Selection")
    choice = st.sidebar.selectbox("Select Role", ["Normal User", "Admin"])
    logger.info(f"Role selected: {choice}")

    if choice == "Normal User":
        if 'user_id' not in st.session_state:
            st.session_state.user_id = None
        logger.info(f"Current user_id in session: {st.session_state.user_id}")

        if st.session_state.user_id is None:
            st.title("📄 Smart Resume Screener & Analyzer")
            login_tab, register_tab = st.tabs(["Login", "Register"])
            with login_tab:
                username, password = display_login_form()
                if username and password:
                    logger.info(
                        f"Login form submitted for username: {username}")
                    user_id = login_user(cursor, username, password)
                    if user_id:
                        st.session_state.user_id = user_id
                        logger.info(
                            f"User {username} logged in successfully. User ID: {user_id}")
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                        logger.warning(
                            f"Login failed for username: {username}")
            with register_tab:
                new_username, email, new_password = display_registration_form()
                if new_username and email and new_password:
                    logger.info(
                        f"Registration form submitted for new username: {new_username}")
                    register_user(connection, cursor,
                                  new_username, email, new_password)
        else:
            logger.info(
                f"User already logged in with ID: {st.session_state.user_id}")
            display_notifications(connection, cursor, st.session_state.user_id)

            handle_normal_user(connection, cursor)
    elif choice == "Admin":
        logger.info("Admin role selected.")
        handle_admin_user(connection, cursor)


if __name__ == "__main__":
    main()
