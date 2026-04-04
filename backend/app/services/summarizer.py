"""Text summarization: extractive, TF-IDF, and TextRank based summarization."""

import math
from collections import Counter, defaultdict

from app.utils.text_utils import tokenize, split_sentences


class Summarizer:
    @staticmethod
    def extract_summary(text: str, max_sentences: int = 3) -> str:
        if not text or len(text.strip()) < 20:
            return text.strip()
        sentences = split_sentences(text)
        if len(sentences) <= max_sentences:
            return " ".join(sentences)
        return Summarizer._text_rank_summarize(text, max_sentences)

    @staticmethod
    def extract_detailed_summary(text: str, max_sentences: int = 6) -> str:
        return Summarizer._text_rank_summarize(text, max_sentences)

    @staticmethod
    def _tfidf_summarize(text: str, max_sentences: int = 3) -> str:
        sentences = split_sentences(text)
        if not sentences:
            return ""
        if len(sentences) <= max_sentences:
            return " ".join(sentences)

        sentence_tokens = []
        df = defaultdict(int)
        for s in sentences:
            toks = tokenize(s)
            sentence_tokens.append(toks)
            for t in set(toks):
                df[t] += 1

        n = len(sentences)
        idf = {term: math.log((n + 1) / (dfi + 1)) + 1.0 for term, dfi in df.items()}

        scores = []
        for idx, toks in enumerate(sentence_tokens):
            if not toks:
                scores.append((idx, 0.0))
                continue
            tf = Counter(toks)
            score = sum(cnt * idf.get(term, 0.0) for term, cnt in tf.items()) / max(1, len(toks))
            if idx == 0:
                score *= 1.2
            elif idx == len(sentences) - 1:
                score *= 1.1
            scores.append((idx, score))

        num = min(max_sentences, len(sentences))
        top = sorted(scores, key=lambda x: x[1], reverse=True)[:num]
        top_sorted = sorted(top, key=lambda x: x[0])
        return " ".join(sentences[i] for i, _ in top_sorted).strip()

    @staticmethod
    def _text_rank_summarize(text: str, max_sentences: int = 3) -> str:
        sentences = split_sentences(text)
        if not sentences or len(sentences) <= max_sentences:
            return " ".join(sentences) if sentences else ""

        sentence_tokens = [tokenize(s) for s in sentences]
        n = len(sentences)

        similarity_matrix = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                sim = Summarizer._sentence_similarity(sentence_tokens[i], sentence_tokens[j])
                similarity_matrix[i][j] = sim
                similarity_matrix[j][i] = sim

        scores = Summarizer._pagerank(similarity_matrix, damping=0.85, iterations=30)

        scored_sentences = [(i, scores[i]) for i in range(n)]
        scored_sentences.sort(key=lambda x: x[1], reverse=True)

        num = min(max_sentences, n)
        top = scored_sentences[:num]
        top_sorted = sorted(top, key=lambda x: x[0])
        return " ".join(sentences[i] for i, _ in top_sorted).strip()

    @staticmethod
    def _sentence_similarity(tokens_a: list, tokens_b: list) -> float:
        if not tokens_a or not tokens_b:
            return 0.0
        set_a = set(tokens_a)
        set_b = set(tokens_b)
        intersection = set_a & set_b
        if not intersection:
            return 0.0
        log_len_a = math.log(len(tokens_a) + 1)
        log_len_b = math.log(len(tokens_b) + 1)
        return len(intersection) / (log_len_a + log_len_b)

    @staticmethod
    def _pagerank(matrix: list, damping: float = 0.85, iterations: int = 30) -> list:
        n = len(matrix)
        if n == 0:
            return []

        scores = [1.0 / n] * n
        for _ in range(iterations):
            new_scores = [0.0] * n
            for i in range(n):
                for j in range(n):
                    if i == j:
                        continue
                    row_sum = sum(matrix[j])
                    if row_sum > 0:
                        new_scores[i] += matrix[j][i] / row_sum * scores[j]
                new_scores[i] = (1 - damping) + damping * new_scores[i]
            scores = new_scores

        total = sum(scores)
        if total > 0:
            scores = [s / total for s in scores]
        return scores
