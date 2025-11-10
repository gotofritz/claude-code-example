# Anki Card Converter: Project Plan

## Overview

Convert a large Anki deck of German language cards (3293+) from "normal" format to Cloze deletion format using an interactive CLI backed by a local LLM. The tool learns card structures through user interaction, building a template library as it progresses.

## Current State

- Source deck: [German Language Deck - 1272878976](https://ankiweb.net/shared/info/1272878976)
- 3293+ cards across ~25 different structures
- Cards are currently in "normal" question/answer format
- Design & architecture agreed upon; ready to implement

## Breakdown

### Step 1: Extract & Parse Anki Deck

- [ ] Research `.apkg` format (ZIP structure, database layout)
- [ ] Write `AnkiDeckParser` class to extract cards from `.apkg`
- [ ] Convert cards to a standard internal format (dict/dataclass with fields)
- [ ] Handle edge cases (media, HTML formatting, special characters)
- [ ] Write tests to verify parsing on sample cards

**Reasoning:** Decouples data extraction from transformation logic. Once cards are in a standard format, everything else is simpler.

**Dependencies:** None (first step)

**Complexity:** Low-Medium

---

### Step 2: Build Template System

- [ ] Design template data structure (examples, fingerprint, transformation_rule, distinguishing_notes)
- [ ] Create `Template` class with serialization (to/from JSON)
- [ ] Create `TemplateLibrary` class to manage collection of templates
- [ ] Implement template storage (JSON file that persists across runs)
- [ ] Write methods to add, update, and retrieve templates

**Reasoning:** Core abstraction for the entire system. Everything else depends on this.

**Dependencies:** Step 1 (need to understand card format to design template schema)

**Complexity:** Low

---

### Step 3: LLM Classification Module

- [ ] Set up Ollama client connection & model selection
- [ ] Create `CardClassifier` class with `classify(card, template_library)` method
- [ ] Implement prompt that asks LLM to match card against known templates
- [ ] Extract confidence score from LLM response
- [ ] Define confidence threshold for "high confidence" (e.g., >85%)
- [ ] Write fallback: if no templates exist, ask LLM to describe the structure
- [ ] Test with sample cards and manual verification

**Reasoning:** The brain of the system. Accurate classification determines everything downstream.

**Dependencies:** Step 2 (needs template library structure)

**Complexity:** Medium (LLM prompting is iterative)

---

### Step 4: Transformation Engine

- [ ] Create `CardTransformer` class with `transform(card, template)` method
- [ ] Implement cloze syntax generation (Anki format: `{{c1::word}}`)
- [ ] Apply template's transformation_rule to generate output
- [ ] Handle German grammar considerations (case agreement, article handling, etc.)
- [ ] Validate output (check for valid cloze syntax, malformed cards)
- [ ] Write tests with sample German cards

**Reasoning:** Converts classified cards to cloze format according to learned rules.

**Dependencies:** Step 2 (needs templates)

**Complexity:** Medium (German grammar edge cases)

---

### Step 5: State & Resumability

- [ ] Design state file schema (current card index, learned templates, progress markers)
- [ ] Create `State` class to load/save state (JSON)
- [ ] Implement crash recovery (resume from last processed card)
- [ ] Track which cards have been processed and their output file
- [ ] Support batch workflows (work, stop, resume later)
- [ ] Test crash recovery by killing the process mid-run

**Reasoning:** Allows user to work in batches without losing progress. Critical for processing 3000+ cards.

**Dependencies:** Step 2 (templates need to be saved in state)

**Complexity:** Low-Medium

---

### Step 6: CLI Interface & Review Mode

- [ ] Design interactive CLI menu (Accept Cloze / Accept Non-Cloze / No Transform / New Template / Silent Mode)
- [ ] Create `ReviewUI` class to display card and transformation
- [ ] Implement user input handling (keyboard/menu navigation)
- [ ] Build "New Template" flow (prompt user for structure explanation, capture examples)
- [ ] Implement "Silent Mode" toggle (processes high-confidence matches automatically)
- [ ] Add progress indicators (card N of M, templates learned so far)
- [ ] Test with interactive user flows

**Reasoning:** The primary interface. Must be intuitive and responsive.

**Dependencies:** Steps 3, 4, 5 (needs classifier, transformer, state)

**Complexity:** Medium (user interaction loops)

---

### Step 7: Output Generation

- [ ] Design TSV output format compatible with Anki import
- [ ] Create `OutputWriter` class to append cards to TSV files
- [ ] Implement three output streams: `cloze_output.tsv`, `non_cloze_output.tsv`, `no_transform.tsv`
- [ ] Add headers/metadata to TSV files
- [ ] Format cards for Anki re-import (deck field, card type, etc.)
- [ ] Test re-import into a test Anki instance

**Reasoning:** User needs to re-import transformed cards into Anki; format matters.

**Dependencies:** Step 4 (needs transformed cards)

**Complexity:** Low

---

### Step 8: Testing & Validation

- [ ] Run on full deck (or large sample) in interactive mode
- [ ] Manually verify 50-100 cards across different structures
- [ ] Check for common errors (missed cloze marks, malformed German, etc.)
- [ ] Test edge cases (unicode, HTML in cards, complex structures)
- [ ] Stress-test silent mode on high-confidence cards
- [ ] Verify re-import into Anki works correctly
- [ ] Document any issues and refine templates/prompts

**Reasoning:** Last step. Catches bugs, improves LLM prompts, ensures usable output.

**Dependencies:** All prior steps

**Complexity:** Medium (iterative refinement)

---

## Integration

This is a standalone CLI tool with minimal integration needs:

- Reads: Anki `.apkg` file (input)
- Writes: TSV files + state JSON (can be re-imported or deleted)
- No integration with existing systems (self-contained)
- Can be run multiple times on the same deck without conflict (state file tracks progress)

---

## Blockers

1. **LLM Prompt Engineering** — Confidence scoring and template matching will need iteration. May need multiple prompt attempts to get reliable classification.

2. **German Grammar Edge Cases** — Some structures may require nuanced grammar understanding (case agreement, article selection). Unclear how well the LLM will handle these without explicit rules.

3. **Template Ambiguity** — Some cards might genuinely match multiple templates with similar confidence. Need a strategy for tiebreaking or manual resolution.

4. **Performance** — 3293 cards × LLM classification = slow. May need batching or optimization (e.g., fast pattern-matching pre-filter before LLM).

5. **User Experience** — Interactive loop needs to be fast/responsive. Ollama latency could be frustrating if responses are slow.
