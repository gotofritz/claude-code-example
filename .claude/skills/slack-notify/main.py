#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "slack-sdk>=3.27.0",
# ]
# ///
"""
Slack notification skill for Claude Code.

Provides message sending and file upload capabilities for Slack.
"""

import argparse
import os
import sys
from pathlib import Path

try:
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError
    from slack_sdk.webhook import WebhookClient
except ImportError:
    sys.exit(1)


def get_webhook_client():
    """
    Create Slack webhook client from environment variable.

    Returns:
        WebhookClient instance

    Raises:
        ValueError: If SLACK_WEBHOOK_URL not set
    """
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook_url:
        raise ValueError("SLACK_WEBHOOK_URL environment variable not set")
    return WebhookClient(webhook_url)


def get_bot_client():
    """
    Create Slack bot client from environment variable.

    Returns:
        WebClient instance

    Raises:
        ValueError: If SLACK_BOT_TOKEN not set
    """
    bot_token = os.getenv("SLACK_BOT_TOKEN")
    if not bot_token:
        raise ValueError("SLACK_BOT_TOKEN environment variable not set")
    return WebClient(token=bot_token)


def send_message(*, channel: str, message: str, thread_ts: str | None = None) -> None:
    """
    Send a message to Slack channel.

    Args:
        channel: Channel name (e.g., "#alerts") or ID
        message: Message text (supports Slack markdown)
        thread_ts: Optional thread timestamp for replies

    Raises:
        SlackApiError: If message sending fails
    """
    try:
        # Try webhook first (simpler, no channel resolution needed)
        webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        if webhook_url:
            client = WebhookClient(webhook_url)
            response = client.send(text=message)
            if response.status_code == 200:
                return
            else:
                pass
                # Fall through to bot token if available

        # Fall back to bot token
        bot_token = os.getenv("SLACK_BOT_TOKEN")
        if not bot_token:
            raise ValueError(
                "Neither SLACK_WEBHOOK_URL nor SLACK_BOT_TOKEN is set. "
                "Set one of these environment variables."
            )

        client = WebClient(token=bot_token)
        response = client.chat_postMessage(channel=channel, text=message, thread_ts=thread_ts)

        if response["ok"]:
            if thread_ts:
                pass
        else:
            sys.exit(1)

    except SlackApiError:
        sys.exit(1)
    except Exception:
        sys.exit(1)


def upload_file(*, channel: str, file_path: str, message: str | None = None) -> None:
    """
    Upload a file to Slack channel.

    Args:
        channel: Channel name (e.g., "#alerts") or ID
        file_path: Path to file to upload
        message: Optional message to include with file

    Raises:
        SlackApiError: If file upload fails
        FileNotFoundError: If file doesn't exist
    """
    file_path_obj = Path(file_path)
    if not file_path_obj.exists():
        sys.exit(1)

    try:
        # File uploads require bot token
        bot_token = os.getenv("SLACK_BOT_TOKEN")
        if not bot_token:
            sys.exit(1)

        client = WebClient(token=bot_token)

        # Upload file
        response = client.files_upload_v2(
            channel=channel,
            file=file_path,
            title=file_path_obj.name,
            initial_comment=message if message else None,
        )

        if response["ok"]:
            pass
        else:
            sys.exit(1)

    except SlackApiError:
        sys.exit(1)
    except Exception:
        sys.exit(1)


def main():
    """Main entry point for the skill."""
    parser = argparse.ArgumentParser(description="Slack notification skill for Claude Code")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Send message command
    send_parser = subparsers.add_parser("send", help="Send message to Slack channel")
    send_parser.add_argument("--channel", required=True, help="Channel name or ID")
    send_parser.add_argument("--message", required=True, help="Message text")
    send_parser.add_argument("--thread-ts", help="Thread timestamp for replies")

    # Upload file command
    upload_parser = subparsers.add_parser("upload", help="Upload file to Slack channel")
    upload_parser.add_argument("--channel", required=True, help="Channel name or ID")
    upload_parser.add_argument("--file", required=True, help="Path to file to upload")
    upload_parser.add_argument("--message", help="Optional message with file")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute command
    if args.command == "send":
        send_message(channel=args.channel, message=args.message, thread_ts=args.thread_ts)
    elif args.command == "upload":
        upload_file(channel=args.channel, file_path=args.file, message=args.message)


if __name__ == "__main__":
    main()
