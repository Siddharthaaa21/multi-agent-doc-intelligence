import os
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
SAMPLE_DOCS_DIR = BASE_DIR / "data" / "sample_documents"

class Settings:
    PROJECT_NAME: str = "Multi-Agent Document Intelligence Orchestrator"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # LLM Settings
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    
    # Provider selection: auto-detect if keys exist, default to "simulation"
    @property
    def LLM_PROVIDER(self) -> str:
        explicit = os.getenv("LLM_PROVIDER")
        if explicit in ["openai", "anthropic", "simulation"]:
            return explicit
        if self.OPENAI_API_KEY and len(self.OPENAI_API_KEY.strip()) > 10:
            return "openai"
        if self.ANTHROPIC_API_KEY and len(self.ANTHROPIC_API_KEY.strip()) > 10:
            return "anthropic"
        return "simulation"

    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    
    # Guardrail and Orchestration thresholds
    GUARDRAIL_CONFIDENCE_THRESHOLD: float = float(os.getenv("GUARDRAIL_CONFIDENCE_THRESHOLD", "0.95"))
    MAX_REFINEMENT_LOOPS: int = int(os.getenv("MAX_REFINEMENT_LOOPS", "2"))
    
    # Database Settings (PostgreSQL / Async SQLAlchemy)
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{BASE_DIR}/orchestrator.db")
    
    # SEC EDGAR Settings
    SEC_EDGAR_USER_AGENT: str = os.getenv("SEC_EDGAR_USER_AGENT", "InstitutionalRiskOrchestrator compliance-team@institution.org")
    SEC_EDGAR_RATE_LIMIT: float = float(os.getenv("SEC_EDGAR_RATE_LIMIT", "10.0"))

    # Celery & Redis Distributed Queue Settings
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    CELERY_TASK_ALWAYS_EAGER: bool = os.getenv("CELERY_TASK_ALWAYS_EAGER", "false").lower() in ("true", "1")
    USE_DISTRIBUTED_QUEUE: bool = os.getenv("USE_DISTRIBUTED_QUEUE", "false").lower() in ("true", "1")

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "*"]

settings = Settings()
