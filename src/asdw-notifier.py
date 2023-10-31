import logging
import os

from bs4 import BeautifulSoup
from datetime import datetime as dt
from discord import SyncWebhook
from hashlib import sha256
from pathlib import Path
from requests import Session
from time import sleep

def get_formatted_last_announcement_time():
    time_obj = dt.utcfromtimestamp(get_last_announcement_time())
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

def send_announcement_notification(time, content):
    logging.info('Sending ASDW announcement notification')
    webhook = SyncWebhook.from_url(discord_webhook_url)
    webhook.send('ASDW: ' + time + "\n" + content)

logging.basicConfig(level=int(os.environ.get('LOG_LEVEL')))

application_data_dir = os.environ.get('APPLICATION_DATA_DIR')
asdw_announcement_url = os.environ.get('ASDW_ANNOUNCEMENT_URL')
discord_webhook_url = os.environ.get('DISCORD_WEBHOOK_URL')

announcement_selector = 'article'
announcement_body_selector = 'p'
announcement_time_class = 'text-left'

announcements_sent = False

s = Session()
s.headers.update({'If-Modified-Since': get_formatted_last_announcement_time()})
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
            send_announcement_notification(
                announcement.find(class_=announcement_time_class).text.strip(),
                announcement.find(announcement_body_selector).text.strip()
            )
            announcements_sent = True
        else:
            logging.debug('ASDW Announcement already sent: ' + announcement_hash)

if not announcements_sent:
    logging.info('No new ASDW announcements!')

sleep(int(os.environ.get('POLL_TIME')))
