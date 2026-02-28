# FL License Scraper & Job Board

A Cloudflare Workers application that scrapes Florida DBPR (Department of Business and Professional Regulation) license data for skilled trades and provides an Angie's List-style job board.

## Features

- **License Search**: Look up any FL skilled trade license by number or name
- **14+ Trade Categories**: Electrical, Plumbing, HVAC, General Contractor, Roofing, and more
- **Legal Cases**: Every tradesperson shows legal cases, disciplinary actions, and fines
- **License Status**: Active/Delinquent/Suspended/Revoked status on every listing
- **Reviews & Ratings**: Angie's List-style A-F letter grades with 5 rating categories
- **Job Board**: Post jobs, receive bids from licensed contractors
- **REST API**: Full JSON API at `/api/*`
- **Scheduled Scraping**: Cron trigger refreshes stale license data

## Tech Stack

- **Runtime**: Cloudflare Workers
- **Framework**: Hono
- **Database**: Cloudflare D1 (SQLite)
- **Cache**: Cloudflare KV
- **Data Source**: Florida DBPR (myfloridalicense.com)

## Deploy

### Prerequisites

- Node.js 18+
- Cloudflare account
- Wrangler CLI (`npm i -g wrangler`)

### Setup

```bash
# Install dependencies
npm install

# Login to Cloudflare
wrangler login

# Create D1 database
wrangler d1 create fl-licenses

# Create KV namespace
wrangler kv namespace create CACHE

# Update wrangler.toml with the database_id and KV id from above commands

# Run migrations
npm run db:migrate

# Seed data
npm run db:seed

# Deploy
npm run deploy
```

### Local Development

```bash
# Run migrations locally
npm run db:migrate:local
npm run db:seed:local

# Start dev server
npm run dev
```

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/licenses?q=` | GET | Search licenses |
| `/api/licenses/:number` | GET | License detail with legal cases & reviews |
| `/api/licenses/:number/scrape` | POST | Scrape/refresh from DBPR |
| `/api/legal-cases` | GET | List legal cases |
| `/api/contractors` | GET | List contractors |
| `/api/contractors/:id` | GET | Contractor detail with reviews & legal |
| `/api/jobs` | GET | List jobs |
| `/api/jobs/:id` | GET | Job detail with bids |
| `/api/reviews` | GET | List reviews |
| `/api/trades` | GET | Trade categories |

## Pages

| URL | Description |
|---|---|
| `/` | Home with stats, featured contractors, trade categories |
| `/search?q=` | License search with results showing status, reviews, legal cases |
| `/licenses/:number` | Full license detail with legal cases & reviews |
| `/contractors` | Contractor directory with filters |
| `/contractors/:id` | Contractor profile with reviews, legal cases, license status |
| `/jobs` | Job board listing |
| `/jobs/:id` | Job detail with bids showing contractor license & legal info |
| `/trades` | All trade categories |
| `/trades/:slug` | Licenses in a trade category |
