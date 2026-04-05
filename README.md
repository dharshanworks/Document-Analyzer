# Document Analyzer

A full-stack web application that reads PDFs, Word docs, and images, then pulls out summaries, key info, sentiment, and deep insights. Built for Track 2 of a hackathon.

## What it does

- Upload a PDF, DOCX, or image — it extracts the text automatically
- Generates a summary using TextRank (PageRank-based, no external LLM needed)
- Pulls out names, dates, orgs, money amounts, emails, phone numbers, URLs, and locations
- Tells you if the document tone is positive, negative, or neutral
- Gives you a full breakdown: readability scores, writing style, topics, risk flags, and action items
- Persists analysis history with user authentication

## Tech Stack

### Backend
- **Framework:** Flask 3.1 (Python 3.11)
- **Database:** SQLite with SQLAlchemy 3.1
- **Auth:** Flask-JWT-Extended 4.7 + API key middleware
- **OCR:** OCR.space REST API (free, no billing needed)
- **NLP:** TextBlob 0.17 for sentiment, custom TextRank for summarization, regex-based entity extraction
- **Document Parsing:** PyPDF2 3.0, python-docx 1.2, Pillow 12.2
- **Architecture:** Modular services with API versioning (`/api/v1/`)

### Frontend
- **Framework:** React 19
- **Routing:** React Router 7
- **HTTP:** Axios 1.14
- **UI:** Custom CSS with glassmorphism design
- **Server:** Express.js for SPA routing on Render

### Deployment
- **Platform:** Render (backend + frontend)
- **CI/CD:** GitHub → Render auto-deploy

## How to run it locally

### Backend
```bash
cd backend
pip install -r requirements.txt
python run.py
```
API runs on `http://localhost:5000`.

### Frontend
```bash
cd frontend
npm install
npm start
```
App opens on `http://localhost:3000`.

### Env vars
Copy `.env.example` to `.env` in the backend folder:
```bash
cp .env.example .env
```

| Variable | What it does |
|---|---|
| `API_KEY` | Key for the `/api/document-analyze` endpoint |
| `SECRET_KEY` | Flask session secret |
| `JWT_SECRET_KEY` | JWT signing secret |
| `OCR_SPACE_API_KEY` | OCR.space API key for image text extraction |

## API

### Analyze a document
```
POST /api/document-analyze
```

Headers:
```
Content-Type: application/json
x-api-key: your_api_key_here
```

Body:
```json
{
  "fileName": "report.pdf",
  "fileType": "pdf",
  "fileBase64": "<base64-encoded file content>"
}
```

Supported file types: `pdf`, `docx`, `txt`, `jpg`, `jpeg`, `png`, `gif`, `bmp`

Response:
```json
{
  "status": "success",
  "fileName": "report.pdf",
  "summary": "Short summary of the document...",
  "entities": {
    "names": ["John Doe"],
    "dates": ["15 Jan 2024"],
    "organizations": ["Acme Corp"],
    "amounts": ["$50,000"],
    "locations": ["New York"]
  },
  "sentiment": "Positive"
}
```

### Upload a file directly
```
POST /upload
```
Send the file as multipart form-data. No base64 needed.

## How the analysis works

**Text extraction** — Each format has its own parser. PDFs go through PyPDF2, DOCX through python-docx, and images through OCR.space REST API. Layout structure (headings, lists, tables) is preserved through markup.

**Summarization** — TextRank algorithm builds a sentence similarity graph and runs PageRank to find the most important sentences. Works well without needing any external LLM API.

**Entity extraction** — Regex-based extraction with heading-word filtering catches names, dates, orgs, amounts, emails, phones, and URLs. Date normalization and deduplication keep results clean.

**Sentiment** — TextBlob gives a baseline polarity score, layered with a rule-based engine (100+ positive/negative words, negation handling, intensifier weighting). When the two disagree, it averages them out.

**Deep analysis** — Document type classification via weighted term matching, content quality scoring (A-F grade), risk assessment, topic modeling with co-occurrence analysis, and thematic categorization across 8 domains.

## AI Tools Used

| Tool | How I used it |
|---|---|
| **Claude** | Research on NLP techniques, algorithm design, and architecture decisions |
| **Qwen 3.6 Plus Free** | Writing code, debugging, and general development chat |
| **ChatGPT** | Prompt engineering, refining project requirements, and documentation |
| **Perplexity** | Deep research on best practices, API design patterns, and deployment strategies |

## Project layout

```
backend/
├── app/
│   ├── api/v1/            # Versioned API endpoints (auth, documents, user)
│   ├── core/              # Config, extensions, security
│   ├── models/            # SQLAlchemy models (User, Analysis)
│   ├── services/          # Business logic (NLP, summarizer, entities, etc.)
│   ├── utils/             # Document parsers and text helpers
│   └── schemas/           # Validation schemas
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── scripts/               # Deployment and utility scripts
├── requirements.txt
└── run.py                 # Entry point

frontend/
├── src/
│   ├── components/        # React pages and UI components
│   ├── hooks/             # Custom React hooks
│   ├── services/          # API service layer
│   ├── utils/             # Helper functions
│   ├── constants/         # App constants
│   └── styles/            # Global styles
├── public/
├── server.js              # Express server for SPA routing
└── package.json
```
