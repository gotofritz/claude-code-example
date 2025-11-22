#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "anki>=25.9.2",
#     "click>=8.1.0",
# ]
# ///
"""Anki skill for reading and writing cards to local Anki collections.

This skill provides safe read/write access to Anki collections using the
official Anki Python API. It supports querying cards, listing decks, and
adding new cards without direct database writes.
"""

import json
import os
import sys
from pathlib import Path

try:
    import click
    from anki.collection import Collection
    from anki.errors import DBError
except ImportError:
    sys.exit(1)


def get_collection_path() -> Path:
    """Get Anki collection path from environment or auto-detect.

    Returns:
        Path to collection.anki2 file

    Raises:
        click.ClickException: If collection cannot be found
    """
    # Check environment variable
    env_path = os.environ.get("ANKI_COLLECTION_PATH")
    if env_path:
        path = Path(env_path)
        if path.exists():
            return path
        raise click.ClickException(f"ANKI_COLLECTION_PATH points to non-existent file: {env_path}")

    # Auto-detect based on platform
    home = Path.home()
    candidates = [
        home / "Library" / "Application Support" / "Anki2" / "User 1" / "collection.anki2",  # macOS
        home / ".local" / "share" / "Anki2" / "User 1" / "collection.anki2",  # Linux
        home / ".var" / "app" / "net.ankiweb.Anki" / "data" / "Anki2" / "User 1" / "collection.anki2",  # Linux Flatpak
    ]

    # Windows path
    appdata = os.environ.get("APPDATA")
    if appdata:
        candidates.append(Path(appdata) / "Anki2" / "User 1" / "collection.anki2")

    for candidate in candidates:
        if candidate.exists():
            return candidate

    raise click.ClickException("Could not locate Anki collection. Use --collection to specify path or set ANKI_COLLECTION_PATH.")


def get_collection(*, collection_path: Path | None = None) -> Collection:
    """Open Anki collection with error handling.

    Args:
        collection_path: Optional path to collection file

    Returns:
        Open Collection object

    Raises:
        click.ClickException: If collection cannot be opened
    """
    path = collection_path or get_collection_path()

    try:
        return Collection(str(path))
    except DBError as e:
        if "database is locked" in str(e).lower():
            raise click.ClickException("Collection is locked. Close Anki and try again.")
        raise click.ClickException(f"Failed to open collection: {e}")
    except Exception as e:
        raise click.ClickException(f"Failed to open collection: {e}")


def format_card_text(*, note: dict, deck_name: str) -> str:
    """Format a single card as text.

    Args:
        note: Note dictionary with fields
        deck_name: Name of the deck

    Returns:
        Formatted text string
    """
    fields = note.get("fields", {})
    front = fields.get("Front", "N/A")
    back = fields.get("Back", "N/A")
    tags = ", ".join(note.get("tags", []))

    return f"[{deck_name}] {front} → {back} (tags: {tags})"


def format_card_markdown(*, note: dict, deck_name: str) -> str:
    """Format a single card as markdown.

    Args:
        note: Note dictionary with fields
        deck_name: Name of the deck

    Returns:
        Formatted markdown string
    """
    fields = note.get("fields", {})
    front = fields.get("Front", "N/A")
    back = fields.get("Back", "N/A")
    tags = ", ".join(note.get("tags", []))

    return f"- **{front}** → {back}\n  - Deck: {deck_name}\n  - Tags: {tags}"


@click.group()
def cli():
    """Anki skill for reading and writing cards."""
    pass


@cli.command(name="read-cards")
@click.option("--query", required=True, help='Anki search query (e.g., "tag:german", "is:due")')
@click.option("--output", help="Output file path (prints to stdout if not specified)")
@click.option(
    "--format",
    type=click.Choice(["json", "csv", "markdown", "text"]),
    default="text",
    help="Output format (default: text)",
)
@click.option("--collection", help="Path to collection.anki2 file (auto-detected if not specified)")
def read_cards(*, query: str, output: str | None, format: str, collection: str | None):
    """Query and export cards from Anki collection."""
    col = None
    try:
        collection_path = Path(collection) if collection else None
        col = get_collection(collection_path=collection_path)

        # Find notes matching query
        note_ids = col.find_notes(query)

        if not note_ids:
            click.echo(f"No cards found matching query: {query}")
            return

        # Collect card data
        cards_data = []
        for note_id in note_ids:
            note = col.get_note(note_id)

            # Get deck name from first card
            card_ids = col.find_cards(f"nid:{note_id}")
            deck_name = "Unknown"
            if card_ids:
                card = col.get_card(card_ids[0])
                deck = col.decks.get(card.did)
                deck_name = deck["name"] if deck else "Unknown"

            # Extract fields
            fields = {}
            for field_name in note.keys():
                fields[field_name] = note[field_name]

            cards_data.append({
                "fields": fields,
                "tags": note.tags,
                "deck": deck_name,
            })

        # Output based on format
        if format == "json":
            output_data = json.dumps(cards_data, indent=2, ensure_ascii=False)
            if output:
                Path(output).write_text(output_data, encoding="utf-8")
                click.echo(f"Exported {len(cards_data)} cards to {output}")
            else:
                click.echo(output_data)

        elif format == "csv":
            output_lines = []
            output_lines.append("Front,Back,Tags,Deck")
            for card in cards_data:
                front = card["fields"].get("Front", "")
                back = card["fields"].get("Back", "")
                tags = ",".join(card["tags"])
                deck = card["deck"]
                output_lines.append(f'"{front}","{back}","{tags}","{deck}"')

            output_data = "\n".join(output_lines)
            if output:
                Path(output).write_text(output_data, encoding="utf-8")
                click.echo(f"Exported {len(cards_data)} cards to {output}")
            else:
                click.echo(output_data)

        elif format == "markdown":
            output_lines = [f"# Anki Cards ({len(cards_data)} cards)\n"]
            for card in cards_data:
                output_lines.append(format_card_markdown(note=card, deck_name=card["deck"]))

            output_data = "\n".join(output_lines)
            if output:
                Path(output).write_text(output_data, encoding="utf-8")
                click.echo(f"Exported {len(cards_data)} cards to {output}")
            else:
                click.echo(output_data)

        else:  # text format
            click.echo(f"Found {len(cards_data)} cards:\n")
            for card in cards_data:
                click.echo(format_card_text(note=card, deck_name=card["deck"]))

    finally:
        if col:
            col.close()


@cli.command(name="list-decks")
@click.option("--collection", help="Path to collection.anki2 file (auto-detected if not specified)")
def list_decks(*, collection: str | None):
    """List all decks in the collection."""
    col = None
    try:
        collection_path = Path(collection) if collection else None
        col = get_collection(collection_path=collection_path)

        decks = col.decks.all()

        click.echo(f"Found {len(decks)} decks:\n")
        for deck in sorted(decks, key=lambda d: d["name"]):
            deck_id = deck["id"]
            deck_name = deck["name"]

            # Count cards in deck
            card_count = len(col.find_cards(f"did:{deck_id}"))

            click.echo(f"  {deck_name}: {card_count} cards")

    finally:
        if col:
            col.close()


@cli.command(name="list-note-types")
@click.option("--collection", help="Path to collection.anki2 file (auto-detected if not specified)")
def list_note_types(*, collection: str | None):
    """List all note types in the collection with their fields."""
    col = None
    try:
        collection_path = Path(collection) if collection else None
        col = get_collection(collection_path=collection_path)

        models = col.models.all()

        click.echo(f"Found {len(models)} note type(s):\n")
        for model in sorted(models, key=lambda m: m["name"]):
            model_name = model["name"]
            model_type = "Cloze" if model["type"] == 1 else "Standard"
            fields = [field["name"] for field in model["flds"]]

            click.echo(f"  {model_name} ({model_type})")
            click.echo(f"    Fields: {', '.join(fields)}")

    finally:
        if col:
            col.close()


@cli.command(name="describe-deck-note-types")
@click.option("--deck", required=True, help="Deck name")
@click.option("--collection", help="Path to collection.anki2 file (auto-detected if not specified)")
def describe_deck_note_types(*, deck: str, collection: str | None):
    """Show note types used in a specific deck with sample data."""
    col = None
    try:
        collection_path = Path(collection) if collection else None
        col = get_collection(collection_path=collection_path)

        # Find deck by name
        deck_obj = col.decks.by_name(deck)
        if not deck_obj:
            raise click.ClickException(f"Deck not found: {deck}")

        # Find all notes in deck
        note_ids = col.find_notes(f"deck:{deck}")
        if not note_ids:
            click.echo(f"No cards found in deck: {deck}")
            return

        # Collect note types and sample cards
        note_type_data = {}
        for note_id in note_ids:
            note = col.get_note(note_id)
            model = col.models.get(note.mid)
            if not model:
                continue

            model_name = model["name"]
            if model_name not in note_type_data:
                model_type = "Cloze" if model["type"] == 1 else "Standard"
                fields = [field["name"] for field in model["flds"]]
                note_type_data[model_name] = {
                    "type": model_type,
                    "fields": fields,
                    "samples": [],
                }

            # Add sample if we have fewer than 3
            if len(note_type_data[model_name]["samples"]) < 3:
                sample_fields = {}
                for field_name in note.keys():
                    sample_fields[field_name] = note[field_name]
                note_type_data[model_name]["samples"].append(sample_fields)

        # Output
        click.echo(f"Deck: {deck}")
        click.echo(f"Found {len(note_type_data)} note type(s) in use:\n")

        for model_name in sorted(note_type_data.keys()):
            data = note_type_data[model_name]
            click.echo(f"  {model_name} ({data['type']})")
            click.echo(f"    Fields: {', '.join(data['fields'])}")
            click.echo("    Sample cards:")

            for i, sample in enumerate(data["samples"], 1):
                click.echo(f"      Sample {i}:")
                for field_name, field_value in sample.items():
                    # Truncate long values
                    display_value = field_value[:80] + "..." if len(field_value) > 80 else field_value
                    # Replace newlines with spaces for cleaner output
                    display_value = display_value.replace("\n", " ")
                    click.echo(f"        {field_name}: {display_value}")
            click.echo()

    finally:
        if col:
            col.close()


@cli.command(name="describe-deck")
@click.option("--deck", required=True, help="Deck name")
@click.option("--collection", help="Path to collection.anki2 file (auto-detected if not specified)")
def describe_deck(*, deck: str, collection: str | None):
    """Show detailed information about a specific deck."""
    col = None
    try:
        collection_path = Path(collection) if collection else None
        col = get_collection(collection_path=collection_path)

        # Find deck by name
        deck_obj = col.decks.by_name(deck)
        if not deck_obj:
            raise click.ClickException(f"Deck not found: {deck}")

        deck_id = deck_obj["id"]

        # Count cards
        total_cards = len(col.find_cards(f"did:{deck_id}"))
        new_cards = len(col.find_cards(f"did:{deck_id} is:new"))
        due_cards = len(col.find_cards(f"did:{deck_id} is:due"))
        suspended_cards = len(col.find_cards(f"did:{deck_id} is:suspended"))

        click.echo(f"Deck: {deck}")
        click.echo(f"  Total cards: {total_cards}")
        click.echo(f"  New: {new_cards}")
        click.echo(f"  Due: {due_cards}")
        click.echo(f"  Suspended: {suspended_cards}")

        # Get unique tags in deck
        note_ids = col.find_notes(f"deck:{deck}")
        all_tags = set()
        for note_id in note_ids:
            note = col.get_note(note_id)
            all_tags.update(note.tags)

        if all_tags:
            click.echo(f"  Tags: {', '.join(sorted(all_tags))}")

    finally:
        if col:
            col.close()


@cli.command(name="add-cards")
@click.option("--deck", required=True, help="Target deck name")
@click.option("--input", "input_file", help="CSV or JSON file with card data")
@click.option("--front", help="Card front (for single card)")
@click.option("--back", help="Card back (for single card)")
@click.option("--tags", help="Comma-separated tags (for single card)")
@click.option("--collection", help="Path to collection.anki2 file (auto-detected if not specified)")
def add_cards(
    *,
    deck: str,
    input_file: str | None,
    front: str | None,
    back: str | None,
    tags: str | None,
    collection: str | None,
):
    """Add new cards to Anki collection. Requires Anki to be closed."""
    col = None
    try:
        collection_path = Path(collection) if collection else None
        col = get_collection(collection_path=collection_path)

        # Find deck by name
        deck_obj = col.decks.by_name(deck)
        if not deck_obj:
            raise click.ClickException(f"Deck not found: {deck}. Use list-decks to see available decks.")

        deck_id = deck_obj["id"]

        # Determine input source
        cards_to_add = []

        if input_file:
            # Load from file
            input_path = Path(input_file)
            if not input_path.exists():
                raise click.ClickException(f"Input file not found: {input_file}")

            if input_path.suffix.lower() == ".json":
                # JSON format
                data = json.loads(input_path.read_text(encoding="utf-8"))
                if not isinstance(data, list):
                    raise click.ClickException("JSON file must contain an array of card objects")

                for item in data:
                    if not isinstance(item, dict):
                        raise click.ClickException("Each card must be an object with 'front' and 'back' fields")
                    if "front" not in item or "back" not in item:
                        raise click.ClickException("Each card must have 'front' and 'back' fields")

                    card_tags = item.get("tags", [])
                    if isinstance(card_tags, str):
                        card_tags = [t.strip() for t in card_tags.split(",")]

                    cards_to_add.append({
                        "front": item["front"],
                        "back": item["back"],
                        "tags": card_tags,
                    })

            elif input_path.suffix.lower() == ".csv":
                # CSV format
                import csv

                with input_path.open("r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if "Front" not in row or "Back" not in row:
                            raise click.ClickException("CSV must have 'Front' and 'Back' columns")

                        card_tags = []
                        if "Tags" in row and row["Tags"]:
                            card_tags = [t.strip() for t in row["Tags"].split(",")]

                        cards_to_add.append({
                            "front": row["Front"],
                            "back": row["Back"],
                            "tags": card_tags,
                        })
            else:
                raise click.ClickException("Input file must be .json or .csv")

        elif front and back:
            # Single card from arguments
            card_tags = []
            if tags:
                card_tags = [t.strip() for t in tags.split(",")]

            cards_to_add.append({
                "front": front,
                "back": back,
                "tags": card_tags,
            })
        else:
            raise click.ClickException("Must provide either --input file or --front/--back arguments")

        # Get the Basic note type
        model = col.models.by_name("Basic")
        if not model:
            raise click.ClickException("Basic note type not found in collection")

        # Add cards using high-level API
        added_count = 0
        for card_data in cards_to_add:
            # Create new note
            note = col.new_note(model)

            # Set fields
            note["Front"] = card_data["front"]
            note["Back"] = card_data["back"]

            # Set tags
            if card_data["tags"]:
                note.tags = card_data["tags"]

            # Add to collection (high-level API, no direct SQL)
            col.add_note(note, deck_id)
            added_count += 1

        # Save changes
        col.save()

        click.echo(f"Successfully added {added_count} card(s) to deck '{deck}'")

    finally:
        if col:
            col.close()


if __name__ == "__main__":
    cli()
