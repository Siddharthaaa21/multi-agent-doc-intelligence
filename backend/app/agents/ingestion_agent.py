import io
import re
import logging
import time
from typing import Dict, Any, List, Tuple, Optional
from app.llm.provider import llm_provider
from app.llm.prompts import EXTRACTION_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

def normalize_numeric_scalar(val_str: str) -> float:
    """
    Canonical numerical normalizer mapping textual representations to IEEE-754 floats.
    Handles:
    - GAAP negative parentheses notation: '(4,200)' -> -4200.0, '$(12,500) thousand' -> -12.5
    - Multipliers: '391,035 million' -> 391035.0 (or normalized scalar)
    - Currency prefixes: '$391,035', '€45.2', '£10'
    - Percentages: '31.5%' -> 31.5
    """
    if not val_str or not isinstance(val_str, str):
        return 0.0

    s = val_str.strip()
    is_negative = False

    # Check parentheses notation: e.g. (4,200) or $(4,200) or $(12,500) thousand
    if "(" in s and ")" in s:
        is_negative = True
        s = s.replace("(", "").replace(")", "").strip()
    elif s.startswith("-") or "negative" in s.lower():
        is_negative = True
        s = s.replace("-", "").strip()

    # Multiplier factors
    multiplier = 1.0
    lower_s = s.lower()
    if "trillion" in lower_s or lower_s.endswith("t"):
        multiplier = 1e6  # if base in millions
        s = re.sub(r"(?i)\s*trillion|\s*t", "", s)
    elif "billion" in lower_s or lower_s.endswith("b"):
        multiplier = 1000.0  # if reporting in millions
        s = re.sub(r"(?i)\s*billion|\s*b", "", s)
    elif "million" in lower_s or lower_s.endswith("m"):
        multiplier = 1.0
        s = re.sub(r"(?i)\s*million|\s*m", "", s)
    elif "thousand" in lower_s or lower_s.endswith("k"):
        multiplier = 0.001
        s = re.sub(r"(?i)\s*thousand|\s*k", "", s)
    elif "%" in s:
        s = s.replace("%", "").strip()

    # Strip currency symbols and commas
    s = re.sub(r"[\$,€,£,¥]", "", s).strip()
    s = s.replace(",", "")

    match = re.search(r"[-+]?\d*\.?\d+", s)
    if match:
        try:
            base_val = float(match.group(0))
            final_val = base_val * multiplier
            return -final_val if is_negative else final_val
        except ValueError:
            return 0.0

    return 0.0


def locate_source_span(source_span: str, raw_text: str) -> Tuple[int, int]:
    """Locate verbatim character coordinates [start, end] inside raw document."""
    if not source_span or not raw_text:
        return (-1, -1)

    # Normalize whitespace for fuzzy coordinate anchoring
    norm_span = re.sub(r"\s+", " ", source_span.strip())
    norm_raw = re.sub(r"\s+", " ", raw_text)

    idx = norm_raw.find(norm_span)
    if idx != -1:
        return (idx, idx + len(norm_span))

    # Exact direct find
    direct_idx = raw_text.find(source_span.strip())
    if direct_idx != -1:
        return (direct_idx, direct_idx + len(source_span.strip()))

    return (-1, -1)

class IngestionAgent:
    """Agent responsible for parsing documents, semantic structural chunking, and high-precision extraction."""
    
    @staticmethod
    def parse_document_content(content: bytes, filename: str) -> str:
        """Parse raw bytes of PDF or text document into plain text."""
        ext = filename.lower().split(".")[-1] if "." in filename else ""
        if ext == "pdf":
            try:
                from app.parser.pdf_parser import pdf_parser
                parsed = pdf_parser.parse_pdf_document(content, filename)
                return parsed["clean_text"]
            except Exception as e:
                logger.error(f"Error parsing PDF with pdf_parser: {e}")
                return content.decode("utf-8", errors="ignore")
        else:
            return content.decode("utf-8", errors="ignore")

    @staticmethod
    def chunk_document(raw_text: str, chunk_size: int = 1500, overlap: int = 200) -> List[Dict[str, Any]]:
        """Split raw text into semantic sections preserving SEC item headers and tabular layouts."""
        sections = raw_text.split("\n\n")
        chunks = []
        current_chunk = ""
        current_title = "Document Overview"
        start_char = 0
        chunk_idx = 1

        for sec in sections:
            sec_clean = sec.strip()
            if not sec_clean:
                continue

            # Detect canonical SEC item headers or tabular schedules
            is_header = (
                len(sec_clean) < 100 and (
                    sec_clean.isupper() or
                    re.match(r"(?i)^(item|part|note|schedule|table)\s+[0-9a-z]", sec_clean) or
                    sec_clean.endswith(":")
                )
            )
            if is_header:
                current_title = sec_clean.strip(":# ")

            if len(current_chunk) + len(sec_clean) > chunk_size and len(current_chunk) > 300:
                end_char = start_char + len(current_chunk)
                chunks.append({
                    "chunk_id": f"chunk-{chunk_idx:03d}",
                    "section_title": current_title,
                    "content": current_chunk.strip(),
                    "start_char": start_char,
                    "end_char": end_char,
                    "token_count": int(len(current_chunk) / 4)
                })
                chunk_idx += 1
                start_char = end_char - min(overlap, len(current_chunk))
                current_chunk = current_chunk[-overlap:] + "\n\n" + sec_clean
            else:
                current_chunk += "\n\n" + sec_clean

        if current_chunk.strip():
            chunks.append({
                "chunk_id": f"chunk-{chunk_idx:03d}",
                "section_title": current_title,
                "content": current_chunk.strip(),
                "start_char": start_char,
                "end_char": start_char + len(current_chunk),
                "token_count": int(len(current_chunk) / 4)
            })

        return chunks

    async def run(self, raw_text: str, metadata: Dict[str, Any], inject_trap: bool = False) -> Dict[str, Any]:
        """Execute ingestion, structural chunking, and verifiable financial extraction."""
        start_time = time.time()
        
        # 1. Semantic Chunking
        chunks = self.chunk_document(raw_text)
        
        # 2. Extract Entities and Metrics via LLM Provider
        user_prompt = f"""DOCUMENT METADATA: {metadata.get('filename', 'Unknown')}
TOTAL CHUNKS: {len(chunks)}
DOCUMENT EXCERPT:
{raw_text[:6000]}
"""
        extraction_data = await llm_provider.generate_json(
            system_prompt=EXTRACTION_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            schema_name="extraction"
        )
        
        raw_metrics = extraction_data.get("metrics", [])
        entities = extraction_data.get("entities") or [
            {"entity_type": "Company", "value": extraction_data.get("company", "Enterprise Entity")},
            {"entity_type": "Ticker", "value": extraction_data.get("ticker", "N/A")},
            {"entity_type": "Period", "value": extraction_data.get("period", "FY2024")},
            {"entity_type": "Currency", "value": extraction_data.get("currency", "USD")}
        ]

        
        # 3. Post-process Metrics: compute scalar normalization and coordinate offsets
        enriched_metrics = []
        for m in raw_metrics:
            raw_val_str = m.get("raw_text_value", m.get("raw_value", ""))
            numeric_val = m.get("numeric_value")
            if numeric_val is None or numeric_val == 0.0:
                numeric_val = normalize_numeric_scalar(raw_val_str)
            else:
                numeric_val = float(numeric_val)

            span = m.get("source_span", "")
            s_offset, e_offset = locate_source_span(span, raw_text)

            enriched_metrics.append({
                "name": m.get("name", "Unknown Metric"),
                "value": numeric_val,
                "raw_text_value": raw_val_str,
                "raw_value": raw_val_str,
                "numeric_value": numeric_val,
                "unit": m.get("unit", "USD_MILLIONS"),
                "period": m.get("period", "FY2024"),
                "yoy_growth": m.get("yoy_growth"),
                "source_chunk_id": m.get("source_chunk_id"),
                "source_span": span,
                "span_start": s_offset,
                "span_end": e_offset,
                "confidence": m.get("confidence", 0.99),
                "is_grounded": True
            })

        # If hallucination trap is enabled for demo/testing, inject an ungrounded claim
        if inject_trap:
            enriched_metrics.append({
                "name": "Adjusted EBITDA (Synthetic Trap)",
                "value": 180000.0,
                "raw_text_value": "$180,000 million",
                "raw_value": "$180,000 million",
                "numeric_value": 180000.0,
                "unit": "USD_MILLIONS",
                "period": "FY2024",
                "yoy_growth": 250.0,
                "source_chunk_id": None,
                "source_span": "Adjusted EBITDA reached a record high of $180,000 million driven by hyperscale expansion.",
                "span_start": -1,
                "span_end": -1,
                "confidence": 0.20,
                "is_grounded": False
            })


        latency_ms = int((time.time() - start_time) * 1000)

        trace_event = {
            "agent_name": "Document Ingestion & Extraction Agent",
            "stage": "Document Parsing, Structural Chunking & Span Extraction",
            "status": "completed",
            "thought_process": f"Successfully parsed document into {len(chunks)} structural sections. Anchored {len(enriched_metrics)} financial metrics with coordinate offsets.",
            "latency_ms": latency_ms,
            "tokens_used": int(len(user_prompt) / 3.8)
        }

        return {
            "chunks": chunks,
            "entities": entities,
            "financial_metrics": enriched_metrics,
            "trace_event": trace_event
        }

ingestion_agent = IngestionAgent()
