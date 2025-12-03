import logging
import os
import re

from bs4 import BeautifulSoup
from datetime import datetime as dt, timezone
from discord import SyncWebhook
from hashlib import sha256
from pathlib import Path
from requests import Session
from time import sleep

def format_announcement(announcement):
    time = announcement.find(class_=announcement_time_class).text.strip()
    content = announcement.find(announcement_body_selector).text.strip()
    formatted_content = re.sub(r'\n\s*\n', '\n', content, flags=re.MULTILINE)
    return time + "\n" + formatted_content

def get_formatted_last_announcement_time():
    time_obj = dt.fromtimestamp(get_last_announcement_time(), tz=timezone.utc)
    return time_obj.strftime('%a, %d %b %Y %H:%M:%S GMT')

def get_last_announcement_time():
    lastrun = 0
    for filename in os.listdir(application_data_dir):
        file_path = os.path.join(application_data_dir, filename)
        if os.path.isfile(file_path):
            modified_time = os.path.getmtime(file_path)
            if modified_time > lastrun:
                lastrun = modified_time
    return lastrun

logging.basicConfig(
    level=int(os.environ.get('LOG_LEVEL')),
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S'
)

application_data_dir = os.environ.get('APPLICATION_DATA_DIR')
asdw_announcement_url = os.environ.get('ASDW_ANNOUNCEMENT_URL')
discord_webhook_url = os.environ.get('DISCORD_WEBHOOK_URL')

announcement_selector = 'article'
announcement_body_selector = 'p'
announcement_time_class = 'text-left'

announcements_sent = False

s = Session()
s.headers.update(
    {
        'If-Modified-Since': get_formatted_last_announcement_time(),
        'User-Agent': 'ASDW Announcement Notifier v1.0'
    }
)
announcement_queue = []

try:
    response = s.get(asdw_announcement_url)

    if response.ok:
        soup = BeautifulSoup(response.text, 'html.parser')
        announcements = soup.find_all(announcement_selector)
        for announcement in announcements:
            announcement_hash = sha256(announcement.text.encode('utf-8')).hexdigest()
            cache_file_path = os.path.join(application_data_dir, announcement_hash)
            if not os.path.isfile(cache_file_path):
                with open(cache_file_path, "w") as cache_file:
                    cache_file.writelines(announcement.text.strip())
                    announcement_queue.append(format_announcement(announcement))
            else:
                logging.debug('ASDW Announcement already sent: ' + announcement_hash)

    if announcement_queue:
        discord_webhook = SyncWebhook.from_url(discord_webhook_url)
        for announcement_content in announcement_queue:
            logging.info('Sending ASDW announcement notification')
            discord_webhook.send(announcement_content)
    else:
        logging.info('No new ASDW announcements!')

except Exception as e:
    logging.error(f'Error requesting URL: {e}')

sleep(int(os.environ.get('POLL_TIME')))
