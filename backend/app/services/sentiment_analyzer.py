"""Sentiment and tone analysis with TextBlob + rule-based fallback for accuracy."""

import re
from typing import Any, Dict, List

from textblob import TextBlob

POSITIVE_WORDS = {
    'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'awesome',
    'outstanding', 'superb', 'brilliant', 'positive', 'happy', 'joy', 'love',
    'best', 'beautiful', 'perfect', 'impressive', 'successful', 'achievement',
    'benefit', 'advantage', 'growth', 'improve', 'improved', 'improvement',
    'increase', 'increased', 'gain', 'progress', 'profit', 'profitable',
    'opportunity', 'satisfaction', 'satisfied', 'pleased', 'delighted',
    'remarkable', 'exceptional', 'favorable', 'promising', 'thriving',
    'strong', 'robust', 'well', 'better', 'win', 'won', 'victory',
    'recommend', 'recommended', 'valuable', 'effective', 'efficient',
    'innovative', 'leading', 'superior', 'advantageous', 'rewarding',
}

NEGATIVE_WORDS = {
    'bad', 'poor', 'terrible', 'awful', 'horrible', 'worst', 'negative',
    'disappointing', 'disappointed', 'disappoints', 'failure', 'failed', 'fail',
    'loss', 'lost', 'decline', 'declined', 'decrease', 'decreased', 'drop',
    'problem', 'issue', 'concern', 'concerns', 'concerning', 'risk', 'risks',
    'threat', 'threats', 'threatening', 'crisis', 'crises', 'damage', 'damaged',
    'harm', 'harmful', 'hurt', 'hurting', 'worse', 'worsening', 'deteriorate',
    'complaint', 'complaints', 'blame', 'fault', 'wrong', 'error', 'errors',
    'mistake', 'mistakes', 'inadequate', 'insufficient', 'lacking', 'lack',
    'difficult', 'difficulty', 'struggle', 'struggling', 'challenge', 'challenges',
    'unfortunately', 'regret', 'regrettable', 'unacceptable', 'unsatisfactory',
    'deficient', 'inferior', 'weak', 'weakness', 'vulnerable', 'vulnerability',
    'fraud', 'scandal', 'corrupt', 'corruption', 'violation', 'violations',
    'penalty', 'penalties', 'fine', 'fines', 'lawsuit', 'litigation',
}

INTENSIFIERS = {
    'very': 1.5, 'extremely': 2.0, 'highly': 1.8, 'incredibly': 2.0,
    'remarkably': 1.7, 'exceptionally': 1.9, 'quite': 1.3, 'really': 1.4,
    'absolutely': 2.0, 'utterly': 2.0, 'significantly': 1.6, 'substantially': 1.6,
}

NEGATORS = {'not', 'no', 'never', 'neither', 'nobody', 'nothing', 'nowhere',
            "isn't", "aren't", "wasn't", "weren't", "doesn't", "don't", "didn't",
            "won't", "wouldn't", "shouldn't", "couldn't", "can't", "cannot",
            "hardly", "barely", "scarcely", "seldom", "rarely"}


class SentimentAnalyzer:
    def analyze(self, text: str) -> Dict[str, Any]:
        if not text or len(text.strip()) < 5:
            return {"classification": "Neutral", "polarity": 0.0, "subjectivity": 0.0}

        textblob_result = self._textblob_sentiment(text)
        rule_result = self._rule_based_sentiment(text)

        polarity = textblob_result["polarity"]
        rule_polarity = rule_result["polarity"]

        if abs(polarity) < 0.15 and abs(rule_polarity) > 0.2:
            polarity = rule_polarity

        if abs(polarity - rule_polarity) > 0.5:
            polarity = (polarity + rule_polarity) / 2

        subjectivity = textblob_result.get("subjectivity", 0.5)

        sentence_sentiments = []
        try:
            blob = TextBlob(text)
            for sent in blob.sentences:
                sp = sent.sentiment.polarity
                sc = "Positive" if sp > 0.1 else ("Negative" if sp < -0.1 else "Neutral")
                sentence_sentiments.append({"text": str(sent)[:80], "polarity": round(sp, 3), "classification": sc})
        except Exception:
            pass

        classification = "Positive" if polarity > 0.1 else ("Negative" if polarity < -0.1 else "Neutral")

        return {
            "classification": classification,
            "polarity": round(polarity, 4),
            "subjectivity": round(subjectivity, 4),
            "sentence_sentiments": sentence_sentiments[:10],
        }

    def _textblob_sentiment(self, text: str) -> Dict[str, float]:
        try:
            blob = TextBlob(text)
            return {
                "polarity": blob.sentiment.polarity,
                "subjectivity": blob.sentiment.subjectivity,
            }
        except Exception:
            return {"polarity": 0.0, "subjectivity": 0.5}

    def _rule_based_sentiment(self, text: str) -> Dict[str, float]:
        words = re.findall(r"\b[\w']+\b", text.lower())
        if not words:
            return {"polarity": 0.0, "subjectivity": 0.0}

        score = 0.0
        total_weight = 0.0
        negation_active = False
        negation_window = 0

        for i, word in enumerate(words):
            if word in NEGATORS:
                negation_active = True
                negation_window = 3
                continue

            if negation_window > 0:
                negation_window -= 1
                if negation_window == 0:
                    negation_active = False

            multiplier = 1.0
            if i > 0 and words[i - 1] in INTENSIFIERS:
                multiplier = INTENSIFIERS[words[i - 1]]

            if negation_active:
                multiplier *= -0.8

            if word in POSITIVE_WORDS:
                score += multiplier
                total_weight += abs(multiplier)
            elif word in NEGATIVE_WORDS:
                score -= multiplier
                total_weight += abs(multiplier)

        if total_weight == 0:
            return {"polarity": 0.0, "subjectivity": 0.0}

        polarity = score / total_weight
        subjectivity = min(1.0, total_weight / len(words) * 3)

        return {"polarity": round(polarity, 4), "subjectivity": round(subjectivity, 4)}

    def analyze_paragraphs(self, text: str) -> List[Dict[str, Any]]:
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        results = []
        for para in paragraphs:
            result = self.analyze(para)
            results.append({
                "text": para[:120],
                "polarity": result["polarity"],
                "subjectivity": result["subjectivity"],
                "classification": result["classification"],
            })
        return results

    def analyze_tone(self, text: str) -> Dict[str, float]:
        lower = text.lower()
        tone_words = {
            "formal": sum(1 for w in ["therefore", "furthermore", "consequently", "herein", "whereas", "notwithstanding", "pursuant", "hereby", "accordingly", "thus"] if w in lower),
            "informal": sum(1 for w in ["gonna", "wanna", "kinda", "sorta", "yeah", "hey", "cool", "awesome", "stuff", "things"] if w in lower),
            "urgent": sum(1 for w in ["urgent", "immediately", "asap", "critical", "emergency", "deadline", "must", "require", "mandatory", "essential"] if w in lower),
            "cautious": sum(1 for w in ["risk", "caution", "warning", "potential", "possible", "may", "might", "could", "uncertain", "concern"] if w in lower),
            "optimistic": sum(1 for w in ["opportunity", "growth", "success", "improve", "benefit", "positive", "gain", "advantage", "progress", "excellent"] if w in lower),
            "pessimistic": sum(1 for w in ["decline", "loss", "failure", "risk", "threat", "problem", "issue", "concern", "negative", "worse"] if w in lower),
        }
        total = sum(tone_words.values()) or 1
        return {tone: round(count / total, 3) for tone, count in tone_words.items()}
