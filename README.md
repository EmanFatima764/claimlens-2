# ClaimLens 2.0 - Multi-Agent Evidence Intelligence Platform

## Overview

ClaimLens 2.0 is a sophisticated evidence-intelligence platform that uses a multi-agent AI system to verify factual claims through automated research, source evaluation, evidence extraction, and conflict analysis.

### Key Capabilities

- **Multi-Agent Orchestration**: 8 specialized AI agents working in sequence
- **Evidence Research**: Automated web search and source collection
- **Source Credibility**: Quality scoring and bias detection
- **Evidence Extraction**: Intelligent fact extraction from sources
- **Conflict Detection**: Identification of contradicting evidence
- **Uncertainty Quantification**: Confidence and uncertainty scoring
- **Evidence Visualization**: Graph-based evidence relationships

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                      │
│              (Investigation + Report Pages)                │
└────────────────────────┬────────────────────────────────────┘
                         │
                    HTTP / REST
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    Backend (FastAPI)                        │
│                                                             │
│  API Routes ──► Services ──► Workflow Orchestrator         │
│                                                             │
│  ┌──────────────────────────────────────────────────┐     │
│  │  Investigation Workflow Graph (LangGraph-style)  │     │
│  │                                                  │     │
│  │  Claim ──► Research ──► Sources ──► Evidence    │     │
│  │     │            │                      │       │     │
│  │     └────────────┴──────────────────────┘       │     │
│  │                                                  │     │
│  │  Verification ──► Conflicts ──► Independence    │     │
│  │                                       │          │     │
│  │  Verdict ◄────────────────────────────┘         │     │
│  │                                                  │     │
│  │  [8 AI Agents + External Integrations]         │     │
│  └──────────────────────────────────────────────────┘     │
│                                                             │
│  Repositories ──► Supabase PostgreSQL                      │
│                                                             │
│  Integrations: Gemini, Anthropic, Tavily, Whisper        │
└────────────────────────┬────────────────────────────────────┘
                         │
              PostgreSQL / REST API
                         │
┌────────────────────────▼────────────────────────────────────┐
│              Supabase (Database + Auth)                    │
│         investigations │ claims │ sources │ evidence       │
│                      verdicts │ conflicts                  │
└─────────────────────────────────────────────────────────────┘
```

### Agent Workflow

1. **ClaimAgent** — Extract and normalize claims from input text
2. **ResearchAgent** — Search web for evidence sources using Tavily
3. **SourceAgent** — Evaluate source credibility and quality
4. **EvidenceAgent** — Extract relevant evidence from sources
5. **VerificationAgent** — Verify claims against collected evidence
6. **ConflictAgent** — Detect contradictions and conflicts
7. **IndependenceAgent** — Analyze source independence and citation chains
8. **VerdictAgent** — Generate final verdict with confidence/uncertainty

## Project Structure

```
claimlens-2/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── health.py
│   │   │   │   ├── investigations.py
│   │   │   │   └── reports.py
│   │   │   └── router.py
│   │   ├── agents/
│   │   │   ├── claim_agent/
│   │   │   ├── research_agent/
│   │   │   ├── source_agent/
│   │   │   ├── evidence_agent/
│   │   │   ├── verification_agent/
│   │   │   ├── conflict_agent/
│   │   │   ├── independence_agent/
│   │   │   └── verdict_agent/
│   │   ├── workflows/
│   │   │   ├── graph.py           # Graph orchestration
│   │   │   ├── build.py           # Graph builder
│   │   │   ├── executor.py        # Workflow executor
│   │   │   ├── investigation_workflow.py
│   │   │   ├── routing.py
│   │   │   ├── checkpoints.py
│   │   │   └── retries.py
│   │   ├── services/
│   │   │   ├── investigation_service.py
│   │   │   └── report_service.py
│   │   ├── repos/
│   │   │   ├── investigation_repo.py
│   │   │   ├── claim_repo.py
│   │   │   ├── source_repo.py
│   │   │   ├── evidence_repo.py
│   │   │   └── verdict_repo.py
│   │   ├── integrations/
│   │   │   ├── supabase_client.py
│   │   │   ├── tavily_client.py
│   │   │   ├── gemini_client.py
│   │   │   ├── anthropic_client.py
│   │   │   ├── whisper_client.py
│   │   │   └── pdf_client.py
│   │   ├── core/
│   │   │   ├── logging.py
│   │   │   ├── exceptions.py
│   │   │   ├── constants.py
│   │   │   └── telemetry.py
│   │   ├── schemas/
│   │   ├── config.py
│   │   └── main.py
│   ├── migrations/
│   │   └── 001_init_schema.sql    # Supabase schema
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx           # Home / Landing
│   │   │   ├── investigate/
│   │   │   │   └── page.tsx
│   │   │   ├── report/
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx
│   │   │   └── globals.css
│   │   ├── components/
│   │   │   ├── investigation/
│   │   │   │   ├── InvestigationForm.tsx
│   │   │   │   └── InvestigationStatus.tsx
│   │   │   └── report/
│   │   │       ├── ReportSummary.tsx
│   │   │       ├── EvidenceCard.tsx
│   │   │       ├── SourceList.tsx
│   │   │       └── ConflictList.tsx
│   │   ├── lib/
│   │   │   ├── api.ts
│   │   │   ├── investigations.ts
│   │   │   └── report.ts
│   │   ├── types/
│   │   │   ├── investigation.ts
│   │   │   └── report.ts
│   │   └── hooks/
│   ├── public/
│   ├── package.json
│   ├── next.config.js
│   ├── tsconfig.json
│   ├── netlify.toml
│   └── .env.example
├── docker-compose.yml
├── .env.example
└── README.md
```

## Technology Stack

### Backend
- **Framework**: FastAPI (Python)
- **AI/ML**: LangGraph (workflow orchestration)
- **LLM Models**: Google Gemini, Anthropic Claude
- **Search**: Tavily API
- **Database**: Supabase PostgreSQL
- **Auth**: Supabase Auth (future)

### Frontend
- **Framework**: Next.js 14 (React 18)
- **Language**: TypeScript
- **Styling**: CSS-in-JS (inline styles + styled-jsx)
- **HTTP**: Native Fetch API
- **Deployment**: Netlify / Vercel

### Infrastructure
- **Database**: Supabase (PostgreSQL + Vector)
- **Hosting**: Render / Railway (backend), Netlify / Vercel (frontend)
- **Monitoring**: TBD (Sentry / Axiom)

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- Supabase account
- API keys: Gemini, Anthropic, Tavily

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your API keys and Supabase credentials

# Run database migrations
# (Copy the contents of backend/migrations/001_init_schema.sql into Supabase SQL Editor)

# Start development server
uvicorn backend.app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set environment variables
cp .env.example .env.local
# Edit .env.local with your API URL
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Start development server
npm run dev
# Visit http://localhost:3000
```

### Database Setup

1. Create a new Supabase project
2. Copy the connection string and API keys
3. In Supabase SQL Editor, run `backend/migrations/001_init_schema.sql`
4. Update `.env` files with Supabase credentials:
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your_anon_key
   SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
   ```

## API Reference

### Health Check
```bash
GET /health
GET /api/v1/health
```

### Investigations

**List Investigations**
```bash
GET /api/v1/investigations?status=completed
```

**Create Investigation**
```bash
POST /api/v1/investigations
Content-Type: application/json

{
  "title": "Verify startup metrics",
  "description": "Company claims 50k users and 180% YoY growth",
  "source_type": "text"
}
```

**Get Investigation**
```bash
GET /api/v1/investigations/{investigation_id}
```

**Run Investigation Workflow**
```bash
POST /api/v1/investigations/{investigation_id}/run
```

### Reports

**Get Report**
```bash
GET /api/v1/reports/{investigation_id}
```

**Export Report**
```bash
GET /api/v1/reports/{investigation_id}/export?format=pdf
```

## Environment Variables

### Backend (.env)
```bash
# Application
APP_ENV=development  # development, staging, production
DEBUG=true

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# LLM APIs
GEMINI_API_KEY=your_gemini_key
ANTHROPIC_API_KEY=your_anthropic_key
TAVILY_API_KEY=your_tavily_key

# CORS
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Deployment

### Deploy Backend to Render

1. Push code to GitHub
2. Create new Web Service on Render
3. Connect to GitHub repository
4. Set environment variables
5. Deploy

```bash
# Render buildpack will run:
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

### Deploy Frontend to Netlify

1. Connect GitHub repository
2. Set build command: `npm run build`
3. Set publish directory: `.next`
4. Set environment variables:
   - `NEXT_PUBLIC_API_URL=https://your-backend.onrender.com`
5. Deploy

### Deploy with Docker

```bash
# Build images
docker-compose build

# Run containers
docker-compose up -d

# Access:
# Backend: http://localhost:8000
# Frontend: http://localhost:3000
```

## Running Tests

### Backend Tests

```bash
cd backend
pytest tests/ -v
pytest tests/ --cov=backend.app
```

### Frontend Tests

```bash
cd frontend
npm run test
npm run test:coverage
```

## Performance Considerations

### Workflow Execution
- Current implementation runs agents sequentially (blocking)
- Production should use async queues (Celery + Redis)
- Implement checkpointing for long-running workflows
- Add caching for duplicate claims

### Database
- Use connection pooling (PgBouncer)
- Index on `investigation_id`, `status`, `created_at`
- Partition large tables by `created_at`
- Regular VACUUM and ANALYZE

### Frontend
- Use SWR or React Query for caching
- Implement pagination for investigation lists
- Add Service Worker for offline support

## Monitoring & Logging

### Logging
- Backend uses Python `logging` module
- Configure log levels in `.env`
- Ship logs to Axiom or Datadog (recommended)

### Metrics
- Track workflow execution time
- Monitor agent accuracy over time
- Count API requests and errors
- Database query performance

### Error Tracking
- Implement Sentry for error reporting
- Alert on critical failures

## Security

- Never commit `.env` files
- Use environment variables for secrets
- Implement rate limiting on API
- Add CORS restrictions
- Validate all inputs
- Use HTTPS in production
- Regular security audits

## Contributing

1. Create a feature branch
2. Make changes
3. Write tests
4. Submit pull request

## Future Enhancements

- [ ] Real-time collaboration on investigations
- [ ] Custom agent workflows
- [ ] Multi-language support
- [ ] Advanced evidence visualization (3D graph)
- [ ] Integration with fact-checking databases
- [ ] API rate limiting and usage analytics
- [ ] Webhook support for external systems
- [ ] Mobile app (React Native)
- [ ] Browser extension for inline fact-checking

## License

MIT License (specify in LICENSE file)

## Support

For issues and questions:
- GitHub Issues: [https://github.com/EmanFatima764/claimlens-2/issues](https://github.com/EmanFatima764/claimlens-2/issues)
- Email: support@claimlens.dev
