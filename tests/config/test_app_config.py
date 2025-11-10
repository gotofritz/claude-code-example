from claude_code_example.config.app_config import ClaudeCodeExampleConfig


def test_settings() -> None:
    settings = ClaudeCodeExampleConfig()
    assert settings.app_name == "claude-code-example"
    assert settings.log_level in ["INFO", "DEBUG"]
