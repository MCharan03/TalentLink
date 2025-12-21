import streamlit as st
import pymysql
import os
import datetime
import json
from logger_config import logger
from database_setup import create_tables, delete_all_data, reset_database


def create_secrets_file_if_not_exists():
    """Creates the .streamlit directory and secrets.toml file if they don't exist."""
    secrets_dir = ".streamlit"
    secrets_file_path = os.path.join(secrets_dir, "secrets.toml")
    if not os.path.exists(secrets_dir):
        os.makedirs(secrets_dir)
    if not os.path.exists(secrets_file_path):
        with open(secrets_file_path, "w") as f:
            f.write("[mysql]\n")
            f.write("host = \"localhost\"\n")
            f.write("user = \"root\"\n")
            f.write("password = \"Gurupadmacherry@36\"\n")
            f.write("database = \"sra\"\n")
            f.write("\n")
            f.write("[admin]\n")
            f.write("username = \"Charan\"\n")
            f.write("password = \"Gurupadmacherry@36\"\n")
            f.write("\n")
            f.write("[google_ai]\n")
            f.write("api_key = \"YOUR_API_KEY\"\n")
            f.write("\n")
            f.write("[email]\n")
            f.write("smtp_server = \"smtp.example.com\"\n")
            f.write("smtp_port = 587\n")
            f.write("smtp_user = \"your_email@example.com\"\n")
            f.write("smtp_password = \"your_email_password\"\n")
        st.info("A new `.streamlit/secrets.toml` file has been created with default credentials. Please edit these for a production environment.")
        st.rerun()


def setup_database():
    """Establishes and caches the database connection."""
    try:
        connection = pymysql.connect(
            host=st.secrets["mysql"]["host"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"],
            connect_timeout=5
        )
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS SRA;")
        connection.select_db("sra")
        create_tables(cursor)
        return connection, cursor
    except (pymysql.err.OperationalError, pymysql.err.InternalError) as e:
        logger.error(f"Database connection error: {e}")
        st.error(
            f"Database connection error: {e}. Please check your credentials in `.streamlit/secrets.toml`.")
        return None, None
    except KeyError:
        logger.error("Database credentials not found in secrets.toml")
        st.error(
            "Database credentials not found. Please ensure you have a `secrets.toml` file.")
        return None, None
    except Exception as e:
        logger.error(
            f"An unexpected error occurred during database setup: {e}")
        st.error(f"An unexpected error occurred during database setup: {e}")
        return None, None


def insert_data(connection, cursor, user_id, name, email, ai_feedback, resume_score, timestamp, no_of_pages, reco_field, cand_level, skills, recommended_skills, courses, quantifiable_achievements_suggestions, formatting_analysis):
    """Inserts data into the user_data table."""
    try:
        DB_table_name = 'user_data'
        insert_sql = f"INSERT INTO {DB_table_name} (user_id, Name, Email_ID, ai_feedback, resume_score, Timestamp, Page_no, Predicted_Field, User_level, Actual_skills, Recommended_skills, Recommended_courses, quantifiable_achievements_suggestions, formatting_analysis) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        rec_values = (user_id, name, email, ai_feedback, resume_score, timestamp, no_of_pages, reco_field, cand_level,
                      skills, recommended_skills, courses, quantifiable_achievements_suggestions, formatting_analysis)
        cursor.execute(insert_sql, rec_values)
        connection.commit()
        logger.info(f"Successfully inserted data for user_id: {user_id}")
    except pymysql.MySQLError as e:
        logger.error(f"Error inserting data for user_id {user_id}: {e}")
        st.error(f"Error inserting data: {e}")
    except Exception as e:
        logger.error(
            f"An unexpected error occurred during data insertion: {e}")
        st.error(f"An unexpected error occurred during data insertion: {e}")


def save_mock_test_results(connection, cursor, user_id, score, assessed_level, test_history):
    """Saves mock test results to the database."""
    try:
        ts = datetime.datetime.fromtimestamp(
            time.time()).strftime('%Y-%m-%d %H:%M:%S')
        test_history_json = json.dumps(test_history)
        insert_sql = "INSERT INTO mock_tests (user_id, timestamp, score, assessed_level, test_history) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(insert_sql, (user_id, ts, score,
                       assessed_level, test_history_json))
        connection.commit()
        logger.info(
            f"Successfully saved mock test results for user_id: {user_id}")
    except pymysql.MySQLError as e:
        logger.error(
            f"Error saving mock test results for user_id {user_id}: {e}")
        st.error(f"Error saving mock test results: {e}")
    except Exception as e:
        logger.error(
            f"An unexpected error occurred during mock test results saving: {e}")
        st.error(
            f"An unexpected error occurred during mock test results saving: {e}")


def save_mock_interview_results(connection, cursor, user_id, overall_summary, interview_history):
    """Saves mock interview results to the database."""
    try:
        ts = datetime.datetime.fromtimestamp(
            time.time()).strftime('%Y-%m-%d %H:%M:%S')
        interview_history_json = json.dumps(interview_history)
        insert_sql = "INSERT INTO mock_interviews (user_id, timestamp, overall_summary, interview_history) VALUES (%s, %s, %s, %s)"
        cursor.execute(
            insert_sql, (user_id, ts, overall_summary, interview_history_json))
        connection.commit()
        logger.info(
            f"Successfully saved mock interview results for user_id: {user_id}")
    except pymysql.MySQLError as e:
        logger.error(
            f"Error saving mock interview results for user_id {user_id}: {e}")
        st.error(f"Error saving mock interview results: {e}")
    except Exception as e:
        logger.error(
            f"An unexpected error occurred during mock interview results saving: {e}")
        st.error(
            f"An unexpected error occurred during mock interview results saving: {e}")


def create_notification(connection, cursor, user_id, message):
    """Creates a new notification for a user."""
    try:
        cursor.execute(
            "INSERT INTO notifications (user_id, message) VALUES (%s, %s)", (user_id, message))
        connection.commit()
        logger.info(f"Created notification for user_id {user_id}: {message}")
    except pymysql.MySQLError as e:
        logger.error(f"Error creating notification for user_id {user_id}: {e}")
        st.error(f"Error creating notification: {e}")
    except Exception as e:
        logger.error(
            f"An unexpected error occurred during notification creation: {e}")
        st.error(
            f"An unexpected error occurred during notification creation: {e}")
