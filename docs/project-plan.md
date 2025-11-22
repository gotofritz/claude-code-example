# Anki Skill Implementation

## Overview

Create a Claude Code skill that enables reading cards from and writing new cards to a local Anki installation. The skill will use the official Anki Python module to safely interact with Anki collections without direct database writes.

## Current State

**Project Setup:**

- Python 3.13+ with uv package manager
- Skills use PEP 723 inline dependencies (self-contained)
- Testing framework: pytest with faker, polyfactory, pytest-data

**Anki Integration Research:**

- Official Anki Python module available (anki>=25.9.2)
- High-level API methods: `col.add_note()`, `col.update_note()`, `col.find_notes()`
- Database locations: `~/Library/Application Support/Anki2/User 1/collection.anki2` (macOS)
- Critical requirement: Anki must be closed during write operations
- Safety: Only use high-level API, never direct SQL writes

**Implementation Status (as of 2025-11-22):**

✅ Steps 1-4 complete: Skill structure, documentation, read operations, write operations
⚠️ Step 5 in progress: Basic tests created, integration tests needed
❌ Step 6 not started: Manual testing and validation pending

## Breakdown

### Step 1: Create Skill Directory Structure ✅ COMPLETE

- [x] Create `.claude/skills/anki/` directory
- [x] Create placeholder files: `SKILL.md`, `main.py`, `test_anki.py`

**Status:** All files created in `.claude/skills/anki/`

**Dependencies:** None

**Complexity:** Low

### Step 2: Write SKILL.md Documentation ✅ COMPLETE

- [x] Write frontmatter with skill metadata (name, description, allowed-tools)
- [x] Document prerequisites (Anki closed for writes, optional env vars)
- [x] List available commands: read-cards, list-decks, describe-deck, add-cards
- [x] Add usage examples for each command
- [x] Document safety considerations (no direct DB writes, collection locking)
- [x] Add output format options (JSON, CSV, Markdown, Text)

**Status:** Complete documentation in `.claude/skills/anki/SKILL.md` (115 lines)

**Reasoning:** Clear documentation is critical for users to understand capabilities and safety requirements.

**Dependencies:** Step 1 complete

**Complexity:** Low

### Step 3: Implement Read Operations in main.py ✅ COMPLETE

- [x] Add PEP 723 script metadata with anki dependency (main.py:1-8)
- [x] Implement collection path detection (auto-detect macOS/Linux/Windows paths) (main.py:29-63)
- [x] Implement `get_collection()` helper with lock checking (main.py:66-87)
- [x] Implement `read_cards()` - query cards with Anki search syntax (main.py:132-225)
- [x] Implement output formatters: JSON, CSV, Markdown, Text (main.py:90-124, 181-221)
- [x] Implement `list_decks()` - list all decks with card counts (main.py:228-251)
- [x] Implement `describe_deck()` - show deck structure and stats (main.py:254-295)
- [x] Add Click CLI with read subcommands (main.py:126-129) - Note: Used Click instead of argparse
- [x] Add proper error handling and resource cleanup (try/finally blocks throughout)

**Status:** Fully implemented with 429 lines of code. All read operations functional.

**Reasoning:** Read operations are lower risk and provide immediate value. Implementing these first validates the approach before adding write capabilities.

**Dependencies:** Step 2 complete

**Complexity:** Medium

### Step 4: Implement Write Operations in main.py ✅ COMPLETE

- [x] Implement `add_cards()` using high-level `col.add_note()` API only (main.py:298-424)
- [x] Support input via JSON/CSV files (main.py:330-378)
- [x] Support input via command arguments for quick card creation (main.py:380-390)
- [x] Add collection lock detection before writes (via get_collection helper)
- [x] Add clear warnings that Anki must be closed (SKILL.md:13-15, 63)
- [x] Validate note types and deck existence before writing (main.py:320-323, 395-397)
- [x] Add Click subcommand for add-cards (main.py:298-304)
- [x] Ensure proper resource cleanup in all error paths (main.py:422-424)

**Status:** Fully implemented. Supports both file-based batch operations and single-card CLI arguments.

**Reasoning:** Write operations require more careful implementation due to data integrity concerns. Using only high-level API prevents database corruption.

**Dependencies:** Step 3 complete

**Complexity:** High

### Step 5: Create Tests ⚠️ PARTIALLY COMPLETE

- [x] Create test fixtures with sample card data (test_anki.py:47-80)
- [x] Test collection path detection logic (test_anki.py:10-44)
- [ ] Test read operations with mock collection (placeholder at test_anki.py:100-104)
- [x] Test output formatters (JSON, CSV, Markdown, Text) - Text/Markdown done (test_anki.py:47-80)
- [ ] Test input validation for write operations (placeholder at test_anki.py:93-97)
- [x] Test error handling (locked collection, missing decks) - Partial (test_anki.py:83-90)
- [ ] Add integration test with temporary Anki collection

**Status:** Basic test structure exists (109 lines) with unit tests for formatters and path detection. Integration tests and comprehensive coverage still needed.

**Remaining Work:**

- Mock Collection objects for read/write operation tests
- Complete output formatter tests (JSON, CSV)
- Add integration test with temporary collection
- Test add_cards input validation thoroughly
- Improve test coverage to reasonable level

**Reasoning:** Tests ensure reliability and catch edge cases, especially important for data operations.

**Dependencies:** Steps 3-4 complete

**Complexity:** Medium

### Step 6: Manual Testing and Validation ❌ NOT STARTED

- [ ] Test read operations against real Anki collection
- [ ] Verify output formats are correct and useful
- [ ] Test add-cards with Anki closed (safe scenario)
- [ ] Verify Anki can open collection after writes
- [ ] Test error messages when Anki is running
- [ ] Validate on macOS (primary platform)
- [ ] Document any platform-specific issues

**Status:** No manual testing performed yet. This is critical before considering the feature production-ready.

**Recommended Approach:**

1. Export/backup existing Anki collection first
2. Test all read operations with real data
3. Create test deck for write operations
4. Verify Anki can sync and open collection after writes
5. Test error scenarios (Anki running, missing decks, etc.)
6. Document any issues or limitations discovered

**Reasoning:** Real-world testing ensures the skill works with actual Anki installations and catches issues automated tests might miss.

**Dependencies:** Step 5 complete (ideally)

**Complexity:** Low

## Integration

**Impact on Existing Code:**

- No changes to existing skills or project structure
- New skill is self-contained in `.claude/skills/anki/`
- Dependencies isolated via PEP 723 inline metadata

**Configuration:**

- Optional environment variable: `ANKI_COLLECTION_PATH`
- Skill registered automatically via .claude/skills/ directory structure

**Documentation Updates:**

- Could update README.md to mention new Anki skill (optional)

## Blockers

**Potential Issues:**

1. **Anki Module Compatibility**

   - Risk: Anki module might have breaking changes or compatibility issues
   - Mitigation: Pin specific version (anki>=25.9.2), test thoroughly

2. **Collection Locking**

   - Risk: Cannot detect if Anki is running on all platforms
   - Mitigation: Catch database lock errors, provide clear error messages

3. **Note Type Complexity**

   - Risk: Anki has complex note types (Basic, Cloze, etc.) with different field structures
   - Mitigation: Start with Basic note type, document supported types clearly

4. **Sync Conflicts**

   - Risk: Direct writes might cause AnkiWeb sync issues
   - Mitigation: Warn users in documentation, suggest backup before first use

5. **Platform Differences**
   - Risk: Collection paths differ across OS, especially with Flatpak on Linux
   - Mitigation: Implement path detection for all platforms, allow custom path via argument

**Open Questions:**

- Should we support all Anki note types or start with Basic?
  - Recommendation: Start with Basic, add others based on user feedback
- Should we implement batch operations for adding multiple cards?
  - Recommendation: Yes, accept CSV/JSON files with multiple cards
- Should we add card editing/deletion capabilities?
  - Recommendation: Not in initial version, focus on read + create first
