import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.documents import router as documents_router
from app.api.orchestrator import router as orchestrator_router
from app.api.evaluation import router as evaluation_router
from app.api.sec import router as sec_router
from app.api.retrieval import router as retrieval_router
from app.db.session import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("doc_orchestrator")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler initializing database schemas on startup."""
    logger.info("Initializing relational database tables...")
    await init_db()
    yield
    logger.info("Application shutdown complete.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Multi-Agent Document Intelligence Orchestrator using LangGraph, FastAPI, and Automated Regression Guardrails.",
    lifespan=lifespan
)


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(documents_router, prefix=settings.API_PREFIX)
app.include_router(orchestrator_router, prefix=settings.API_PREFIX)
app.include_router(evaluation_router, prefix=settings.API_PREFIX)
app.include_router(sec_router, prefix=settings.API_PREFIX)
app.include_router(retrieval_router, prefix=settings.API_PREFIX)

@app.get("/api/health")
async def health_check():
    """System health check and configuration audit."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "llm_provider": settings.LLM_PROVIDER,
        "guardrail_threshold": settings.GUARDRAIL_CONFIDENCE_THRESHOLD,
        "max_refinement_loops": settings.MAX_REFINEMENT_LOOPS
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
