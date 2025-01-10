import pytest # type: ignore
import re
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from models.youtube_stream import (
    global_video_id,
    YOUTUBE_URL_REGEX,
    initialize_youtube_stream,
    is_valid_youtube_url,
    get_youtube_stream_url,
    extract_video_id
)

@pytest.mark.parametrize(
    "url,expected",
    [
        ("https://www.youtube.com/watch?v=AAAAABBBBB1&t=10s", True),
        ("https://www.youtube.com/watch?v=AAAAABBBBB1", True),
        ("https://www.youtube.com/watch?v=AAAAAAAAAAA", True),  # 11-char ID
        ("https://www.youtube.com/watch?v=ABC", False),        # too short
        ("http://www.youtube.com/watch?v=AAAAABBBBB1&t=10s", False),  # missing 'https'
        ("https://youtu.be/AAAAABBBBB1", False),  # does not match the exact regex used here
        ("https://www.youtube.com/watch?x=123", False)
    ]
)

# ----------------------------------------------------------------------------
# Test: test_is_valid_youtube_url  (Unit Test)
# ----------------------------------------------------------------------------
def test_is_valid_youtube_url(url, expected):
    """Test validity of YouTube URLs against the regex."""
    assert is_valid_youtube_url(url) == expected, (
        f"Expected {expected} for YouTube URL validation with '{url}'"
    )

@pytest.mark.parametrize(
    "url,expected",
    [
        ("https://www.youtube.com/watch?v=AAAAABBBBB1", "AAAAABBBBB1"),
        ("https://www.youtube.com/watch?v=iJZcjZD0fw0&t=30s", "iJZcjZD0fw0"),
        ("https://youtu.be/ThisPartShouldBeExtracted", "ThisPartShouldBeExtracted"),
        ("https://www.youtube.com/embed/NoVideoID", None)
    ]
)

# ----------------------------------------------------------------------------
# Test: test_extract_video_id  (Unit Test)
# ----------------------------------------------------------------------------
def test_extract_video_id(url, expected):
    """Check video ID extraction from typical YouTube URLs."""
    result = extract_video_id(url)
    assert result == expected, (
        f"Expected extracted video ID '{expected}', got '{result}'"
    )

# ----------------------------------------------------------------------------
# Test: test_initialize_youtube_stream (Integration Test)
# ----------------------------------------------------------------------------
@patch("models.youtube_stream.get_youtube_stream_url", return_value="mock_stream_url")
def test_initialize_youtube_stream(mock_get_stream):
    """initialize_youtube_stream should call get_youtube_stream_url with a constructed YouTube link."""
    result = initialize_youtube_stream("FAKE12345ID")
    mock_get_stream.assert_called_once_with("https://www.youtube.com/watch?v=FAKE12345ID")
    assert result == "mock_stream_url"

# ----------------------------------------------------------------------------
# Test: test_get_youtube_stream_url (Integration Test)
# ----------------------------------------------------------------------------
@patch("models.youtube_stream.yt_dlp.YoutubeDL.extract_info")
def test_get_youtube_stream_url(mock_extract_info):
    """
    get_youtube_stream_url uses yt_dlp to extract info from the YouTube video,
    then returns the direct stream link from 'info['url']'.
    """
    mock_extract_info.return_value = {"url": "http://youtube.stream/link"}
    result = get_youtube_stream_url("https://www.youtube.com/watch?v=FFFFFGGGGG0")
    mock_extract_info.assert_called_once()
    assert result == "http://youtube.stream/link"