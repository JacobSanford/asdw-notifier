# ASD-W Announcement Notifier

Scrapes the ASD-West announcement page and forwards new notifications it finds to reasonable endpoints.

## Currently Supported Endpoints

* Discord

## Software Prerequisites

You must have the following tools available for use from the command line:

* [docker](https://www.docker.com): Installation steps [are located here](https://docs.docker.com/install/).
* [docker compose plugin](https://docs.docker.com/compose/): Installation steps [are located here](https://docs.docker.com/compose/install/linux/).

## Getting Started

### 1. Create a Discord Webhook

See 'Create a Webhook' section at https://docs.gitlab.com/ee/user/project/integrations/discord_notifications.html#create-webhook.

### 2. Clone this Repository

```bash
git clone https://github.com/JacobSanford/asdw-notifier.git
cd asdw-notifier
```

### 3. Add Hook to asdw-notifier Configuration

Edit the ```env/asdw.env``` file and enter your webhook under DISCORD_WEBHOOK_URL.

### 4. Run Application

```bash
docker compose up -d
```

The application will query the URL every POLLING_TIME seconds.

Specifically, it will sleep for POLLING_TIME seconds after query, terminate and restart based on the ```restart: always``` entry in its docker-compose.yml.

## Background

With the demise of free Twitter API access, no reasonable notification channel existed for pushing ASD-W notifications to devices outside Twitter.

## License

MIT
