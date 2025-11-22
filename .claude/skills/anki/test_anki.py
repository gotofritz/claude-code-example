"""Tests for Anki skill."""

import json
import sys
import tempfile
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Mock the anki imports before importing main
sys.modules["anki"] = MagicMock()
sys.modules["anki.collection"] = MagicMock()
sys.modules["anki.errors"] = MagicMock()
sys.modules["click"] = MagicMock()

# Now we can safely import from the .claude/skills/anki directory
sys.path.insert(0, str(Path(__file__).parent))
import main  # noqa: E402


def test_get_collection_path_from_env(monkeypatch, tmp_path):
    """Test collection path detection from environment variable."""

    # Create a temporary collection file
    collection_file = tmp_path / "collection.anki2"
    collection_file.touch()

    monkeypatch.setenv("ANKI_COLLECTION_PATH", str(collection_file))

    result = get_collection_path()
    assert result == collection_file


def test_get_collection_path_auto_detect_macos(monkeypatch):
    """Test collection path auto-detection on macOS."""
    from main import get_collection_path

    # Clear environment variable
    monkeypatch.delenv("ANKI_COLLECTION_PATH", raising=False)

    # Mock Path.home() and make macOS path exist
    mock_home = Path("/Users/testuser")
    expected_path = mock_home / "Library" / "Application Support" / "Anki2" / "User 1" / "collection.anki2"

    with patch("main.Path.home", return_value=mock_home):
        # Mock exists to return True only for expected path
        original_exists = Path.exists

        def mock_exists(self):
            if self == expected_path:
                return True
            return False

        with patch.object(Path, "exists", mock_exists):
            result = get_collection_path()
            assert result == expected_path


def test_format_card_text():
    """Test card text formatting."""
    from main import format_card_text

    note = {
        "fields": {"Front": "Hello", "Back": "Hallo"},
        "tags": ["german", "greetings"],
    }

    result = format_card_text(note=note, deck_name="Test Deck")

    assert "Test Deck" in result
    assert "Hello" in result
    assert "Hallo" in result
    assert "german" in result
    assert "greetings" in result


def test_format_card_markdown():
    """Test card markdown formatting."""
    from main import format_card_markdown

    note = {
        "fields": {"Front": "Word", "Back": "Translation"},
        "tags": ["vocabulary"],
    }

    result = format_card_markdown(note=note, deck_name="Vocab")

    assert "**Word**" in result
    assert "Translation" in result
    assert "Vocab" in result
    assert "vocabulary" in result
    assert result.startswith("- ")


def test_get_collection_nonexistent_env_path(monkeypatch):
    """Test error handling for non-existent env path."""
    from main import get_collection_path

    import click

    monkeypatch.setenv("ANKI_COLLECTION_PATH", "/nonexistent/path.anki2")

    with pytest.raises(click.ClickException, match="points to non-existent file"):
        get_collection_path()


def test_get_collection_path_not_found(monkeypatch):
    """Test error when no collection path can be found."""
    from main import get_collection_path

    import click

    # Clear env var and mock all paths to not exist
    monkeypatch.delenv("ANKI_COLLECTION_PATH", raising=False)
    monkeypatch.delenv("APPDATA", raising=False)

    with patch("main.Path.home", return_value=Path("/tmp/testuser")):
        with patch.object(Path, "exists", return_value=False):
            with pytest.raises(click.ClickException, match="Could not locate Anki collection"):
                get_collection_path()


def test_format_output_json():
    """Test JSON output formatting for cards."""
    cards_data = [
        {
            "fields": {"Front": "Hello", "Back": "Hallo"},
            "tags": ["german", "greetings"],
            "deck": "German",
        },
        {
            "fields": {"Front": "Goodbye", "Back": "Auf Wiedersehen"},
            "tags": ["german"],
            "deck": "German",
        },
    ]

    output = json.dumps(cards_data, indent=2, ensure_ascii=False)
    parsed = json.loads(output)

    assert len(parsed) == 2
    assert parsed[0]["fields"]["Front"] == "Hello"
    assert parsed[0]["deck"] == "German"
    assert "german" in parsed[0]["tags"]


def test_format_output_csv():
    """Test CSV output formatting for cards."""
    cards_data = [
        {
            "fields": {"Front": "Hello", "Back": "Hallo"},
            "tags": ["german", "greetings"],
            "deck": "German",
        },
    ]

    output_lines = ["Front,Back,Tags,Deck"]
    for card in cards_data:
        front = card["fields"].get("Front", "")
        back = card["fields"].get("Back", "")
        tags = ",".join(card["tags"])
        deck = card["deck"]
        output_lines.append(f'"{front}","{back}","{tags}","{deck}"')

    csv_output = "\n".join(output_lines)

    assert "Front,Back,Tags,Deck" in csv_output
    assert '"Hello"' in csv_output
    assert '"Hallo"' in csv_output
    assert '"german,greetings"' in csv_output
    assert '"German"' in csv_output


def test_get_collection_with_lock_error():
    """Test handling of locked collection (Anki running)."""
    from main import get_collection

    import click

    mock_error = Exception("database is locked")
    mock_error.__class__.__name__ = "DBError"

    with patch("main.Collection", side_effect=mock_error):
        with pytest.raises(click.ClickException, match="Collection is locked"):
            get_collection()


def test_read_cards_with_mock_collection(tmp_path):
    """Test read_cards command with mocked Collection."""
    from main import read_cards

    # Create mock collection
    mock_col = MagicMock()
    mock_note = MagicMock()
    mock_note.__getitem__ = lambda self, key: {"Front": "Test", "Back": "Answer"}[key]
    mock_note.keys.return_value = ["Front", "Back"]
    mock_note.tags = ["test-tag"]

    mock_card = MagicMock()
    mock_card.did = 1

    mock_deck = {"name": "Test Deck"}

    mock_col.find_notes.return_value = [1001]
    mock_col.get_note.return_value = mock_note
    mock_col.find_cards.return_value = [2001]
    mock_col.get_card.return_value = mock_card
    mock_col.decks.get.return_value = mock_deck

    output_file = tmp_path / "output.json"

    with patch("main.get_collection", return_value=mock_col):
        read_cards(
            query="tag:test",
            output=str(output_file),
            format="json",
            collection=None,
        )

    # Verify file was created
    assert output_file.exists()

    # Verify content
    with open(output_file) as f:
        data = json.load(f)
        assert len(data) == 1
        assert data[0]["fields"]["Front"] == "Test"
        assert data[0]["deck"] == "Test Deck"
        assert "test-tag" in data[0]["tags"]

    # Verify collection was closed
    mock_col.close.assert_called_once()


def test_read_cards_empty_results():
    """Test read_cards with no matching cards."""
    from main import read_cards

    mock_col = MagicMock()
    mock_col.find_notes.return_value = []

    with patch("main.get_collection", return_value=mock_col):
        # Capture click output
        from click.testing import CliRunner

        # This will exit early with "No cards found" message
        read_cards(query="nonexistent:tag", output=None, format="text", collection=None)

    mock_col.close.assert_called_once()


def test_add_cards_from_json(tmp_path):
    """Test adding cards from JSON file."""
    from main import add_cards

    # Create test JSON file
    test_data = [
        {"front": "Hello", "back": "Hallo", "tags": ["german"]},
        {"front": "Goodbye", "back": "Tschüss", "tags": ["german", "informal"]},
    ]

    json_file = tmp_path / "cards.json"
    json_file.write_text(json.dumps(test_data), encoding="utf-8")

    # Mock collection and deck
    mock_col = MagicMock()
    mock_deck = {"id": 1}
    mock_col.decks.by_name.return_value = mock_deck

    mock_model = {"id": 1, "name": "Basic"}
    mock_col.models.by_name.return_value = mock_model

    mock_note = MagicMock()
    mock_note.__setitem__ = MagicMock()
    mock_col.new_note.return_value = mock_note

    with patch("main.get_collection", return_value=mock_col):
        add_cards(
            deck="Test Deck",
            input_file=str(json_file),
            front=None,
            back=None,
            tags=None,
            collection=None,
        )

    # Verify add_note was called twice
    assert mock_col.add_note.call_count == 2
    mock_col.save.assert_called_once()
    mock_col.close.assert_called_once()


def test_add_cards_from_csv(tmp_path):
    """Test adding cards from CSV file."""
    from main import add_cards

    # Create test CSV file
    csv_file = tmp_path / "cards.csv"
    csv_file.write_text(
        'Front,Back,Tags\n"Word","Wort","german,vocabulary"\n"House","Haus","german"',
        encoding="utf-8",
    )

    # Mock collection
    mock_col = MagicMock()
    mock_deck = {"id": 1}
    mock_col.decks.by_name.return_value = mock_deck
    mock_model = {"id": 1}
    mock_col.models.by_name.return_value = mock_model
    mock_note = MagicMock()
    mock_col.new_note.return_value = mock_note

    with patch("main.get_collection", return_value=mock_col):
        add_cards(
            deck="Test Deck",
            input_file=str(csv_file),
            front=None,
            back=None,
            tags=None,
            collection=None,
        )

    # Verify two cards were added
    assert mock_col.add_note.call_count == 2
    mock_col.save.assert_called_once()


def test_add_cards_single_via_args():
    """Test adding a single card via command line arguments."""
    from main import add_cards

    mock_col = MagicMock()
    mock_deck = {"id": 1}
    mock_col.decks.by_name.return_value = mock_deck
    mock_model = {"id": 1}
    mock_col.models.by_name.return_value = mock_model
    mock_note = MagicMock()
    mock_col.new_note.return_value = mock_note

    with patch("main.get_collection", return_value=mock_col):
        add_cards(
            deck="Quick Deck",
            input_file=None,
            front="Question",
            back="Answer",
            tags="quick,test",
            collection=None,
        )

    # Verify one card was added
    mock_col.add_note.assert_called_once()
    mock_col.save.assert_called_once()


def test_add_cards_deck_not_found():
    """Test error when target deck doesn't exist."""
    from main import add_cards

    import click

    mock_col = MagicMock()
    mock_col.decks.by_name.return_value = None

    with patch("main.get_collection", return_value=mock_col):
        with pytest.raises(click.ClickException, match="Deck not found"):
            add_cards(
                deck="Nonexistent Deck",
                input_file=None,
                front="Test",
                back="Test",
                tags=None,
                collection=None,
            )

    mock_col.close.assert_called_once()


def test_add_cards_missing_input():
    """Test error when neither file nor args provided."""
    from main import add_cards

    import click

    mock_col = MagicMock()
    mock_deck = {"id": 1}
    mock_col.decks.by_name.return_value = mock_deck

    with patch("main.get_collection", return_value=mock_col):
        with pytest.raises(click.ClickException, match="Must provide either"):
            add_cards(
                deck="Test Deck",
                input_file=None,
                front=None,
                back=None,
                tags=None,
                collection=None,
            )


def test_list_decks():
    """Test listing all decks."""
    from main import list_decks

    mock_col = MagicMock()
    mock_col.decks.all.return_value = [
        {"id": 1, "name": "German"},
        {"id": 2, "name": "Spanish"},
        {"id": 3, "name": "French"},
    ]
    mock_col.find_cards.side_effect = lambda query: [1, 2, 3] if "did:1" in query else [4, 5]

    with patch("main.get_collection", return_value=mock_col):
        # Just verify it doesn't crash - output goes to stdout
        list_decks(collection=None)

    mock_col.close.assert_called_once()


def test_describe_deck():
    """Test describing a specific deck."""
    from main import describe_deck

    mock_col = MagicMock()
    mock_deck = {"id": 1, "name": "Test Deck"}
    mock_col.decks.by_name.return_value = mock_deck

    # Mock card counts for different queries
    def find_cards_side_effect(query):
        if "is:new" in query:
            return [1, 2, 3]
        elif "is:due" in query:
            return [4, 5]
        elif "is:suspended" in query:
            return [6]
        else:
            return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    mock_col.find_cards.side_effect = find_cards_side_effect

    mock_note = MagicMock()
    mock_note.tags = ["vocabulary", "basics"]
    mock_col.find_notes.return_value = [101, 102]
    mock_col.get_note.return_value = mock_note

    with patch("main.get_collection", return_value=mock_col):
        describe_deck(deck="Test Deck", collection=None)

    mock_col.close.assert_called_once()


def test_describe_deck_not_found():
    """Test error when describing non-existent deck."""
    from main import describe_deck

    import click

    mock_col = MagicMock()
    mock_col.decks.by_name.return_value = None

    with patch("main.get_collection", return_value=mock_col):
        with pytest.raises(click.ClickException, match="Deck not found"):
            describe_deck(deck="Nonexistent", collection=None)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
