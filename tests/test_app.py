import os
import pytest # type: ignore
from dotenv import load_dotenv
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

@pytest.fixture
def client():
    """
    Pytest fixture to create a test client from the Flask app.
    """
    with app.test_client() as test_client:
        yield test_client

# ----------------------------------------------------------------------------
# Test: test_app_creation (Unit Test)
# ----------------------------------------------------------------------------
def test_app_creation():
    """
    Test to ensure the Flask application instance is created.
    """
    assert app is not None, "App instance should be created"

# ----------------------------------------------------------------------------
# Test: test_environment_vars (Unit Test)
# ----------------------------------------------------------------------------
def test_environment_vars():
    """
    Test environment variables loaded from .env (SECRET_KEY in this case).
    """
    load_dotenv()
    secret_key = os.getenv("SECRET_KEY")
    assert secret_key is not None, "SECRET_KEY should be set in .env"

# ----------------------------------------------------------------------------
# Test: test_blueprint_registration (Integration Test)
# ----------------------------------------------------------------------------
def test_blueprint_registration():
    """
    Test that the main_blueprint and video_blueprint are registered.
    """
    registered_endpoints = [rule.endpoint for rule in app.url_map.iter_rules()]
    # Example endpoints that might come from main_bp and video_bp:
    # e.g., 'main_controller.index', 'video_controller.list_videos', etc.
    # Adjust these according to the actual endpoints in your controllers.
    expected_endpoints = [
        "main.login",  
        "video.toggle_video"
    ]
    for endpoint in expected_endpoints:
        assert endpoint in registered_endpoints, f"{endpoint} should be registered"

# ----------------------------------------------------------------------------
# Test: test_root_endpoint (Integration Test)
# ----------------------------------------------------------------------------
def test_root_endpoint(client):
    """
    Example test to ensure that hitting the root endpoint returns a response.
    """
    response = client.get('/')
    # Depending on how the root route is configured, the status code may vary.
    # If no root route is defined, this can return 404.
    assert response.status_code in [200, 404], "Root endpoint should return 200 or 404"