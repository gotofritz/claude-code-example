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

- [x] Modify JSON parser to accept `fields` object
- [x] Maintain backward compatibility with `front`/`back` keys
- [x] Update CSV parser for flexible columns
  - Auto-detect columns from header row
  - Map column names to note type fields (case-insensitive)
- [x] Add validation for CSV format with non-standard fields
- [x] Update example files in documentation

**Status**: ✅ Complete (implemented in Step 3 commit 60cd5eb)

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

### Step 6: Add Cloze-Specific Features ✅ Complete

- [x] Add basic Cloze deletion syntax validation
  - Error if Text field missing `{{c1::...}}` syntax (CLI shortcuts)
  - Warning for batch imports (skips invalid cards)
  - Suggest correct format in error message
- [x] Add `--cloze-text` and `--cloze-extra` shortcuts for CLI
  - Convenience parameters for single Cloze card creation
  - Maps to Text/Extra fields automatically
  - Strict validation on CLI input
- [x] Add Cloze examples to documentation
  - JSON format with cloze syntax
  - Multiple cloze deletions example
  - Hints in cloze deletions

**Status**: ✅ Complete (commit 499e874)

**Reasoning**: Cloze cards have special syntax requirements. Basic validation and convenience features improve user experience and reduce errors. However, Anki itself validates cloze syntax, so this is nice-to-have rather than critical.

**Dependencies**: Steps 2-3 complete (need note type support)

**Complexity**: Low (~30-45 minutes)

- Simple regex validation
- Additional CLI parameters
- Documentation examples

**Code Location**: New validation function, `main.py:298-313` (add parameters)

---

### Step 7: Comprehensive Testing ✅ Complete

- [x] Add tests for Cloze card creation
  - test_format_card_text_cloze, test_format_card_markdown_cloze
  - test_add_cards_cloze_explicit_fields, test_add_cards_cloze_via_cli_shortcut
  - test_add_cards_cloze_invalid_syntax, test_has_cloze_deletion
  - test_add_cards_batch_cloze_with_invalid_skips
- [x] Add tests for FSI German-style card creation (3-field custom type)
  - test_add_cards_custom_note_type_flexible
  - test_add_cards_csv_flexible_columns
- [x] Add tests for discovery commands
  - test_list_note_types, test_describe_deck_note_types
  - test_describe_deck_note_types_not_found, test_describe_deck_note_types_empty_deck
- [x] Add tests for field mapping logic
  - test_add_cards_invalid_field_name, test_add_cards_front_back_with_wrong_note_type
  - test_add_cards_no_matching_fields
- [x] Add tests for flexible formatters
  - test_format_card_text_custom_fields, test_format_card_markdown_custom_fields
  - Cloze formatters (above)
- [x] Add tests for error cases (missing fields, invalid note type)
  - test_add_cards_deck_not_found, test_add_cards_missing_input
  - test_add_cards_invalid_note_type, field mapping errors (above)
- [x] Update existing tests to use parameterized note types
  - Added cloze_text/cloze_extra parameters to all 9 existing add_cards tests
- [x] Test backward compatibility (Basic note type still works)
  - test_add_cards_from_json, test_add_cards_from_csv, test_add_cards_single_via_args

**Status**: ✅ Complete (38 tests, all passing)

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

1. **What exactly is the FSI deck's note type name?** ⚠️ User Action Required

   - **Status**: Can be discovered using built commands
   - **Resolution**: User runs `skill: anki list-note-types` and `skill: anki describe-deck-note-types --deck "DEU FSI German Basic Course Drills"`
   - **Impact**: Low - framework supports any note type name
   - **Example provided**: Documentation uses "FSI German Drills" as placeholder

2. **Does the FSI note type have any custom JavaScript/CSS?** ℹ️ Low Priority

   - **Status**: Unknown until user inspects their collection
   - **Resolution**: User can inspect note type templates after discovery
   - **Impact**: None - write operations don't touch templates or JS/CSS
   - **Decision**: Not a blocker for MVP

3. **Should we support card type specification (for note types with multiple templates)?** ✅ Resolved

   - **Decision**: Defer to future - default template sufficient for MVP
   - **Rationale**: Uses Anki's default (first) template, matches expected behavior
   - **Status**: Not a blocker, can be added in future if needed

4. **How to handle required vs optional fields?** ✅ Resolved
   - **Decision**: Allow empty fields, warn but don't block
   - **Rationale**: Anki itself permits empty fields
   - **Implementation**: Field mapper allows empty values
   - **Status**: Implemented and tested

**Potential Issues - All Resolved:**

1. **Field Name Conflicts** ✅ **RESOLVED**

   - **Implementation**: Case-insensitive matching in `map_input_to_note_fields()` (.claude/skills/anki/main.py:161)
   - **Test Coverage**: `test_add_cards_custom_note_type_flexible`
   - **Status**: ✅ Complete

2. **Cloze Syntax Errors** ✅ **RESOLVED**

   - **Implementation**: `_has_cloze_deletion()` validation function with regex (.claude/skills/anki/main.py:110)
   - **Behavior**: Strict validation for CLI, warning-based for batch imports
   - **Test Coverage**: `test_has_cloze_deletion`, `test_add_cards_cloze_invalid_syntax`, `test_add_cards_batch_cloze_with_invalid_skips`
   - **Status**: ✅ Complete

3. **Breaking Existing Tests** ✅ **RESOLVED**

   - **Result**: All 38 tests passing (15 pre-existing + 23 new multi-note-type tests)
   - **Backward Compatibility**: Verified with `test_add_cards_from_json`, `test_add_cards_from_csv`, `test_add_cards_single_via_args`
   - **Status**: ✅ Complete

4. **CSV Column Ordering Ambiguity** ✅ **RESOLVED**
   - **Implementation**: CSV parser uses header row for explicit field names (.claude/skills/anki/main.py:657)
   - **Documentation**: Examples provided for all note types in SKILL.md
   - **Test Coverage**: `test_add_cards_csv_flexible_columns`
   - **Status**: ✅ Complete

### Blocker Summary

- **Blocking Issues**: 0
- **User Action Items**: 1 (optional - discover FSI note type name from their collection)
- **Resolved Issues**: 6/6
- **Deferred to Future**: 1 (multiple templates support)

**Risk Assessment:**

| Risk                     | Probability | Impact | Mitigation                              |
| ------------------------ | ----------- | ------ | --------------------------------------- |
| Existing workflows break | Low         | High   | Default to "Basic", comprehensive tests |
| Field mapping bugs       | Medium      | Medium | Thorough testing, clear errors          |
| Performance degradation  | Low         | Low    | Minimal - same API usage                |
| User confusion           | Medium      | Low    | Good documentation, examples            |
| Cloze syntax issues      | Low         | Low    | Validation, error messages              |

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
