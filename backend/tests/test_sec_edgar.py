import pytest
import asyncio
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.sec.rate_limiter import SECRateLimiter
from app.sec.client import SECClient, DEFAULT_TICKER_CIK_MAP
from app.sec.parser import SECFilingParser
from app.sec.scheduler import SECWatchlistScheduler
from app.models.schemas import SECWebhookPayload

@pytest.fixture
def client():
    return TestClient(app)

# ------------------------------------------------------------------------------
# 1. Rate Limiter Tests
# ------------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_rate_limiter_burst_and_throttle():
    limiter = SECRateLimiter(rate=5.0, capacity=2.0)
    
    # First 2 requests should have virtually zero wait time
    w1 = await limiter.acquire()
    w2 = await limiter.acquire()
    assert w1 == 0.0
    assert w2 == 0.0
    
    # 3rd request should trigger throttle wait
    w3 = await limiter.acquire()
    assert w3 > 0.0
    assert limiter.throttled_requests >= 1
    
    stats = limiter.get_stats()
    assert stats["total_requests"] == 3
    assert stats["throttled_requests"] >= 1
    assert stats["rate_limit_per_sec"] == 5.0

# ------------------------------------------------------------------------------
# 2. SEC Client Tests
# ------------------------------------------------------------------------------
def test_sec_client_user_agent_and_headers():
    sec_c = SECClient(user_agent="InstitutionalAnalyst team@fund.com")
    headers = sec_c.get_headers("data.sec.gov")
    assert headers["User-Agent"] == "InstitutionalAnalyst team@fund.com"
    assert headers["Host"] == "data.sec.gov"
    assert "gzip" in headers["Accept-Encoding"]

def test_sec_client_cik_resolution():
    sec_c = SECClient()
    # Ticker to 10-digit zero-padded CIK
    assert sec_c.resolve_cik("AAPL") == "0000320193"
    assert sec_c.resolve_cik("NVDA") == "0001045810"
    assert sec_c.resolve_cik("msft") == "0000789019"
    # Raw numeric CIK to zero-padded
    assert sec_c.resolve_cik("320193") == "0000320193"
    assert sec_c.resolve_cik("1045810") == "0001045810"
    
    # Reverse lookup
    assert sec_c.resolve_ticker("0000320193") == "AAPL"

@pytest.mark.asyncio
async def test_sec_client_get_submissions_mocked():
    sec_c = SECClient()
    mock_payload = {
        "cik": "0000320193",
        "entityType": "operating",
        "sic": "3571",
        "name": "Apple Inc.",
        "tickers": ["AAPL"],
        "filings": {
            "recent": {
                "accessionNumber": ["0000320193-24-000106"],
                "filingDate": ["2024-11-01"],
                "reportDate": ["2024-09-28"],
                "form": ["10-K"],
                "primaryDocument": ["aapl-20240928.htm"],
                "primaryDocDescription": ["10-K"],
                "size": [1234567]
            }
        }
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_payload

    with patch("httpx.AsyncClient.get", new=AsyncMock(return_value=mock_resp)):
        summary = await sec_c.get_submissions("AAPL")
        assert summary.ticker == "AAPL"
        assert summary.company_name == "Apple Inc."
        assert len(summary.recent_filings) == 1
        assert summary.recent_filings[0].accession_number == "0000320193-24-000106"
        assert summary.recent_filings[0].form == "10-K"

@pytest.mark.asyncio
async def test_sec_client_backoff_on_429():
    sec_c = SECClient()
    resp_429 = MagicMock()
    resp_429.status_code = 429
    
    resp_200 = MagicMock()
    resp_200.status_code = 200
    resp_200.text = "<html>Filing content</html>"

    with patch("httpx.AsyncClient.get", side_effect=[resp_429, resp_200]):
        async with httpx.AsyncClient() as client:
            resp = await sec_c._fetch_with_backoff(client, "http://mock.sec.gov", {}, max_retries=2)
            assert resp.status_code == 200

# ------------------------------------------------------------------------------
# 3. SEC Filing Parser Tests
# ------------------------------------------------------------------------------
def test_parser_strip_inline_xbrl():
    parser = SECFilingParser()
    raw_html = """
    <ix:header>
        <ix:hidden>Taxonomy Schemas and contexts</ix:hidden>
    </ix:header>
    <div>
        Total Net Sales: <ix:nonFraction contextRef="c1" unitRef="USD" decimals="-6">391035</ix:nonFraction> million.
        Document Form: <ix:nonNumeric contextRef="c2" name="dei:DocumentType">10-K</ix:nonNumeric>
    </div>
    """
    cleaned = parser.strip_inline_xbrl(raw_html)
    assert "Taxonomy Schemas" not in cleaned
    assert "391035" in cleaned
    assert "10-K" in cleaned
    assert "<ix:" not in cleaned

def test_parser_table_to_markdown():
    parser = SECFilingParser()
    table_html = """
    <table>
        <tr><th>Segment</th><th>FY 2024</th><th>FY 2023</th></tr>
        <tr><td>iPhone</td><td>$201,183</td><td>$200,583</td></tr>
        <tr><td>Services</td><td>$96,169</td><td>$85,200</td></tr>
    </table>
    """
    md = parser.parse_html_table_to_markdown(table_html)
    assert md is not None
    assert "| Segment | FY 2024 | FY 2023 |" in md
    assert "| iPhone | $201,183 | $200,583 |" in md
    assert "| Services | $96,169 | $85,200 |" in md

def test_parser_segment_key_items():
    parser = SECFilingParser()
    doc_text = """
    PREAMBLE
    ITEM 1. BUSINESS
    Apple designs and manufactures hardware and software.
    
    ITEM 1A. RISK FACTORS
    Global supply chain and component availability risks.
    
    ITEM 7. MANAGEMENT'S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION
    Revenue grew 2.0% year-over-year.
    """
    sections = parser.segment_key_items(doc_text)
    assert "ITEM 1" in sections
    assert "ITEM 1A" in sections
    assert "ITEM 7" in sections
    assert "Apple designs" in sections["ITEM 1"]
    assert "supply chain" in sections["ITEM 1A"]

# ------------------------------------------------------------------------------
# 4. Watchlist & Scheduler Tests
# ------------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_watchlist_operations():
    scheduler = SECWatchlistScheduler()
    initial_count = len(scheduler.get_watchlist())
    assert initial_count >= 5

    # Add custom ticker
    item = scheduler.add_to_watchlist("GOOGL", "Alphabet Inc.", "Digital Search & Cloud")
    assert item.ticker == "GOOGL"
    assert item.cik == "0001652044"
    assert len(scheduler.get_watchlist()) == initial_count + 1

    # Remove ticker
    removed = scheduler.remove_from_watchlist("GOOGL")
    assert removed is True
    assert len(scheduler.get_watchlist()) == initial_count

@pytest.mark.asyncio
async def test_scheduler_ingest_document_triggers_orchestrator():
    scheduler = SECWatchlistScheduler()
    record = await scheduler.ingest_filing_document(
        ticker="AAPL",
        form_type="10-K",
        llm_provider="simulation"
    )
    assert record["ticker"] == "AAPL"
    assert record["cik"] == "0000320193"
    assert "job_id" in record
    assert record["status"] == "queued"
    assert record["form"] == "10-K"

# ------------------------------------------------------------------------------
# 5. API Route Integration Tests
# ------------------------------------------------------------------------------
def test_api_get_supported_tickers(client):
    response = client.get("/api/sec/tickers")
    assert response.status_code == 200
    tickers = response.json()
    assert any(t["ticker"] == "AAPL" for t in tickers)
    assert any(t["ticker"] == "NVDA" for t in tickers)

def test_api_get_filings_by_ticker(client):
    response = client.get("/api/sec/filings/AAPL")
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "AAPL"
    assert data["cik"] == "0000320193"
    assert len(data["recent_filings"]) > 0

def test_api_ingest_sec_filing_endpoint(client):
    payload = {
        "ticker": "MSFT",
        "form_type": "10-Q",
        "llm_provider": "simulation"
    }
    response = client.post("/api/sec/ingest", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "MSFT"
    assert "job_id" in data
    assert data["status"] == "queued"

def test_api_watchlist_endpoints(client):
    # GET
    res_get = client.get("/api/sec/watchlist")
    assert res_get.status_code == 200
    assert "watchlist" in res_get.json()

    # POST add
    res_add = client.post("/api/sec/watchlist?ticker=TSLA&sector=Automotive")
    assert res_add.status_code == 200
    assert res_add.json()["ticker"] == "TSLA"

    # DELETE
    res_del = client.delete("/api/sec/watchlist/TSLA")
    assert res_del.status_code == 200
    assert res_del.json()["status"] == "removed"

def test_api_webhook_endpoint(client):
    webhook_data = {
        "event": "filing.submitted",
        "cik": "0001045810",
        "ticker": "NVDA",
        "form": "10-Q",
        "accession_number": "0001045810-24-000080",
        "primary_document": "nvda-20240728.htm",
        "filing_date": "2024-08-28"
    }
    response = client.post("/api/sec/webhook", json=webhook_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "processed"
    assert data["result"]["ticker"] == "NVDA"

def test_api_rate_limiter_stats(client):
    response = client.get("/api/sec/rate-limiter/stats")
    assert response.status_code == 200
    stats = response.json()
    assert "rate_limit_per_sec" in stats
    assert stats["rate_limit_per_sec"] == 10.0
