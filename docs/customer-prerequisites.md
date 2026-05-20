# A05 Customer Prerequisites

## Access and Ownership

- VPS or dedicated Ubuntu server with sudo access
- Domain or subdomain prepared for the API
- Rubika bot token owned by the customer
- Decision-maker contact for deployment approval

## Required Infrastructure

- Python 3.12 runtime support
- PostgreSQL 16
- Redis 7
- Reverse proxy support such as Nginx
- systemd for API, worker, and scheduler services

## Required Inputs Before Start

- Final domain for webhook and API access
- `RUBIKA_BOT_TOKEN`
- `WEBHOOK_SECRET` if webhook validation is required
- Production JWT secret
- Customer-approved database and Redis locations

## Deployment Preconditions

- DNS record resolves to the target server
- Ports `80` and `443` are available for proxy and TLS
- Outbound access to Rubika Bot API is allowed
- Backup owner is identified before go-live

## Operational Preconditions

- Customer agrees on who monitors the services after launch
- Customer confirms who can restart services and rotate secrets
- Customer designates where credentials are stored

## Not Ready Signals

- No stable server access
- No domain control
- Shared or temporary secrets in chat
- Unclear ownership for operations after handoff
