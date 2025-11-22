---
name: slack-notify
description: Send messages and file attachments to Slack channels. Use when needing to send notifications, alerts, or share data via Slack. Supports both simple text messages and rich formatted messages.
allowed-tools: Bash, Read, Write
---

# Slack Notification Skill

Send messages, formatted notifications, and file attachments to Slack channels.

## Prerequisites

Required environment variables (choose one):

**Option 1: Webhook URL** (simpler, recommended for basic notifications)
- `SLACK_WEBHOOK_URL` - Incoming webhook URL from Slack

**Option 2: Bot Token** (full API access, required for file uploads)
- `SLACK_BOT_TOKEN` - Bot user OAuth token (starts with `xoxb-`)

## Available Commands

### Send Simple Message

Send a plain text message:

```bash
uv run .claude/skills/slack-notify/main.py send \
  --channel "#alerts" \
  --message "System check completed successfully"
```

### Send Formatted Message

Send a message with markdown formatting:

```bash
uv run .claude/skills/slack-notify/main.py send \
  --channel "#alerts" \
  --message "*Alert:* Database has 150 rows matching criteria"
```

### Upload File

Upload a file with optional message:

```bash
uv run .claude/skills/slack-notify/main.py upload \
  --channel "#alerts" \
  --file /tmp/data.csv \
  --message "Daily report attached"
```

## Usage Notes

- Script uses uv inline script metadata (PEP 723) - dependencies auto-installed on first run
- Webhook URLs are channel-specific and simpler to set up
- Bot tokens provide full API access including file uploads
- Messages support Slack markdown (bold, italic, links, code blocks)
- Rate limiting is handled with exponential backoff
- File uploads require bot token (webhooks don't support files)

## Security Considerations

- Never commit tokens or webhook URLs to version control
- Use environment variables or secrets management
- Webhook URLs grant posting access to specific channel
- Bot tokens should have minimal required scopes
- Rotate tokens periodically
