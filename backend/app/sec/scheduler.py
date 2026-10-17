import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from app.models.schemas import SECWatchlistItem, SECWebhookPayload
from app.sec.client import sec_client
from app.sec.parser import sec_parser
from app.orchestrator.runner import runner

logger = logging.getLogger(__name__)

DEFAULT_WATCHLIST: List[Dict[str, str]] = [
    {"ticker": "AAPL", "cik": "0000320193", "company_name": "Apple Inc.", "sector": "Consumer Electronics & Silicon"},
    {"ticker": "NVDA", "cik": "0001045810", "company_name": "NVIDIA Corporation", "sector": "Semiconductors & AI Compute"},
    {"ticker": "MSFT", "cik": "0000789019", "company_name": "Microsoft Corporation", "sector": "Enterprise Software & Cloud"},
    {"ticker": "AMZN", "cik": "0001018724", "company_name": "Amazon.com Inc.", "sector": "E-Commerce & Cloud Infrastructure"},
    {"ticker": "TSLA", "cik": "0001318605", "company_name": "Tesla, Inc.", "sector": "Automotive & Energy Storage"},
    {"ticker": "JPM", "cik": "0000019617", "company_name": "JPMorgan Chase & Co.", "sector": "Commercial & Investment Banking"}
]

class SECWatchlistScheduler:
    """
    Manages institutional watchlists, filing poll schedules, and real-time webhook ingestion.
    """

    def __init__(self):
        self._watchlist: Dict[str, SECWatchlistItem] = {}
        self._recently_ingested: List[Dict[str, Any]] = []
        self._initialize_defaults()

    def _initialize_defaults(self):
        for item in DEFAULT_WATCHLIST:
            self._watchlist[item["ticker"]] = SECWatchlistItem(
                ticker=item["ticker"],
                cik=item["cik"],
                company_name=item["company_name"],
                sector=item["sector"],
                active=True,
                last_checked=datetime.now(timezone.utc).isoformat(),
                last_filing_date="2024-11-01",
                last_accession=None
            )

    def get_watchlist(self) -> List[SECWatchlistItem]:
        return list(self._watchlist.values())

    def add_to_watchlist(self, ticker: str, company_name: Optional[str] = None, sector: Optional[str] = None) -> SECWatchlistItem:
        ticker_clean = ticker.strip().upper()
        cik = sec_client.resolve_cik(ticker_clean)
        name = company_name or f"{ticker_clean} Corp"
        sec = sector or "General Corporate"

        item = SECWatchlistItem(
            ticker=ticker_clean,
            cik=cik,
            company_name=name,
            sector=sec,
            active=True,
            last_checked=datetime.now(timezone.utc).isoformat()
        )
        self._watchlist[ticker_clean] = item
        return item

    def remove_from_watchlist(self, ticker: str) -> bool:
        ticker_clean = ticker.strip().upper()
        if ticker_clean in self._watchlist:
            del self._watchlist[ticker_clean]
            return True
        return False

    async def ingest_filing_document(
        self,
        ticker: Optional[str] = None,
        cik: Optional[str] = None,
        form_type: str = "10-K",
        accession_number: Optional[str] = None,
        primary_document: Optional[str] = None,
        llm_provider: Optional[str] = None,
        inject_hallucination_trap: bool = False
    ) -> Dict[str, Any]:
        """
        End-to-end filing ingestion:
        1. Resolve CIK and look up submissions
        2. Download raw HTM filing from SEC EDGAR Archives
        3. Parse, strip XBRL, format tables into Markdown
        4. Trigger LangGraph Multi-Agent Orchestrator
        """
        # Resolve CIK and ticker
        target_cik = cik
        target_ticker = ticker
        if not target_cik and target_ticker:
            target_cik = sec_client.resolve_cik(target_ticker)
        elif target_cik and not target_ticker:
            target_ticker = sec_client.resolve_ticker(target_cik) or "SEC_FILING"

        if not target_cik:
            raise ValueError("Must provide either a valid ticker symbol or 10-digit CIK")

        # Get submissions history to locate specific filing if accession not provided
        summary = await sec_client.get_submissions(target_cik)
        company_name = summary.company_name

        matched_filing = None
        if accession_number:
            for f in summary.recent_filings:
                if f.accession_number == accession_number:
                    matched_filing = f
                    break
        
        if not matched_filing:
            for f in summary.recent_filings:
                if f.form.upper() == form_type.upper() or f.form.upper().startswith(form_type.upper()):
                    matched_filing = f
                    break

        if not matched_filing:
            # Prefer major periodic reports (10-K, 10-Q, 8-K) over minor filings (Form 4, 144)
            for f in summary.recent_filings:
                if f.form.upper() in ["10-K", "10-Q", "8-K"]:
                    matched_filing = f
                    break

        if not matched_filing and summary.recent_filings:
            matched_filing = summary.recent_filings[0]

        form = matched_filing.form if (matched_filing and matched_filing.form.upper().startswith(form_type.upper())) else form_type
        accession = matched_filing.accession_number if matched_filing else (accession_number or "0000320193-24-000106")
        p_doc = matched_filing.primary_document if matched_filing else (primary_document or f"{target_ticker.lower()}-filing.htm")

        # Fetch raw document
        raw_html = await sec_client.get_filing_document(
            cik=target_cik,
            accession_number=accession,
            primary_document=p_doc
        )

        # Parse and convert to structured orchestrator text
        parsed = sec_parser.parse_document(
            raw_content=raw_html,
            company_name=company_name,
            form_type=form,
            accession_no=accession
        )

        filename = f"SEC_EDGAR_{target_ticker}_{form}_{accession}.txt"
        
        # Launch multi-agent orchestrator job
        job_id = runner.create_job(
            raw_text=parsed["orchestrator_text"],
            filename=filename,
            inject_hallucination_trap=inject_hallucination_trap,
            llm_provider=llm_provider or "simulation"
        )

        # Execute job in background
        asyncio.create_task(runner.run_job(job_id))

        record = {
            "job_id": job_id,
            "ticker": target_ticker,
            "cik": target_cik,
            "company_name": company_name,
            "form": form,
            "accession_number": accession,
            "primary_document": p_doc,
            "tables_extracted": parsed["tables_extracted_count"],
            "sections_found": parsed["sections_found"],
            "status": "queued",
            "ingested_at": datetime.now(timezone.utc).isoformat()
        }
        self._recently_ingested.insert(0, record)
        if len(self._recently_ingested) > 50:
            self._recently_ingested.pop()

        # Update watchlist record
        if target_ticker in self._watchlist:
            self._watchlist[target_ticker].last_checked = datetime.now(timezone.utc).isoformat()
            self._watchlist[target_ticker].last_accession = accession
            if matched_filing:
                self._watchlist[target_ticker].last_filing_date = matched_filing.filing_date

        return record

    async def handle_webhook(self, payload: SECWebhookPayload) -> Dict[str, Any]:
        """Process incoming SEC EDGAR webhook notification and start automated ingestion."""
        logger.info(f"Received SEC webhook event '{payload.event}' for CIK {payload.cik} (form {payload.form})")
        return await self.ingest_filing_document(
            ticker=payload.ticker,
            cik=payload.cik,
            form_type=payload.form,
            accession_number=payload.accession_number,
            primary_document=payload.primary_document
        )

    def get_recent_ingestions(self) -> List[Dict[str, Any]]:
        return self._recently_ingested

sec_scheduler = SECWatchlistScheduler()
