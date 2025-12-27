# Quilent - AI Agent Platform for Data Intelligence

Quilent is a B2B SaaS platform that transforms public data into actionable intelligence using AI.

## Products

- **GovBids AI** - Government contract intelligence for small businesses
- **SEC Intel** - SEC filing analysis for retail investors (coming soon)
- **Academic Research** - Research paper intelligence (coming soon)

## Tech Stack

| Layer | Technology |
|-------|------------|
| API Backend | FastAPI + Python 3.12 |
| Frontend | Next.js 15 + TypeScript |
| Database | PostgreSQL 16 |
| Cache/Queue | Redis 7 |
| AI | Claude API (Anthropic) |
| Payments | Stripe |
| Hosting | Railway |

## Project Structure

```
quilent/
├── services/
│   ├── api/          # FastAPI Backend
│   ├── worker/       # Celery Background Worker
│   ├── web/          # Marketing Site
│   └── govbids/      # GovBids App (Next.js)
├── packages/
│   └── ui/           # Shared React Components
├── docker-compose.yml
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 20+
- Docker & Docker Compose
- pnpm

### Local Development

1. **Start infrastructure:**
   ```bash
   docker compose up -d postgres redis
   ```

2. **Start API:**
   ```bash
   cd services/api
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your API keys
   uvicorn app.main:app --reload
   ```

3. **Start Frontend (after setup):**
   ```bash
   cd services/govbids
   pnpm install
   pnpm dev
   ```

### Using Docker Compose

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f api

# Stop all services
docker compose down
```

## API Documentation

Once the API is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

See `services/api/.env.example` for required environment variables.

## License

Proprietary - All rights reserved.
