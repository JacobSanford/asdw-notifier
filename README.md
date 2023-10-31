# ASD-W Announcement Notifier

Scrapes the ASD-West announcement page and forwards new notifications it finds to reasonable endpoints.

## Currently Supported Endpoints

* Discord

## Getting Started

### 1. Create a Discord Webhook

See 'Create a Webhook' section at https://docs.gitlab.com/ee/user/project/integrations/discord_notifications.html#create-webhook.

### 2. Add Hook to asdw-notifier Configuration

Edit the ```env/asdw.env``` file and enter your webhook under DISCORD_WEBHOOK_URL.

### 3. Run Application

```bash
docker compose up -d
```

The application will query the URL every POLLING_TIME seconds.

## Background

With the demise of free Twitter API access, no reasonable notification channel existed for pushing ASD-W notifications to devices outside Twitter.

## License

MIT
