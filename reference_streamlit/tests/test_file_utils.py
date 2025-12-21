from file_utils import format_as_bullet_list, get_pdf_text
import sys
import os
from unittest.mock import MagicMock, patch

# Add the parent directory to the path to allow imports from the main project
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

# Mock streamlit before importing file_utils
sys.modules['streamlit'] = MagicMock()


def test_format_as_bullet_list_with_valid_list_string():
    """
    Tests that a string representation of a list is correctly formatted.
    """
    list_string = "['Skill 1', 'Skill 2', 'Skill 3']"
    expected_output = "* Skill 1\n* Skill 2\n* Skill 3"
    assert format_as_bullet_list(list_string) == expected_output


def test_format_as_bullet_list_with_plain_string():
    """
    Tests that a plain string is returned as is.
    """
    plain_string = "Just a regular string"
    assert format_as_bullet_list(plain_string) == plain_string


def test_format_as_bullet_list_with_empty_string():
    """
    Tests that an empty string is handled correctly.
    """
    assert format_as_bullet_list("") == ""


@patch('file_utils.st.cache_data', lambda func: func)
def test_get_pdf_text():
    """
    Tests that the get_pdf_text function correctly extracts text from a PDF file.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(current_dir, "test_data", "test.pdf")
    text, page_count = get_pdf_text(pdf_path)
    assert "This is a test PDF file." in text
    assert page_count == 1
