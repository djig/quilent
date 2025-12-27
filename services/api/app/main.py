from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import init_db
from app.middleware.rate_limit import limiter
from app.routers import ai, alerts, auth, billing, entities, search


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    pass


app = FastAPI(
    title="Quilent API",
    description="AI Agent Platform for Data Intelligence",
    version="1.0.0",
    lifespan=lifespan,
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "quilent-api"}


# Routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(entities.router, prefix="/api/entities", tags=["entities"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
app.include_router(billing.router, prefix="/api/billing", tags=["billing"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)  # noqa: S104
