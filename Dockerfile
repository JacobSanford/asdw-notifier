FROM python:3.8

COPY src/ /usr/src/app/

WORKDIR /usr/src/app
RUN pip install --no-cache-dir -r requirements.txt

ENV APPLICATION_DATA_DIR /data
ENV ASDW_ANNOUNCEMENT_URL https://asdw.nbed.ca/news/alerts-dashboard/
ENV DISCORD_WEBHOOK_URL https://discord.com/api/webhooks/1234567890/abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz
ENV LOG_LEVEL 20
ENV POLL_TIME 300

CMD [ "python", "./asdw-notifier.py" ]
