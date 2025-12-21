from database import setup_database, insert_data
import pymysql
import sys
import os
import pytest
from unittest.mock import MagicMock, patch

# Add the parent directory to the path to allow imports from the main project
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

# Mock streamlit before importing database
sys.modules['streamlit'] = MagicMock()


@pytest.fixture
def mock_db_connection():
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value = cursor
    return conn, cursor


@patch('database.st')
@patch('database.pymysql.connect')
def test_setup_database_success(mock_connect, mock_st):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn
    conn, cursor = setup_database()
    assert conn is not None
    assert cursor is not None
    mock_connect.assert_called_once()


@patch('database.st')
@patch('database.pymysql.connect')
def test_setup_database_failure(mock_connect, mock_st):
    mock_connect.side_effect = pymysql.err.OperationalError(
        "Connection failed")
    conn, cursor = setup_database()
    assert conn is None
    assert cursor is None
    mock_connect.assert_called_once()
    mock_st.error.assert_called_once()


@patch('database.st')
def test_insert_data_success(mock_st, mock_db_connection):
    conn, cursor = mock_db_connection
    insert_data(conn, cursor, 1, "Test User", "test@example.com", "Good resume", "80", "2025-10-31", "1",
                "Data Scientist", "Intermediate", "[\'python\', \'sql\']", "[\'machine learning\']", "[\'Coursera\']", "[]", "")
    cursor.execute.assert_called_once()
    conn.commit.assert_called_once()


@patch('database.st')
def test_insert_data_failure(mock_st, mock_db_connection):
    conn, cursor = mock_db_connection
    cursor.execute.side_effect = pymysql.MySQLError("Insertion failed")
    insert_data(conn, cursor, 1, "Test User", "test@example.com", "Good resume", "80", "2025-10-31", "1",
                "Data Scientist", "Intermediate", "[\'python\', \'sql\']", "[\'machine learning\']", "[\'Coursera\']", "[]", "")
    cursor.execute.assert_called_once()
    conn.commit.assert_not_called()
    mock_st.error.assert_called_once()
