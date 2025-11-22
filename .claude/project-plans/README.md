# Project Plans Archive

This directory contains historical project plans that were active during different development phases.

## Naming Convention

Files are named: `yyyy-mm-dd-{short-hash}-{description}.md`

- `yyyy-mm-dd`: Date when the plan was archived (usually when PR was created)
- `short-hash`: First 7 characters of the commit hash at time of archival
- `description`: Short kebab-case description (max 30 chars) derived from branch name or PR title

## Example

`2024-11-12-87356bd-demo-customers-removal.md`

## Automation

Project plans are automatically archived when using the `/pr` slash command, which:
1. Copies the current `.claude/project-plan.md` to this directory with the naming convention
2. Proceeds with PR creation

## Current Plan

The active project plan is always at `.claude/project-plan.md`
