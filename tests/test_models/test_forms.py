import pytest # type: ignore
from flask import Flask
from wtforms import ValidationError
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from models.forms import LoginForm, URLForm

# Create a Flask app for testing
@pytest.fixture(scope="module")
def test_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "testsecret"
    app.config["WTF_CSRF_ENABLED"] = False  # Disable CSRF for tests
    return app


@pytest.mark.parametrize(
    "username,password,expected_valid",
    [
        ("testuser", "secret123", True),  # Both fields meet length requirements
        ("ab", "secret123", False),       # Username too short (< 4 chars)
        ("testuser", "abc", False),       # Password too short (< 6 chars)
        ("", "", False),                  # Both fields empty
    ]
)

# ----------------------------------------------------------------------------
# Test: test_login_form (Unit Test)
# ----------------------------------------------------------------------------
def test_login_form(test_app, username, password, expected_valid):
    """
    Tests the LoginForm with various username and password combinations.
    """
    with test_app.test_request_context():  # Create request context
        form = LoginForm(data={"username": username, "password": password})
        assert form.validate() == expected_valid, (
            f"Expected form validation to be {expected_valid} for username={username}, password={password}"
        )

@pytest.mark.parametrize(
    "youtube_url,expected_valid",
    [
        ("https://www.youtube.com/watch?v=AAAAABBBBB1&t=10s", True),  # Valid URL
        ("https://www.youtube.com/", False),                          # Missing 'watch?v='
        ("http://www.youtube.com/watch?v=AAAAABBBBB1", False),        # Incorrect protocol
        ("https://www.youtube.com/watch?v=123456&t=10s", False),      # Malformed video ID
        ("https://www.youtube.com/watch?v=iJZcjZD0fw0&t=1s", True),   # Default URL
    ]
)

# ----------------------------------------------------------------------------
# Test: test_url_form (Unit Test)
# ----------------------------------------------------------------------------
def test_url_form(test_app, youtube_url, expected_valid):
    """
    Tests the URLForm with various YouTube URLs.
    """
    with test_app.test_request_context():  # Create request context
        form = URLForm(data={"youtube_url": youtube_url})
        assert form.validate() == expected_valid, (
            f"Expected form validation to be {expected_valid} for YouTube URL={youtube_url}"
        )