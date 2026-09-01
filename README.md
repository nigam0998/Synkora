<div align="center">

# Synkora

**AI-Powered Software Evolution Intelligence Platform**

*Understand. Analyze. Evolve.*

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Next.js](https://img.shields.io/badge/Next.js-15-black?logo=next.js)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?logo=typescript)](https://typescriptlang.org)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python)](https://python.org)

</div>

---

## What is Synkora?

Synkora is an **enterprise-grade DevTools SaaS platform** that analyzes GitHub repositories to understand the complete evolution of software projects. It combines static code analysis, Git history mining, knowledge graphs, vector search, AI agents, and large language models to deliver deep architectural insights.

### Key Capabilities

| Feature | Description |
|---------|-------------|
| **Architecture Reconstruction** | Auto-generate architecture diagrams from code |
| **Code Evolution Timeline** | Visualize how your codebase evolved over time |
| **Semantic Code Search** | Natural-language search across your entire codebase |
| **AI Code Assistant** | Context-aware AI chat that understands your repo |
| **Dependency Graph** | Interactive visualization of all dependencies |
| **Bug Prediction** | Identify high-risk files before bugs appear |
| **Auto Documentation** | Generate documentation from code analysis |
| **Technical Debt Detection** | Find and prioritize code smells and debt |
| **Security Scanning** | Detect common vulnerability patterns |
| **Team Analytics** | Contribution patterns and collaboration insights |

---

## Architecture

```
synkora/
├── web/                    # Next.js 15 Frontend (TypeScript)
│   ├── src/
│   │   ├── app/            # App Router pages
│   │   ├── components/     # Reusable UI components
│   │   ├── lib/            # Utilities and API client
│   │   └── styles/         # CSS design system
│   └── public/             # Static assets
│
├── api/                    # FastAPI Backend (Python)
│   ├── app/
│   │   ├── core/           # Config, logging, security
│   │   ├── models/         # SQLAlchemy ORM models
│   │   ├── routers/        # API route handlers
│   │   ├── schemas/        # Pydantic validation schemas
│   │   └── services/       # Business logic layer
│   └── tests/              # Backend test suite
│
└── shared/                 # Shared types and constants
    └── types/              # TypeScript + Python type definitions
```

---

## Tech Stack

### Frontend
- **Next.js 15** — React framework with App Router & Server Components
- **TypeScript** — Type-safe development
- **CSS** — Custom design system with CSS variables
- **D3.js** — Data visualization for graphs and charts

### Backend
- **FastAPI** — High-performance async Python API
- **PostgreSQL** — Primary database with SQLAlchemy ORM
- **Redis** — Caching and background job queues
- **Tree-sitter** — Multi-language code parsing (AST)
- **GitPython** — Git repository analysis

### AI / ML
- **Google Gemini** — LLM for code understanding and chat
- **Vector Embeddings** — Semantic code search
- **Knowledge Graphs** — Code relationship mapping

### Infrastructure
- **Docker** — Containerized development and deployment
- **GitHub Actions** — CI/CD pipeline
- **Alembic** — Database migrations

---

## Getting Started

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.12+
- **PostgreSQL** 15+
- **Redis** 7+
- **Git** 2.30+

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/synkora.git
cd synkora

# ── Frontend Setup ──────────────────────────────
cd web
npm install
cp .env.example .env.local    # Configure environment
npm run dev                    # Starts on http://localhost:3000

# ── Backend Setup (new terminal) ────────────────
cd api
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env           # Configure environment
uvicorn app.main:app --reload  # Starts on http://localhost:8000
```

### Docker (Local Development)

```bash
docker-compose up -d
```

### Production Deployment

To deploy Synkora to a production server (e.g., AWS EC2, DigitalOcean):

1. Clone the repository on your server.
2. Copy `.env.example` to `.env` and fill in your secure credentials (like `SECRET_KEY`, `GITHUB_CLIENT_SECRET`, and `AI_API_KEY`).
3. Run the automated deployment script:
   ```bash
   chmod +x deployment/deploy.sh
   ./deployment/deploy.sh
   ```

The `deploy.sh` script will automatically pull the latest code, build the optimized Docker images, and start the cluster with an **Nginx** reverse proxy handling traffic on port 80.

---

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) before submitting a pull request.

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with dedication by Devyansh Nigam**

*Understand your code. Evolve your software.*

</div>
