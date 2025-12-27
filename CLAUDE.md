# Quilent - AI Agent Platform for Data Intelligence

## Project Overview

Quilent is a B2B SaaS platform that transforms public data (government contracts, SEC filings, research papers, patents) into actionable intelligence using AI.

### Business Model
- **Platform approach**: One generic backend serving multiple product verticals
- **First product**: GovBids AI (government contract intelligence for small businesses)
- **Second product**: SEC Intel (SEC filing analysis for retail investors)
- **Pricing**: Freemium, $15-99/month depending on product and tier

## Tech Stack

| Layer | Technology | Hosting |
|-------|------------|---------|
| **GovBids App** | Next.js 15 + TypeScript | Railway |
| **API Backend** | FastAPI + Python 3.12 | Railway |
| **Background Worker** | Celery + Python | Railway |
| **Database** | PostgreSQL 16 | Railway |
| **Cache/Queue** | Redis 7 | Railway |
| **Auth** | NextAuth.js 5 | - |
| **AI** | Claude API (Anthropic) | - |
| **Payments** | Stripe | - |
| **Email** | Resend | - |

## Project Structure

```
quilent/
├── services/
│   ├── api/                      # FastAPI Backend (Railway)
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py           # FastAPI app entry
│   │   │   ├── config.py         # Settings & env vars
│   │   │   ├── database.py       # DB connection
│   │   │   ├── routers/          # API endpoints
│   │   │   ├── services/         # Business logic
│   │   │   ├── adapters/         # Data source adapters
│   │   │   ├── models/           # SQLAlchemy models
│   │   │   ├── schemas/          # Pydantic schemas
│   │   │   └── middleware/       # Auth middleware
│   │   ├── requirements.txt
│   │   ├── Dockerfile
│   │   └── railway.toml
│   │
│   ├── worker/                   # Background Worker (Railway)
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── celery_app.py
│   │   │   └── tasks/
│   │   ├── requirements.txt
│   │   ├── Dockerfile
│   │   └── railway.toml
│   │
│   ├── web/                      # Marketing Site (Railway)
│   │   └── (Next.js app)
│   │
│   └── govbids/                  # GovBids App (Railway)
│       ├── src/
│       │   ├── app/              # Next.js App Router
│       │   ├── components/       # React components
│       │   └── lib/              # Utilities
│       ├── package.json
│       └── railway.toml
│
├── packages/
│   └── ui/                       # Shared React Components
│
├── docker-compose.yml            # Local development
├── .env.example                  # Environment template
├── CLAUDE.md                     # This file
└── README.md
```

## Key Commands

### Local Development

```bash
# Start all services with Docker
docker compose up -d

# Start API only
cd services/api
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Start GovBids frontend
cd services/govbids
pnpm dev

# Run database migrations
cd services/api
alembic upgrade head
```

### Testing

```bash
# Backend tests
cd services/api
pytest

# Frontend tests
cd services/govbids
pnpm test
```

### Deployment

```bash
# Deploy to Railway
railway up
```

## Environment Variables

### API Service
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `ANTHROPIC_API_KEY` - Claude API key
- `SAM_GOV_API_KEY` - SAM.gov API key
- `STRIPE_SECRET_KEY` - Stripe secret key
- `STRIPE_WEBHOOK_SECRET` - Stripe webhook secret
- `RESEND_API_KEY` - Resend email API key
- `JWT_SECRET_KEY` - JWT signing key
- `CORS_ORIGINS` - Allowed CORS origins

### Frontend Service
- `NEXT_PUBLIC_API_URL` - Backend API URL
- `NEXTAUTH_URL` - NextAuth URL
- `NEXTAUTH_SECRET` - NextAuth secret
- `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` - Stripe public key

## API Endpoints

### Health
- `GET /health` - Health check

### Entities
- `GET /api/entities` - List entities
- `GET /api/entities/{id}` - Get entity details
- `POST /api/entities/{id}/save` - Save entity
- `DELETE /api/entities/{id}/save` - Unsave entity

### Search
- `GET /api/search` - Search entities with filters
- `GET /api/search/recent` - Get recent entities

### AI
- `POST /api/ai/summarize/{id}` - Generate AI summary
- `POST /api/ai/ask/{id}` - Ask question about entity

### Alerts
- `GET /api/alerts` - List user alerts
- `POST /api/alerts` - Create alert
- `PUT /api/alerts/{id}` - Update alert
- `DELETE /api/alerts/{id}` - Delete alert

### Billing
- `POST /api/billing/create-checkout-session` - Create Stripe checkout
- `POST /api/billing/webhook` - Stripe webhook handler

## Database Models

### Entity
Stores all data items (contracts, filings, papers) with product-agnostic schema:
- `id` - UUID primary key
- `product_id` - Product identifier (gov, sec, academic)
- `source_id` - External ID from data source
- `entity_type` - Type (contract, filing, paper)
- `title` - Title
- `source_url` - Original URL
- `published_at` - Publication date
- `data` - JSON field with product-specific data
- `summary` - AI-generated summary (cached)

### User
- `id` - UUID primary key
- `email` - User email
- `name` - Display name

### Alert
- `id` - UUID primary key
- `user_id` - Owner
- `product_id` - Product
- `name` - Alert name
- `conditions` - JSON matching rules
- `channels` - Notification channels
- `is_active` - Active status

### Subscription
- `id` - UUID primary key
- `user_id` - Owner
- `product_id` - Product
- `tier` - Subscription tier (free, pro, agency)
- `stripe_customer_id` - Stripe customer
- `stripe_subscription_id` - Stripe subscription

## Data Adapters

### SAM.gov Adapter
Fetches government contract opportunities from SAM.gov API:
- Search by keywords, NAICS codes, agencies
- Get recent opportunities
- Normalize to Entity schema

### Future Adapters
- SEC EDGAR (SEC filings)
- arXiv (research papers)
- USPTO (patents)

## AI Integration

Using Claude API for:
- **Summarization**: Generate 2-3 sentence summaries (Haiku model)
- **Analysis**: Deep contract analysis (Sonnet model)
- **Q&A**: Answer questions about entities (Haiku model)
- **Matching**: Score contract-profile fit (Sonnet model)

## Products

### GovBids AI (First Product)
- Target: Small businesses seeking federal contracts
- Data: SAM.gov
- Pricing: Free / $29 Pro / $99 Agency

### SEC Intel (Second Product)
- Target: Retail investors
- Data: SEC EDGAR
- Pricing: Free / $15 Pro / $49 Premium

### Academic Research (Third Product)
- Target: Researchers, PhD students
- Data: arXiv, PubMed
- Pricing: Free / $8 Student / $19 Pro

## Development Phases

### Phase 1 (Current): GovBids AI MVP
- 8 weeks to launch
- Core features: Search, Alerts, AI Summaries, Billing
- Goal: First paying customers

### Phase 2: Platform Extraction
- Extract reusable platform components
- Launch SEC Intel in 3 weeks (vs 8 weeks)
- Prove platform velocity

### Phase 3: Scale
- Additional products
- Enterprise features
- Seed fundraising

## Documentation

See `/docs/` in the ai-agent-platform directory for:
- `TECH_SPEC_BACKEND.md` - Backend technical specification
- `TECH_SPEC_FRONTEND.md` - Frontend technical specification
- `DOCKER_LOCAL_SETUP.md` - Docker setup guide
- `DEPLOYMENT.md` - Deployment guide
- `PHASE_1_DETAILED_PLAN.md` - Implementation plan

## Contact

Solo technical founder building this as primary focus.
