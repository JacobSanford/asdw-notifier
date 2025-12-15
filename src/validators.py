"""
Validation functions for environment variables.
"""
import json
import os
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse


class ConfigValidationError(Exception):
    """Raised when environment variable validation fails."""

    def __init__(self, errors: list[str]):
        self.errors = errors
        message = "Configuration validation failed:\n" + "\n".join(f"  - {err}" for err in errors)
        super().__init__(message)


def validate_directory(value: str, var_name: str) -> Optional[str]:
    """
    Validate that a directory exists and is writable.

    Args:
        value: Directory path to validate
        var_name: Name of the environment variable (for error messages)

    Returns:
        Error message if validation fails, None otherwise
    """
    if not value:
        return f"{var_name}: Directory path cannot be empty"

    path = Path(value)

    if not path.exists():
        return f"{var_name}: Directory '{value}' does not exist"

    if not path.is_dir():
        return f"{var_name}: Path '{value}' is not a directory"

    # Test write permission by attempting to create a temp file
    try:
        test_file = path / ".write_test"
        test_file.touch()
        test_file.unlink()
    except (OSError, PermissionError) as e:
        return f"{var_name}: Directory '{value}' is not writable - {e}"

    return None


def validate_url(value: str, var_name: str) -> Optional[str]:
    """
    Validate that a string is a valid URL with http/https scheme.

    Args:
        value: URL to validate
        var_name: Name of the environment variable (for error messages)

    Returns:
        Error message if validation fails, None otherwise
    """
    if not value:
        return f"{var_name}: URL cannot be empty"

    try:
        parsed = urlparse(value)
        if parsed.scheme not in ('http', 'https'):
            return f"{var_name}: URL must use http:// or https://, got: '{value}'"
        if not parsed.netloc:
            return f"{var_name}: Invalid URL format: '{value}'"
    except Exception as e:
        return f"{var_name}: Failed to parse URL '{value}' - {e}"

    return None


def validate_discord_webhook_url(value: str, var_name: str) -> Optional[str]:
    """
    Validate that a string is a valid Discord webhook URL.

    Args:
        value: URL to validate
        var_name: Name of the environment variable (for error messages)

    Returns:
        Error message if validation fails, None otherwise
    """
    # First validate as a general URL
    url_error = validate_url(value, var_name)
    if url_error:
        return url_error

    # Check Discord-specific requirements
    if '/api/webhooks/' not in value:
        return f"{var_name}: Discord webhook URL must contain '/api/webhooks/', got: '{value}'"

    parsed = urlparse(value)
    if 'discord.com' not in parsed.netloc:
        return f"{var_name}: Discord webhook URL must be from discord.com domain, got: '{parsed.netloc}'"

    return None


def validate_discord_webhook_urls(value: str, var_name: str) -> tuple[Optional[list[str]], Optional[str]]:
    """
    Validate a JSON array of Discord webhook URLs.

    Args:
        value: JSON array string containing webhook URLs
        var_name: Name of the environment variable (for error messages)

    Returns:
        Tuple of (list_of_urls, error_message)
        If validation succeeds: (urls_list, None)
        If validation fails: (None, error_message)
    """
    if not value:
        return None, f"{var_name}: Value cannot be empty"

    try:
        urls = json.loads(value)
    except json.JSONDecodeError as e:
        return None, f"{var_name}: Invalid JSON format - {e}"

    if not isinstance(urls, list):
        return None, f"{var_name}: Must be a JSON array, got: {type(urls).__name__}"

    if len(urls) == 0:
        return None, f"{var_name}: Array cannot be empty, at least one webhook URL is required"

    errors = []
    for i, url in enumerate(urls):
        if not isinstance(url, str):
            errors.append(f"  [{i}]: Must be a string, got: {type(url).__name__}")
            continue
        url_error = validate_discord_webhook_url(url, f"{var_name}[{i}]")
        if url_error:
            errors.append(f"  [{i}]: {url_error.split(': ', 1)[1]}")

    if errors:
        return None, f"{var_name}: Invalid webhook URL(s):\n" + "\n".join(errors)

    return urls, None


def validate_int_range(value: str, var_name: str, min_val: int = None,
                       max_val: int = None, allowed_values: list[int] = None) -> tuple[Optional[int], Optional[str]]:
    """
    Validate that a string can be converted to an integer within a range.

    Args:
        value: String to validate and convert
        var_name: Name of the environment variable (for error messages)
        min_val: Minimum allowed value (inclusive)
        max_val: Maximum allowed value (inclusive)
        allowed_values: If provided, value must be in this list

    Returns:
        Tuple of (converted_int, error_message)
        If validation succeeds: (int_value, None)
        If validation fails: (None, error_message)
    """
    if not value:
        return None, f"{var_name}: Value cannot be empty"

    try:
        int_val = int(value)
    except ValueError:
        return None, f"{var_name}: Must be an integer, got: '{value}'"

    if allowed_values is not None and int_val not in allowed_values:
        return None, f"{var_name}: Must be one of {allowed_values}, got: {int_val}"

    if min_val is not None and int_val < min_val:
        return None, f"{var_name}: Must be >= {min_val}, got: {int_val}"

    if max_val is not None and int_val > max_val:
        return None, f"{var_name}: Must be <= {max_val}, got: {int_val}"

    return int_val, None


def get_validation_warning(value: int, var_name: str, threshold: int, message: str) -> Optional[str]:
    """
    Generate a warning message if a value is below a threshold.

    Args:
        value: Integer value to check
        var_name: Name of the environment variable
        threshold: Threshold value for warning
        message: Warning message template

    Returns:
        Warning message if threshold is crossed, None otherwise
    """
    if value < threshold:
        return f"WARNING - {var_name}: {message}"
    return None
