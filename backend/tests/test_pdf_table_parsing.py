import pytest
import io
from fastapi.testclient import TestClient

from app.main import app
from app.parser.pdf_parser import HighFidelityPDFParser, pdf_parser
from app.agents.ingestion_agent import IngestionAgent

@pytest.fixture
def client():
    return TestClient(app)

# ------------------------------------------------------------------------------
# 1. Running Header / Footer Elimination Tests
# ------------------------------------------------------------------------------
def test_running_header_footer_elimination():
    parser = HighFidelityPDFParser()
    headers_and_footers = [
        "Page 14 of 95",
        "  42  ",
        "Table of Contents",
        "Apple Inc. | Form 10-K | 45",
        "CONFIDENTIAL INVESTMENT MEMORANDUM",
        "UNITED STATES SECURITIES AND EXCHANGE COMMISSION",
        "Washington, D.C. 20549"
    ]
    for line in headers_and_footers:
        assert parser.is_running_header_footer(line) is True, f"Failed to detect header/footer: {line}"

    regular_lines = [
        "Total net sales were $391,035 million.",
        "Operating lease liabilities under ASC 842",
        "Item 1A. Risk Factors"
    ]
    for line in regular_lines:
        assert parser.is_running_header_footer(line) is False

def test_zero_hallucinated_rows_from_headers_in_table():
    parser = HighFidelityPDFParser()
    raw_table_with_header_noise = [
        "Apple Inc. | Form 10-K | 45",  # Header noise
        "Page 45 of 95",                 # Footer noise
        "Consolidated Statements of Operations    Twelve Months Ended Sept 28, 2024    Twelve Months Ended Sept 30, 2023",
        "Net sales (1)                           $391,035                             $383,285",
        "Cost of sales                           $210,352                             $214,137",
        "Gross margin                            $180,683                             $169,148",
        "(1) Includes $11,540 million in stock-based compensation expense."
    ]
    
    tbl = parser.parse_table_block(raw_table_with_header_noise, page_num=1)
    assert tbl is not None
    
    # Assert zero header/footer noise rows were parsed into table data rows
    for r in tbl["rows"]:
        for c in r["cells"]:
            assert "Form 10-K" not in c["value"]
            assert "Page 45" not in c["value"]

# ------------------------------------------------------------------------------
# 2. Multi-Period Comparative Table Alignment Tests
# ------------------------------------------------------------------------------
def test_multi_period_comparative_table_100_percent_alignment():
    parser = HighFidelityPDFParser()
    three_period_statement = [
        "Line Item                                FY 2024     FY 2023     FY 2022",
        "Products Net Sales                       $294,866    $298,085    $316,199",
        "Services Net Sales (1)                   $96,169     $85,200     $78,129",
        "Total Net Sales                          $391,035    $383,285    $394,328",
        "Operating Income                         $123,216    $114,301    $119,437",
        "Net Income                               $93,736     $96,995     $99,803",
        "(1) Services segment includes AppleCare, Cloud Services, and Advertising."
    ]

    tbl = parser.parse_table_block(three_period_statement, page_num=1)
    assert tbl is not None
    assert tbl["columns_count"] == 4  # Line Item, 2024, 2023, 2022
    
    # 100% column alignment preservation check across all rows
    for r in tbl["rows"]:
        assert len(r["cells"]) == 4, f"Row index {r['row_idx']} does not have exactly 4 columns"

    # Verify Markdown formatting preserves all 4 columns
    for md_line in tbl["markdown_table"].split("\n"):
        assert md_line.startswith("|") and md_line.endswith("|")
        # 4 columns means 5 pipe separators
        assert md_line.count("|") == 5

# ------------------------------------------------------------------------------
# 3. Footnote Linking & Cross-Referencing Tests
# ------------------------------------------------------------------------------
def test_footnote_detection_and_cross_referencing():
    parser = HighFidelityPDFParser()
    table_with_footnotes = [
        "Financial Indicator (a)                 Reported Value    Target Benchmark",
        "Syndicated Debt Facility (1)            $1,200M           $1,500M",
        "Fixed Charge Coverage (2)               2.85x             2.00x",
        "(1) Refinanced on October 15 with 5-year SOFR + 185 bps floating spread.",
        "(2) Calculated pursuant to Section 6.04 of Credit Agreement."
    ]

    tbl = parser.parse_table_block(table_with_footnotes, page_num=2)
    assert tbl is not None
    assert "1" in tbl["footnotes"]
    assert "2" in tbl["footnotes"]
    assert "SOFR + 185 bps" in tbl["footnotes"]["1"]
    
    # Verify that the debt row links directly to footnote (1)
    debt_row = tbl["rows"][1]
    assert "1" in debt_row["linked_footnotes"]
    assert "SOFR + 185 bps" in debt_row["linked_footnotes"]["1"]

# ------------------------------------------------------------------------------
# 4. Cell Bounding Box Coordinate Retention Tests
# ------------------------------------------------------------------------------
def test_cell_and_table_bounding_box_geometry():
    parser = HighFidelityPDFParser()
    table_lines = [
        "Metric                 Current Period      Prior Period",
        "Free Cash Flow         $47,700M            $32,200M"
    ]
    tbl = parser.parse_table_block(table_lines, page_num=1, y_offset_start=150.0)
    assert tbl is not None
    
    # Check table bounding box: [x0, y0, x1, y1]
    t_box = tbl["bounding_box"]
    assert len(t_box) == 4
    assert t_box[2] > t_box[0]  # x1 > x0
    assert t_box[3] > t_box[1]  # y1 > y0

    # Check cell bounding boxes
    for row in tbl["rows"]:
        for cell in row["cells"]:
            c_box = cell["bounding_box"]
            assert len(c_box) == 4
            assert c_box[2] > c_box[0]
            assert c_box[3] > c_box[1]

# ------------------------------------------------------------------------------
# 5. Ingestion Agent & API Endpoint Integration Tests
# ------------------------------------------------------------------------------
def test_ingestion_agent_parse_document_with_pdf_parser():
    raw_pdf_text = """
    Page 1 of 10
    Consolidated Statements of Operations
    Product Sales      $200,000    $180,000
    Service Sales      $90,000     $80,000
    Page 2 of 10
    """
    clean_text = IngestionAgent.parse_document_content(raw_pdf_text.encode("utf-8"), "financial_report.pdf")
    assert clean_text is not None
    assert "Product Sales" in clean_text
    # Page noise should be stripped
    assert "Page 1 of 10" not in clean_text

def test_api_parse_pdf_endpoint(client):
    fake_pdf_content = b"""
    MICROSOFT CORPORATION FORM 10-Q
    Segment Revenue          Q1 FY25     Q1 FY24
    Intelligent Cloud (1)    $24,100M    $20,300M
    Productivity & Business  $28,300M    $25,600M
    (1) Driven by Azure AI revenue expansion of 33%.
    """
    files = {"file": ("microsoft_q1.pdf", fake_pdf_content, "application/pdf")}
    response = client.post("/api/documents/parse-pdf", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "tables" in data
    assert data["total_tables_extracted"] >= 1
    assert "clean_text" in data
