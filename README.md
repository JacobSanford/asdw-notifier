# ASD-W Announcement Notifier

Scrapes the ASD-West announcement page and forwards new notifications it finds to reasonable endpoints.

## Currently Supported Endpoints

* Discord

## Software Prerequisites

You must have the following tools available for use from the command line:

* [docker](https://www.docker.com): Installation steps [are located here](https://docs.docker.com/install/).
* [docker compose plugin](https://docs.docker.com/compose/): Installation steps [are located here](https://docs.docker.com/compose/install/linux/).

## Getting Started

### 1. Create Discord Webhook(s)

Create one or more Discord webhooks. See 'Create a Webhook' section at https://docs.gitlab.com/ee/user/project/integrations/discord_notifications.html#create-webhook.

### 2. Clone this Repository

```bash
git clone https://github.com/JacobSanford/asdw-notifier.git
cd asdw-notifier
```

### 3. Configure Environment Variables

Edit `env/asdw.env` and set your Discord webhook URL(s). Optional variables can be customized as needed.

#### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DISCORD_WEBHOOK_URLS` | Yes | - | JSON array of Discord webhook URLs (e.g., `["https://discord.com/api/webhooks/..."]`) |
| `ANNOUNCEMENT_SELECTOR` | No | `article` | CSS selector for announcement wrapper |
| `ANNOUNCEMENT_BODY_SELECTOR` | No | `p` | CSS selector for announcement body |
| `ANNOUNCEMENT_TIME_CLASS` | No | `text-left` | CSS class for announcement time |
| `APPLICATION_DATA_DIR` | No | `/data` | Container data dir / cache directory. See docker-compose.yaml for use. |
| `ASDW_ANNOUNCEMENT_URL` | No | `https://asdw.nbed.ca/news/alerts-dashboard/` | Announcement page URL |
| `HTTP_TIMEOUT` | No | `30` | Timeout in seconds for all HTTP requests |
| `LOG_LEVEL` | No | `20` (INFO) | Logging level (10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR, 50=CRITICAL) |
| `POLL_TIME` | No | `300` | Seconds between checking announcements |
| `USER_AGENT` | No | `ASDW Status Notifier 0.1` | User-Agent header for HTTP requests |

### 4. Run Application

```bash
docker compose up -d
docker compose logs -f
```

The application queries the URL every `POLL_TIME` seconds, then sleeps, terminates, and restarts (via `restart: unless-stopped` in docker-compose.yml).

## Data Storge / Cache

- Announcements are cached per day to prevent duplicate notifications
- Cache files are stored as JSON in `APPLICATION_DATA_DIR` with format: `{"text": "...", "fetch_datetime": "2025-12-03T10:30:45+00:00"}`
- Identical announcements on different days are treated as unique and sent

## Background

With the demise of free Twitter API access, no reasonable notification channel existed for pushing ASD-W notifications to devices outside Twitter.

## License

MIT
