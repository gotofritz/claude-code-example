# /pr [no-archive]

1. Run `/archive` to archive project plan (skip if "no-archive" arg provided)
2. Check CLAUDE.md Project Info for issue tracker (Linear or GitHub Issues)
3. Push branch if needed
4. Create PR with `gh pr create`:
   - If Linear: `--body "### Linear Issue 🎟\nRef {branch[:7]}\n### Main Changes 🤹\n{summary}"`
   - If GitHub: `--body "### Related Issue 🎟\nCloses #{issue-number}\n### Main Changes 🤹\n{summary}"`
