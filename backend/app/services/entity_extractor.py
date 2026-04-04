"""Entity extraction: NER with spaCy and regex fallback."""

import re
from collections import defaultdict
from typing import Dict, List

from dateutil.parser import parse as parse_date

from app.utils.text_utils import STOP_WORDS

MONTHS = {
    'jan', 'january', 'feb', 'february', 'mar', 'march', 'apr', 'april', 'may', 'jun',
    'june', 'jul', 'july', 'aug', 'august', 'sep', 'sept', 'september', 'oct', 'october',
    'nov', 'november', 'dec', 'december'
}

ORG_SUFFIXES = {
    'ltd', 'inc', 'corp', 'corporation', 'company', 'co', 'co.', 'llc', 'llp', 'pvt', 'pvt.',
    'limited', 'group', 'bank', 'industries', 'services', 'service', 'association',
    'institute', 'university', 'college', 'foundation', 'authority', 'agency', 'bureau',
    'department', 'ministry', 'commission', 'council', 'board', 'committee'
}

HEADING_WORDS = {
    'executive', 'summary', 'introduction', 'conclusion', 'overview', 'abstract',
    'highlights', 'key', 'findings', 'results', 'discussion', 'methodology',
    'references', 'appendix', 'chapter', 'section', 'part', 'volume',
    'report', 'analysis', 'review', 'assessment', 'evaluation', 'recommendations',
    'financial', 'quarterly', 'annual', 'monthly', 'weekly',
    'table', 'figure', 'chart', 'graph', 'diagram',
    'contents', 'index', 'glossary', 'acknowledgments',
    'background', 'objective', 'objectives', 'scope',
    'purpose', 'method', 'methods', 'data', 'approach',
}

TITLE_WORDS = {
    'mr', 'mrs', 'ms', 'dr', 'prof', 'sir', 'madam', 'lord', 'lady',
    'president', 'ceo', 'cto', 'cfo', 'coo', 'vp', 'director', 'manager',
    'chief', 'officer', 'head', 'lead', 'chairman', 'chairperson',
}


class EntityExtractor:
    def __init__(self):
        try:
            import spacy
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                import subprocess
                subprocess.check_call(["python", "-m", "spacy", "download", "en_core_web_sm"])
                self.nlp = spacy.load("en_core_web_sm")
        except ImportError:
            self.nlp = None

    def extract(self, text: str) -> Dict[str, List[str]]:
        entities = self._regex_extract(text)

        if self.nlp:
            try:
                spacy_ents = self._spacy_extract(text)
                entities["names"] = spacy_ents["names"] + entities["names"]
                entities["organizations"] = spacy_ents["organizations"] + entities["organizations"]
                entities["amounts"] = spacy_ents["amounts"] + entities["amounts"]
                spacy_dates = [str(d).strip() for d in spacy_ents["dates"] if not re.fullmatch(r"\d{5,}", str(d).strip())]
                entities["dates"] = spacy_dates + entities["dates"]
            except Exception as e:
                print(f"Spacy NER failed: {e}, using fallback")

        entities = self._clean_entities(entities)
        return entities

    def _spacy_extract(self, text: str) -> Dict[str, List[str]]:
        entities = {"names": [], "dates": [], "organizations": [], "amounts": [], "locations": []}
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                entities["names"].append(ent.text)
            elif ent.label_ == "ORG":
                entities["organizations"].append(ent.text)
            elif ent.label_ == "DATE":
                entities["dates"].append(ent.text)
            elif ent.label_ == "MONEY":
                entities["amounts"].append(ent.text)
            elif ent.label_ in ("GPE", "LOC"):
                entities["locations"].append(ent.text)
        return entities

    def _regex_extract(self, text: str) -> Dict[str, List[str]]:
        entities = {"names": [], "dates": [], "organizations": [], "amounts": [], "emails": [], "phones": [], "urls": [], "locations": []}

        for pattern in [
            r'\d{1,2}[\s\-\/]\w+[\s\-\/]\d{2,4}',
            r'\d{1,2}[\s\-\/]\d{1,2}[\s\-\/]\d{2,4}',
            r'\w+\s+\d{1,2},?\s+\d{4}',
            r'\d{1,2}\w{2}\s+\w+\s+\d{4}',
        ]:
            for candidate in re.findall(pattern, text, re.IGNORECASE):
                try:
                    dt = parse_date(candidate, fuzzy=True, dayfirst=True)
                    entities["dates"].append(dt.strftime("%d %b %Y"))
                except Exception:
                    pass

        for pattern in [
            r'[₹\$£€]\s*[\d,]+(?:\.\d{1,2})?',
            r'(?:Rs\.?|USD|INR|GBP|EUR)\s+[\d,]+(?:\.\d{1,2})?',
            r'[\d,]+(?:\.\d{1,2})?\s*(?:dollars|rupees|pounds|euros)',
        ]:
            entities["amounts"].extend(re.findall(pattern, text, re.IGNORECASE))

        entities["emails"] = list(dict.fromkeys(re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', text)))

        for pattern in [r'\+?\d[\d\s\-\(\)]{7,}\d', r'\(\d{3}\)\s*\d{3}[\-\s]?\d{4}']:
            entities["phones"].extend(re.findall(pattern, text))
        entities["phones"] = list(dict.fromkeys(entities["phones"]))

        entities["urls"] = list(dict.fromkeys(re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', text)))

        words = re.findall(r"\b[A-Za-z][A-Za-z'-]*\b", text)
        for i in range(len(words) - 1):
            w1, w2 = words[i], words[i + 1]
            if w1[0].isupper() and w2[0].isupper() and len(w1) > 2 and len(w2) > 2:
                if w1.lower() in HEADING_WORDS or w2.lower() in HEADING_WORDS:
                    continue
                if w1.lower() in MONTHS or w2.lower() in MONTHS:
                    continue
                if w1.lower() in STOP_WORDS or w2.lower() in STOP_WORDS:
                    continue
                full = f"{w1} {w2}"
                if full not in entities["names"]:
                    entities["names"].append(full)

        for pattern in [r'\b[A-Z][\w&]*(?:\s+[A-Z][\w&]*){0,4}\s*(?:Ltd|Inc|Corp|Corporation|Company|Co\.?|LLC|LLP|Pvt|Limited|Group|Bank|Industries|Services|Association|Institute|University|College|Foundation|Authority|Agency|Bureau|Department|Ministry|Commission|Council|Board|Committee)\b']:
            for m in re.findall(pattern, text, re.IGNORECASE):
                cleaned = " ".join(m.split()).strip()
                if 0 < len(cleaned) <= 90:
                    entities["organizations"].append(cleaned)

        return entities

    def _clean_entities(self, entities: Dict[str, List[str]]) -> Dict[str, List[str]]:
        filtered_names = []
        for n in entities["names"]:
            s = str(n).strip()
            if not s:
                continue
            words_in_name = s.split()
            if len(words_in_name) < 2 or len(words_in_name) > 4:
                continue
            if any(w.lower() in HEADING_WORDS for w in words_in_name):
                continue
            if any(w.lower() in STOP_WORDS for w in words_in_name):
                continue
            if any(w.lower() in MONTHS for w in words_in_name):
                continue
            last = re.sub(r"[^A-Za-z\.]", "", words_in_name[-1]).lower()
            if last in ORG_SUFFIXES:
                continue
            if any(w.lower() in TITLE_WORDS for w in words_in_name):
                continue
            if not all(w[0].isupper() for w in words_in_name):
                continue
            filtered_names.append(s)
        entities["names"] = list(dict.fromkeys(filtered_names))

        raw_dates = list(dict.fromkeys(x for x in entities["dates"] if str(x).strip()))
        normalized = []
        seen = set()
        for d in raw_dates:
            s = str(d).strip()
            if re.fullmatch(r'\d{4}', s):
                norm = s
            elif re.search(r'[A-Za-z]', s):
                try:
                    dt = parse_date(s, fuzzy=True, dayfirst=True)
                    norm = dt.strftime("%d %b %Y")
                except Exception:
                    continue
            else:
                continue
            if norm not in seen:
                seen.add(norm)
                normalized.append(norm)
        entities["dates"] = normalized

        filtered_orgs = []
        for org in entities["organizations"]:
            s = str(org).strip()
            if not s:
                continue
            words = re.findall(r"[A-Za-z]+", s)
            if not words:
                continue
            if any(w.lower() in HEADING_WORDS for w in words):
                continue
            ok = True
            for w in words:
                wl = w.lower()
                if wl in STOP_WORDS or wl in ORG_SUFFIXES:
                    continue
                if not w[0].isupper():
                    ok = False
                    break
            if ok:
                filtered_orgs.append(s)
        entities["organizations"] = list(dict.fromkeys(filtered_orgs))
        entities["amounts"] = list(dict.fromkeys(x for x in entities["amounts"] if str(x).strip()))

        return entities
