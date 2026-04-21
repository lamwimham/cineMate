"""
CineMate FastAPI Backend
REST API + WebSocket for Web UI.

Usage:
    uvicorn cine_mate.api.main:app --reload --port 8000
    
API Docs:
    http://localhost:8000/docs        (Swagger UI)
    http://localhost:8000/redoc       (ReDoc)
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from cine_mate.api.routes.runs import router as runs_router
from cine_mate.api.routes.websocket import router as ws_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown events."""
    # Startup: initialize database
    from cine_mate.core.store import Store
    db_path = Path("./cinemate.db")
    store = Store(db_path)
    await store.init_db()
    app.state.db_path = str(db_path)
    app.state.store = store

    yield

    # Shutdown: cleanup (if needed)


app = FastAPI(
    title="CineMate API",
    description="AI Video Production OS — REST API + WebSocket for Web UI",
    version="0.2.0",
    lifespan=lifespan,
)

# Register routes
app.include_router(runs_router)
app.include_router(ws_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "cinemate-api"}


@app.get("/")
async def root():
    """API root with links."""
    return {
        "service": "CineMate API",
        "version": "0.2.0",
        "docs": "/docs",
        "health": "/health",
        "runs": "/runs",
        "websocket_progress": "/ws/progress",
    }
