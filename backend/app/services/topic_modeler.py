"""Topic modeling and theme extraction using TF-IDF and co-occurrence."""

import math
import re
from collections import Counter, defaultdict
from typing import Dict, List, Tuple

from app.utils.text_utils import tokenize, split_sentences, STOP_WORDS


class TopicModeler:
    def extract_topics(self, text: str, top_n: int = 5) -> List[Dict[str, any]]:
        sentences = split_sentences(text)
        if not sentences:
            return []

        sentence_tokens = [tokenize(s) for s in sentences]
        df = defaultdict(int)
        tf_total = Counter()
        for toks in sentence_tokens:
            for t in set(toks):
                df[t] += 1
            tf_total.update(toks)

        n = len(sentences)
        term_scores = {}
        for term, tf_val in tf_total.items():
            idf = math.log((n + 1) / (df.get(term, 0) + 1)) + 1.0
            term_scores[term] = tf_val * idf

        sorted_terms = sorted(term_scores.items(), key=lambda x: x[1], reverse=True)
        top_terms = sorted_terms[:top_n * 3]

        topics = []
        used = set()
        for term, score in top_terms:
            if term in used:
                continue
            related = self._find_related_terms(term, sentence_tokens, top_terms, used)
            topics.append({
                "topic": term,
                "score": round(score, 3),
                "related_terms": related[:5],
            })
            used.add(term)
            used.update(related)
            if len(topics) >= top_n:
                break

        return topics

    def _find_related_terms(self, seed: str, sentence_tokens: List[List[str]],
                            all_terms: List[Tuple[str, float]], used: set) -> List[str]:
        related = []
        for term, score in all_terms:
            if term in used or term == seed:
                continue
            co_occurs = 0
            for toks in sentence_tokens:
                if seed in toks and term in toks:
                    co_occurs += 1
            if co_occurs > 0:
                related.append(term)
        return related[:5]

    def extract_themes(self, text: str) -> Dict[str, List[str]]:
        lower = text.lower()
        theme_categories = {
            "technology": ["software", "algorithm", "data", "cloud", "api", "system", "platform", "digital", "automation", "ai", "machine learning", "database", "server", "network", "security"],
            "finance": ["revenue", "profit", "cost", "budget", "investment", "market", "stock", "financial", "income", "expense", "tax", "audit", "fund", "capital", "asset"],
            "legal": ["contract", "agreement", "compliance", "regulation", "liability", "clause", "legal", "law", "court", "litigation", "patent", "copyright", "intellectual property"],
            "healthcare": ["patient", "clinical", "treatment", "medical", "health", "hospital", "doctor", "therapy", "diagnosis", "pharmaceutical", "drug", "surgery"],
            "education": ["student", "teacher", "curriculum", "learning", "assessment", "academic", "university", "school", "training", "course", "exam", "degree"],
            "environment": ["climate", "carbon", "emission", "sustainable", "renewable", "pollution", "conservation", "ecosystem", "biodiversity", "green"],
            "human_resources": ["employee", "recruitment", "performance", "salary", "benefits", "workforce", "training", "management", "team", "culture"],
            "operations": ["process", "workflow", "efficiency", "production", "supply chain", "logistics", "quality", "optimization", "delivery", "inventory"],
        }

        detected_themes = {}
        for theme, keywords in theme_categories.items():
            matches = [kw for kw in keywords if kw in lower]
            if matches:
                detected_themes[theme] = matches

        return detected_themes

    def extract_keywords_and_phrases(self, text: str, top_k: int = 15) -> Tuple[List[str], List[str]]:
        sentences = split_sentences(text)
        if not sentences:
            return [], []

        sentence_tokens = [tokenize(s) for s in sentences]
        df = defaultdict(int)
        tf_total = Counter()
        for toks in sentence_tokens:
            for t in set(toks):
                df[t] += 1
            tf_total.update(toks)

        n = len(sentences)
        term_scores = {}
        for term, tf_val in tf_total.items():
            idf = math.log((n + 1) / (df.get(term, 0) + 1)) + 1.0
            term_scores[term] = tf_val * idf
        keywords = [t for t, _ in sorted(term_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]]

        phrase_tf = Counter()
        phrase_df = defaultdict(int)
        for toks in sentence_tokens:
            grams = []
            for ng in (2, 3):
                if len(toks) < ng:
                    continue
                for i in range(len(toks) - ng + 1):
                    g = toks[i:i + ng]
                    if any(tok in STOP_WORDS for tok in g):
                        continue
                    grams.append(" ".join(g))
            for g in set(grams):
                phrase_df[g] += 1
            phrase_tf.update(grams)

        phrase_scores = {}
        for phrase, tf_val in phrase_tf.items():
            idf = math.log((n + 1) / (phrase_df.get(phrase, 0) + 1)) + 1.0
            phrase_scores[phrase] = tf_val * idf
        key_phrases = [p for p, _ in sorted(phrase_scores.items(), key=lambda x: x[1], reverse=True)[:top_k] if len(p) <= 60]

        return keywords, key_phrases
