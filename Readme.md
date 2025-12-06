# Interactive Fact-Anchor

**A lightweight research companion that finds, ranks, and inserts verifiable evidence for claims — instantly.**

Highlight a sentence or type a claim, click *Find Evidence*, and get short, source-linked snippets you can insert into your draft with one click.

## Why This Exists

Writers, researchers, and editors spend hours hunting for reliable citations. This tool dramatically shortens that research loop by combining sentence-level embeddings with vector search to surface concise, high-quality evidence with full provenance.

**Who should care:**
- Journalists and fact-checkers who need fast, traceable evidence
- Academics and students who want quick access to source sentences and citations
- Product teams building writing/editing tools with verifiable content features
- Engineers looking to learn and ship a full-stack information retrieval + embeddings pipeline

## Core Features

### Highlight-to-Search
Select any sentence in the editor and fetch the top matching evidence snippets from a curated corpus.

### Sentence-Level Provenance
Each result returns the exact sentence, source title, link, confidence score, and a short rationale for why it matched.

### Insert Citation
Insert a formatted in-text citation at the cursor (or append) with one click.

### Local, Audit-Friendly Corpus
Uses a curated set of Wikipedia pages and reputable news RSS feeds. All source text is stored locally for verifiable provenance.

### Fast, Explainable Retrieval
- SBERT embeddings + FAISS vector search 
- Lightweight lexical re-ranking 
- Optional cross-encoder re-ranker
- Target: <1s search latency

### Deployable Stack
Containerized services (frontend, app-backend, ML microservice) for easy local development and cloud deployment.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React App     │    │  Node.js API    │    │ Python ML API   │
│   (Frontend)    │◄──►│   (Backend)     │◄──►│  (Embeddings)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                       ┌─────────────────┐    ┌─────────────────┐
                       │ SQLite/MongoDB  │    │  FAISS Index    │
                       │   (Metadata)    │    │   (Vectors)     │
                       └─────────────────┘    └─────────────────┘
```

**Technology Stack:**
- Frontend: React + TypeScript (contenteditable-based editor)
- App backend: Node.js + Express (API, caching, persistence)
- AI microservice: Python + PyTorch (sentence-transformers) + FastAPI
- Vector store: FAISS (local index)
- Metadata store: SQLite or MongoDB (optional)
- Dev & deploy: Docker / docker-compose; deployable to Render, Railway, or Vercel

## Getting Started

### Prerequisites
- Docker and docker-compose
- Node.js 18+
- Python 3.9+

### Quick Start
```bash
# Clone the repo
git clone https://github.com/yourusername/interactive-fact-anchor.git
cd interactive-fact-anchor

# Start all services
docker-compose up -d

# Index a small seed corpus (Wikipedia + news RSS)
docker-compose exec ml-service python scripts/build_corpus.py

# Open the editor
open http://localhost:3000
```

### Try It Out
1. Type or paste some text into the editor
2. Highlight any sentence you want to fact-check
3. Click "Find Evidence"
4. Review the ranked results with confidence scores
5. Click "Insert Citation" to add a reference

## Evaluation Goals

**Target Metrics:**
- Precision@1: >60% on a 20-claim test set
- Precision@3: >70% on a 20-claim test set
- Search latency: <1s for pre-computed embeddings

**Demo Goal:**
2-minute video showing the complete writer workflow from highlight to citation.

## Configuration

Basic configuration through environment variables:

```bash
# .env
PORT=8000
NODE_ENV=development
DATABASE_URL=sqlite:./data/app.db

# .env.ml  
ML_SERVICE_PORT=8001
MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
FAISS_INDEX_PATH=./data/faiss.index
```

## Development

### Local Development
```bash
# Frontend
cd frontend && npm install && npm run dev

# Backend
cd backend && npm install && npm run dev

# ML Service  
cd ml-service && pip install -r requirements.txt && uvicorn main:app --reload
```

### Adding New Sources
1. Add a crawler in `ml-service/crawlers/`
2. Update corpus config
3. Rebuild the index: `python scripts/build_index.py`

## Deployment

### Simple Deploy Options
- **Railway**: `railway up` (recommended for MVP)
- **Render**: Connect GitHub repo, configure services
- **Self-hosted**: `docker-compose -f docker-compose.prod.yml up`

## Contributing

This is an early-stage project. Contributions welcome!

1. Fork the repo
2. Create a feature branch
3. Make changes and add tests
4. Submit a pull request

**Areas that need help:**
- Additional citation formats (APA, Chicago)
- Mobile-responsive editor improvements
- Performance optimizations
- Documentation improvements

## Project Status

Currently in active development. Building toward first stable release with core highlight-to-search functionality.

## Acknowledgments

- [sentence-transformers](https://github.com/UKPLab/sentence-transformers) for embedding models
- [FAISS](https://github.com/facebookresearch/faiss) for vector similarity search
- The open-source community for foundational tools

---

**Built for writers, researchers, and anyone who values accuracy and transparency.**