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

- Node.js 22+ (for frontend)
- Docker & Docker Compose
- pnpm

> **Note:** No Python installation needed! Backend runs entirely in Docker.

### Local Development (Recommended)

Use the dev start script for the easiest setup:

```bash
./scripts/dev-start.sh
```

This script will:
- Check if required ports are available (5433, 6379, 8000, 3000)
- Offer to stop conflicting services if ports are in use
- Start Docker containers (PostgreSQL, Redis, API)
- Run database migrations automatically

Then start the frontend in a separate terminal:
```bash
cd services/govbids
pnpm install
pnpm dev
```

### Manual Setup

If you prefer manual control:

1. **Start backend services (Docker):**
   ```bash
   docker-compose up -d postgres redis api
   ```

2. **Run database migrations:**
   ```bash
   docker-compose exec api alembic upgrade head
   ```

3. **Start frontend (local):**
   ```bash
   cd services/govbids
   pnpm install
   pnpm dev
   ```

### Services & Ports

| Service | Port | URL |
|---------|------|-----|
| PostgreSQL | 5433 | - |
| Redis | 6379 | - |
| API | 8000 | http://localhost:8000 |
| API Docs | 8000 | http://localhost:8000/docs |
| Frontend | 3000 | http://localhost:3000 |

### Common Commands

```bash
# Start all backend services
docker-compose up -d postgres redis api

# View API logs
docker-compose logs -f api

# Restart API after code changes
docker-compose restart api

# Stop all services
docker-compose down

# Full reset (removes database data)
docker-compose down -v

# Run database migrations
docker-compose exec api alembic upgrade head

# Access database shell
docker-compose exec postgres psql -U quilent
```

## API Documentation

Once the API is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

### Backend (services/api)
See `services/api/.env.example` for required environment variables.

### Frontend (services/govbids)
Create `services/govbids/.env.local`:

```env
# NextAuth Configuration
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-key-here
AUTH_TRUST_HOST=true

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# OAuth Providers (optional for local dev)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
```

Generate NEXTAUTH_SECRET:
```bash
openssl rand -base64 32
```

## License

Proprietary - All rights reserved.
