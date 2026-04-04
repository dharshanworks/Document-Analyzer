"""Writing style analysis: voice, transitions, complexity, style classification."""

import re
from typing import Any, Dict

from app.utils.text_utils import split_sentences


class StyleAnalyzer:
    def analyze(self, text: str) -> Dict[str, Any]:
        sentences = split_sentences(text)
        words = re.findall(r"\b[\w'-]+\b", text)
        if not words or not sentences:
            return {}

        word_lengths = [len(w) for w in words if re.search(r"[A-Za-z]", w)]
        sent_lengths = [len(re.findall(r"\b[\w'-]+\b", s)) for s in sentences]
        avg_word_len = sum(word_lengths) / len(word_lengths)
        avg_sent_len = sum(sent_lengths) / len(sent_lengths)

        passive_count = self._count_passive_voice(text)
        transition_count = self._count_transitions(text)
        question_count = len(re.findall(r'\?', text))
        exclamation_count = len(re.findall(r'!', text))
        quote_count = len(re.findall(r'["\u201c\u201d]', text)) // 2

        vocabulary_richness = len(set(w.lower() for w in words)) / len(words) * 100

        writing_style = self._classify_writing_style(avg_sent_len, vocabulary_richness, passive_count, transition_count)

        return {
            "writing_style": writing_style,
            "avg_word_length": round(avg_word_len, 2),
            "avg_sentence_length": round(avg_sent_len, 2),
            "passive_voice_instances": passive_count,
            "transition_words": transition_count,
            "questions": question_count,
            "exclamations": exclamation_count,
            "quotes": quote_count,
            "vocabulary_richness": round(vocabulary_richness, 2),
        }

    def _count_passive_voice(self, text: str) -> int:
        passive_patterns = [
            r'\b(is|was|were|been|being|be|am|are)\s+\w+ed\b',
            r'\b(was|were)\s+\w+en\b',
        ]
        count = 0
        for pattern in passive_patterns:
            count += len(re.findall(pattern, text, re.IGNORECASE))
        return count

    def _count_transitions(self, text: str) -> int:
        transitions = [
            'however', 'therefore', 'furthermore', 'moreover', 'consequently',
            'additionally', 'nevertheless', 'meanwhile', 'subsequently', 'accordingly',
            'in addition', 'on the other hand', 'in conclusion', 'as a result',
            'for example', 'in contrast', 'similarly', 'thus', 'hence',
        ]
        lower = text.lower()
        return sum(1 for t in transitions if t in lower)

    def _classify_writing_style(self, avg_sent_len: float, vocab_richness: float,
                                passive: int, transitions: int) -> str:
        if avg_sent_len > 25 and passive > 5:
            return "Academic / Formal"
        elif avg_sent_len < 15 and transitions < 3:
            return "Conversational / Informal"
        elif transitions > 8 and avg_sent_len > 18:
            return "Professional / Business"
        elif avg_sent_len > 20 and vocab_richness > 60:
            return "Technical / Analytical"
        elif avg_sent_len < 12:
            return "Simple / Direct"
        else:
            return "Standard / Mixed"
