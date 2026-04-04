# Document Analyzer

A web app that reads PDFs, Word docs, and images, then pulls out summaries, key info, and sentiment. Built for Track 2 of a hackathon.

## What it does

- Upload a PDF, DOCX, or image — it extracts the text automatically
- Generates a summary using TextRank (no external API needed)
- Pulls out names, dates, orgs, money amounts, emails, phone numbers, URLs
- Tells you if the document tone is positive, negative, or neutral
- Gives you a full breakdown: readability scores, writing style, topics, risk flags, and action items

## Tech I used

- **Backend:** Flask (Python)
- **Frontend:** React
- **DB:** SQLite with SQLAlchemy
- **Auth:** JWT + API key
- **OCR:** Tesseract via pytesseract
- **NLP:** TextBlob for sentiment, custom TextRank for summarization, regex-based entity extraction with spaCy fallback

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

The important ones:

| Variable | What it does |
|---|---|
| `API_KEY` | Key for the `/api/document-analyze` endpoint |
| `SECRET_KEY` | Flask session secret |
| `JWT_SECRET_KEY` | JWT signing secret |

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

**Text extraction** — Each format has its own parser. PDFs go through PyPDF2, DOCX through python-docx, and images through Tesseract OCR. I added some image preprocessing (grayscale, thresholding, denoising) to improve OCR accuracy.

**Summarization** — I implemented TextRank from scratch. It builds a graph of sentence similarities and runs PageRank to find the most important sentences. Works well without needing any external LLM API.

**Entity extraction** — spaCy handles the heavy lifting when available, but I also wrote a solid regex fallback that catches names, dates, orgs, amounts, emails, phones, and URLs. Added filters to stop things like "Executive Summary" from showing up as a person's name.

**Sentiment** — TextBlob gives a baseline polarity score, but I layered a rule-based engine on top with about 100 positive/negative words, negation handling ("not good" = negative), and intensifiers ("very good" = stronger). When the two disagree, it averages them out.

## Project layout

```
backend/
├── app/
│   ├── routes/          # Flask blueprints (auth, documents, user)
│   ├── services/        # Analysis logic (summarizer, entities, sentiment, etc.)
│   ├── utils/           # Document parsers and text helpers
│   ├── middleware/      # API key auth
│   ├── models.py        # SQLAlchemy models
│   └── config.py        # App config
└── run.py               # Entry point

frontend/
├── src/
│   ├── components/      # React pages
│   └── hooks/           # Custom hooks
└── server.js            # Express server for SPA routing
```
