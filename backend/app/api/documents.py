from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List, Dict, Any
from app.config import SAMPLE_DOCS_DIR
from app.agents.ingestion_agent import ingestion_agent

router = APIRouter(prefix="/documents", tags=["Documents"])

SAMPLE_CATALOG = [
    {
        "id": "apple_10k_fy24.txt",
        "title": "Apple Inc. Form 10-K (FY2024)",
        "doc_type": "10-K (Annual Report)",
        "entity": "Apple Inc. (AAPL)",
        "description": "Full-year financial report detailing $94.93B quarterly revenue, 46.2% gross margin, and EU regulatory scrutiny.",
        "size_kb": 2.4
    },
    {
        "id": "nvidia_q2_fy25.txt",
        "title": "NVIDIA Corp Form 10-Q (Q2 FY2025)",
        "doc_type": "10-Q (Quarterly Report)",
        "entity": "NVIDIA Corporation (NVDA)",
        "description": "Q2 earnings report featuring record $30.04B revenue, 75.1% gross margin, and Hopper architecture data center growth.",
        "size_kb": 2.1
    },
    {
        "id": "stripe_series_i_memo.txt",
        "title": "Stripe Inc. Series I Investment Memo",
        "doc_type": "M&A Investment Memo",
        "entity": "Stripe, Inc. (Private)",
        "description": "Confidential growth memo reviewing $1.01T TPV milestone, $1.15B EBITDA, and interchange fee regulatory exposure.",
        "size_kb": 1.9
    },
    {
        "id": "barclays_credit_memo.txt",
        "title": "Barclays Corporate Credit Underwriting Memo",
        "doc_type": "Credit Assessment Memo",
        "entity": "Apex Industrial Holdings Ltd.",
        "description": "Commercial banking facility review for $450M revolving facility with 2.36x leverage ratio and covenant compliance audit.",
        "size_kb": 2.2
    },
    {
        "id": "microsoft_10q_fy25.txt",
        "title": "Microsoft Corp Form 10-Q (Q1 FY2025)",
        "doc_type": "10-Q (Quarterly Report)",
        "entity": "Microsoft Corporation (MSFT)",
        "description": "Quarterly cloud & AI filing detailing $65.59B revenue, $19B infrastructure CapEx, and Intelligent Cloud segment performance.",
        "size_kb": 2.3
    },
    {
        "id": "amazon_10k_fy24.txt",
        "title": "Amazon.com Inc Form 10-K (FY2024)",
        "doc_type": "10-K (Annual Report)",
        "entity": "Amazon.com, Inc. (AMZN)",
        "description": "Annual report covering $620.13B net sales, $105.25B AWS cloud revenues, and $47.7B free cash flow generation.",
        "size_kb": 2.4
    },
    {
        "id": "jpmorgan_credit_memo.txt",
        "title": "JPMorgan Commercial Credit Facility Memo",
        "doc_type": "Credit Assessment Memo",
        "entity": "Titan Logistics & Cold-Chain Corp",
        "description": "Syndicated underwriting brief for $1.2B Senior Secured Facility evaluating 2.39x leverage and 4.65x interest coverage.",
        "size_kb": 2.1
    },
    {
        "id": "tesla_10q_fy24.txt",
        "title": "Tesla Inc Form 10-Q (Q3 2024)",
        "doc_type": "10-Q (Quarterly Report)",
        "entity": "Tesla, Inc. (TSLA)",
        "description": "Q3 operational filing detailing $25.18B revenue, 6.9 GWh energy storage deployment record, and $2.74B free cash flow.",
        "size_kb": 2.2
    },
    {
        "id": "blackstone_real_estate_memo.txt",
        "title": "Blackstone Real Estate Debt Underwriting Memo",
        "doc_type": "Credit Assessment Memo",
        "entity": "BREIT Core-Plus Portfolio",
        "description": "Real estate credit memo for $3.85B logistics asset pool evaluating 50.0% LTV, 2.15x DSCR, and interest rate cap hedging.",
        "size_kb": 2.0
    },
    {
        "id": "snowflake_earnings_transcript.txt",
        "title": "Snowflake Q3 FY2025 Earnings Call Transcript",
        "doc_type": "Earnings Call Transcript",
        "entity": "Snowflake Inc. (SNOW)",
        "description": "Institutional earnings transcript reviewing $900.3M product revenue, 128% Net Revenue Retention, and $5.7B RPO backlog.",
        "size_kb": 1.9
    }
]

@router.get("/samples", response_model=List[Dict[str, Any]])
async def list_sample_documents():
    """List preloaded institutional financial documents available for immediate analysis."""
    return SAMPLE_CATALOG

@router.get("/sample/{filename}")
async def get_sample_content(filename: str):
    """Retrieve raw text content of a sample document."""
    file_path = SAMPLE_DOCS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Sample document not found")
    
    content = file_path.read_text(encoding="utf-8")
    return {
        "filename": filename,
        "content": content,
        "size_bytes": len(content.encode("utf-8"))
    }

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload custom PDF or text document and extract raw content."""
    try:
        content_bytes = await file.read()
        parsed_text = ingestion_agent.parse_document_content(content_bytes, file.filename)
        
        return {
            "filename": file.filename,
            "content": parsed_text,
            "size_bytes": len(content_bytes),
            "preview": parsed_text[:500] + ("..." if len(parsed_text) > 500 else "")
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse document: {str(e)}")
