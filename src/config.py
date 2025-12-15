"""
Configuration management for asdw-notifier.
Loads and validates environment variables on startup.
"""
import os
from dataclasses import dataclass

from validators import (
    ConfigValidationError,
    validate_directory,
    validate_url,
    validate_discord_webhook_urls,
    validate_int_range,
    get_validation_warning
)


# Default values from Dockerfile
DEFAULT_APPLICATION_DATA_DIR = '/data'
DEFAULT_ASDW_ANNOUNCEMENT_URL = 'https://asdw.nbed.ca/news/alerts-dashboard/'
DEFAULT_LOG_LEVEL = 20  # INFO
DEFAULT_POLL_TIME = 300  # 5 minutes
DEFAULT_HTTP_TIMEOUT = 30  # 30 seconds
DEFAULT_USER_AGENT = 'ASDW Status Notifier 0.1'

# Default CSS selectors for announcement scraping
DEFAULT_ANNOUNCEMENT_SELECTOR = 'article'
DEFAULT_ANNOUNCEMENT_BODY_SELECTOR = 'p'
DEFAULT_ANNOUNCEMENT_TIME_CLASS = 'text-left'

# Valid logging levels
VALID_LOG_LEVELS = [10, 20, 30, 40, 50]  # DEBUG, INFO, WARNING, ERROR, CRITICAL


@dataclass
class Config:
    """Application configuration loaded from environment variables."""
    application_data_dir: str
    asdw_announcement_url: str
    discord_webhook_urls: list[str]
    log_level: int
    poll_time: int
    http_timeout: int
    user_agent: str
    announcement_selector: str
    announcement_body_selector: str
    announcement_time_class: str


def load_config() -> Config:
    """
    Load and validate configuration from environment variables.

    This function performs validation on all environment variables and fails
    fast with a detailed error message if any validation fails.

    Returns:
        Config object with validated configuration values

    Raises:
        ConfigValidationError: If any validation fails (includes all errors)
    """
    errors = []
    warnings = []

    # Get raw values with defaults
    application_data_dir = os.environ.get('APPLICATION_DATA_DIR', DEFAULT_APPLICATION_DATA_DIR)
    asdw_announcement_url = os.environ.get('ASDW_ANNOUNCEMENT_URL', DEFAULT_ASDW_ANNOUNCEMENT_URL)
    discord_webhook_urls_str = os.environ.get('DISCORD_WEBHOOK_URLS')
    log_level_str = os.environ.get('LOG_LEVEL', str(DEFAULT_LOG_LEVEL))
    poll_time_str = os.environ.get('POLL_TIME', str(DEFAULT_POLL_TIME))
    http_timeout_str = os.environ.get('HTTP_TIMEOUT', str(DEFAULT_HTTP_TIMEOUT))
    user_agent = os.environ.get('USER_AGENT', DEFAULT_USER_AGENT)

    # CSS selectors for announcement scraping
    announcement_selector = os.environ.get('ANNOUNCEMENT_SELECTOR', DEFAULT_ANNOUNCEMENT_SELECTOR)
    announcement_body_selector = os.environ.get('ANNOUNCEMENT_BODY_SELECTOR', DEFAULT_ANNOUNCEMENT_BODY_SELECTOR)
    announcement_time_class = os.environ.get('ANNOUNCEMENT_TIME_CLASS', DEFAULT_ANNOUNCEMENT_TIME_CLASS)

    # Validate APPLICATION_DATA_DIR
    dir_error = validate_directory(application_data_dir, 'APPLICATION_DATA_DIR')
    if dir_error:
        errors.append(dir_error)

    # Validate ASDW_ANNOUNCEMENT_URL
    url_error = validate_url(asdw_announcement_url, 'ASDW_ANNOUNCEMENT_URL')
    if url_error:
        errors.append(url_error)

    # Validate DISCORD_WEBHOOK_URLS (required, no default)
    if not discord_webhook_urls_str:
        errors.append("DISCORD_WEBHOOK_URLS: Required environment variable is not set")
        discord_webhook_urls = []
    else:
        discord_webhook_urls, webhook_error = validate_discord_webhook_urls(discord_webhook_urls_str, 'DISCORD_WEBHOOK_URLS')
        if webhook_error:
            errors.append(webhook_error)
            discord_webhook_urls = []

    # Validate LOG_LEVEL
    log_level, log_level_error = validate_int_range(
        log_level_str,
        'LOG_LEVEL',
        allowed_values=VALID_LOG_LEVELS
    )
    if log_level_error:
        errors.append(log_level_error)
        log_level = DEFAULT_LOG_LEVEL  # Use default for fallback

    # Validate POLL_TIME
    poll_time, poll_time_error = validate_int_range(
        poll_time_str,
        'POLL_TIME',
        min_val=1
    )
    if poll_time_error:
        errors.append(poll_time_error)
        poll_time = DEFAULT_POLL_TIME  # Use default for fallback
    else:
        # Check for warning condition (rate limiting concern)
        poll_warning = get_validation_warning(
            poll_time,
            'POLL_TIME',
            60,
            f"{poll_time} seconds is quite frequent. Consider using >= 60 seconds to avoid rate limiting."
        )
        if poll_warning:
            warnings.append(poll_warning)

    # Validate HTTP_TIMEOUT
    http_timeout, http_timeout_error = validate_int_range(
        http_timeout_str,
        'HTTP_TIMEOUT',
        min_val=1,
        max_val=300  # Max 5 minutes seems reasonable
    )
    if http_timeout_error:
        errors.append(http_timeout_error)
        http_timeout = DEFAULT_HTTP_TIMEOUT  # Use default for fallback

    # If any validation errors occurred, raise exception with all errors
    if errors:
        raise ConfigValidationError(errors)

    # Log warnings (but don't fail)
    if warnings:
        # Note: We can't log here yet because logging isn't configured
        # These warnings will be printed to stdout
        for warning in warnings:
            print(f"[CONFIG WARNING] {warning}")

    return Config(
        application_data_dir=application_data_dir,
        asdw_announcement_url=asdw_announcement_url,
        discord_webhook_urls=discord_webhook_urls,
        log_level=log_level,
        poll_time=poll_time,
        http_timeout=http_timeout,
        user_agent=user_agent,
        announcement_selector=announcement_selector,
        announcement_body_selector=announcement_body_selector,
        announcement_time_class=announcement_time_class
    )
