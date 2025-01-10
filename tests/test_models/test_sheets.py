import os
import pytest # type: ignore
import time
import datetime
import io
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from models import sheets

@pytest.fixture(autouse=True)
def setup_env(monkeypatch):
    """Fixture to set required environment variables for testing."""
    monkeypatch.setenv('SPREADSHEET_ID', 'dummy_spreadsheet_id')
    # Reset global variables before each test
    sheets.global_sheet = None
    sheets.cache = {'data': None, 'timestamp': 0}
    yield

@pytest.fixture
def mock_gspread_service_account():
    """Mock the gspread.service_account call."""
    with patch('gspread.service_account') as mock_service:
        yield mock_service

@pytest.fixture
def mock_sheets_client(mock_gspread_service_account):
    """Fixture to create a mocked gspread client and sheet."""
    mock_client = MagicMock()
    mock_sheet = MagicMock()
    mock_client.open.return_value.sheet1 = mock_sheet
    mock_gspread_service_account.return_value = mock_client
    return mock_sheet

# ----------------------------------------------------------------------------
# Test: test_get_service_account_file_found_credentials  (Unit Test)
# ----------------------------------------------------------------------------
def test_get_service_account_file_found_credentials(monkeypatch):
    """Test the get_service_account_file function when credentials.json is present."""
    with patch('os.path.exists', side_effect=lambda x: True if x == 'credentials.json' else False):
        sheets.get_service_account_file()
        assert sheets.SERVICE_ACCOUNT_FILE == 'credentials.json', \
            "Should set SERVICE_ACCOUNT_FILE to 'credentials.json' when it exists"

# ----------------------------------------------------------------------------
# Test: test_get_service_account_file_found_gauth_credentials  (Unit Test)
# ----------------------------------------------------------------------------
def test_get_service_account_file_found_gauth_credentials(monkeypatch):
    """Test the get_service_account_file function when gauth-credentials.json is present."""
    def side_effect(path):
        if path == 'credentials.json':
            return False
        if path == 'gauth-credentials.json':
            return True
        return False
    with patch('os.path.exists', side_effect=side_effect):
        with patch('models.state.DecryptionStatus.set_decryption_status') as mock_decrypt_status:
            sheets.get_service_account_file()
            mock_decrypt_status.assert_called_once()
            assert sheets.SERVICE_ACCOUNT_FILE == 'gauth-credentials.json', \
                "Should set SERVICE_ACCOUNT_FILE to 'gauth-credentials.json' when it exists"

# ----------------------------------------------------------------------------
# Test: test_initialize_google_sheets  (Unit Test)
# ----------------------------------------------------------------------------
def test_initialize_google_sheets(mock_sheets_client):
    """Test that initialize_google_sheets returns a sheet object."""
    sheet_instance = sheets.initialize_google_sheets('dummy-sheet')
    assert sheet_instance is mock_sheets_client, "Should return the mock sheet instance"

# ----------------------------------------------------------------------------
# Test: test_fetch_data_from_sheets_first_call  (Integration Test - Involves interactions between global state, caching, and 
# data fetching)
# ----------------------------------------------------------------------------
def test_fetch_data_from_sheets_first_call(mock_sheets_client):
    """Test that fetch_data_from_sheets initializes global_sheet if None and fetches data."""
    mock_sheets_client.get_all_records.return_value = [{'test_key': 'test_value'}]
    data = sheets.fetch_data_from_sheets()
    assert data == [{'test_key': 'test_value'}], "Should return records from the sheet"
    assert sheets.global_sheet is mock_sheets_client, \
        "global_sheet should be set to the mock sheet object after first call"

# ----------------------------------------------------------------------------
# Test: test_write_csv_to_string  (Unit Test)
# ----------------------------------------------------------------------------
def test_write_csv_to_string():
    """Test that write_csv_to_string produces the correct CSV and filename format."""
    sample_data = [{'col1': 'val1', 'col2': 'val2'}, {'col1': 'val3', 'col2': 'val4'}]
    csv_str, filename = sheets.write_csv_to_string(sample_data)
    assert 'col1,col2' in csv_str, "CSV header should be present"
    assert 'val1,val2' in csv_str, "CSV row should be present for first entry"
    assert filename.startswith('data_'), "Filename should start with 'data_'"
    assert filename.endswith('.csv'), "Filename should end with '.csv'"

# ----------------------------------------------------------------------------
# Test: test_clear_google_sheets_data  (Unit Test)
# ----------------------------------------------------------------------------
def test_clear_google_sheets_data(mock_gspread_service_account):
    """Test that clear_google_sheets_data clears the specified worksheet."""
    mock_gc_instance = MagicMock()
    mock_ws = MagicMock()
    mock_gc_instance.open.return_value.worksheet.return_value = mock_ws
    mock_gspread_service_account.return_value = mock_gc_instance

    sheets.clear_google_sheets_data('dummy-sheet', 'dummy-worksheet')
    mock_gc_instance.open.assert_called_once_with('dummy-sheet')
    mock_gc_instance.open.return_value.worksheet.assert_called_once_with('dummy-worksheet')
    mock_ws.clear.assert_called_once(), "Should clear the specified worksheet"

# ----------------------------------------------------------------------------
# Test: test_get_cached_data_first_call  (Unit Test)
# ----------------------------------------------------------------------------
def test_get_cached_data_first_call(mock_sheets_client):
    """Test get_cached_data when there's no cached data and global_sheet is None."""
    mock_sheets_client.get_all_records.return_value = [{'key': 'value'}]
    result = sheets.get_cached_data()
    assert result == [{'key': 'value'}], "Should fetch fresh data if cache is empty"
    assert sheets.cache['data'] == [{'key': 'value'}], "Cache should store the fetched data"

# ----------------------------------------------------------------------------
# Test: test_get_cached_data_with_recent_cache  (Unit Test)
# ----------------------------------------------------------------------------
def test_get_cached_data_with_recent_cache(mock_sheets_client):
    """Test get_cached_data returns cached data if within CACHE_DURATION."""
    # Set up the cache with some data and timestamp
    sheets.cache['data'] = [{'cached': 'data'}]
    sheets.cache['timestamp'] = time.time()
    result = sheets.get_cached_data()
    # Should not fetch new data from the sheet
    mock_sheets_client.get_all_records.assert_not_called()
    assert result == [{'cached': 'data'}], "Should return cached data if cache is still valid"

# ----------------------------------------------------------------------------
# Test: test_datastorage_store_and_get_stored_data  (Unit Test)
# ----------------------------------------------------------------------------
def test_datastorage_store_and_get_stored_data():
    """Test that DataStorage can store and retrieve data."""
    test_data = {"test_key": "test_value"}
    sheets.DataStorage.store_data_temporarily(test_data)
    assert sheets.DataStorage.get_stored_data() == test_data, \
        "Should retrieve the stored data from the class attribute"

# ----------------------------------------------------------------------------
# Test: test_datastorage_clear_stored_data  (Unit Test)
# ----------------------------------------------------------------------------
def test_datastorage_clear_stored_data():
    """Test that DataStorage can clear data."""
    test_data = {"test_key": "test_value"}
    sheets.DataStorage.store_data_temporarily(test_data)
    sheets.DataStorage.clear_stored_data()
    assert sheets.DataStorage.get_stored_data() is None, \
        "Should return None after clearing the stored data"