import json
import logging
import re
import sys

from bs4 import BeautifulSoup
from bs4.element import Tag
from datetime import datetime as dt, timezone
from discord import SyncWebhook
from hashlib import sha256
from pathlib import Path
from requests import Session
from time import sleep

from config import load_config, ConfigValidationError

def format_announcement(announcement: Tag) -> str:
    """Format an announcement by extracting time and content."""
    time = announcement.find(class_=announcement_time_class).text.strip()
    content = announcement.find(announcement_body_selector).text.strip()
    formatted_content = re.sub(r'\n\s*\n', '\n', content, flags=re.MULTILINE)
    return time + "\n" + formatted_content

def get_formatted_last_announcement_time() -> str:
    """Get the last announcement time formatted as HTTP date string."""
    time_obj = dt.fromtimestamp(get_last_announcement_time(), tz=timezone.utc)
    return time_obj.strftime('%a, %d %b %Y %H:%M:%S GMT')

def get_last_announcement_time() -> float:
    """Get the most recent file modification time from cache directory."""
    lastrun: float = 0
    cache_dir = Path(application_data_dir)
    if cache_dir.exists():
        for file_path in cache_dir.iterdir():
            if file_path.is_file():
                modified_time: float = file_path.stat().st_mtime
                if modified_time > lastrun:
                    lastrun = modified_time
    return lastrun

# Load and validate configuration
try:
    config = load_config()
except ConfigValidationError as e:
    print(f"ERROR: {e}", file=sys.stderr)
    print("Sleeping 60 seconds before exit to prevent rapid restart loop...", file=sys.stderr)
    sleep(60)
    sys.exit(1)

# Configure logging with validated log level
logging.basicConfig(
    level=config.log_level,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S'
)

# Extract config values for backward compatibility with existing code
application_data_dir: Path = Path(config.application_data_dir)
asdw_announcement_url: str = config.asdw_announcement_url
discord_webhook_url: str = config.discord_webhook_url
http_timeout: int = config.http_timeout
announcement_selector: str = config.announcement_selector
announcement_body_selector: str = config.announcement_body_selector
announcement_time_class: str = config.announcement_time_class

# Ensure cache directory exists
try:
    application_data_dir.mkdir(parents=True, exist_ok=True)
except Exception as e:
    logging.error(f'Failed to create cache directory {application_data_dir}: {e}')
    print(f"ERROR: Cannot create cache directory: {e}", file=sys.stderr)
    print("Sleeping 60 seconds before exit to prevent rapid restart loop...", file=sys.stderr)
    sleep(60)
    sys.exit(1)

announcements_sent: bool = False

s: Session = Session()
s.headers.update({'If-Modified-Since': get_formatted_last_announcement_time()})
announcement_queue: list[str] = []

# Capture fetch datetime (UTC ISO format) for cache metadata
fetch_datetime: str = dt.now(timezone.utc).isoformat()
fetch_date: str = fetch_datetime[:10]  # Extract YYYY-MM-DD for hash

try:
    response = s.get(asdw_announcement_url, timeout=http_timeout)

    if response.ok:
        soup = BeautifulSoup(response.text, 'html.parser')
        announcements = soup.find_all(announcement_selector)
        for announcement in announcements:
            # Include fetch date in hash to treat identical announcements on different days as unique
            announcement_hash: str = sha256((announcement.text + fetch_date).encode('utf-8')).hexdigest()
            cache_file_path: Path = application_data_dir / announcement_hash
            if not cache_file_path.is_file():
                try:
                    cache_data = {
                        "text": announcement.text.strip(),
                        "fetch_datetime": fetch_datetime
                    }
                    cache_file_path.write_text(json.dumps(cache_data, indent=2))
                    # Only queue announcement if cache write succeeded
                    announcement_queue.append(format_announcement(announcement))
                except Exception as e:
                    logging.error(f'Failed to write cache file {cache_file_path}: {e}')
                    logging.warning(f'Skipping announcement {announcement_hash} due to cache write failure')
            else:
                logging.debug('ASDW Announcement already sent: ' + announcement_hash)

    if announcement_queue:
        discord_webhook: SyncWebhook = SyncWebhook.from_url(discord_webhook_url)
        for announcement_content in announcement_queue:
            try:
                logging.info('Sending ASDW announcement notification')
                discord_webhook.send(announcement_content)
            except Exception as e:
                logging.error(f'Failed to send Discord webhook notification: {e}')
                logging.debug(f'Failed announcement content: {announcement_content[:100]}...')
    else:
        logging.info('No new ASDW announcements!')

except Exception as e:
    logging.error(f'Error requesting URL: {e}')

sleep(config.poll_time)
