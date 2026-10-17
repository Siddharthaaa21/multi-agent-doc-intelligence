import logging
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import List, Optional, Dict, Any

from app.models.schemas import (
    SECCompanySummary,
    SECIngestRequest,
    SECWatchlistItem,
    SECWebhookPayload
)
from app.sec.client import sec_client, DEFAULT_TICKER_CIK_MAP
from app.sec.scheduler import sec_scheduler

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sec", tags=["SEC EDGAR Integration"])

@router.get("/tickers")
async def list_supported_tickers():
    """List pre-mapped institutional tickers and their 10-digit SEC CIKs."""
    return [
        {"ticker": ticker, "cik": cik}
        for ticker, cik in sorted(DEFAULT_TICKER_CIK_MAP.items())
    ]

@router.get("/filings/{identifier}", response_model=SECCompanySummary)
async def get_company_filings(identifier: str):
    """
    Query SEC EDGAR Submissions API for recent 10-K, 10-Q, and 8-K filings.
    Accepts ticker (e.g. 'AAPL', 'NVDA') or numeric CIK (e.g. '0000320193').
    """
    try:
        summary = await sec_client.get_submissions(identifier)
        return summary
    except Exception as e:
        logger.error(f"Error querying SEC filings for {identifier}: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/ingest")
async def ingest_sec_filing(req: SECIngestRequest):
    """
    Ingest an official SEC filing directly from SEC EDGAR:
    - Fetches primary HTML filing document from EDGAR Archives.
    - Strips inline XBRL (iXBRL) and extracts financial tables to Markdown.
    - Initiates LangGraph Multi-Agent Orchestrator pipeline.
    """
    try:
        result = await sec_scheduler.ingest_filing_document(
            ticker=req.ticker,
            cik=req.cik,
            form_type=req.form_type,
            accession_number=req.accession_number,
            primary_document=req.primary_document,
            llm_provider=req.llm_provider,
            inject_hallucination_trap=req.inject_hallucination_trap
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to ingest SEC filing: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"SEC Ingestion failed: {str(e)}")

@router.get("/watchlist")
async def get_watchlist():
    """Retrieve institutional monitored watchlists and recently ingested filings."""
    return {
        "watchlist": sec_scheduler.get_watchlist(),
        "recent_ingestions": sec_scheduler.get_recent_ingestions()
    }

@router.post("/watchlist", response_model=SECWatchlistItem)
async def add_watchlist_ticker(ticker: str = Query(..., description="Ticker symbol e.g. MSFT"), sector: Optional[str] = None):
    """Add a corporate ticker to the institutional SEC EDGAR watchlist."""
    try:
        return sec_scheduler.add_to_watchlist(ticker=ticker, sector=sector)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/watchlist/{ticker}")
async def remove_watchlist_ticker(ticker: str):
    """Remove a ticker from the institutional SEC EDGAR watchlist."""
    removed = sec_scheduler.remove_from_watchlist(ticker)
    if not removed:
        raise HTTPException(status_code=404, detail=f"Ticker '{ticker}' not in watchlist")
    return {"status": "removed", "ticker": ticker.upper()}

@router.post("/webhook")
async def receive_sec_webhook(payload: SECWebhookPayload):
    """Webhook listener for automated SEC EDGAR filing notifications."""
    try:
        result = await sec_scheduler.handle_webhook(payload)
        return {"status": "processed", "result": result}
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rate-limiter/stats")
async def get_rate_limiter_stats():
    """Audit token bucket rate limiter compliance metrics."""
    return sec_client.rate_limiter.get_stats()
