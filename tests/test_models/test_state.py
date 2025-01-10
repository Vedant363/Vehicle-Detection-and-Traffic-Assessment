import pytest # type: ignore
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from models.state import VideoState, DecryptionStatus, StopExecution

# ----------------------------------------------------------------------------
# Test: test_video_state  (Unit Test)
# ----------------------------------------------------------------------------
def test_video_state():
    # Verify the default state
    assert VideoState.get_show_video() is True

    # Change the state and verify
    VideoState.set_show_video(False)
    assert VideoState.get_show_video() is False

    # Reset to original state and verify
    VideoState.set_show_video(True)
    assert VideoState.get_show_video() is True

# ----------------------------------------------------------------------------
# Test: test_decryption_status  (Unit Test)
# ----------------------------------------------------------------------------
def test_decryption_status():
    # Verify the default state
    assert DecryptionStatus.get_decryption_status() is False

    # Change the state and verify
    DecryptionStatus.set_decryption_status(True)
    assert DecryptionStatus.get_decryption_status() is True

    # Reset to original state and verify
    DecryptionStatus.set_decryption_status(False)
    assert DecryptionStatus.get_decryption_status() is False

# ----------------------------------------------------------------------------
# Test: test_stop_execution  (Unit Test)
# ----------------------------------------------------------------------------
def test_stop_execution():
    # Verify the default state
    assert StopExecution.get_stop_execution_status() is False

    # Change the state and verify
    StopExecution.set_stop_execution_status(True)
    assert StopExecution.get_stop_execution_status() is True

    # Reset to original state and verify
    StopExecution.set_stop_execution_status(False)
    assert StopExecution.get_stop_execution_status() is False