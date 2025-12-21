
import pymysql
from logger_config import logger
import streamlit as st


def create_tables(cursor):
    """Creates all the necessary tables in the database."""
    DB_table_name = 'user_data'
    table_sql = f"""
    CREATE TABLE IF NOT EXISTS {DB_table_name} (
        ID INT NOT NULL AUTO_INCREMENT,
        Name VARCHAR(100),
        Email_ID VARCHAR(50),
        ai_feedback TEXT,
        Timestamp VARCHAR(50),
        Page_no VARCHAR(5),
        Predicted_Field VARCHAR(100),
        User_level VARCHAR(30),
        Actual_skills TEXT,
        Recommended_skills TEXT,
        Recommended_courses TEXT,
        PRIMARY KEY (ID)
    );
    """
    cursor.execute(table_sql)

    users_table_sql = f"""
    CREATE TABLE IF NOT EXISTS users (
        id INT NOT NULL AUTO_INCREMENT,
        username VARCHAR(255) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        role VARCHAR(50) NOT NULL DEFAULT 'user',
        PRIMARY KEY (id)
    );
    """
    cursor.execute(users_table_sql)

    cursor.execute("SHOW COLUMNS FROM users LIKE 'email'")
    if not cursor.fetchone():
        cursor.execute(
            "ALTER TABLE users ADD COLUMN email VARCHAR(255) NOT NULL UNIQUE AFTER username")

    cursor.execute(f"SHOW COLUMNS FROM {DB_table_name} LIKE 'user_id'")
    user_id_exists = cursor.fetchone()
    if not user_id_exists:
        cursor.execute(
            f"ALTER TABLE {DB_table_name} ADD COLUMN user_id INT, ADD FOREIGN KEY (user_id) REFERENCES users(id)")

    cursor.execute(f"SHOW COLUMNS FROM {DB_table_name} LIKE 'ai_feedback'")
    ai_feedback_exists = cursor.fetchone()

    cursor.execute(f"SHOW COLUMNS FROM {DB_table_name} LIKE 'resume_score'")
    resume_score_exists = cursor.fetchone()

    if not ai_feedback_exists and resume_score_exists:
        cursor.execute(
            f"ALTER TABLE {DB_table_name} CHANGE COLUMN resume_score ai_feedback TEXT")
    elif not ai_feedback_exists:
        cursor.execute(
            f"ALTER TABLE {DB_table_name} ADD COLUMN ai_feedback TEXT")

    mock_tests_table_sql = """
    CREATE TABLE IF NOT EXISTS mock_tests (
        id INT NOT NULL AUTO_INCREMENT,
        user_id INT,
        timestamp VARCHAR(50),
        score VARCHAR(20),
        assessed_level VARCHAR(50),
        test_history JSON,
        PRIMARY KEY (id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """
    cursor.execute(mock_tests_table_sql)

    mock_interviews_table_sql = """
    CREATE TABLE IF NOT EXISTS mock_interviews (
        id INT NOT NULL AUTO_INCREMENT,
        user_id INT,
        timestamp VARCHAR(50),
        overall_summary TEXT,
        interview_history JSON,
        PRIMARY KEY (id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """
    cursor.execute(mock_interviews_table_sql)

    job_postings_table_sql = """
    CREATE TABLE IF NOT EXISTS job_postings (
        id INT NOT NULL AUTO_INCREMENT,
        title VARCHAR(255) NOT NULL,
        description TEXT,
        required_skills TEXT,
        min_experience_level VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status VARCHAR(50) DEFAULT 'open',
        PRIMARY KEY (id)
    );
    """
    cursor.execute(job_postings_table_sql)

    job_applications_table_sql = """
    CREATE TABLE IF NOT EXISTS job_applications (
        id INT NOT NULL AUTO_INCREMENT,
        user_id INT,
        job_id INT,
        application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status VARCHAR(50) DEFAULT 'applied',
        PRIMARY KEY (id),
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (job_id) REFERENCES job_postings(id)
    );
    """
    cursor.execute(job_applications_table_sql)

    notifications_table_sql = """
    CREATE TABLE IF NOT EXISTS notifications (
        id INT NOT NULL AUTO_INCREMENT,
        user_id INT,
        message VARCHAR(255),
        is_read BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """
    cursor.execute(notifications_table_sql)

    cursor.execute(f"SHOW COLUMNS FROM {DB_table_name} LIKE 'status'")
    if not cursor.fetchone():
        cursor.execute(
            f"ALTER TABLE {DB_table_name} ADD COLUMN status VARCHAR(50) DEFAULT 'New'")

    cursor.execute(f"SHOW COLUMNS FROM {DB_table_name} LIKE 'resume_score'")
    if not cursor.fetchone():
        cursor.execute(
            f"ALTER TABLE {DB_table_name} ADD COLUMN resume_score VARCHAR(10)")

    cursor.execute(
        f"SHOW COLUMNS FROM {DB_table_name} LIKE 'quantifiable_achievements_suggestions'")
    if not cursor.fetchone():
        cursor.execute(
            f"ALTER TABLE {DB_table_name} ADD COLUMN quantifiable_achievements_suggestions TEXT")

    cursor.execute(
        f"SHOW COLUMNS FROM {DB_table_name} LIKE 'formatting_analysis'")
    if not cursor.fetchone():
        cursor.execute(
            f"ALTER TABLE {DB_table_name} ADD COLUMN formatting_analysis TEXT")


def delete_all_data(connection, cursor):
    """Deletes all data from all tables in the database, respecting foreign key constraints."""
    try:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

        tables_to_truncate = [
            "job_applications",
            "mock_tests",
            "mock_interviews",
            "notifications",
            "user_data",
            "job_postings",
            "users"
        ]

        for table in tables_to_truncate:
            cursor.execute(f"TRUNCATE TABLE {table};")
            logger.info(f"Truncated table: {table}")

        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        connection.commit()
        logger.info("All data deleted successfully from the database.")
        return True
    except pymysql.MySQLError as e:
        logger.error(f"Error deleting all data: {e}")
        st.error(f"Error deleting all data: {e}")
        return False


def reset_database(connection, cursor):
    """Drops all tables and recreates them, effectively resetting the database."""
    try:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

        cursor.execute("SHOW TABLES;")
        tables = [table[0] for table in cursor.fetchall()]

        for table in tables:
            cursor.execute(f"DROP TABLE IF EXISTS {table};")
            logger.info(f"Dropped table: {table}")

        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        connection.commit()
        logger.info("All tables dropped. Recreating database schema...")

        create_tables(cursor)
        logger.info("Database schema recreated successfully.")
        return True
    except pymysql.MySQLError as e:
        logger.error(f"Error resetting database: {e}")
        st.error(f"Error resetting database: {e}")
        return False
