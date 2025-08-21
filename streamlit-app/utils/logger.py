"""
Centralized logging configuration for the Pokemon Translation app
"""

import logging
import sys
from datetime import datetime
from pathlib import Path


def setup_logger(
    name: str, log_file: str = None, level: int = logging.INFO
) -> logging.Logger:
    """
    Set up a logger with both file and console handlers

    Args:
        name: Logger name
        log_file: Optional log file path
        level: Logging level

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    logger.setLevel(level)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler with proper encoding
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    # Fix Unicode encoding issue on Windows
    if hasattr(console_handler.stream, "reconfigure"):
        try:
            console_handler.stream.reconfigure(encoding="utf-8", errors="replace")
        except:
            pass  # Fallback if reconfigure fails
    logger.addHandler(console_handler)

    # File handler (optional) with proper encoding
    if log_file:
        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding="utf-8", errors="replace")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_pokemon_parser_logger() -> logging.Logger:
    """Get the Pokemon parser logger"""
    return setup_logger(
        "pokemon_parser", log_file="logs/pokemon_parser.log", level=logging.DEBUG
    )


def get_api_logger() -> logging.Logger:
    """Get the API interaction logger"""
    return setup_logger("api_client", log_file="logs/api.log", level=logging.INFO)


def get_auth_logger() -> logging.Logger:
    """Get the authentication logger"""
    return setup_logger(
        "auth",
        log_file="logs/auth.log",
        level=logging.WARNING,  # Only log warnings and errors for security
    )


class PokemonParsingMetrics:
    """Track Pokemon parsing performance and success rates"""

    def __init__(self):
        self.logger = get_pokemon_parser_logger()
        self.parsing_stats = {
            "total_attempts": 0,
            "successful_parses": 0,
            "failed_parses": 0,
            "pokemon_extracted": 0,
            "processing_times": [],
        }

    def log_parsing_attempt(self, url: str):
        """Log a parsing attempt"""
        self.parsing_stats["total_attempts"] += 1
        self.logger.info(f"Starting Pokemon parsing for URL: {url}")

    def log_parsing_success(self, pokemon_count: int, processing_time: float):
        """Log a successful parsing operation"""
        self.parsing_stats["successful_parses"] += 1
        self.parsing_stats["pokemon_extracted"] += pokemon_count
        self.parsing_stats["processing_times"].append(processing_time)

        self.logger.info(
            f"Successfully parsed {pokemon_count} Pokemon in {processing_time:.2f}s"
        )

    def log_parsing_failure(self, error: str):
        """Log a parsing failure"""
        self.parsing_stats["failed_parses"] += 1
        self.logger.error(f"Pokemon parsing failed: {error}")

    def log_pokemon_details(self, pokemon_index: int, pokemon_name: str, details: dict):
        """Log detailed Pokemon parsing information"""
        self.logger.debug(
            f"Pokemon {pokemon_index + 1}: {pokemon_name} - "
            f"Moves: {len(details.get('moves', []))}, "
            f"EVs: {bool(details.get('evs'))}, "
            f"Nature: {bool(details.get('nature'))}"
        )

    def get_success_rate(self) -> float:
        """Calculate parsing success rate"""
        if self.parsing_stats["total_attempts"] == 0:
            return 0.0
        return (
            self.parsing_stats["successful_parses"]
            / self.parsing_stats["total_attempts"]
        )

    def get_average_processing_time(self) -> float:
        """Calculate average processing time"""
        times = self.parsing_stats["processing_times"]
        return sum(times) / len(times) if times else 0.0


# Global metrics instance
pokemon_metrics = PokemonParsingMetrics()
