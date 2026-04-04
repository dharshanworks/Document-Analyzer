"""Deep analysis engine: document classification, risk assessment, content quality, actionable insights."""

import re
from collections import Counter
from typing import Any, Dict, List

from app.utils.text_utils import STOP_WORDS


class DeepAnalyzer:
    def analyze(self, text: str, entities: Dict, sentiment: Dict, statistics: Dict,
                readability: Dict, topics: List, themes: Dict, style: Dict,
                structure: Dict, keywords: List, key_phrases: List,
                summary: str, detailed_summary: str) -> Dict[str, Any]:

        doc_type = self._classify_document_type(text)
        confidence = self._assess_confidence(text, keywords, statistics)
        key_findings = self._generate_key_findings(entities, summary, topics, themes, doc_type)
        risk_flags = self._assess_risks(sentiment, statistics, readability, entities, doc_type)
        action_items = self._generate_action_items(doc_type, entities, risk_flags, themes)
        content_quality = self._score_content_quality(statistics, readability, style, structure)
        audience_fit = self._assess_audience_fit(readability, style, doc_type)
        recommendations = self._generate_recommendations(doc_type, content_quality, audience_fit, risk_flags)

        return {
            "document_type": doc_type,
            "confidence": confidence,
            "executive_summary": summary,
            "detailed_summary": detailed_summary,
            "key_findings": key_findings[:10],
            "risk_flags": risk_flags[:8],
            "recommended_actions": action_items[:10],
            "content_quality": content_quality,
            "audience_fit": audience_fit,
            "recommendations": recommendations,
            "timeline": entities.get("dates", [])[:10],
            "primary_entities": {
                "people": entities.get("names", [])[:10],
                "organizations": entities.get("organizations", [])[:10],
                "locations": entities.get("locations", [])[:10],
                "amounts": entities.get("amounts", [])[:10],
                "emails": entities.get("emails", [])[:5],
                "phones": entities.get("phones", [])[:5],
                "urls": entities.get("urls", [])[:5],
            },
            "topic_signals": {
                "topics": topics[:5],
                "themes": themes,
                "keywords": keywords[:15],
                "key_phrases": key_phrases[:12],
            },
        }

    def _classify_document_type(self, text: str) -> Dict[str, Any]:
        lower_text = text.lower()

        type_scores = {
            "financial": {
                "terms": {"invoice", "amount", "payment", "paid", "due", "balance", "revenue", "cost", "budget", "tax", "total", "price", "profit", "loss", "expense", "income", "salary", "fee", "charge", "refund", "quarterly", "annual", "fiscal", "audit", "dividend", "earnings", "cash flow", "assets", "liabilities", "equity", "margin", "roi", "forecast"},
                "weight": 1.0,
            },
            "legal": {
                "terms": {"agreement", "contract", "clause", "liability", "compliance", "policy", "terms", "party", "obligation", "warranty", "indemnification", "jurisdiction", "arbitration", "termination", "breach", "damages", "confidentiality", "provision", "statute", "regulation", "plaintiff", "defendant", "counsel", "litigation", "settlement", "negligence"},
                "weight": 1.2,
            },
            "technical": {
                "terms": {"api", "server", "model", "analysis", "algorithm", "system", "platform", "pipeline", "database", "framework", "module", "function", "class", "method", "interface", "protocol", "endpoint", "deployment", "infrastructure", "microservice", "docker", "kubernetes", "cloud", "devops", "ci/cd", "repository", "compile", "runtime"},
                "weight": 1.0,
            },
            "medical": {
                "terms": {"patient", "diagnosis", "treatment", "symptom", "medication", "dosage", "prescription", "clinical", "hospital", "doctor", "nurse", "surgery", "therapy", "pharmaceutical", "pathology", "oncology", "cardiology", "neurology", "prognosis", "biopsy", "chronic", "acute", "infection"},
                "weight": 1.2,
            },
            "academic": {
                "terms": {"research", "study", "hypothesis", "methodology", "literature review", "findings", "discussion", "conclusion", "references", "abstract", "peer review", "citation", "thesis", "dissertation", "experiment", "sample size", "statistical", "correlation", "significance"},
                "weight": 1.1,
            },
            "business": {
                "terms": {"strategy", "market", "competitive", "stakeholder", "objective", "milestone", "deliverable", "roi", "kpi", "benchmark", "initiative", "roadmap", "scalability", "synergy", "leverage", "optimize", "value proposition", "brand", "customer", "acquisition"},
                "weight": 1.0,
            },
        }

        scored = {}
        for dtype, config in type_scores.items():
            count = sum(1 for t in config["terms"] if t in lower_text)
            scored[dtype] = round(count * config["weight"], 1)

        primary = max(scored, key=lambda k: scored[k]) if any(scored.values()) else "general"
        secondary_candidates = [(k, v) for k, v in sorted(scored.items(), key=lambda x: x[1], reverse=True) if k != primary and v > 0]
        secondary = secondary_candidates[0][0] if secondary_candidates else None

        return {
            "primary": primary,
            "secondary": secondary,
            "scores": scored,
        }

    def _assess_confidence(self, text: str, keywords: List, statistics: Dict) -> str:
        wc = statistics.get("word_count", 0)
        if len(keywords) >= 8 and wc >= 200:
            return "high"
        elif len(keywords) >= 4 and wc >= 60:
            return "medium"
        else:
            return "low"

    def _generate_key_findings(self, entities: Dict, summary: str, topics: List,
                               themes: Dict, doc_type: Dict) -> List[str]:
        findings = []
        if summary:
            findings.append(f"Summary: {summary}")
        if entities.get("organizations"):
            findings.append(f"Organizations mentioned: {', '.join(entities['organizations'][:4])}")
        if entities.get("names"):
            findings.append(f"Key individuals: {', '.join(entities['names'][:4])}")
        if entities.get("amounts"):
            findings.append(f"Financial figures: {', '.join(entities['amounts'][:4])}")
        if entities.get("dates"):
            findings.append(f"Timeline references: {', '.join(entities['dates'][:5])}")
        if entities.get("emails"):
            findings.append(f"Contact emails: {', '.join(entities['emails'][:3])}")
        if entities.get("phones"):
            findings.append(f"Phone contacts: {', '.join(entities['phones'][:3])}")
        if topics:
            topic_names = [t["topic"] for t in topics[:3]]
            findings.append(f"Primary topics: {', '.join(topic_names)}")
        if themes:
            theme_names = list(themes.keys())
            findings.append(f"Thematic categories: {', '.join(theme_names[:4])}")
        if doc_type.get("secondary"):
            findings.append(f"Document classified as {doc_type['primary'].title()} (secondary: {doc_type['secondary'].title()})")
        return findings

    def _assess_risks(self, sentiment: Dict, statistics: Dict, readability: Dict,
                      entities: Dict, doc_type: Dict) -> List[str]:
        risks = []
        if sentiment.get("classification") == "Negative":
            risks.append("Negative overall tone may indicate disputes, complaints, or adverse conditions.")
        if sentiment.get("subjectivity", 0) > 0.7:
            risks.append("High subjectivity suggests opinion-heavy content; verify factual claims.")
        if statistics.get("word_count", 0) > 5000:
            risks.append("Very large document; critical details may be buried in lengthy content.")
        if statistics.get("word_count", 0) < 50:
            risks.append("Very short document; may lack sufficient context for meaningful analysis.")
        if readability.get("flesch_kincaid_grade") is not None and readability["flesch_kincaid_grade"] > 14:
            risks.append("Very high reading complexity; may be inaccessible to general audiences.")
        if readability.get("flesch_reading_ease") is not None and readability["flesch_reading_ease"] < 30:
            risks.append("Difficult readability score; consider simplifying language for broader comprehension.")
        if not entities.get("dates"):
            risks.append("No temporal references found; document may lack timeline context.")
        if not entities.get("organizations") and not entities.get("names"):
            risks.append("No named entities detected; document may be generic or lack specificity.")
        if doc_type.get("primary") == "legal" and not entities.get("dates"):
            risks.append("Legal document without clear dates; verify effective dates and deadlines.")
        if doc_type.get("primary") == "financial" and not entities.get("amounts"):
            risks.append("Financial document without monetary amounts; verify completeness.")
        return risks

    def _generate_action_items(self, doc_type: Dict, entities: Dict,
                               risks: List, themes: Dict) -> List[str]:
        items = []
        primary = doc_type.get("primary", "general")

        if primary == "financial":
            items.extend([
                "Cross-check all monetary figures against source documents.",
                "Verify payment terms, due dates, and financial obligations.",
                "Review budget allocations and expense categories for accuracy.",
                "Assess financial projections against historical data.",
            ])
        elif primary == "legal":
            items.extend([
                "Review all obligations, liabilities, and compliance requirements.",
                "Verify effective dates, termination clauses, and renewal terms.",
                "Consult legal counsel on ambiguous provisions.",
                "Ensure all parties are correctly identified and authorized.",
            ])
        elif primary == "technical":
            items.extend([
                "Validate technical specifications and implementation requirements.",
                "Review system architecture and integration points.",
                "Assess scalability and performance considerations.",
                "Verify security and data protection measures.",
            ])
        elif primary == "medical":
            items.extend([
                "Verify medical information accuracy against clinical guidelines.",
                "Cross-reference patient data with medical records.",
                "Review treatment protocols for compliance with standards.",
                "Ensure informed consent documentation is complete.",
            ])
        elif primary == "academic":
            items.extend([
                "Verify methodology and data collection procedures.",
                "Review statistical analysis for validity and significance.",
                "Check citations and references for completeness.",
                "Assess conclusions against presented evidence.",
            ])
        elif primary == "business":
            items.extend([
                "Review strategic objectives against current market conditions.",
                "Validate KPIs and performance metrics.",
                "Assess competitive positioning and market analysis.",
                "Review stakeholder alignment and communication plan.",
            ])
        else:
            items.extend([
                "Review document for completeness and accuracy.",
                "Identify key stakeholders and action owners.",
                "Establish timeline for follow-up actions.",
            ])

        if entities.get("dates"):
            items.append("Create a timeline checklist from identified dates and deadlines.")
        if entities.get("emails"):
            items.append("Verify contact information for all identified parties.")
        if risks:
            items.append(f"Address {len(risks)} identified risk flag(s) before finalizing.")

        return items

    def _score_content_quality(self, statistics: Dict, readability: Dict,
                               style: Dict, structure: Dict) -> Dict[str, Any]:
        score = 0
        max_score = 100
        breakdown = {}

        wc = statistics.get("word_count", 0)
        if wc >= 500:
            score += 20
            breakdown["content_length"] = "Excellent"
        elif wc >= 200:
            score += 15
            breakdown["content_length"] = "Good"
        elif wc >= 100:
            score += 10
            breakdown["content_length"] = "Adequate"
        else:
            score += 5
            breakdown["content_length"] = "Limited"

        fre = readability.get("flesch_reading_ease")
        if fre is not None:
            if 60 <= fre <= 70:
                score += 20
                breakdown["readability"] = "Optimal"
            elif 50 <= fre <= 80:
                score += 15
                breakdown["readability"] = "Good"
            elif 30 <= fre <= 90:
                score += 10
                breakdown["readability"] = "Acceptable"
            else:
                score += 5
                breakdown["readability"] = "Needs improvement"

        vocab = statistics.get("vocabulary_richness", 0)
        if vocab >= 50:
            score += 20
            breakdown["vocabulary"] = "Rich"
        elif vocab >= 35:
            score += 15
            breakdown["vocabulary"] = "Good"
        elif vocab >= 20:
            score += 10
            breakdown["vocabulary"] = "Adequate"
        else:
            score += 5
            breakdown["vocabulary"] = "Limited"

        struct_score = structure.get("structure_score", "Unstructured")
        struct_points = {"Well-structured": 20, "Moderately structured": 15, "Partially structured": 10, "Unstructured": 5}
        score += struct_points.get(struct_score, 5)
        breakdown["structure"] = struct_score

        passive = style.get("passive_voice_instances", 0)
        if passive <= 3:
            score += 10
            breakdown["voice"] = "Active"
        elif passive <= 8:
            score += 7
            breakdown["voice"] = "Mixed"
        else:
            score += 3
            breakdown["voice"] = "Passive-heavy"

        transitions = style.get("transition_words", 0)
        if transitions >= 5:
            score += 10
            breakdown["coherence"] = "Strong"
        elif transitions >= 2:
            score += 7
            breakdown["coherence"] = "Moderate"
        else:
            score += 3
            breakdown["coherence"] = "Weak"

        if score >= 80:
            grade = "A"
        elif score >= 65:
            grade = "B"
        elif score >= 50:
            grade = "C"
        elif score >= 35:
            grade = "D"
        else:
            grade = "F"

        return {
            "overall_score": score,
            "max_score": max_score,
            "grade": grade,
            "breakdown": breakdown,
        }

    def _assess_audience_fit(self, readability: Dict, style: Dict, doc_type: Dict) -> Dict[str, Any]:
        fk = readability.get("flesch_kincaid_grade", 0) or 0
        writing_style = style.get("writing_style", "Standard / Mixed")

        audiences = []
        if fk <= 8:
            audiences.append("General public")
        if fk <= 12:
            audiences.append("High school educated")
        if fk <= 14:
            audiences.append("College students")
        if fk <= 16:
            audiences.append("Professionals")
        if fk > 12:
            audiences.append("Subject matter experts")

        if doc_type.get("primary") == "legal":
            audiences.append("Legal professionals")
        elif doc_type.get("primary") == "technical":
            audiences.append("Technical professionals")
        elif doc_type.get("primary") == "medical":
            audiences.append("Healthcare professionals")
        elif doc_type.get("primary") == "financial":
            audiences.append("Financial analysts")

        return {
            "recommended_audiences": audiences if audiences else ["General readers"],
            "reading_level": readability.get("reading_level", "Unknown"),
            "writing_style": writing_style,
            "grade_level": fk,
        }

    def _generate_recommendations(self, doc_type: Dict, content_quality: Dict,
                                  audience_fit: Dict, risks: List) -> List[str]:
        recs = []
        grade = content_quality.get("grade", "C")

        if grade in ("D", "F"):
            recs.append("Consider expanding content and improving structure for better clarity.")
        if grade == "C":
            recs.append("Document is adequate but could benefit from improved organization and detail.")

        if audience_fit.get("grade_level", 0) > 14:
            recs.append("Consider simplifying language for broader audience comprehension.")

        if doc_type.get("primary") == "general":
            recs.append("Add domain-specific terminology to improve classification accuracy.")

        risk_count = len(risks)
        if risk_count > 3:
            recs.append(f"High risk count ({risk_count}); thorough review recommended before distribution.")
        elif risk_count > 0:
            recs.append(f"Address {risk_count} risk flag(s) to improve document quality.")

        if not recs:
            recs.append("Document meets quality standards. Proceed with confidence.")

        return recs
