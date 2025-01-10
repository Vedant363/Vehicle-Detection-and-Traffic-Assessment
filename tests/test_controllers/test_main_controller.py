import pytest # type: ignore
from flask import session
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from app import app  # Adjust import to match your project structure

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

# ----------------------------------------------------------------------------
# Test: GET / and GET /login
# ----------------------------------------------------------------------------
def test_login_page(client):
    """
    Tests that the login page is accessible and returns either 200 on GET,
    or 500 if decryption fails.
    """
    response = client.get('/login')
    assert response.status_code in [200, 500], (
        "Login should return 200 for success or 500 if credentials are missing."
    )

@patch('controllers.main_controller.check_decryption_status', return_value=True)
def test_login_post(mock_check_decryption, client):
    """
    Tests the login flow with valid credentials.
    """
    data = {
        'username': 'test',
        'password': 'test123'
    }
    response = client.post('/login', data=data, follow_redirects=True)
    # If credentials match, we expect a redirect to passfunc or home
    assert response.status_code in [200, 302], (
        "The login POST should redirect to the passfunc/home route for valid credentials."
    )

# ----------------------------------------------------------------------------
# Test: /e -> passfunc
# ----------------------------------------------------------------------------
@pytest.mark.usefixtures('logged_in_session')
def test_passfunc_redirect(client):
    """
    If the user is logged in and hits /e, they should be redirected to /main/home.
    """
    response = client.get('/e', follow_redirects=True)
    # The passfunc route ultimately redirects to /enterrurl ( = home ).
    # So check if we land on the correct final route or a 200 code.
    assert response.status_code == 200

# ----------------------------------------------------------------------------
# Test: /enterrurl -> home
# ----------------------------------------------------------------------------
@pytest.mark.usefixtures('logged_in_session')
def test_home_view(client):
    """
    Tests the home route to ensure it renders the youtube_url_entry.html template.
    """
    response = client.get('/enterrurl')
    print(response.data)  # Debugging: See the HTML response in the test output for inspection

    # Check if the response status is 200 (OK)
    assert response.status_code == 200
    
    # Check for a <form> element in the HTML, which indicates the form is rendered
    assert b'<form' in response.data, "Expected a form to be in the response"

    # Check for the <h1> element with the text "Enter URL of Traffic Video"
    assert b'Enter URL of Traffic Video' in response.data, "Expected 'Enter URL of Traffic Video' in the response"

    # Check for the input element with the 'youtube_url' ID to ensure the form has the correct field
    assert b'id="youtube_url"' in response.data, "Expected input field with id='youtube_url' in the response"

    # Check for the submit button with its label (form.submit.label)
    assert b'Enter YouTube URL' in response.data, "Expected 'Enter YouTube URL' placeholder in the input field"


# ----------------------------------------------------------------------------
# Test: /submit
# ----------------------------------------------------------------------------
@patch('controllers.main_controller.extract_video_id', return_value='fake_video_id')
@pytest.mark.usefixtures('logged_in_session')
def test_submit_valid_video_id(mock_extract_video_id, client):
    """
    Tests submitting a valid YouTube URL that extracts a valid video ID.
    """
    data = {'youtube_url': 'https://youtube.com/watch?v=fake'}
    response = client.post('/submit', data=data, follow_redirects=True)
    # If valid, it should redirect to /index or somewhere after setting global_video_id
    assert response.status_code in [200, 302]

@patch('controllers.main_controller.extract_video_id', return_value=None)
@pytest.mark.usefixtures('logged_in_session')
def test_submit_invalid_video_id(mock_extract_video_id, client):
    """
    Tests submitting an invalid YouTube URL that does not yield a valid video ID.
    """
    data = {'youtube_url': 'invalid_url'}
    response = client.post('/submit', data=data, follow_redirects=True)
    # Should flash an error and redirect back to /home
    assert response.status_code in [200, 302]

# ----------------------------------------------------------------------------
# Test: /index -> dashboard
# ----------------------------------------------------------------------------
@patch('controllers.main_controller.initialize_google_sheets', return_value='dummy_sheet')
@patch('controllers.main_controller.get_cached_data', return_value=[{'Timestamp': '10:00 AM', 'Class Name': 'Car', 'Width': '0.5', 'Height': '0.75'}])
@pytest.mark.usefixtures('logged_in_session')
def test_dashboard_view(mock_get_cached_data, mock_init_gsheets, client):
    """
    Tests the dashboard route to ensure it renders 'dashboard.html'.
    """
    response = client.get('/index')
    assert response.status_code == 200
    assert b'<canvas' in response.data, "Expected to render canvas element for chart"
    assert b'id="roadOccupancyChart"' in response.data, "Expected to render id field for canvas charts"

# ----------------------------------------------------------------------------
# Test: /traffic_data
# ----------------------------------------------------------------------------
@patch('models.tracking.traffic_analysis_data', {
    'vehicle_count': 5,
    'avg_speed': 45.5,
    'is_traffic_jam': True,
    'too_many_heavy_vehicles': False,
    'estimated_clearance_time': 10.0,
    'traffic_light_decision': ['Green', 60]
})
@pytest.mark.usefixtures('logged_in_session')
def test_traffic_data(client):
    """
    Validates JSON structure for traffic data endpoint.
    """
    response = client.get('/traffic_data')

    # Assert status code
    assert response.status_code == 200, "Response status code should be 200"

    # Parse JSON response
    json_data = response.get_json()

    # Validate the structure and values
    assert 'vehicle_count' in json_data, "'vehicle_count' key is missing in the response"
    assert json_data['vehicle_count'] == 5, "Vehicle count should be 5"
    assert json_data['avg_speed'] == 45.5, "Average speed should be 45.5"
    assert json_data['is_traffic_jam'] is True, "is_traffic_jam should be True"
    assert json_data['too_many_heavy_vehicles'] is False, "too_many_heavy_vehicles should be False"
    assert json_data['estimated_clearance_time'] == 10.0, "Estimated clearance time should be 10.0"
    assert json_data['traffic_light_decision'] == ['Green', 60], "Traffic light decision should be ['Green', 60]"

    
# ----------------------------------------------------------------------------
# Test: /get_chart_data
# ----------------------------------------------------------------------------
@patch('controllers.main_controller.get_cached_data', return_value=[
    {'Timestamp': '10:00:00', 'Class Name': 'Car', 'Width': '2.0', 'Height': '1.5'},
    {'Timestamp': '10:00:05', 'Class Name': 'Truck', 'Width': '3.0', 'Height': '2.0'},
])
@pytest.mark.usefixtures('logged_in_session')
def test_get_chart_data(mock_data, client):
    """
    Checks if chart data is returned correctly in JSON format.
    """
    response = client.get('/get_chart_data')
    assert response.status_code == 200
    json_data = response.get_json()
    assert 'classLabels' in json_data
    assert 'timeData' in json_data
    assert 'roadOccupancy' in json_data

# ----------------------------------------------------------------------------
# Test: /final_page -> stop_execution
# ----------------------------------------------------------------------------
@patch('models.state.StopExecution.set_stop_execution_status')
@patch('models.sheets.initialize_google_sheets')
@patch('models.sheets.get_cached_data', return_value=[{'Timestamp': '2025-01-01 10:00:00', 'X1': 10, 'Y1': 20, 'X2': 50, 'Y2': 60, 'Width': 40, 'Height': 40, 'Class Name': 'Car', 'Confidence': 0.95, 'Track ID': 1}])
@patch('models.sheets.fetch_data_from_sheets', return_value=[
    {'Timestamp': '2025-01-01 10:00:00', 'X1': 10, 'Y1': 20, 'X2': 50, 'Y2': 60, 'Width': 40, 'Height': 40, 'Class Name': 'Car', 'Confidence': 0.95, 'Track ID': 1},
    {'Timestamp': '2025-01-01 10:05:00', 'X1': 15, 'Y1': 25, 'X2': 55, 'Y2': 65, 'Width': 40, 'Height': 40, 'Class Name': 'Bus', 'Confidence': 0.90, 'Track ID': 2},
    {'Timestamp': '2025-01-01 10:10:00', 'X1': 20, 'Y1': 30, 'X2': 60, 'Y2': 70, 'Width': 40, 'Height': 40, 'Class Name': 'Bike', 'Confidence': 0.85, 'Track ID': 3},
    {'Timestamp': '2025-01-01 10:10:00', 'X1': 20, 'Y1': 30, 'X2': 60, 'Y2': 70, 'Width': 40, 'Height': 40, 'Class Name': 'Bike', 'Confidence': 0.85, 'Track ID': 4}
])
@patch('models.sheets.clear_google_sheets_data')
@patch('models.sheets.DataStorage')
@pytest.mark.usefixtures('logged_in_session')
def test_stop_execution_success(mock_data_storage, mock_clear_data, mock_fetch_data, mock_get_data, mock_init_sheets, mock_stop_status, client):
    """
    If data1 has more than 2 rows, route should render dashboard2.html.
    """
    
    # Create a mock object that mimics the behavior of the sheet handler
    mock_sheets_obj = MagicMock()
    mock_sheets_obj.get_all_records.return_value = [
        {'Timestamp': '2025-01-01 10:00:00', 'X1': 10, 'Y1': 20, 'X2': 50, 'Y2': 60, 'Width': 40, 'Height': 40, 'Class Name': 'Car', 'Confidence': 0.95, 'Track ID': 1},
        {'Timestamp': '2025-01-01 10:05:00', 'X1': 15, 'Y1': 25, 'X2': 55, 'Y2': 65, 'Width': 40, 'Height': 40, 'Class Name': 'Bus', 'Confidence': 0.90, 'Track ID': 2}
    ]
    
    # Mock the behavior of the `initialize_google_sheets` to return this mocked object
    mock_init_sheets.return_value = mock_sheets_obj
    
    # Mock the store_data_temporarily method
    mock_storage_instance = MagicMock()
    mock_data_storage.return_value = mock_storage_instance
    mock_storage_instance.store_data_temporarily.return_value = None  # Mocking the store method to do nothing

    # Make the request to the route
    response = client.get('/final_page')

    # Debugging: See the HTML response in the test output for inspection
    print(response.data.decode())  # Printing the raw HTML response

    assert response.status_code == 200
    assert b'class="chart-item1"' in response.data, "Expected to render chart-item1 div"
    assert b'id="vehicleTimeChart"' in response.data, "Expected to render vehicleTimeChart id"
    assert b'<tbody' in response.data, "Expected to render table body component"
    
    # Ensure that store_data_temporarily was called with the data fetched from the sheets
    mock_storage_instance.store_data_temporarily.assert_called_once_with(mock_fetch_data.return_value)


# ----------------------------------------------------------------------------
# Test: /download_csv
# ----------------------------------------------------------------------------
@patch('models.sheets.write_csv_to_string')
@patch('models.sheets.DataStorage')
@patch('models.sheets.clear_google_sheets_data')
@pytest.mark.usefixtures('logged_in_session')
def test_download_csv(mock_clear_google_data, mock_data_storage, mock_write_csv, client):
    """
    Test for the /download_csv route to check if CSV is generated and returned correctly.
    """
    # Mock the DataStorage instance to return some stored data
    mock_storage_instance = MagicMock()
    mock_data_storage.return_value = mock_storage_instance
    mock_storage_instance.get_stored_data.return_value = [
        {'Timestamp': '2025-01-01 10:00:00', 'X1': 10, 'Y1': 20, 'X2': 50, 'Y2': 60, 'Width': 40, 'Height': 40, 'Class Name': 'Car', 'Confidence': 0.95, 'Track ID': 1},
        {'Timestamp': '2025-01-01 10:05:00', 'X1': 15, 'Y1': 25, 'X2': 55, 'Y2': 65, 'Width': 40, 'Height': 40, 'Class Name': 'Bus', 'Confidence': 0.90, 'Track ID': 2}
    ]
    
    # Mock the write_csv_to_string function to return dummy CSV content and filename
    mock_write_csv.return_value = ("Timestamp,X1,Y1,X2,Y2,Width,Height,Class Name,Confidence,Track ID\n"
                                   "2025-01-01 10:00:00,10,20,50,60,40,40,Car,0.95,1\n"
                                   "2025-01-01 10:05:00,15,25,55,65,40,40,Bus,0.90,2\n"), "detections.csv"
    
    # Make the request to the route
    response = client.get('/download_csv')

    # Debugging: See the response content
    print(response.data.decode())  # Printing the raw CSV content in the test output

    # Assert the status code is 200 (OK)
    assert response.status_code == 200

    # Assert the mimetype is correct for CSV
    assert response.content_type.startswith('text/csv')

    # Assert the correct filename is in the Content-Disposition header
    assert 'Content-Disposition' in response.headers
    assert 'attachment;filename=detections.csv' in response.headers['Content-Disposition']

    # Assert that the content matches the mock CSV data
    expected_csv_content = ("Timestamp,X1,Y1,X2,Y2,Width,Height,Class Name,Confidence,Track ID\n"
                            "2025-01-01 10:00:00,10,20,50,60,40,40,Car,0.95,1\n"
                            "2025-01-01 10:05:00,15,25,55,65,40,40,Bus,0.90,2\n")
    assert response.data.decode() == expected_csv_content

    # Ensure that stored data is cleared after generating the CSV
    mock_storage_instance.clear_stored_data.assert_called_once()

    # Ensure that Google Sheets data is cleared
    mock_clear_google_data.assert_called_once_with('vehicle-detection', 'Sheet1')


# ----------------------------------------------------------------------------
# Test: /complete_stop
# ----------------------------------------------------------------------------
@patch('models.sheets.clear_google_sheets_data')
@pytest.mark.usefixtures('logged_in_session')
def test_call_complete_stop(mock_clear_google_data, client):
    """
    Test for the /complete_stop route to ensure session is cleared, necessary functions are called,
    and the response is correct.
    """

    # Make the request to the route
    response = client.get('/complete_stop')

    # Assert the status code is 200 (OK)
    assert response.status_code == 200

    # Assert the correct JSON response
    response_json = response.get_json()
    assert response_json['message'] == "Execution stopped successfully. You can close this page now!!"

    # Ensure that clear_google_sheets_data is called with the correct parameters
    mock_clear_google_data.assert_called_once_with('vehicle-detection', 'Sheet1')

# ----------------------------------------------------------------------------
# Test: /test
# ----------------------------------------------------------------------------
@pytest.mark.usefixtures('logged_in_session')
def test_hi(client):
    """
    Simple endpoint check for /test route, returns JSON response with code 200.
    """
    response = client.get('/test')
    assert response.status_code == 200
    assert b"OK" in response.data

# ----------------------------------------------------------------------------
# Test: /logout
# ----------------------------------------------------------------------------
@pytest.mark.usefixtures('logged_in_session')
def test_logout(client):
    """
    Tests the logout route to ensure session is cleared and user is redirected.
    """
    response = client.post('/logout', follow_redirects=True)
    assert response.status_code in [200, 302]
    assert b"You have been logged out!" in response.data