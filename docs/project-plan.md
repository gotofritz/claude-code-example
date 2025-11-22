# Multi-Note-Type Support for Anki Skill

## Overview

Extend the Anki skill to support multiple note types beyond "Basic", specifically:
1. **Cloze** note type (Text/Extra fields) for creating fill-in-the-blank cards
2. **FSI German Drills** custom note type (Prompt1/Prompt2/Answer fields) used by the DEU FSI German Basic Course Drills deck

Currently, the skill hardcodes the "Basic" note type (Front/Back fields), limiting its usefulness for language learning workflows that benefit from Cloze deletions and drill-style cards.

## Current State

**Existing Anki Skill (Production-Ready):**
- **Location**: `.claude/skills/anki/`
- **Commands**: list-decks, describe-deck, read-cards, add-cards
- **429 lines** of production code in main.py
- **472 lines** of test code (8/19 passing)
- **Validated** against real collection (34MB, 16,268 cards)

**Current Limitations:**
- Note type "Basic" hardcoded at `main.py:395`
- Field names "Front"/"Back" hardcoded at `main.py:406-407`
- Input format (JSON/CSV) expects only "front"/"back" keys
- Formatters assume Front/Back structure for display

**Known Note Types in Collection:**
From investigation of DEU FSI German Basic Course Drills deck:
- **Custom Note Type**: Has 3 fields - `Prompt1`, `Prompt2`, `Answer`
- **Structure**: Drill-style with template sentence, article hint, and complete answer
- **Example**:
  - Prompt1: `<u>_____</u> <u>ist</u> dort.` (template)
  - Prompt2: `D- Flughafen` (article hint)
  - Answer: `<u>Der Flughafen</u> <u>ist</u> dort.` (complete answer)

## Breakdown

### Step 1: Add Discovery Commands ✅ High Priority

- [x] Implement `list-note-types` command
  - List all note types in collection with field names
  - Show type (Standard vs Cloze)
  - Sort alphabetically for readability
- [x] Implement `describe-deck-note-types` command
  - Show which note types are used in a specific deck
  - Include field structure for each
  - Show sample card data
- [x] Add tests for discovery commands
- [x] Update SKILL.md with new command documentation

**Status**: ✅ Complete

**Reasoning**: Need to discover what note types exist before implementing multi-type support. This allows users to see available note types and validate assumptions about FSI deck structure.

**Dependencies**: None - can use existing `get_collection()` helper

**Complexity**: Low-Medium (~2-3 hours)
- Simple Anki API usage (`col.models.all()`, `col.models.get()`)
- Straightforward output formatting
- Minimal error handling needed

**Acceptance Criteria:**
- Can list all note types with their fields
- Can show note types used in FSI deck
- Output clearly shows field structure
- Commands follow existing CLI pattern

---

### Step 2: Add Note Type Parameter to add-cards 🔥 Critical

- [x] Add `--note-type` CLI parameter (default: "Basic")
- [x] Replace hardcoded `col.models.by_name("Basic")` with dynamic lookup
- [x] Add validation: error if note type doesn't exist
- [x] List available note types in error message
- [x] Update help text and examples
- [x] Maintain backward compatibility (Basic as default)

**Status**: ✅ Complete

**Reasoning**: This is the core change needed. Without dynamic note type selection, cannot create Cloze or FSI-style cards. Keeping "Basic" as default ensures existing workflows don't break.

**Dependencies**: None (can proceed without Step 1, but Step 1 helps users discover options)

**Complexity**: Low (~30-45 minutes)
- One parameter addition
- Simple string substitution
- Clear validation logic
- Minimal risk

**Code Location**: `main.py:298-304` (add parameter), `main.py:394-397` (implement)

---

### Step 3: Implement Dynamic Field Mapping 🔥 Critical

- [x] Remove hardcoded `note["Front"]` and `note["Back"]` assignments
- [x] Implement flexible field mapping based on note type structure
- [x] Support multiple input formats:
  - Explicit fields object: `{"fields": {"Text": "...", "Extra": "..."}}`
  - Legacy front/back: `{"front": "...", "back": "..."}` (maps to Front/Back)
  - Flexible keys: `{"text": "..."}` (case-insensitive match to note type fields)
- [x] Add validation: error if required fields missing
- [x] List expected fields in error message
- [x] Add helper function `map_input_to_note_fields()`

**Status**: ✅ Complete

**Reasoning**: Dynamic field mapping is essential for supporting multiple note types. Different note types have different field structures (Front/Back vs Text/Extra vs Prompt1/Prompt2/Answer). Must handle gracefully while maintaining backward compatibility.

**Dependencies**: Step 2 complete (need note type selected)

**Complexity**: Medium-High (~2-3 hours)
- Complex logic for field matching
- Multiple input format support
- Backward compatibility critical
- Need comprehensive error messages

**Code Location**: `main.py:405-407` (replace), new helper function (~30-40 lines)

---

### Step 4: Update Input Parsing (JSON/CSV) 🔶 Important

- [ ] Modify JSON parser to accept `fields` object
- [ ] Maintain backward compatibility with `front`/`back` keys
- [ ] Update CSV parser for flexible columns
  - Auto-detect columns from header row
  - Map column names to note type fields (case-insensitive)
- [ ] Add validation for CSV format with non-standard fields
- [ ] Update example files in documentation

**Status**: Not started

**Reasoning**: Users need to provide data for arbitrary fields. JSON can use nested `fields` object, CSV needs flexible column mapping. Both must work intuitively for different note types.

**Dependencies**: Step 3 complete (need field mapping logic)

**Complexity**: Medium (~1-2 hours)
- JSON changes are simple (add `fields` key support)
- CSV is more complex (dynamic column detection)
- Need clear examples for each note type

**Code Location**: `main.py:330-378` (JSON/CSV parsing)

---

### Step 5: Update Read Operation Formatters 🔶 Important

- [x] Make `format_card_text()` flexible
  - Try Front/Back first (Basic)
  - Fall back to Text (Cloze)
  - Fall back to first N fields (custom types)
- [x] Make `format_card_markdown()` flexible
- [x] Update CSV export formatter for arbitrary fields
- [x] Ensure JSON export already works (it should - it outputs all fields)
- [x] Test with all three note types (Basic, Cloze, FSI)

**Status**: ✅ Complete

**Reasoning**: Read operations currently assume Front/Back fields. When displaying Cloze or FSI cards, they show "N/A → N/A" in text format. Making formatters flexible improves UX.

**Dependencies**: None (can work independently), but Step 1 helps validate changes

**Complexity**: Low-Medium (~1 hour)
- Simple conditional logic
- Mostly cosmetic improvements
- Low risk (doesn't affect data integrity)

**Code Location**: `main.py:101-102, 119-120, 193-194`

---

### Step 6: Add Cloze-Specific Features 🔷 Nice to Have

- [ ] Add basic Cloze deletion syntax validation
  - Warn if Text field missing `{{c1::...}}` syntax
  - Suggest correct format in error message
- [ ] Add `--cloze-text` and `--cloze-extra` shortcuts for CLI
  - Convenience parameters for single Cloze card creation
  - Maps to Text/Extra fields automatically
- [ ] Add Cloze examples to documentation
  - JSON format with cloze syntax
  - Multiple cloze deletions example
  - Hints in cloze deletions

**Status**: Not started

**Reasoning**: Cloze cards have special syntax requirements. Basic validation and convenience features improve user experience and reduce errors. However, Anki itself validates cloze syntax, so this is nice-to-have rather than critical.

**Dependencies**: Steps 2-3 complete (need note type support)

**Complexity**: Low (~30-45 minutes)
- Simple regex validation
- Additional CLI parameters
- Documentation examples

**Code Location**: New validation function, `main.py:298-313` (add parameters)

---

### Step 7: Comprehensive Testing 🔥 Critical

- [ ] Add tests for Cloze card creation
- [ ] Add tests for FSI German-style card creation (3-field custom type)
- [ ] Add tests for discovery commands
- [ ] Add tests for field mapping logic
- [ ] Add tests for flexible formatters
- [ ] Add tests for error cases (missing fields, invalid note type)
- [ ] Update existing tests to use parameterized note types
- [ ] Test backward compatibility (Basic note type still works)

**Status**: Not started

**Reasoning**: Multi-note-type support adds significant complexity. Comprehensive tests ensure reliability and prevent regressions. Current test coverage is 8/19 passing; need to improve and extend.

**Dependencies**: Steps 2-5 complete (need implemented features to test)

**Complexity**: Medium (~2-3 hours)
- ~200-300 new test lines estimated
- Need mock note type structures
- Field mapping tests most critical
- Existing test infrastructure helps

**Code Location**: `.claude/skills/anki/test_anki.py`

---

### Step 8: Documentation Updates 📝 Important

- [x] Add Cloze note type examples to SKILL.md
  - JSON format with cloze syntax
  - CSV format for batch Cloze import
  - CLI example for single Cloze card
- [x] Add FSI German Drills examples
  - 3-field structure (Prompt1/Prompt2/Answer)
  - Batch import format
- [x] Document `--note-type` parameter
- [x] Document discovery commands (list-note-types, describe-deck-note-types)
- [x] Add "Supported Note Types" section
  - Basic, Cloze, Custom (any arbitrary fields)
- [x] Add troubleshooting section for field mapping issues
- [x] Update README.md if needed

**Status**: ✅ Complete

**Reasoning**: Clear documentation is critical for usability. Users need examples for each note type to understand input format requirements. Troubleshooting section helps resolve common issues.

**Dependencies**: Steps 1-6 complete (document implemented features)

**Complexity**: Low (~30-45 minutes)
- Mostly writing examples
- Can reuse manual testing examples
- Important for user adoption

**Code Location**: `.claude/skills/anki/SKILL.md`, possibly `README.md`

---

## Integration

**Impact on Existing Code:**
- **main.py**: ~150-200 new lines, ~50-80 modified lines
- **SKILL.md**: ~100-150 new documentation lines
- **test_anki.py**: ~200-300 new test lines
- **No breaking changes**: Basic note type remains default, existing workflows unaffected

**Affected Functions:**
- `add_cards()`: Add parameter, remove hardcoding
- `format_card_text()`, `format_card_markdown()`: Make flexible
- New: `list_note_types()`, `describe_deck_note_types()`, `map_input_to_note_fields()`

**Backward Compatibility:**
- `--note-type` defaults to "Basic"
- Legacy `front`/`back` keys still work
- Existing JSON/CSV files continue to work
- No changes to read operations API

**Data Safety:**
- Read operations unaffected (no data modification)
- Write operations use same high-level Anki API
- Field mapping errors caught before writes
- No direct SQL (maintains safety guarantee)

---

## Blockers

**Open Questions:**

1. **What exactly is the FSI deck's note type name?**
   - **Status**: Partially resolved - cards use 3 fields (Prompt1, Prompt2, Answer)
   - **Need**: Run Step 1 (list-note-types) to get exact note type name
   - **Impact**: Medium - need name for documentation and examples

2. **Does the FSI note type have any custom JavaScript/CSS?**
   - **Risk**: May affect card display or behavior
   - **Mitigation**: Inspect note type templates after Step 1
   - **Impact**: Low - write operations don't touch templates

3. **Should we support card type specification (for note types with multiple templates)?**
   - **Example**: Basic has 1 template, but custom types can have multiple
   - **Current**: Uses default template (first one)
   - **Decision**: Defer to future - default template sufficient for MVP

4. **How to handle required vs optional fields?**
   - **Current Anki behavior**: All fields are technically optional
   - **Decision**: Allow empty fields, warn but don't block
   - **Rationale**: Anki itself permits empty fields

**Potential Issues:**

1. **Field Name Conflicts**
   - **Risk**: User provides "front" but note type expects "Front" (capitalization)
   - **Mitigation**: Case-insensitive matching in field mapper
   - **Severity**: Medium - confusing errors if not handled

2. **Cloze Syntax Errors**
   - **Risk**: Invalid cloze syntax (`{{c1::text}}`) causes card generation failure
   - **Mitigation**: Basic validation (Step 6), clear error messages
   - **Severity**: Low-Medium - Anki validates, but earlier validation improves UX

3. **Breaking Existing Tests**
   - **Risk**: Changes to add_cards() might break 8 currently passing tests
   - **Mitigation**: Maintain backward compatibility, update tests carefully
   - **Severity**: Medium - important not to regress working functionality

4. **CSV Column Ordering Ambiguity**
   - **Risk**: Multiple fields, user unclear on which column maps to which field
   - **Mitigation**: Use header row for explicit field names
   - **Severity**: Low - clear documentation resolves

**Risk Assessment:**

| Risk | Probability | Impact | Mitigation |
|------|-------------|---------|------------|
| Existing workflows break | Low | High | Default to "Basic", comprehensive tests |
| Field mapping bugs | Medium | Medium | Thorough testing, clear errors |
| Performance degradation | Low | Low | Minimal - same API usage |
| User confusion | Medium | Low | Good documentation, examples |
| Cloze syntax issues | Low | Low | Validation, error messages |

---

## Success Criteria

**Must Have (MVP):**
- ✅ Can create Cloze cards with Text/Extra fields
- ✅ Can create FSI-style cards with Prompt1/Prompt2/Answer fields
- ✅ Existing Basic card creation still works (backward compatibility)
- ✅ Clear error messages when note type or fields invalid
- ✅ Comprehensive tests for all three note types

**Should Have:**
- ✅ Discovery commands to explore note types
- ✅ Flexible formatters show non-Basic cards correctly
- ✅ Documentation with examples for each note type
- ✅ CSV/JSON support for all note types

**Nice to Have:**
- Cloze-specific validation
- Auto-detection of note type from deck
- Field mapping configuration file
- Dry-run mode for previewing cards

---

## Timeline Estimate

**Phase 1: Discovery** (~2-3 hours)
- Step 1: Discovery commands

**Phase 2: Core Functionality** (~4-6 hours)
- Step 2: Add note type parameter
- Step 3: Dynamic field mapping
- Step 4: Input parsing updates

**Phase 3: Polish** (~2-3 hours)
- Step 5: Formatter updates
- Step 6: Cloze-specific features (optional)

**Phase 4: Quality Assurance** (~2-3 hours)
- Step 7: Testing
- Step 8: Documentation

**Total Estimated Time:** 10-15 hours

**Recommended Approach:**
1. Start with Step 1 (discovery) to validate FSI deck structure
2. Implement Steps 2-3 (core changes) as MVP
3. Test manually with small batches
4. Proceed with Steps 4-5 if MVP works
5. Add Step 6 (Cloze features) based on user feedback

---

## Next Actions

**Immediate (Today):**
1. Run Step 1 implementation to discover exact FSI note type name
2. Create examples of Cloze and FSI card JSON/CSV formats
3. Confirm user requirements (which note type is higher priority?)

**Short Term (This Week):**
1. Implement Step 2 (note type parameter) - quick win
2. Implement Step 3 (field mapping) - most complex
3. Test with small batch of real cards

**Medium Term (Next Week):**
1. Complete Steps 4-5 (input parsing, formatters)
2. Add comprehensive tests (Step 7)
3. Update documentation (Step 8)
4. Consider Step 6 (Cloze features) based on feedback
