# /plan command

Analyze codebase and create a project plan for: {TASK}

**Analysis:**

- Map current code structure relevant to this task
- Identify what exists vs. what needs building
- Flag architectural constraints or dependencies

**Output to claude/project-plan.md:**

```markdown
## Overview

What are we doing and why?

## Current State

What exists today that's relevant?

## Breakdown

### Step 1: [Title]

- [ ] Subtask
- [ ] Subtask

Reasoning: Why this step? What does it unblock?
Dependencies: Prior steps needed
Complexity: Low/Medium/High

### Step 2: [Title]

...

## Integration

How do these changes affect the rest of the codebase?

## Blockers

What uncertainties or risks?
```
