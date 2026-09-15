# The Lenny Growth Assistant

A full-stack AI-powered conversational assistant grounded in Lenny's Podcast transcripts.

The product is designed for product managers, founders, and growth teams who want reliable product and growth insights without needing to understand prompts, retrieval infrastructure, or model configuration.

The application combines transcript-grounded RAG, persistent conversations, specialized writing skills, and in-app Markdown/HTML artifact generation.

---

## 1. Product Overview

The Lenny Growth Assistant helps users:

- Ask product management and growth questions
- Receive answers grounded in Lenny's Podcast transcripts
- See the transcript sources used to generate an answer
- Continue conversations with session-level context
- Generate Ship 30 for 30-style essays
- Generate Markdown and HTML/CSS artifacts
- Preview HTML artifacts directly inside the application
- Run locally using Ollama
- Optionally switch to Anthropic Claude through the Claude Agent SDK

The mandatory demo path uses Ollama locally.

---

## 2. Architecture

The application consists of four main layers:

### Frontend

- Next.js
- React
- TypeScript
- Chat interface
- Session management
- LLM provider selector
- Artifact Viewer

### Backend

- FastAPI
- Agent orchestration layer
- RAG retrieval
- Transcript ingestion
- Artifact generation
- HTML sanitization
- API validation and error handling

### Data Layer

- PostgreSQL
- pgvector
- Persistent sessions
- Persistent messages
- Transcript documents
- Transcript chunks
- Embeddings
- Source metadata

### Model Layer

Local provider:

- Ollama
- `llama3.2:3b`
- `nomic-embed-text`

Optional cloud provider:

- Anthropic Claude
- Claude Agent SDK

High-level flow:

    User
      |
      v
    Next.js Frontend
      |
      v
    FastAPI API
      |
      +---- Session / Message Persistence ----> PostgreSQL
      |
      +---- Retrieval ------------------------> pgvector
      |
      +---- Agent / Skill Layer
      |          |
      |          +---- Ollama
      |          |
      |          +---- Anthropic Claude Agent SDK
      |
      +---- Artifact Sanitization
                 |
                 v
          Artifact Viewer

---

## 3. Prerequisites

Install:

- Docker Desktop
- Docker Compose

Recommended:

- At least 8 GB RAM available to Docker
- Internet connection for the initial transcript/model downloads

No local Python, Node.js, PostgreSQL, or Ollama installation is required when using Docker Compose.

---

## 4. Quick Start

Clone the repository:

    git clone https://github.com/Harshith91939/lenny-growth-assistant.git

Enter the project:

    cd lenny-growth-assistant

Create the environment file:

    cp .env.example .env

On Windows PowerShell, if `cp` is unavailable:

    Copy-Item .env.example .env

Start the application:

    docker compose up --build -d

Download the local models:

    docker compose exec ollama ollama pull llama3.2:3b

    docker compose exec ollama ollama pull nomic-embed-text

Ingest the transcript knowledge base:

    docker compose exec backend python -m app.ingest --limit 10

The demo dataset contains 10 transcripts and was successfully ingested into PostgreSQL.

Open:

    http://localhost:3000

Backend health endpoint:

    http://localhost:8000/health

---

## 5. Environment Configuration

Copy:

    .env.example

to:

    .env

The local demo defaults to Ollama.

Important variables include:

    DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/lenny
    LLM_PROVIDER=ollama
    OLLAMA_BASE_URL=http://ollama:11434
    OLLAMA_MODEL=llama3.2:3b
    EMBEDDING_MODEL=nomic-embed-text

Optional Anthropic configuration:

    ANTHROPIC_API_KEY=
    ANTHROPIC_MODEL=claude-sonnet-4-6

Never commit real API keys or secrets.

---

## 6. LLM Provider Configuration

The UI exposes the selected provider.

### Local Ollama

The default provider is:

    ollama

The mandatory demonstration uses:

    llama3.2:3b

Embeddings use:

    nomic-embed-text

This allows the complete product to run locally without requiring a paid cloud LLM API.

### Anthropic

The application also integrates the Anthropic Claude Agent SDK.

Set:

    LLM_PROVIDER=anthropic
    ANTHROPIC_API_KEY=your_api_key

Then restart:

    docker compose up -d --build

The Anthropic path requires a valid API key and is optional for the local demonstration.

---

## 7. Knowledge Base / RAG

The knowledge base is built from Lenny's Podcast transcript repository:

https://github.com/ChatPRD/lennys-podcast-transcripts

The ingestion pipeline:

1. Loads episode transcript Markdown files
2. Parses transcript metadata/frontmatter
3. Extracts transcript text
4. Splits transcripts into searchable chunks
5. Generates embeddings using Ollama
6. Stores documents, chunks, embeddings, and source metadata in PostgreSQL/pgvector
7. Uses vector similarity retrieval for user questions
8. Passes retrieved evidence to the model
9. Returns answers with source attribution

The current successful demo ingestion contains:

- 10 transcript documents
- 562 transcript chunks

To ingest a larger set:

    docker compose exec backend python -m app.ingest --limit 30

The ingestion limit can be adjusted depending on available machine resources.

---

## 8. Grounded Conversational Assistant

The assistant is designed to ground answers in retrieved transcript evidence.

The conversation pipeline is:

    User question
        |
        v
    Session context
        |
        v
    Vector retrieval
        |
        v
    Transcript evidence
        |
        v
    Agent / LLM
        |
        v
    Grounded response + sources

The assistant also receives recent messages from the current session so that follow-up questions retain conversational context.

If relevant transcript evidence is not available, the system is instructed not to invent supporting evidence and can acknowledge that the available material does not sufficiently support the answer.

---

## 9. Ship 30 for 30 Skill

The application contains a dedicated Ship 30 for 30 writing skill rather than treating essay generation as an arbitrary one-off prompt.

The skill instructs the model to produce approximately 1,250 words with:

- A compelling opening hook
- One clear central idea
- Narrative progression
- Specific transcript-grounded examples
- Short, skimmable paragraphs
- Useful headings
- Selective emphasis
- A practical takeaway
- A human, readable voice
- No invented facts, statistics, or quotations

The skill uses the current conversation and retrieved transcript evidence as inputs.

---

## 10. Artifact Generation

The assistant can generate:

- Markdown documents
- HTML documents
- HTML/CSS landing pages
- Product plans
- Playbooks
- Other structured written artifacts

Generated artifacts appear in the in-app Artifact Viewer.

The goal is to keep the user inside the product rather than requiring them to copy generated code into another application.

---

## 11. Artifact Security

Generated HTML is treated as untrusted content.

The backend sanitizes generated HTML before it is returned to the frontend.

The sanitization layer removes or blocks:

- `<script>`
- `<iframe>`
- `<object>`
- `<embed>`
- Inline event handlers such as `onclick` and `onerror`
- Dangerous URL schemes such as `javascript:`
- Unsafe protocols

Allowed styling is restricted through a CSS sanitizer.

The frontend renders HTML artifacts inside a sandboxed iframe with scripts disabled.

This provides two layers of protection:

    Generated HTML
          |
          v
    Backend sanitization
          |
          v
    Sandboxed iframe
          |
          v
    Artifact Viewer

The viewer is intentionally more restrictive than a normal web page because generated HTML should be considered untrusted.

---

## 12. API

### Health

    GET /health

Returns backend health information.

### Sessions

    POST /api/sessions

Create a new conversation session.

    GET /api/sessions

List available sessions.

    GET /api/sessions/{id}/messages

Retrieve messages for a session.

### Messages

    POST /api/sessions/{id}/messages

Send a user message and receive a grounded response.

The request supports:

- `content`
- `provider`

Supported providers:

- `ollama`
- `anthropic`

### Artifacts

    POST /api/sessions/{id}/artifacts

Generate a Markdown or HTML artifact from the current conversation.

---

## 13. Persistence

PostgreSQL stores:

- Session IDs
- Session timestamps
- Message roles
- Message content
- Message timestamps
- Provider metadata
- Retrieved source metadata
- Transcript documents
- Transcript chunks
- Embeddings

Because sessions and messages are persisted in PostgreSQL, conversations survive application/browser restarts as long as the PostgreSQL volume is retained.

---

## 14. Observability

The backend uses Python logging for operational visibility.

Useful logs can be viewed with:

    docker compose logs -f backend

Frontend logs:

    docker compose logs -f frontend

PostgreSQL logs:

    docker compose logs -f postgres

Ollama logs:

    docker compose logs -f ollama

These logs help diagnose:

- Model availability
- Model generation failures
- Embedding failures
- Retrieval failures
- Database problems
- Artifact-generation problems
- Startup/configuration issues

---

## 15. Resilience and Failure Handling

The application handles common failure cases including:

### Missing Anthropic API key

The Anthropic provider returns a clear configuration error instead of silently failing.

### Ollama unavailable

Embedding and generation calls return application-level errors that can be diagnosed through backend logs.

### Model timeout

Model calls use explicit request timeouts suitable for local inference.

### Empty retrieval

The assistant receives an explicit indication when no transcript evidence was retrieved.

### Database failures

Database/API failures are surfaced as application errors rather than returning fabricated results.

### Invalid requests

FastAPI/Pydantic validation prevents malformed or oversized message/artifact requests.

---

## 16. Useful Commands

Check services:

    docker compose ps

View backend logs:

    docker compose logs -f backend

View frontend logs:

    docker compose logs -f frontend

View Ollama logs:

    docker compose logs -f ollama

View PostgreSQL logs:

    docker compose logs -f postgres

Stop services:

    docker compose down

Stop services and remove database volumes:

    docker compose down -v

Run backend tests:

    docker compose exec backend pytest -q

Check installed Ollama models:

    docker compose exec ollama ollama list

---

## 17. Troubleshooting

### Ollama unavailable

    docker compose restart ollama

    docker compose exec ollama ollama list

### Model not found

    docker compose exec ollama ollama pull llama3.2:3b

    docker compose exec ollama ollama pull nomic-embed-text

### Database unavailable

    docker compose ps postgres

    docker compose logs postgres

### No retrieval results

Make sure the models are installed and transcripts have been ingested:

    docker compose exec ollama ollama list

    docker compose exec backend python -m app.ingest --limit 10

### Rebuild the application

    docker compose down

    docker compose build --no-cache

    docker compose up -d

---

## 18. Testing

Backend tests are located under:

    backend/tests/

Run:

    docker compose exec backend pytest -q

The current test suite includes artifact extraction and security tests covering:

- HTML extraction from fenced responses
- HTML extraction without fences
- Script removal
- Event-handler removal
- JavaScript URL removal
- Preservation of safe HTML/CSS

The project also includes a manual UI test plan covering:

1. Create a new chat
2. Ask a transcript-grounded product/growth question
3. Confirm sources are displayed
4. Ask a follow-up question
5. Ask an unsupported question and verify the assistant can acknowledge insufficient evidence
6. Generate a Ship 30 for 30 essay
7. Generate a Markdown artifact
8. Generate an HTML artifact
9. Confirm the artifact appears in the Artifact Viewer
10. Restart the application and verify persisted sessions

---

## 19. Agent Transcripts

Development and debugging transcripts are stored under:

    agent-transcripts/

They document representative engineering failures and corrections, including:

- npm network/ECONNRESET recovery
- Docker BuildKit/cache recovery
- Transcript ingestion and JSONB correction
- Ollama generation/timeout recovery

Secrets and sensitive credentials must not be included in these logs.

---

## 20. Project Structure

    lenny-growth-assistant/
    |
    +-- backend/
    |   +-- app/
    |   |   +-- api.py
    |   |   +-- config.py
    |   |   +-- db.py
    |   |   +-- models.py
    |   |   +-- retrieval.py
    |   |   +-- llm.py
    |   |   +-- agent.py
    |   |   +-- artifacts.py
    |   |   +-- ingest.py
    |   |   +-- skills.py
    |   |   +-- main.py
    |   +-- tests/
    |
    +-- frontend/
    |
    +-- docs/
    |   +-- PRD.md
    |   +-- design.md
    |   +-- architecture.md
    |
    +-- agent-transcripts/
    |
    +-- docker-compose.yml
    +-- .env.example
    +-- README.md

---

## 21. Design Decisions and Trade-offs

### Local-first model execution

Ollama was selected for the mandatory demo because it allows the evaluator to run the complete product without requiring a paid cloud API.

Trade-off:

Local models can have lower reasoning and writing quality than larger cloud models, while also consuming local CPU/RAM resources.

### PostgreSQL + pgvector

Using PostgreSQL for both application persistence and vector retrieval keeps the architecture simple and reduces infrastructure dependencies.

Trade-off:

A specialized vector database could provide additional retrieval features at larger scale, but PostgreSQL/pgvector is more practical for this engagement.

### Retrieval before generation

The assistant retrieves transcript evidence before generating grounded answers.

Trade-off:

Retrieval introduces latency, but improves traceability and reduces unsupported claims.

### Sandboxed artifacts

Generated HTML is sanitized and rendered inside a sandboxed iframe.

Trade-off:

Some advanced browser functionality is intentionally unavailable, but this substantially reduces the risk of generated HTML executing unwanted behavior.

---

## 22. Forward Deployment Perspective

The system is intentionally designed as a small deployable engagement rather than only a prototype.

The key principles are:

- Ground first, generate second
- Make provider choice visible
- Keep sessions persistent
- Treat generated HTML as untrusted
- Keep infrastructure reproducible
- Document operational failure modes
- Separate specialized skills from generic chat behavior
- Optimize for evaluator/client handoff

---

## 23. Demo

The recommended 2–3 minute demo flow is:

### 0:00–0:20

Explain the user problem and product.

### 0:20–1:00

Ask a product/growth question and show transcript-grounded sources.

### 1:00–1:20

Ask a follow-up question to demonstrate session context.

### 1:20–1:50

Generate a Ship 30 for 30-style essay and show the Artifact Viewer.

### 1:50–2:15

Generate an HTML/CSS artifact and show it rendered in the application.

### 2:15–2:35

Show that the application is running with local Ollama and briefly explain the local-first model trade-off.

### 2:35–2:50

Show the repository and mention Docker Compose, PostgreSQL/pgvector, tests, documentation, and optional Claude Agent SDK integration.

---

## 24. License / Assignment

This repository was created as a take-home engineering assignment demonstrating product judgment, AI engineering, RAG, full-stack development, deployment, security, and operational handoff.