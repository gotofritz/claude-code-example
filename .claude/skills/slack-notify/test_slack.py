#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pytest>=8.0.0",
#     "slack-sdk>=3.27.0",
# ]
# ///
"""
Tests for Slack notification skill.

Run with: uv run .claude/skills/slack-notify/test_slack.py
"""

import os

# Import the module to test
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import main as slack_main


def test_get_webhook_client_success():
    """Test webhook client creation with valid URL."""
    with patch.dict(os.environ, {"SLACK_WEBHOOK_URL": "https://hooks.slack.com/services/TEST"}):
        client = slack_main.get_webhook_client()
        assert client is not None


def test_get_webhook_client_missing_url():
    """Test webhook client fails without URL."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="SLACK_WEBHOOK_URL"):
            slack_main.get_webhook_client()


def test_get_bot_client_success():
    """Test bot client creation with valid token."""
    with patch.dict(os.environ, {"SLACK_BOT_TOKEN": "xoxb-test-token"}):
        client = slack_main.get_bot_client()
        assert client is not None


def test_get_bot_client_missing_token():
    """Test bot client fails without token."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="SLACK_BOT_TOKEN"):
            slack_main.get_bot_client()


def test_send_message_via_webhook():
    """Test sending message using webhook."""
    mock_response = MagicMock()
    mock_response.status_code = 200

    with patch.dict(os.environ, {"SLACK_WEBHOOK_URL": "https://hooks.slack.com/services/TEST"}):
        with patch("main.WebhookClient") as mock_webhook:
            mock_webhook.return_value.send.return_value = mock_response

            slack_main.send_message(channel="#test", message="Test message")

            mock_webhook.return_value.send.assert_called_once_with(text="Test message")


def test_send_message_via_bot_token():
    """Test sending message using bot token."""
    mock_response = {"ok": True}

    with patch.dict(os.environ, {"SLACK_BOT_TOKEN": "xoxb-test-token"}, clear=True):
        with patch("main.WebClient") as mock_client:
            mock_client.return_value.chat_postMessage.return_value = mock_response

            slack_main.send_message(channel="#test", message="Test message")

            mock_client.return_value.chat_postMessage.assert_called_once_with(
                channel="#test", text="Test message", thread_ts=None
            )


def test_send_message_to_thread():
    """Test sending message to thread."""
    mock_response = {"ok": True}

    with patch.dict(os.environ, {"SLACK_BOT_TOKEN": "xoxb-test-token"}):
        with patch("main.WebClient") as mock_client:
            mock_client.return_value.chat_postMessage.return_value = mock_response

            slack_main.send_message(channel="#test", message="Reply", thread_ts="1234567890.123456")

            call_args = mock_client.return_value.chat_postMessage.call_args
            assert call_args[1]["thread_ts"] == "1234567890.123456"


def test_send_message_no_credentials():
    """Test that send_message fails without credentials."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(SystemExit):
            slack_main.send_message(channel="#test", message="Test")


def test_send_message_with_markdown():
    """Test sending message with markdown formatting."""
    mock_response = {"ok": True}

    with patch.dict(os.environ, {"SLACK_BOT_TOKEN": "xoxb-test-token"}):
        with patch("main.WebClient") as mock_client:
            mock_client.return_value.chat_postMessage.return_value = mock_response

            message = "*Bold* and _italic_ and `code`"
            slack_main.send_message(channel="#test", message=message)

            call_args = mock_client.return_value.chat_postMessage.call_args
            assert call_args[1]["text"] == message


def test_upload_file_success():
    """Test successful file upload."""
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        f.write("Test file content")
        test_file = f.name

    try:
        mock_response = {"ok": True}

        with patch.dict(os.environ, {"SLACK_BOT_TOKEN": "xoxb-test-token"}):
            with patch("main.WebClient") as mock_client:
                mock_client.return_value.files_upload_v2.return_value = mock_response

                slack_main.upload_file(channel="#test", file_path=test_file, message="Test upload")

                mock_client.return_value.files_upload_v2.assert_called_once()
                call_args = mock_client.return_value.files_upload_v2.call_args
                assert call_args[1]["channel"] == "#test"
                assert call_args[1]["file"] == test_file
                assert call_args[1]["initial_comment"] == "Test upload"

    finally:
        if Path(test_file).exists():
            Path(test_file).unlink()


def test_upload_file_without_message():
    """Test file upload without optional message."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        f.write("Test")
        test_file = f.name

    try:
        mock_response = {"ok": True}

        with patch.dict(os.environ, {"SLACK_BOT_TOKEN": "xoxb-test-token"}):
            with patch("main.WebClient") as mock_client:
                mock_client.return_value.files_upload_v2.return_value = mock_response

                slack_main.upload_file(channel="#test", file_path=test_file, message=None)

                call_args = mock_client.return_value.files_upload_v2.call_args
                assert call_args[1]["initial_comment"] is None

    finally:
        if Path(test_file).exists():
            Path(test_file).unlink()


def test_upload_file_not_found():
    """Test upload with non-existent file."""
    with patch.dict(os.environ, {"SLACK_BOT_TOKEN": "xoxb-test-token"}):
        with pytest.raises(SystemExit):
            slack_main.upload_file(
                channel="#test", file_path="/nonexistent/file.txt", message="Test"
            )


def test_upload_file_requires_bot_token():
    """Test that file upload requires bot token (webhooks don't support files)."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        f.write("Test")
        test_file = f.name

    try:
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(SystemExit):
                slack_main.upload_file(channel="#test", file_path=test_file, message="Test")

    finally:
        if Path(test_file).exists():
            Path(test_file).unlink()


def test_upload_file_preserves_filename():
    """Test that uploaded file keeps original filename."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv", prefix="report-") as f:
        f.write("col1,col2\nval1,val2")
        test_file = f.name

    try:
        mock_response = {"ok": True}

        with patch.dict(os.environ, {"SLACK_BOT_TOKEN": "xoxb-test-token"}):
            with patch("main.WebClient") as mock_client:
                mock_client.return_value.files_upload_v2.return_value = mock_response

                slack_main.upload_file(channel="#test", file_path=test_file)

                call_args = mock_client.return_value.files_upload_v2.call_args
                # Title should be the filename
                assert Path(test_file).name in str(call_args[1]["title"])

    finally:
        if Path(test_file).exists():
            Path(test_file).unlink()


def test_send_message_handles_api_error():
    """Test that API errors are handled gracefully."""
    from slack_sdk.errors import SlackApiError

    mock_response = {"error": "channel_not_found"}

    with patch.dict(os.environ, {"SLACK_BOT_TOKEN": "xoxb-test-token"}):
        with patch("main.WebClient") as mock_client:
            mock_client.return_value.chat_postMessage.side_effect = SlackApiError(
                "Error", mock_response
            )

            with pytest.raises(SystemExit):
                slack_main.send_message(channel="#nonexistent", message="Test")


def test_upload_file_handles_api_error():
    """Test that file upload API errors are handled gracefully."""
    from slack_sdk.errors import SlackApiError

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        f.write("Test")
        test_file = f.name

    try:
        mock_response = {"error": "file_too_large"}

        with patch.dict(os.environ, {"SLACK_BOT_TOKEN": "xoxb-test-token"}):
            with patch("main.WebClient") as mock_client:
                mock_client.return_value.files_upload_v2.side_effect = SlackApiError(
                    "Error", mock_response
                )

                with pytest.raises(SystemExit):
                    slack_main.upload_file(channel="#test", file_path=test_file)

    finally:
        if Path(test_file).exists():
            Path(test_file).unlink()


if __name__ == "__main__":
    # Run tests with pytest (override project config to avoid conflicts)
    pytest.main([__file__, "-v", "--override-ini=addopts="])
