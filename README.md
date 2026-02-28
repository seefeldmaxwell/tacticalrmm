# FL License Lookup

**Florida Skilled Trade License Scraper & Job Board**

A platform for searching Florida DBPR (Department of Business and Professional Regulation) skilled trade licenses, viewing legal cases/disciplinary actions, and connecting homeowners with verified licensed contractors — similar to Angie's List.

## Features

### License Search
- Real-time lookup of Florida DBPR licenses by number, name, county, or trade
- Covers 14+ skilled trades: electrical, plumbing, HVAC, general contractor, roofing, and more
- Automatic caching with periodic refresh from DBPR
- Full license history tracking (status changes, renewals, etc.)

### Legal Case Search
- View disciplinary actions, complaints, and legal cases against any license
- Tracks fines, penalties, license actions (suspensions, revocations)
- Sources: DBPR enforcement actions, Florida court records
- Case documents and notes

### Job Board (Angie's List Style)
- Homeowners post projects and receive bids from licensed contractors
- Contractor profiles with verified Florida licenses
- Angie's List-style letter grade ratings (A through F)
- Rating categories: quality, price, punctuality, professionalism, responsiveness
- Contractor portfolio and review system
- Budget ranges, urgency levels, location-based matching

### REST API
- Full API for all features (license lookup, legal cases, jobs, contractors)
- Swagger/OpenAPI documentation at `/api/docs/`
- Filtering, search, and pagination

## Tech Stack

- **Backend**: Django 4.2, Django REST Framework
- **Scraping**: httpx, BeautifulSoup4, lxml
- **Database**: PostgreSQL (SQLite for development)
- **Task Queue**: Celery + Redis (background scraping)
- **Frontend**: Django Templates, Bootstrap 5
- **Container**: Docker & Docker Compose

## Quick Start

### Local Development

```bash
# Clone and setup
git clone <repo-url>
cd fl-license-scraper

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup database
python manage.py migrate
python manage.py seed_data
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Docker

```bash
docker compose up --build
```

The app will be available at `http://localhost:8000`.

## Management Commands

```bash
# Seed trade categories
python manage.py seed_data

# Look up a specific license
python manage.py scrape_licenses --license EC13012345

# Search by name
python manage.py scrape_licenses --name "John Smith" --trade electrical

# Scrape all licenses for a trade
python manage.py scrape_licenses --trade plumbing

# Scrape all trades
python manage.py scrape_licenses --trade all
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/licenses/` | List all licenses |
| `GET /api/licenses/lookup/<license_number>/` | Look up a specific license (live scrape if needed) |
| `GET /api/licenses/categories/` | List trade categories |
| `GET /api/legal/cases/` | List legal cases |
| `GET /api/legal/lookup/<license_number>/` | Get cases for a license |
| `GET /api/jobs/postings/` | List job postings |
| `GET /api/jobs/contractors/` | List verified contractors |
| `GET /api/jobs/reviews/` | List reviews |
| `GET /api/docs/` | Swagger API documentation |

## Supported Florida Trades

| Trade | License Prefix | DBPR Code |
|-------|---------------|-----------|
| Electrical Contractors | EC | 5102 |
| Plumbing | CFC | 5901 |
| Air Conditioning (HVAC) | CAC | 5001 |
| General Contractor | CGC | 5301 |
| Building Contractor | CBC | 5302 |
| Roofing Contractor | CCC | 5303 |
| Swimming Pool | CPC | 5304 |
| Solar Contractor | CSC | 5305 |
| Underground Utility | CUC | 5306 |
| Alarm System | EF | 5100 |
| Glass and Glazing | SCC | 5307 |
| Mechanical Contractor | CMC | 5308 |
| Sheet Metal Contractor | SMC | 5309 |
| Pollutant Storage | PCS | 5310 |

## Running Tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Environment Variables

See `.env.example` for all configuration options.

## License

MIT
