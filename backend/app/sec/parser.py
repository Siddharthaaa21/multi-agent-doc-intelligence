import re
import html
import logging
from typing import List, Dict, Any, Tuple, Optional

logger = logging.getLogger(__name__)

class SECFilingParser:
    """
    Parser for SEC EDGAR HTML/iXBRL filing documents:
    - Strips inline XBRL (iXBRL) taxonomies and metadata tags while preserving numeric/text content.
    - Converts HTML tabular statements (Income Statement, Balance Sheet, Cash Flows) into structured Markdown tables.
    - Segments standard statutory SEC items (Item 1, Item 1A Risk Factors, Item 7 MD&A, Item 8 Financials).
    - Preserves exact numeric figures, signs, and units for groundedness verification.
    """

    def __init__(self):
        # Regex patterns for XBRL and HTML cleansing
        self._xbrl_header_pattern = re.compile(r"<ix:header>.*?</ix:header>", re.DOTALL | re.IGNORECASE)
        self._ix_tags_pattern = re.compile(r"</?ix:[a-zA-Z0-9_]+(\s+[^>]*)?>", re.DOTALL | re.IGNORECASE)
        self._xbrl_tags_pattern = re.compile(r"</?xbrl[a-zA-Z0-9_:]*(\s+[^>]*)?>", re.DOTALL | re.IGNORECASE)
        self._script_style_pattern = re.compile(r"<(script|style)[^>]*>.*?</\1>", re.DOTALL | re.IGNORECASE)
        self._comment_pattern = re.compile(r"<!--.*?-->", re.DOTALL)
        self._table_pattern = re.compile(r"<table[^>]*>(.*?)</table>", re.DOTALL | re.IGNORECASE)
        self._tr_pattern = re.compile(r"<tr[^>]*>(.*?)</tr>", re.DOTALL | re.IGNORECASE)
        self._cell_pattern = re.compile(r"<(?:td|th)[^>]*>(.*?)</(?:td|th)>", re.DOTALL | re.IGNORECASE)
        self._tag_pattern = re.compile(r"<[^>]+>")

        # SEC Item Section Patterns
        self._item_patterns = {
            "ITEM 1": re.compile(r"(?:ITEM\s+1\b[.:\s]|Item\s+1\b[.:\s])(?!\s*A\b)", re.IGNORECASE),
            "ITEM 1A": re.compile(r"(?:ITEM\s+1A\b[.:\s]|Item\s+1A\b[.:\s])(?:\s*[-–—:]*\s*RISK\s+FACTORS)?", re.IGNORECASE),
            "ITEM 7": re.compile(r"(?:ITEM\s+7\b[.:\s]|Item\s+7\b[.:\s])(?:\s*[-–—:]*\s*MANAGEMENT['’]S\s+DISCUSSION)?", re.IGNORECASE),
            "ITEM 8": re.compile(r"(?:ITEM\s+8\b[.:\s]|Item\s+8\b[.:\s])(?:\s*[-–—:]*\s*FINANCIAL\s+STATEMENTS)?", re.IGNORECASE),
        }

    def strip_inline_xbrl(self, raw_html: str) -> str:
        """Strip iXBRL headers and wrapper tags while retaining values."""
        # 1. Remove ix:header entirely (contains machine schemas, not text)
        cleaned = self._xbrl_header_pattern.sub("", raw_html)
        # 2. Strip comment blocks
        cleaned = self._comment_pattern.sub("", cleaned)
        # 3. Strip script and style blocks
        cleaned = self._script_style_pattern.sub("", cleaned)
        # 4. Strip <ix:...> tags but retain inner values (e.g. <ix:nonFraction ...>391,035</ix:nonFraction>)
        cleaned = self._ix_tags_pattern.sub("", cleaned)
        cleaned = self._xbrl_tags_pattern.sub("", cleaned)
        return cleaned

    def parse_html_table_to_markdown(self, table_html: str) -> Optional[str]:
        """Convert an individual HTML financial table into a clean Markdown table."""
        rows_data: List[List[str]] = []
        for tr_match in self._tr_pattern.finditer(table_html):
            tr_content = tr_match.group(1)
            row_cells: List[str] = []
            for cell_match in self._cell_pattern.finditer(tr_content):
                cell_raw = cell_match.group(1)
                # Strip nested HTML tags
                text = self._tag_pattern.sub(" ", cell_raw)
                text = html.unescape(text)
                text = re.sub(r"\s+", " ", text).strip()
                if text:
                    row_cells.append(text)
            
            # Avoid empty or single-character spacer rows
            filtered_cells = [c for c in row_cells if c not in ["$", "—", "–", ""]]
            if filtered_cells:
                rows_data.append(filtered_cells)

        if len(rows_data) < 2:
            return None

        # Determine column width (normalize to most frequent row length >= 2)
        lengths = [len(r) for r in rows_data]
        max_cols = max(lengths)
        if max_cols < 2:
            return None

        # Normalize rows to max_cols
        normalized_rows: List[List[str]] = []
        for r in rows_data:
            if len(r) == max_cols:
                normalized_rows.append(r)
            elif len(r) > max_cols:
                normalized_rows.append(r[:max_cols])
            elif len(r) > 1:
                # Pad row
                normalized_rows.append(r + [""] * (max_cols - len(r)))

        if len(normalized_rows) < 2:
            return None

        header = normalized_rows[0]
        markdown_lines = [
            "| " + " | ".join(header) + " |",
            "| " + " | ".join([":---"] * max_cols) + " |"
        ]
        for row in normalized_rows[1:]:
            markdown_lines.append("| " + " | ".join(row) + " |")

        return "\n".join(markdown_lines)

    def extract_and_convert_tables(self, html_content: str) -> Tuple[str, List[str]]:
        """
        Extract tables, replace in text with structured table placeholders,
        and collect converted markdown tables.
        """
        markdown_tables: List[str] = []
        table_counter = 1

        def replace_table(match: re.Match) -> str:
            nonlocal table_counter
            tbl_html = match.group(0)
            md = self.parse_html_table_to_markdown(tbl_html)
            if md:
                markdown_tables.append(md)
                table_placeholder = f"\n\n[FINANCIAL STATEMENT TABLE {table_counter}]\n{md}\n\n"
                table_counter += 1
                return table_placeholder
            else:
                # If table is layout only, return plain text inside
                inner_text = self._tag_pattern.sub(" ", tbl_html)
                return " " + inner_text + " "

        processed_html = self._table_pattern.sub(replace_table, html_content)
        return processed_html, markdown_tables

    def clean_text(self, text: str) -> str:
        """Strip remaining HTML tags, unescape entities, and clean spacing."""
        text = self._tag_pattern.sub(" ", text)
        text = html.unescape(text)
        # Normalize non-breaking spaces and line wraps
        text = text.replace("\xa0", " ")
        # Reduce multiple spaces while preserving paragraphs
        lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]
        # Group empty lines
        cleaned_text = "\n".join(lines)
        cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text)
        return cleaned_text.strip()

    def segment_key_items(self, text: str) -> Dict[str, str]:
        """Split text into primary SEC items (Item 1, 1A, 7, 8)."""
        sections: Dict[str, str] = {}
        positions: List[Tuple[str, int]] = []

        for item_name, pattern in self._item_patterns.items():
            matches = list(pattern.finditer(text))
            if matches:
                # If there are multiple matches (e.g. Table of Contents vs Actual Content),
                # pick the match further down if the first is in the first 5000 chars
                chosen_match = matches[-1] if len(matches) > 1 and matches[0].start() < 5000 else matches[0]
                positions.append((item_name, chosen_match.start()))

        positions.sort(key=lambda x: x[1])

        for i, (name, pos) in enumerate(positions):
            next_pos = positions[i + 1][1] if i + 1 < len(positions) else len(text)
            sections[name] = text[pos:next_pos].strip()

        return sections

    def parse_document(
        self,
        raw_content: str,
        company_name: str = "Company",
        form_type: str = "10-K",
        accession_no: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        High-level parser converting raw SEC EDGAR HTML/text into orchestrator-ready document payload.
        """
        # 1. Strip iXBRL
        no_xbrl = self.strip_inline_xbrl(raw_content)
        
        # 2. Extract and format financial tables
        with_md_tables, extracted_tables = self.extract_and_convert_tables(no_xbrl)
        
        # 3. Clean full text
        clean_doc_text = self.clean_text(with_md_tables)
        
        # 4. Extract statutory items
        sections = self.segment_key_items(clean_doc_text)

        # 5. Format unified orchestrator text
        header = f"""================================================================================
UNITED STATES SECURITIES AND EXCHANGE COMMISSION (SEC EDGAR INGESTION)
COMPANY: {company_name.upper()}
FILING FORM: {form_type.upper()}
ACCESSION NUMBER: {accession_no or 'N/A'}
INGESTION PROTOCOL: SEC EDGAR Submissions API v1.0
================================================================================
"""
        orchestrator_text = header + "\n" + clean_doc_text

        return {
            "orchestrator_text": orchestrator_text,
            "char_count": len(orchestrator_text),
            "tables_extracted_count": len(extracted_tables),
            "tables": extracted_tables,
            "sections_found": list(sections.keys()),
            "sections": sections
        }

sec_parser = SECFilingParser()
