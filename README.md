# AI-Powered Document Analysis & Extraction

An intelligent document processing system that extracts, analyses, and summarises content from PDF, DOCX, and image files using AI-powered NLP techniques.

## Tech Stack

- **Backend:** Python 3 / Flask
- **Frontend:** React 19
- **Database:** SQLite (Flask-SQLAlchemy)
- **Authentication:** JWT (Flask-JWT-Extended) + API Key
- **OCR:** Tesseract (pytesseract) with image preprocessing
- **NLP:** spaCy, TextBlob, custom TF-IDF + TextRank summarization
- **Async:** Celery + Redis (optional)

## Features

- **Multi-format support:** PDF, DOCX, TXT, JPG, PNG (via OCR)
- **Layout-aware text extraction:** Preserves headings, lists, tables, and structure
- **AI-powered summarization:** TextRank (PageRank-based) extractive summarization
- **Entity extraction:** Names, dates, organizations, monetary amounts, emails, phones, URLs
- **Sentiment analysis:** Hybrid TextBlob + rule-based engine with negation handling
- **Deep analysis:** Document classification, content quality scoring, risk assessment, topic modeling, thematic categorization

## Setup Instructions

### Prerequisites

- Python 3.10+
- Node.js 18+
- Tesseract OCR installed on your system

### Backend

```bash
cd backend
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python run.py
```

The API will be available at `http://localhost:5000`.

### Frontend

```bash
cd frontend
npm install
npm start
```

The frontend will be available at `http://localhost:3000`.

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

| Variable | Description |
|---|---|
| `API_KEY` | Secret key for API authentication |
| `SECRET_KEY` | Flask secret key |
| `JWT_SECRET_KEY` | JWT signing secret |
| `DATABASE_URL` | Database connection string |
| `DEBUG` | Enable debug mode |

## API Usage

### Authentication

All requests to `/api/document-analyze` require an API key in the header:

```
x-api-key: YOUR_SECRET_API_KEY
```

### Endpoint

```
POST /api/document-analyze
```

### Request

```bash
curl -X POST http://localhost:5000/api/document-analyze \
  -H "Content-Type: application/json" \
  -H "x-api-key: sk_track2_default_key_change_this" \
  -d '{
    "fileName": "sample.pdf",
    "fileType": "pdf",
    "fileBase64": "JVBERi0xLjQKJcfsj6IK..."
  }'
```

### Response

```json
{
  "status": "success",
  "fileName": "sample.pdf",
  "summary": "This document is an invoice issued by ABC Pvt Ltd to Ravi Kumar...",
  "entities": {
    "names": ["Ravi Kumar"],
    "dates": ["10 March 2026"],
    "organizations": ["ABC Pvt Ltd"],
    "amounts": ["₹10,000"]
  },
  "sentiment": "Neutral"
}
```

## Approach

### Data Extraction Strategy

1. **Text Extraction:** Documents are parsed using format-specific extractors (PyPDF2 for PDF, python-docx for DOCX, Tesseract OCR for images). Layout structure (headings, lists, tables) is preserved through markup.

2. **Summarization:** TextRank algorithm builds a sentence similarity graph and applies PageRank to identify the most representative sentences. This produces concise, accurate summaries without any external LLM dependency.

3. **Entity Extraction:** spaCy's NER model (en_core_web_sm) extracts PERSON, ORG, DATE, and MONEY entities. A regex fallback handles emails, phones, URLs, and monetary amounts. Results are cleaned with heading-word filtering and date normalization.

4. **Sentiment Analysis:** Hybrid approach combining TextBlob polarity with a rule-based engine (100+ word lexicons, negation handling, intensifier weighting). When the two methods disagree significantly, results are averaged for robustness.

5. **Deep Analysis:** Document type classification via weighted term matching, content quality scoring (A-F grade), risk assessment, topic modeling with co-occurrence analysis, and thematic categorization across 8 domains.

## Project Structure

```
backend/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── config.py                # Configuration
│   ├── extensions.py            # Flask extensions
│   ├── models.py                # Database models
│   ├── middleware/
│   │   └── auth.py              # API key authentication
│   ├── routes/
│   │   ├── auth.py              # Auth endpoints
│   │   ├── documents.py         # Document analysis endpoint
│   │   └── user.py              # User history/stats
│   ├── services/
│   │   ├── document_service.py  # Orchestration layer
│   │   ├── nlp_service.py       # NLP coordinator
│   │   ├── summarizer.py        # TextRank summarization
│   │   ├── entity_extractor.py  # NER extraction
│   │   ├── sentiment_analyzer.py # Sentiment analysis
│   │   ├── topic_modeler.py     # Topic modeling
│   │   ├── style_analyzer.py    # Writing style analysis
│   │   ├── structure_analyzer.py # Document structure
│   │   └── deep_analyzer.py     # Deep analysis engine
│   └── utils/
│       ├── document_parser.py   # File format parsers
│       └── text_utils.py        # Text processing utilities
├── requirements.txt
├── .env.example
└── run.py
```
