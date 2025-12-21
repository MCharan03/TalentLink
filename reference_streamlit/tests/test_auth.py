from auth import register_user, login_user
import sys
import os
import pytest
from unittest.mock import MagicMock, patch
import bcrypt

# Add the parent directory to the path to allow imports from the main project
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def mock_db_connection():
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value = cursor
    return conn, cursor


@patch('auth.create_notification')
@patch('auth.send_email')
@patch('auth.st.error')
@patch('auth.st.success')
@patch('bcrypt.hashpw')
def test_register_user_success(mock_hashpw, mock_st_success, mock_st_error, mock_send_email, mock_create_notification, mock_db_connection):
    connection, cursor = mock_db_connection
    # First call: user doesn't exist, Second call: return user_id
    cursor.fetchone.side_effect = [None, (1,)]
    mock_hashpw.return_value = b'$2b$12$fMON0l2hK9PdGfhYFE.tCONxUI2PczyO9zDY/ozRsAS4WDBZnLj/m'

    result = register_user(connection, cursor, "newuser", "password123")

    assert result is True
    cursor.execute.assert_any_call(
        "SELECT * FROM users WHERE username = %s", ("newuser",))
    cursor.execute.assert_any_call("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", (
        "newuser", b'$2b$12$fMON0l2hK9PdGfhYFE.tCONxUI2PczyO9zDY/ozRsAS4WDBZnLj/m', 'user'))
    cursor.execute.assert_any_call(
        "SELECT id FROM users WHERE username = %s", ("newuser",))
    connection.commit.assert_called_once()
    mock_st_success.assert_called_once_with(
        "Registration successful! Please login.")
    mock_send_email.assert_called_once()
    mock_create_notification.assert_called_once()


@patch('auth.st.error')
def test_register_user_duplicate_username(mock_st_error, mock_db_connection):
    connection, cursor = mock_db_connection
    cursor.fetchone.return_value = (
        "1", "existinguser", "hashedpass", "user")  # Username exists

    result = register_user(connection, cursor, "existinguser", "password123")

    assert result is False
    cursor.execute.assert_called_once_with(
        "SELECT * FROM users WHERE username = %s", ("existinguser",))
    connection.commit.assert_not_called()
    mock_st_error.assert_called_once_with("Username already exists")


@patch('auth.st.error')
def test_login_user_success(mock_st_error, mock_db_connection):
    connection, cursor = mock_db_connection
    hashed_password = bcrypt.hashpw(
        "password123".encode('utf-8'), bcrypt.gensalt())
    cursor.fetchone.return_value = (
        1, "testuser", hashed_password.decode('utf-8'), "user")

    user_id = login_user(cursor, "testuser", "password123")

    assert user_id == 1
    cursor.execute.assert_called_once_with(
        "SELECT * FROM users WHERE username = %s", ("testuser",))


@patch('auth.st.error')
def test_login_user_invalid_password(mock_st_error, mock_db_connection):
    connection, cursor = mock_db_connection
    hashed_password = bcrypt.hashpw(
        "correctpassword".encode('utf-8'), bcrypt.gensalt())
    cursor.fetchone.return_value = (
        1, "testuser", hashed_password.decode('utf-8'), "user")

    user_id = login_user(cursor, "testuser", "wrongpassword")

    assert user_id is None
    cursor.execute.assert_called_once_with(
        "SELECT * FROM users WHERE username = %s", ("testuser",))


@patch('auth.st.error')
def test_login_user_non_existent_user(mock_st_error, mock_db_connection):
    connection, cursor = mock_db_connection
    cursor.fetchone.return_value = None

    user_id = login_user(cursor, "nonexistent", "password123")

    assert user_id is None
    cursor.execute.assert_called_once_with(
        "SELECT * FROM users WHERE username = %s", ("nonexistent",))
