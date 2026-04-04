"""Document structure analysis: headings, sections, lists, tables detection."""

import re
from typing import Any, Dict, List


class StructureAnalyzer:
    def analyze(self, text: str) -> Dict[str, Any]:
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        lines = [ln for ln in text.splitlines() if ln.strip()]

        headings = self._detect_headings(text)
        lists_found = self._detect_lists(text)
        tables_found = self._detect_tables(text)
        section_count = self._count_sections(text)
        avg_paragraph_length = self._avg_paragraph_length(paragraphs)
        paragraph_length_variance = self._paragraph_length_variance(paragraphs)
        has_abstract = bool(re.search(r'\b(abstract|executive summary|overview|introduction)\b', text[:1000], re.IGNORECASE))
        has_conclusion = bool(re.search(r'\b(conclusion|summary|closing|final remarks|recommendations)\b', text[-2000:], re.IGNORECASE))
        has_references = bool(re.search(r'\b(references|bibliography|works cited|sources|citations)\b', text, re.IGNORECASE))
        has_appendix = bool(re.search(r'\b(appendix|annex|supplementary)\b', text, re.IGNORECASE))

        return {
            "headings": headings[:20],
            "lists_detected": lists_found,
            "tables_detected": tables_found,
            "section_count": section_count,
            "paragraph_count": len(paragraphs),
            "line_count": len(lines),
            "avg_paragraph_length": round(avg_paragraph_length, 1),
            "paragraph_length_variance": round(paragraph_length_variance, 1),
            "has_abstract_or_intro": has_abstract,
            "has_conclusion": has_conclusion,
            "has_references": has_references,
            "has_appendix": has_appendix,
            "structure_score": self._score_structure(has_abstract, has_conclusion, has_references, section_count, len(headings)),
        }

    def _detect_headings(self, text: str) -> List[str]:
        headings = []
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if re.match(r'^#{1,6}\s+', stripped):
                headings.append(stripped.lstrip('#').strip())
            elif len(stripped) < 100 and stripped.isupper() and len(stripped.split()) <= 10:
                headings.append(stripped)
            elif re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*$', stripped) and len(stripped.split()) <= 6:
                if not stripped.endswith('.'):
                    headings.append(stripped)
        return headings

    def _detect_lists(self, text: str) -> int:
        patterns = [
            r'^\s*[\-\*\u2022]\s+',
            r'^\s*\d+[\.\\)]\s+',
            r'^\s*[a-z][\.\\)]\s+',
        ]
        count = 0
        for line in text.splitlines():
            for pattern in patterns:
                if re.match(pattern, line, re.MULTILINE):
                    count += 1
                    break
        return count

    def _detect_tables(self, text: str) -> int:
        count = 0
        in_table = False
        for line in text.splitlines():
            if '|' in line and line.count('|') >= 2:
                if not in_table:
                    count += 1
                    in_table = True
            else:
                in_table = False
        return count

    def _count_sections(self, text: str) -> int:
        section_markers = [
            r'\b(section|chapter|part|article)\s+\d+',
            r'\b\d+\.\s+[A-Z]',
            r'^#{1,3}\s+',
        ]
        count = 0
        for pattern in section_markers:
            count += len(re.findall(pattern, text, re.MULTILINE | re.IGNORECASE))
        return max(1, count)

    def _avg_paragraph_length(self, paragraphs: list) -> float:
        if not paragraphs:
            return 0.0
        lengths = [len(p.split()) for p in paragraphs]
        return sum(lengths) / len(lengths)

    def _paragraph_length_variance(self, paragraphs: list) -> float:
        if len(paragraphs) < 2:
            return 0.0
        lengths = [len(p.split()) for p in paragraphs]
        avg = sum(lengths) / len(lengths)
        variance = sum((l - avg) ** 2 for l in lengths) / len(lengths)
        return variance

    def _score_structure(self, has_abstract: bool, has_conclusion: bool,
                         has_references: bool, section_count: int, heading_count: int) -> str:
        score = 0
        if has_abstract:
            score += 2
        if has_conclusion:
            score += 2
        if has_references:
            score += 1
        if section_count >= 3:
            score += 2
        if heading_count >= 3:
            score += 1
        if score >= 6:
            return "Well-structured"
        elif score >= 4:
            return "Moderately structured"
        elif score >= 2:
            return "Partially structured"
        else:
            return "Unstructured"
