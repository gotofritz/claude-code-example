# /catchup command

Review branch changes since main and sync with project plan.

**Analysis:**

- Run: `git diff main..HEAD --stat` and `git diff main..HEAD`
- Understand what's been completed and what needs finishing
- Compare actual changes against claude/project-plan.md

**Output:**

```markdown
## Changes Summary

[Key files changed, lines added/removed]

## What's Complete

[Steps/tasks marked done in commits]

## What's In Progress

[Incomplete or partial changes]

## Plan Discrepancies

[What doesn't match the project plan]

## Next Steps

[Recommended actions or plan updates]
```

Offer to update claude/project-plan.md if needed.
