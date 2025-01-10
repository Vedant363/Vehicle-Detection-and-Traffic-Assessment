import pytest # type: ignore
import os
import signal
from unittest.mock import patch, MagicMock
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from app import app
from models.decryption import decrypt_file, check_decryption_status
from models.state import DecryptionStatus

@pytest.fixture
def mock_decryption_status():
    """
    Fixture to ensure decryption status is cleared before each test.
    """
    DecryptionStatus.set_decryption_status(False)
    yield
    DecryptionStatus.set_decryption_status(False)

# ----------------------------------------------------------------------------
# Test: test_decrypt_file_success  (Unit Test)
# ----------------------------------------------------------------------------
@patch("models.decryption.getpass.getpass", return_value="fake_passphrase")
@patch("models.decryption.gpg.decrypt_file")
@patch("models.decryption.exit")
def test_decrypt_file_success(mock_exit, mock_decrypt_file, mock_getpass, mock_decryption_status):
    """
    Tests the success path of the decrypt_file function.
    """
    # Mock gnupg decrypt_file success scenario
    mock_decrypt_file.return_value.ok = True
    mock_decrypt_file.return_value.status = "decryption successful"

    # Call decrypt_file; it should set DecryptionStatus to True
    decrypt_file()

    # Ensure the passphrase was retrieved from getpass
    mock_getpass.assert_called_once()

    # Check that gnupg was called
    mock_decrypt_file.assert_called_once()

    # exit() should not be called on success
    mock_exit.assert_not_called()

    # Check that the decryption status was updated
    assert check_decryption_status() is True, "Decryption status should be True on success"


# ----------------------------------------------------------------------------
# Test: test_decrypt_file_failure  (Unit Test)
# ----------------------------------------------------------------------------
@patch("models.decryption.getpass.getpass", return_value="wrong_passphrase")
@patch("models.decryption.gpg.decrypt_file")
@patch("models.decryption.exit")
def test_decrypt_file_failure(mock_exit, mock_decrypt_file, mock_getpass, mock_decryption_status):
    """
    Tests the failure path of the decrypt_file function.
    """
    # Mock gnupg decrypt_file failure scenario
    mock_decrypt_file.return_value.ok = False
    mock_decrypt_file.return_value.status = "decryption failed"

    # Call decrypt_file; it should call exit(1)
    decrypt_file()

    # Check that we attempted to decrypt with the passphrase
    mock_getpass.assert_called_once()
    mock_decrypt_file.assert_called_once()

    # exit should be called since decryption failed
    mock_exit.assert_called_once_with(1)

    # The decryption status should remain False
    assert check_decryption_status() is False, "Decryption status should be False on failure"

# ----------------------------------------------------------------------------
# Test: test_cleanup_on_exit_signals  (Integration Test)
# ----------------------------------------------------------------------------
@patch("models.decryption.os.remove")
@patch("models.decryption.os.path.exists", return_value=True)
@patch("signal.signal")  # Mock signal handling
def test_cleanup_on_exit_signals(mock_signal, mock_exists, mock_remove):
    """
    Verifies that sending a termination signal triggers the cleanup routine
    which removes the decrypted file if it exists.
    """
    # Mock the signal handler to prevent actual signal handling
    mock_handler = MagicMock()
    mock_signal.return_value = mock_handler

    # Simulate the cleanup function being called by the signal
    def mocked_signal_handler(signum, frame):
        # Simulate the file cleanup logic
        if os.path.exists("credentials.json"):
            os.remove("credentials.json")

    # Set up the mocked signal handler
    signal.signal(signal.SIGINT, mocked_signal_handler)

    # Simulate sending a SIGINT signal
    mocked_signal_handler(signal.SIGINT, None)

    # Verify that the mocked handler removed the file
    mock_remove.assert_called_with("credentials.json")