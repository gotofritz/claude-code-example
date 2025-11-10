from claude_code_example import __app_name__
from claude_code_example.config.app_config import ClaudeCodeExampleConfig
from claude_code_example.logging.logging import setup_logger


class AppContext:
    """Holds all the objects needed by commands"""

    def __init__(self) -> None:
        self.app_config = ClaudeCodeExampleConfig(app_name=__app_name__)
        self.logger = setup_logger(log_level=self.app_config.log_level, app_name=__app_name__)
