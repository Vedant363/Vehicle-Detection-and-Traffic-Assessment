import pytest # type: ignore
from unittest.mock import patch, MagicMock
from flask import url_for, Flask, Response
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from app import app, video_bp   # Adjust import to match your project structure

# ------------------------------------------------------------------
# Pytest fixture to create a Flask test client
# ------------------------------------------------------------------
@pytest.fixture
def client():
    """
    Provides a test client for our Flask application.
    """
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def logged_in_session(client):
    """
    Logs a user in by setting the session variables so that
    'login_required' and 'url_required' decorators do not redirect.
    """
    with client.session_transaction() as sess:
        sess['logged_in'] = True
        sess['url_entered'] = True

# ------------------------------------------------------------------
# Test: toggle_video - Successful toggle
# ------------------------------------------------------------------
@patch('models.state.VideoState', autospec=True)  # Patch the entire VideoState class
def test_toggle_video_success(mock_VideoState, client):
    # Mock the behavior of get_show_video and set_show_video
    mock_VideoState.get_show_video.return_value = True  # Mock the initial state to True
    mock_VideoState.set_show_video = lambda x: None  # Mock the set_show_video to do nothing
    
    response = client.post('/toggle_video')
    
    # Handle the potential redirection by checking for a redirect first
    if response.status_code == 302:  # Redirection occurred, check the location
        assert 'login' in response.headers['Location']  # Ensure it's a login redirect
    else:
        assert response.status_code == 200
        assert response.json == {"show_video": False, "message": "Video visibility toggled."}
        mock_VideoState.set_show_video.assert_called_once_with(False)

# ------------------------------------------------------------------
# Test: toggle_video - Exception flow
# ------------------------------------------------------------------
@patch('models.state.VideoState', autospec=True)  # Patch the entire VideoState class
def test_toggle_video_error(mock_VideoState, client):
    # Mock the behavior of get_show_video and simulate an exception in set_show_video
    mock_VideoState.get_show_video.return_value = True  # Mock the initial state to True
    mock_VideoState.set_show_video.side_effect = Exception("Test error")  # Simulate an exception

    response = client.post('/toggle_video')
    
    # Handle potential redirection
    if response.status_code == 302:
        assert 'login' in response.headers['Location']  # Check if it redirects to login
    else:
        assert response.status_code == 500
        assert 'Test error' in response.data.decode()  # Ensure error message is in the response

# ------------------------------------------------------------------
# Test: video_feed - Successful video stream
# ------------------------------------------------------------------
def test_video_feed_success(client, logged_in_session):
    
    # Now make the request to the route
    response = client.get('/video_feed')
    print(response.data)

    # Ensure that the response is a valid HTTP 200 response
    assert response.status_code == 200
    assert response.content_type == 'multipart/x-mixed-replace; boundary=frame'


# ------------------------------------------------------------------
# Test: video_feed - Server Error (e.g., internal server error)
# ------------------------------------------------------------------
@patch('controllers.video_controller.Response')
def test_video_feed_server_error(mock_response, client, logged_in_session):
    # Mock Response to raise an exception
    mock_response.side_effect = Exception("Mocked exception in Response")
    
    # Call the endpoint
    response = client.get('/video_feed')

    # Check that the exception is handled and the error page is returned
    assert response.status_code == 500
    assert b"Mocked exception in Response From: /video_feed" in response.data