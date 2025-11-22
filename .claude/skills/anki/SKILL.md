---
name: anki
description: Read cards from and write new cards to a local Anki installation
allowed-tools: Bash
---

# Anki Skill

Read and query existing Anki cards, or add new cards directly to your local Anki collection.

## Prerequisites

**For Write Operations:**
- Anki must be closed before adding cards
- Collection database will be locked if Anki is running

**Optional Configuration:**
```bash
# Custom collection path (auto-detected if not set)
export ANKI_COLLECTION_PATH="/path/to/collection.anki2"
```

## Available Commands

### read-cards
Query and export cards from your Anki collection using Anki search syntax.

```bash
# Export all cards with tag "german" as JSON
skill: anki read-cards --query "tag:german" --format json --output cards.json

# Export due cards as CSV
skill: anki read-cards --query "is:due" --format csv --output due.csv

# Show cards from a specific deck as markdown
skill: anki read-cards --query "deck:Vocabulary" --format markdown

# Query all cards (returns as text summary)
skill: anki read-cards --query ""
```

**Formats:**
- `json` - Structured data with all fields and metadata
- `csv` - Tabular format (Front, Back, Tags, Deck)
- `markdown` - Human-readable formatted list
- `text` - Simple text summary (default)

### list-decks
List all decks in your collection with card counts.

```bash
skill: anki list-decks
```

### describe-deck
Show detailed information about a specific deck.

```bash
skill: anki describe-deck --deck "German Vocabulary"
```

### add-cards
Add new cards to your Anki collection. **Requires Anki to be closed.**

```bash
# Add cards from CSV file
skill: anki add-cards --input cards.csv --deck "Vocabulary"

# Add cards from JSON file
skill: anki add-cards --input cards.json --deck "German"

# Add a single card via arguments
skill: anki add-cards --deck "Quick" --front "Hello" --back "Hallo" --tags "german,greetings"
```

**CSV Format:**
```csv
Front,Back,Tags
"Word","Translation","tag1,tag2"
```

**JSON Format:**
```json
[
  {
    "front": "Word",
    "back": "Translation",
    "tags": ["tag1", "tag2"]
  }
]
```

## Usage Notes

- Dependencies auto-installed via PEP 723 inline metadata (`anki>=25.9.2`)
- Collection path auto-detected: `~/Library/Application Support/Anki2/User 1/collection.anki2` (macOS)
- Override with `--collection` argument or `ANKI_COLLECTION_PATH` environment variable
- All write operations use high-level Anki API (no direct database writes)
- Collection is properly closed after each operation

## Error Handling

**Common Errors:**

- `Collection is locked` - Anki is currently running. Close it and try again.
- `Deck not found` - Specified deck doesn't exist. Use `list-decks` to see available decks.
- `Collection not found` - Cannot locate Anki collection. Specify path with `--collection`.

## Security Considerations

- **Safe API Usage**: Only uses high-level Anki API methods (`col.add_note`, `col.find_notes`)
- **No Direct SQL**: Never writes directly to database to prevent corruption
- **Resource Cleanup**: Collection always closed properly, even on errors
- **Input Validation**: Card data validated before writing to collection
