# Contract Drift Detector

A SaaS contract monitoring system that detects material legal changes using clause-level semantic fingerprinting, orchestrated through n8n workflows.

![System Architecture](./docs/architecture-diagram.png)

## 🎯 Features

- **Multi-format Contract Ingestion**: Upload PDFs, scrape URLs, or paste text
- **Intelligent Clause Segmentation**: Automatically identify and categorize contract clauses
- **Semantic Fingerprinting**: Track changes using TF-IDF + Google Gemini API
- **Drift Detection**: Identify added, removed, modified, and rewritten clauses
- **Risk Classification**: Automatic risk scoring with AI-generated explanations
- **Smart Alerts**: Email (Resend) and Slack notifications for high-risk changes
- **Version History**: Complete audit trail with clause-level diffs

## 🏗️ Architecture

```
User (Web UI)
    ↓
Frontend (Next.js)
    ↓
Backend API (FastAPI)
    ↓
n8n Automation Engine
    ↓
Processing Services → PostgreSQL
```

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 16
- **ORM**: SQLAlchemy + Alembic
- **Frontend**: Next.js 14 + TypeScript
- **Automation**: n8n (self-hosted)
- **NLP**: Google Gemini API + scikit-learn
- **Email**: Resend
- **Package Manager**: pnpm

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- pnpm (`npm install -g pnpm`)

### 1. Clone and Setup

```bash
git clone <repository-url>
cd contract-drifter

# Copy environment variables
cp .env.example .env

# Edit .env and add your API keys:
# - RESEND_API_KEY
# - GEMINI_API_KEY
```

### 2. Start Services

```bash
# Start all services with Docker Compose
docker-compose up -d

# Check service status
docker-compose ps
```

### 3. Initialize Database

```bash
# Run migrations
docker-compose exec backend alembic upgrade head
```

### 4. Access Applications

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **n8n**: http://localhost:5678 (admin/admin123)

## 📁 Project Structure

```
contract-drifter/
├── backend/                 # FastAPI application
│   ├── alembic/            # Database migrations
│   ├── models.py           # SQLAlchemy models
│   ├── schemas.py          # Pydantic schemas
│   ├── routers/            # API endpoints
│   ├── services/           # Business logic
│   │   ├── text_extractor.py
│   │   ├── clause_segmenter.py
│   │   ├── fingerprint_engine.py
│   │   ├── drift_detector.py
│   │   ├── risk_classifier.py
│   │   └── gemini_service.py
│   └── main.py             # Application entry
├── frontend/               # Next.js 16 + React 19
│   ├── src/
│   │   ├── app/           # App router pages
│   │   └── utils/         # Utilities & API client
│   └── Dockerfile.dev     # Development container
├── n8n-workflows/         # n8n workflow definitions
├── docs/                  # Documentation
├── uploads/              # File uploads (gitignored)
├── Makefile              # Development commands
└── docker-compose.yml    # Service orchestration
```

## 🔧 Development

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload
```

### Frontend Development

```bash
cd frontend

# Install dependencies
pnpm install

# Run development server
pnpm dev
```

### Database Migrations

```bash
# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# Apply migrations
docker-compose exec backend alembic upgrade head

# Rollback migration
docker-compose exec backend alembic downgrade -1
```

## 📊 n8n Workflows

Import workflows from `n8n-workflows/` directory:

1. Access n8n at http://localhost:5678
2. Go to **Workflows** → **Import from File**
3. Import each JSON file in order:
   - `01-contract-ingest.json`
   - `02-text-extraction.json`
   - `03-clause-segmentation.json`
   - `04-fingerprint-generation.json`
   - `05-drift-detection.json`
   - `06-risk-scoring.json`
   - `07-alert-dispatch.json`

## 🧪 Testing

```bash
# Backend tests
docker-compose exec backend pytest

# Frontend tests
cd frontend && pnpm test

# E2E tests
cd frontend && pnpm test:e2e
```

## 📖 Documentation

- [Architecture Details](./docs/architecture.md)
- [API Documentation](./docs/api.md)
- [n8n Setup Guide](./docs/n8n-setup.md)

## 🔐 Security Notes

- Never commit `.env` file
- Change default passwords in production
- Use strong `SECRET_KEY` for JWT tokens
- Enable HTTPS in production
- Rotate API keys regularly

## 📝 License

MIT

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines first.

## 📧 Support

For issues and questions, please open a GitHub issue.
