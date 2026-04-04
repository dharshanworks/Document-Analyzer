"""NLP service coordinator: orchestrates all analysis modules."""

import re
import math
from collections import Counter, defaultdict
from datetime import datetime
from typing import Any, Dict, List, Tuple

from app.services.summarizer import Summarizer
from app.services.entity_extractor import EntityExtractor
from app.services.sentiment_analyzer import SentimentAnalyzer
from app.services.topic_modeler import TopicModeler
from app.services.style_analyzer import StyleAnalyzer
from app.services.structure_analyzer import StructureAnalyzer
from app.services.deep_analyzer import DeepAnalyzer
from app.utils.text_utils import split_sentences, STOP_WORDS


class NLPService:
    def __init__(self):
        self.summarizer = Summarizer()
        self.entity_extractor = EntityExtractor()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.topic_modeler = TopicModeler()
        self.style_analyzer = StyleAnalyzer()
        self.structure_analyzer = StructureAnalyzer()
        self.deep_analyzer = DeepAnalyzer()

    def analyze(self, text: str, file_name: str = "document") -> Dict[str, Any]:
        if not text or len(text.strip()) < 10:
            raise ValueError("Document text is too short for analysis")

        summary = self.summarizer.extract_summary(text, max_sentences=3)
        detailed_summary = self.summarizer.extract_detailed_summary(text, max_sentences=6)
        entities = self.entity_extractor.extract(text)
        sentiment = self.sentiment_analyzer.analyze(text)
        paragraph_sentiments = self.sentiment_analyzer.analyze_paragraphs(text)
        tone = self.sentiment_analyzer.analyze_tone(text)
        statistics = self._compute_statistics(text)
        readability = self._compute_readability(text)
        keywords, key_phrases = self.topic_modeler.extract_keywords_and_phrases(text)
        topics = self.topic_modeler.extract_topics(text, top_n=5)
        themes = self.topic_modeler.extract_themes(text)
        style = self.style_analyzer.analyze(text)
        structure = self.structure_analyzer.analyze(text)
        deep = self.deep_analyzer.analyze(
            text, entities, sentiment, statistics, readability,
            topics, themes, style, structure, keywords, key_phrases,
            summary, detailed_summary
        )

        return {
            "status": "success",
            "fileName": file_name,
            "summary": summary,
            "detailed_summary": detailed_summary,
            "entities": entities,
            "sentiment": sentiment,
            "paragraph_sentiments": paragraph_sentiments[:15],
            "tone": tone,
            "statistics": statistics,
            "readability": readability,
            "keywords": keywords,
            "key_phrases": key_phrases,
            "topics": topics,
            "themes": themes,
            "style": style,
            "structure": structure,
            "deep_analysis": deep,
            "timestamp": datetime.now().isoformat()
        }

    def _compute_statistics(self, text: str) -> Dict[str, Any]:
        lines = [ln for ln in text.splitlines() if ln.strip()]
        sentences = split_sentences(text)
        raw_words = re.findall(r"\b[\w'-]+\b", text)
        word_count = len(raw_words)
        char_count = len(text)
        char_no_spaces = len(text.replace(" ", "").replace("\n", "").replace("\r", "").replace("\t", ""))
        avg_word_len = (sum(len(w) for w in raw_words) / word_count) if word_count else 0.0
        avg_sent_len = (word_count / len(sentences)) if sentences else 0.0
        unique_words = set(w.lower() for w in raw_words)
        vocab_richness = (len(unique_words) / word_count * 100) if word_count else 0.0
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        freq = Counter(w.lower() for w in raw_words)
        for sw in STOP_WORDS:
            freq.pop(sw, None)
        top_terms = [term for term, _ in freq.most_common(15)]
        longest = max(raw_words, key=len) if raw_words else ""
        shortest = min((w for w in raw_words if len(w) > 2), key=len) if raw_words else ""

        return {
            "word_count": word_count,
            "character_count": char_count,
            "character_count_no_spaces": char_no_spaces,
            "line_count": len(lines),
            "paragraph_count": len(paragraphs),
            "sentence_count": len(sentences),
            "average_word_length": round(avg_word_len, 2),
            "average_sentence_length": round(avg_sent_len, 2),
            "unique_words": len(unique_words),
            "vocabulary_richness": round(vocab_richness, 2),
            "longest_word": longest,
            "shortest_word": shortest if len(shortest) > 2 else "",
            "word_frequency": top_terms,
        }

    def _compute_readability(self, text: str) -> Dict[str, Any]:
        from app.utils.text_utils import count_syllables
        sentences = split_sentences(text)
        if not sentences:
            return {"flesch_reading_ease": None, "flesch_kincaid_grade": None, "gunning_fog": None, "smog_index": None}

        words = [w for w in re.findall(r"\b[\w'-]+\b", text) if re.search(r"[A-Za-z]", w)]
        wc = len(words)
        sc = len(sentences)
        if wc == 0:
            return {"flesch_reading_ease": None, "flesch_kincaid_grade": None, "gunning_fog": None, "smog_index": None}

        syllables = sum(count_syllables(w) for w in words)
        wps = wc / sc
        spw = syllables / wc
        fre = 206.835 - 1.015 * wps - 84.6 * spw
        fk = 0.39 * wps + 11.8 * spw - 15.59
        complex_words = sum(1 for w in words if count_syllables(w) >= 3)
        complex_pct = (complex_words / wc) * 100
        gunning = 0.4 * (wps + complex_pct)
        smog = 1.0430 * math.sqrt(complex_words * (30 / sc)) + 3.1291

        if fre >= 90:
            level = "Very Easy (5th grade)"
        elif fre >= 80:
            level = "Easy (6th grade)"
        elif fre >= 70:
            level = "Fairly Easy (7th grade)"
        elif fre >= 60:
            level = "Standard (8th-9th grade)"
        elif fre >= 50:
            level = "Fairly Difficult (10th-12th grade)"
        elif fre >= 30:
            level = "Difficult (College)"
        else:
            level = "Very Difficult (College graduate)"

        return {
            "flesch_reading_ease": round(fre, 2),
            "flesch_kincaid_grade": round(fk, 2),
            "gunning_fog": round(gunning, 2),
            "smog_index": round(smog, 2),
            "reading_level": level,
            "complex_words": complex_words,
            "complex_word_percentage": round(complex_pct, 2),
        }
