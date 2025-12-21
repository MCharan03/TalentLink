import streamlit as st
import bcrypt
from logger_config import logger
from email_utils import send_email
from database import create_notification
import pymysql


def register_user(connection, cursor, username, email, password):
    logger.info(f"Attempting to register user: {username}")
    """Registers a new user."""
    try:
        # Check if username or email already exists
        cursor.execute(
            "SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
        if cursor.fetchone():
            logger.warning(
                f"Failed registration attempt for existing username or email: {username}/{email}")
            st.error("Username or email already exists")
            return False

        # Hash the password
        hashed_password = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt())

        # Insert new user
        insert_sql = "INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_sql, (username, email, hashed_password, 'user'))
        connection.commit()
        logger.info(f"New user registered: {username}")

        # Get user_id of the new user
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        user_id = cursor.fetchone()[0]

        # Send welcome email
        send_email(email, "Welcome to the Smart Resume Screener & Analyzer!",
                   "Thank you for registering! We are excited to have you on board.")

        # Create in-app notification
        create_notification(connection, cursor, user_id,
                            "Welcome to the Smart Resume Screener & Analyzer!")

        st.success("Registration successful! Please login.")
        return True
    except pymysql.MySQLError as e:
        logger.error(
            f"Database error during user registration for {username}: {e}")
        st.error(
            f"A database error occurred during registration. Please try again. Error: {e}")
        return False
    except Exception as e:
        logger.error(
            f"An unexpected error occurred during user registration for {username}: {e}")
        st.error(
            f"An unexpected error occurred during registration. Please try again. Error: {e}")
        return False


def login_user(cursor, username, password):
    logger.info(f"Attempting to log in user: {username}")
    """Logs in a user."""
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    if user:
        logger.info(f"User {username} found in DB. Verifying password.")
        if bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
            logger.info(f"User logged in successfully: {username}")
            return user[0]  # Return user ID
        else:
            logger.warning(
                f"Failed login attempt for username: {username} - Incorrect password.")
    else:
        logger.warning(
            f"Failed login attempt for username: {username} - User not found.")
    return None


def display_login_form():
    st.subheader("Login")
    with st.form("login_form"):
        username = st.text_input("Username", autocomplete="username")
        password = st.text_input(
            "Password", type="password", autocomplete="current-password")
        submitted = st.form_submit_button("Login")
        if submitted:
            logger.info(
                f"Login form submitted. Username: {username}, Password provided: {'*' * len(password) if password else 'None'}")
            return username, password
    return None, None


def display_registration_form():
    st.subheader("Create an Account")
    with st.form("registration_form"):
        new_username = st.text_input(
            "New Username", autocomplete="new-username")
        email = st.text_input("Email", autocomplete="email")
        new_password = st.text_input(
            "New Password", type="password", autocomplete="new-password")
        confirm_password = st.text_input(
            "Confirm Password", type="password", autocomplete="new-password")
        submitted = st.form_submit_button("Register")
        if submitted:
            if not new_username or not new_password or not email:
                st.error("Username, email, and password cannot be empty")
            elif new_password != confirm_password:
                st.error("Passwords do not match")
            else:
                return new_username, email, new_password
    return None, None, None
