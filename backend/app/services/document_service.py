"""Document analysis orchestration: extract text -> run NLP -> format output."""

import re
from datetime import datetime

from app.utils.document_parser import extract_text, DocumentParser
from app.services.nlp_service import NLPService

nlp = NLPService()


def _filter_textual_terms(terms):
    if not terms:
        return []
    return [t for t in terms if re.search(r"[A-Za-z]", str(t))]


def analyze_document(file_base64: str, file_type: str, file_name: str) -> dict:
    extracted_text, success = extract_text(file_base64, file_type)
    if not success:
        return {"status": "error", "fileName": file_name, "message": f"Failed to extract text: {extracted_text}"}

    if not extracted_text or len(extracted_text.strip()) < 10:
        return {"status": "error", "fileName": file_name, "message": "No text content found in the document"}

    try:
        file_bytes = __import__('base64').b64decode(file_base64)
        metadata = DocumentParser.get_metadata(file_bytes, file_type)
    except Exception:
        metadata = {}

    result = nlp.analyze(extracted_text, file_name)
    result["metadata"] = metadata
    result["keywords"] = _filter_textual_terms(result.get("keywords", []))
    result["key_phrases"] = _filter_textual_terms(result.get("key_phrases", []))
    return result


def analyze_and_format(file_base64: str, file_type: str, file_name: str) -> dict:
    result = analyze_document(file_base64, file_type, file_name)
    if result.get("status") == "error":
        return result

    analysis = result
    entities = analysis.get("entities", {})
    sentiment_data = analysis.get("sentiment", {})
    if isinstance(sentiment_data, dict):
        sentiment_label = sentiment_data.get("classification", "Neutral")
    else:
        sentiment_label = str(sentiment_data)

    stats = analysis.get("statistics", {})
    read = analysis.get("readability", {})
    deep = analysis.get("deep_analysis", {})
    topics = analysis.get("topics", [])
    themes = analysis.get("themes", {})
    style = analysis.get("style", {})
    structure = analysis.get("structure", {})
    tone = analysis.get("tone", {})
    content_quality = deep.get("content_quality", {})
    audience_fit = deep.get("audience_fit", {})

    extracted_text, success = extract_text(file_base64, file_type)
    text_preview = extracted_text[:500] if success else ""

    metadata = analysis.get("metadata", {})

    report = _generate_report(file_name, analysis, sentiment_data, sentiment_label, stats, read, entities, deep, topics, themes, style, structure, tone, content_quality, audience_fit, metadata)

    return {
        "success": True,
        "filename": file_name,
        "timestamp": datetime.now().isoformat(),
        "text_preview": text_preview,
        "metadata": metadata,
        "analysis": {
            "summary": analysis.get("summary", ""),
            "detailed_summary": analysis.get("detailed_summary", ""),
            "entities": entities,
            "sentiment": sentiment_label,
            "sentiment_detail": sentiment_data if isinstance(sentiment_data, dict) else {},
            "tone": tone,
            "statistics": stats,
            "readability": read,
            "keywords": analysis.get("keywords", []),
            "key_phrases": analysis.get("key_phrases", []),
            "topics": topics,
            "themes": themes,
            "style": style,
            "structure": structure,
            "deep_analysis": deep,
            "content_quality": content_quality,
            "audience_fit": audience_fit,
            "metadata": metadata,
        },
        "report": report.strip(),
    }


def _generate_report(file_name, analysis, sentiment_data, sentiment_label, stats, read, entities, deep, topics, themes, style, structure, tone, content_quality, audience_fit, metadata):
    return f"""
{'='*70}
  DOCUMENT ANALYSIS REPORT
{'='*70}

  File:          {file_name}
  Generated:     {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
  Document Type: {deep.get('document_type', {}).get('primary', 'General').title()}
  Confidence:    {deep.get('confidence', 'N/A').title()}
  Pages:         {metadata.get('page_count', 'N/A')}
  Author:        {metadata.get('author', 'N/A') or 'N/A'}
  Title:         {metadata.get('title', 'N/A') or 'N/A'}

{'─'*70}
  EXECUTIVE SUMMARY
{'─'*70}

  {analysis.get('summary', 'N/A')}

{'─'*70}
  DETAILED SUMMARY
{'─'*70}

  {analysis.get('detailed_summary', 'N/A')}

{'─'*70}
  CONTENT QUALITY
{'─'*70}

  Overall Score:   {content_quality.get('overall_score', 'N/A')}/{content_quality.get('max_score', 'N/A')}
  Grade:           {content_quality.get('grade', 'N/A')}
  Breakdown:
  {'  - '.join(f'{k}: {v}' for k, v in content_quality.get('breakdown', {}).items()) or '  N/A'}

{'─'*70}
  SENTIMENT ANALYSIS
{'─'*70}

  Overall:       {sentiment_label}
  Polarity:      {sentiment_data.get('polarity', 'N/A') if isinstance(sentiment_data, dict) else 'N/A'}
  Subjectivity:  {sentiment_data.get('subjectivity', 'N/A') if isinstance(sentiment_data, dict) else 'N/A'}

  Tone Profile:
  {'  '.join(f'{k}: {v}' for k, v in tone.items()) or '  N/A'}

{'─'*70}
  DOCUMENT STATISTICS
{'─'*70}

  Words:                 {stats.get('word_count', 0):,}
  Characters:            {stats.get('character_count', 0):,}
  Characters (no spaces):{stats.get('character_count_no_spaces', 0):,}
  Sentences:             {stats.get('sentence_count', 0):,}
  Paragraphs:            {stats.get('paragraph_count', 0):,}
  Lines:                 {stats.get('line_count', 0):,}
  Unique Words:          {stats.get('unique_words', 0):,}
  Vocabulary Richness:   {stats.get('vocabulary_richness', 0)}%
  Avg Word Length:       {stats.get('average_word_length', 0)}
  Avg Sentence Length:   {stats.get('average_sentence_length', 0)}

{'─'*70}
  READABILITY METRICS
{'─'*70}

  Flesch Reading Ease:   {read.get('flesch_reading_ease', 'N/A')}
  Flesch-Kincaid Grade:  {read.get('flesch_kincaid_grade', 'N/A')}
  Gunning Fog Index:     {read.get('gunning_fog', 'N/A')}
  SMOG Index:            {read.get('smog_index', 'N/A')}
  Reading Level:         {read.get('reading_level', 'N/A')}
  Complex Words:         {read.get('complex_words', 0)} ({read.get('complex_word_percentage', 0)}%)

{'─'*70}
  WRITING STYLE
{'─'*70}

  Style:             {style.get('writing_style', 'N/A')}
  Passive Voice:     {style.get('passive_voice_instances', 0)} instances
  Transition Words:  {style.get('transition_words', 0)}
  Questions:         {style.get('questions', 0)}
  Exclamations:      {style.get('exclamations', 0)}

{'─'*70}
  DOCUMENT STRUCTURE
{'─'*70}

  Structure Score:   {structure.get('structure_score', 'N/A')}
  Headings:          {len(structure.get('headings', []))}
  Lists:             {structure.get('lists_detected', 0)} items
  Tables:            {structure.get('tables_detected', 0)}
  Sections:          {structure.get('section_count', 0)}
  Has Introduction:  {'Yes' if structure.get('has_abstract_or_intro') else 'No'}
  Has Conclusion:    {'Yes' if structure.get('has_conclusion') else 'No'}
  Has References:    {'Yes' if structure.get('has_references') else 'No'}

{'─'*70}
  TOPICS & THEMES
{'─'*70}

  Topics:
  {'  '.join(f"- {t['topic']} (score: {t['score']})" for t in topics[:5]) or '  None detected'}

  Thematic Categories:
  {'  '.join(f"- {k}: {', '.join(v[:3])}" for k, v in themes.items()) or '  None detected'}

{'─'*70}
  EXTRACTED ENTITIES
{'─'*70}

  Names:          {', '.join(entities.get('names', [])[:10]) or 'None detected'}
  Organizations:  {', '.join(entities.get('organizations', [])[:10]) or 'None detected'}
  Dates:          {', '.join(entities.get('dates', [])[:10]) or 'None detected'}
  Amounts:        {', '.join(entities.get('amounts', [])[:10]) or 'None detected'}
  Emails:         {', '.join(entities.get('emails', [])[:5]) or 'None detected'}
  Phone Numbers:  {', '.join(entities.get('phones', [])[:5]) or 'None detected'}
  URLs:           {', '.join(entities.get('urls', [])[:5]) or 'None detected'}

{'─'*70}
  KEYWORDS & PHRASES
{'─'*70}

  Keywords:       {', '.join(analysis.get('keywords', [])[:15]) or 'None'}
  Key Phrases:    {', '.join(analysis.get('key_phrases', [])[:10]) or 'None'}

{'─'*70}
  DEEP ANALYSIS
{'─'*70}

  Key Findings:
  {'  • ' + chr(10) + '  • '.join(deep.get('key_findings', [])) or '  None'}

  Risk Flags:
  {'  • ' + chr(10) + '  • '.join(deep.get('risk_flags', [])) or '  None'}

  Recommended Actions:
  {'  • ' + chr(10) + '  • '.join(deep.get('recommended_actions', [])) or '  None'}

{'─'*70}
  AUDIENCE FIT
{'─'*70}

  Recommended:     {', '.join(audience_fit.get('recommended_audiences', ['N/A']))}
  Reading Level:   {audience_fit.get('reading_level', 'N/A')}
  Grade Level:     {audience_fit.get('grade_level', 'N/A')}

{'─'*70}
  RECOMMENDATIONS
{'─'*70}

  {'  • ' + chr(10) + '  • '.join(deep.get('recommendations', [])) or '  None'}

{'─'*70}
  TOP WORDS BY FREQUENCY
{'─'*70}

  {', '.join(stats.get('word_frequency', [])[:15]) or 'None'}

{'='*70}
  END OF REPORT
{'='*70}
"""
