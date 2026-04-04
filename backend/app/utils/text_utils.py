"""Text processing utilities: tokenization, sentence splitting, syllable counting."""

import re
from typing import List

STOP_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'is', 'was', 'are', 'were', 'be', 'been',
    'of', 'in', 'to', 'for', 'with', 'by', 'from', 'on', 'at', 'as', 'it', 'this', 'that',
    'these', 'those', 'i', 'you', 'he', 'she', 'they', 'we', 'me', 'my', 'your', 'our', 'their',
    'there', 'here', 'not', 'no', 'yes', 'can', 'could', 'should', 'would', 'will', 'just',
    'than', 'then', 'so', 'do', 'does', 'did', 'doing', 'done', 'have', 'has', 'had',
    'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between',
    'out', 'off', 'over', 'under', 'again', 'further', 'once', 'all', 'each', 'every',
    'both', 'few', 'more', 'most', 'other', 'some', 'such', 'only', 'own', 'same',
    'very', 'also', 'back', 'even', 'still', 'way', 'take', 'come', 'make', 'like',
    'long', 'great', 'little', 'right', 'old', 'big', 'high', 'different', 'small',
    'large', 'next', 'early', 'young', 'important', 'public', 'bad', 'good', 'new',
    'first', 'last', 'long', 'great', 'little', 'own', 'other', 'old', 'right', 'big',
    'high', 'different', 'small', 'large', 'next', 'early', 'young', 'important',
    'public', 'real', 'possible', 'particular', 'special', 'major', 'better', 'best',
    'however', 'therefore', 'because', 'although', 'while', 'whether', 'since',
    'unless', 'until', 'where', 'when', 'why', 'how', 'what', 'which', 'who', 'whom',
}


def tokenize(text: str) -> List[str]:
    tokens = re.findall(r"[A-Za-z]+", text.lower())
    return [t for t in tokens if len(t) > 2 and t not in STOP_WORDS]


def split_sentences(text: str) -> List[str]:
    text = text.replace('\n', ' ').replace('\r', ' ')
    text = re.sub(r'\s+', ' ', text)
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    if not sentences or (len(sentences) == 1 and len(text.split()) < 10):
        return [text.strip()] if text.strip() else []
    return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 3]


def count_syllables(word: str) -> int:
    w = re.sub(r"[^a-zA-Z]", "", word).lower()
    if not w:
        return 0
    vowels = "aeiouy"
    count = 0
    prev_is_vowel = False
    for ch in w:
        is_vowel = ch in vowels
        if is_vowel and not prev_is_vowel:
            count += 1
        prev_is_vowel = is_vowel
    if w.endswith('e') and count > 1:
        count -= 1
    if w.endswith('le') and len(w) > 2 and w[-3] not in vowels:
        count += 1
    return max(1, count)
