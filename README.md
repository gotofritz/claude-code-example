# Anki German Card Converter: Normal → Cloze

## The Problem

I wanted to convert [this](https://ankiweb.net/shared/info/1272878976) large Anki deck (3293+ cards) of German language cards in "normal" format—typically a question/answer pair to Cloze deletion format, which is a more effective learning method that focuses on active recall of specific terms.

## Why This Matters

The existing cards already test retrieval of missing words, but they do so through a variety of ad-hoc formats and layouts that are cumbersome to process. Cloze deletion is the standardized Anki format for this exact task—cleaner, more consistent, and easier to work with. However, the existing deck uses ~25 different card structures, many loosely defined, making automated conversion tricky.

## What This Tool Does

**Anki German Card Converter** is an interactive CLI application that:

1. Loads your Anki deck and processes cards one at a time
2. Uses a local LLM to identify which structure each card matches
3. Shows you how it would transform the card to Cloze format
4. Lets you accept, reject, or explain new structures
5. Learns new card structures as you work, building a template library
6. Outputs transformed cards to TSV files ready to re-import into Anki
7. Saves progress so you can work in batches and resume later

## How It Works

The tool maintains a **template library** learned interactively:

- Show it a card → LLM classifies it against known templates
- High confidence match? → Auto-transforms and shows you the result
- Low confidence or unknown? → Stops and asks what structure this is
- You explain the structure with examples → LLM generates a fingerprint
- Template is saved → next similar card is handled automatically
- Repeat until done, or switch to **silent mode** where the LLM processes high-confidence matches alone

You control everything through a simple review interface with options to accept, skip, or explain.

## Quick Example

**Input card (Normal format):**

```
Prompt1: `Er hat _____.`
Prompt2: `Füller; ein- neu- amerikansich-`
Answer: `Er hat _einen_neuen_amerikanischen_Füller_.`
```

**Output card (Cloze format):**

```
Text: `Er hat {{c1::einen neuen amerikanischen Füller::Füller; ein- neu- amerikansich-}}.`
Extra: ` `
```

The tool shows you each transformation and lets you accept or adjust it.

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- [UV](https://github.com/astral-sh/uv) installed globally
- [Ollama](https://ollama.com/) running locally with a capable model (e.g., Mistral, Llama 2/3)
- An exported Anki deck (`.apkg` file)
- Basic understanding of German grammar (you'll be explaining structures to the tool)

### Installation

1. **Clone the repository:**

   ```sh
   git clone https://github.com/gotofritz/claude-code-example.git
   cd  claude-code-example
   ```

2. **Install dependencies:**

   ```sh
   uv sync
   ```

3. **Activate the virtual environment:**

   ```sh
   # On Unix/macOS
   source .venv/bin/activate

   # On Windows
   .venv\Scripts\activate
   ```

### Development Setup

1. **Install pre-commit hooks:**

   ```sh
   pre-commit install
   ```

2. **Run the test suite:**

   ```sh
   task test
   ```

3. **Check code quality:**

   ```sh
   task qa
   ```

## 🖥️ CLI Usage

claude-code-example includes a command-line interface for easy interaction:

```sh
# Show available commands
uv run claude-code-example --help

# Run a simple command
uv run claude-code-example simple-command "hello world"

# Use subcommands
uv run claude-code-example subcommand --help
```

Example usage:

```sh
❯ uv run claude-code-example --help
Usage: claude-code-example [OPTIONS] COMMAND [ARGS]...

  Main entry point for the CLI.

Options:
  -v, --version  Show the version and exit.
  -h, --help     Show this message and exit.

Commands:
  simple-command  This is a simple command.
  subcommand      This contains sub-subcommands
```

## 🛠️ Development

### Available Commands

This project uses various tools for development. Here are the most common commands:

```sh
# Install dependencies
uv sync

# Run tests with coverage
task test

# open the code coverage in a web browser
task coverage

# Format code with ruff
task lint-fix

# Lint code
task qa

# Run pre-commit on all files
uv run pre-commit run --all-files
```

### Project Structure

```
claude-code-example/
├── claude-code-example/                  # Main package
│   ├── cli/               # CLI commands
│   └── ...                # Other modules
├── tests/                 # Test suite
├── pyproject.toml        # Project configuration
└── README.md             # This file
```

### Making Changes

1. **Create a feature branch:**

   ```sh
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and ensure tests pass:

   ```sh
   uv run pytest
   ```

3. **Commit using conventional commits:**

   ```sh
   git commit -m "feat: add new feature"
   ```

4. **Push and create a pull request.**

### Versioning

This project follows [Semantic Versioning](https://semver.org/) and uses [Conventional Commits](https://www.conventionalcommits.org/) for automated changelog generation.

To create a new release:

```sh
uv run cz bump
git push --follow-tags
```

## 🧪 Testing

Run the full test suite:

```sh
# Run all tests
task test
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass and code quality checks succeed
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Homepage:** [https://github.com/gotofritz/claude-code-example](https://github.com/gotofritz/claude-code-example)
- **Documentation:** [https://github.com/gotofritz/claude-code-example](https://github.com/gotofritz/claude-code-example)
- **Issues:** [https://github.com/gotofritz/claude-code-example/issues](https://github.com/gotofritz/claude-code-example/issues)
- **Changelog:** [CHANGELOG.md](CHANGELOG.md)
