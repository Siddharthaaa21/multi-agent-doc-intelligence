import io
import logging
import time
from typing import Dict, Any, List
from app.llm.provider import llm_provider
from app.llm.prompts import EXTRACTION_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

class IngestionAgent:
    """Agent responsible for parsing documents, semantic chunking, and high-precision financial extraction."""
    
    @staticmethod
    def parse_document_content(content: bytes, filename: str) -> str:
        """Parse raw bytes of PDF or text document into plain text."""
        ext = filename.lower().split(".")[-1] if "." in filename else ""
        if ext == "pdf":
            try:
                from pypdf import PdfReader
                reader = PdfReader(io.BytesIO(content))
                text_pages = [page.extract_text() or "" for page in reader.pages]
                return "\n\n--- PAGE BREAK ---\n\n".join(text_pages)
            except Exception as e:
                logger.error(f"Error parsing PDF with pypdf: {e}")
                return content.decode("utf-8", errors="ignore")
        else:
            return content.decode("utf-8", errors="ignore")

    @staticmethod
    def chunk_document(raw_text: str, chunk_size: int = 1500, overlap: int = 200) -> List[Dict[str, Any]]:
        """Split raw text into semantic sections or sliding window chunks with token estimation."""
        # Check for natural section breaks
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

            # Detect potential section headers (short uppercase or capitalized lines)
            if len(sec_clean) < 80 and (sec_clean.isupper() or sec_clean.startswith("Item") or sec_clean.startswith("Note") or sec_clean.endswith(":")):
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
        """Execute ingestion, chunking, and extraction node."""
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
        
        metrics = extraction_data.get("metrics", [])
        
        # If hallucination trap is enabled for demo/testing, inject an ungrounded claim
        if inject_trap:
            metrics.append({
                "name": "Projected TAM (Synthetic Trap)",
                "value": 500.0,
                "raw_text_value": "$500.0 billion",
                "unit": "USD Billion",
                "period": "2030",
                "yoy_growth": 250.0,
                "source_span": "[Synthetically Injected Hallucination Trap]",
                "confidence": 0.20
            })

        latency_ms = int((time.time() - start_time) * 1000)
        
        trace_event = {
            "agent_name": "Ingestion & Extraction Agent",
            "stage": "Document Ingestion & Semantic Extraction",
            "status": "completed",
            "thought_process": f"Parsed document ({len(raw_text)} chars) into {len(chunks)} semantic chunks. Extracted {len(metrics)} key financial metrics with cited raw spans.",
            "latency_ms": latency_ms,
            "tokens_used": int(len(raw_text[:6000]) / 3.8)
        }
        
        return {
            "chunks": chunks,
            "entities": [
                {"entity_type": "Company", "value": extraction_data.get("company", "Enterprise Entity")},
                {"entity_type": "Ticker", "value": extraction_data.get("ticker", "N/A")},
                {"entity_type": "Period", "value": extraction_data.get("period", "FY2024")},
                {"entity_type": "Currency", "value": extraction_data.get("currency", "USD")}
            ],
            "financial_metrics": metrics,
            "trace_event": trace_event
        }

ingestion_agent = IngestionAgent()
