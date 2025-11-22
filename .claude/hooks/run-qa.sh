#!/usr/bin/env bash
# Hook to run QA checks after code changes
# Triggered by Edit or Write tool use in Claude Code

set -e

# Change to project directory
cd "$CLAUDE_PROJECT_DIR"

# Activate virtual environment and run QA
source .venv/bin/activate
task qa

exit 0
