# The Lenny Growth Assistant

A full-stack, locally runnable AI assistant grounded in Lenny's Podcast transcripts.

## Stack

- Next.js + TypeScript frontend
- FastAPI backend
- PostgreSQL + pgvector
- Ollama for the mandatory local-model demo
- Optional Anthropic cloud provider
- RAG retrieval with source attribution
- Ship 30 for 30 writing skill
- Sanitized/sandboxed HTML artifact viewer
- Docker Compose

## Quick start

Prerequisites: Docker Desktop with at least ~8 GB RAM available.

```bash
cp .env.example .env
docker compose up --build -d
docker compose exec ollama ollama pull llama3.2:3b
docker compose exec ollama ollama pull nomic-embed-text
docker compose exec backend python -m app.ingest --limit 30
```

Open http://localhost:3000

The first model download may take several minutes.

## Cloud model

Set in `.env`:

```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_key
ANTHROPIC_MODEL=claude-3-5-sonnet-latest
```

Then restart:

```bash
docker compose up -d --build
```

## Useful commands

```bash
docker compose ps
docker compose logs -f backend
docker compose logs -f frontend
docker compose down
docker compose down -v
docker compose exec backend pytest -q
```

## API

- `GET /health`
- `POST /api/sessions`
- `GET /api/sessions`
- `GET /api/sessions/{id}/messages`
- `POST /api/sessions/{id}/messages`
- `POST /api/sessions/{id}/artifacts`

## Knowledge ingestion

The ingestion command downloads Markdown transcripts from:

https://github.com/ChatPRD/lennys-podcast-transcripts

It parses frontmatter, chunks transcript text, obtains embeddings from Ollama, and stores documents/chunks in PostgreSQL + pgvector.

For a faster demo, use `--limit 10`. For broader coverage, remove the limit.

## Troubleshooting

### Ollama unavailable

```bash
docker compose restart ollama
docker compose exec ollama ollama list
```

### Database unavailable

```bash
docker compose ps postgres
docker compose logs postgres
```

### No retrieval results

Make sure embeddings and transcripts were ingested:

```bash
docker compose exec backend python -m app.ingest --limit 30
```

### Model not found

```bash
docker compose exec ollama ollama pull llama3.2:3b
docker compose exec ollama ollama pull nomic-embed-text
```

## Security

Generated HTML is treated as untrusted. The backend removes scripts, iframes, embeds, event handlers, and dangerous URL schemes. The frontend renders sanitized HTML in a sandboxed iframe with scripts disabled.

## Project structure

```text
backend/app/
  api.py
  config.py
  db.py
  models.py
  retrieval.py
  llm.py
  agent.py
  artifacts.py
  ingest.py
  main.py
  skills/
frontend/
docs/
tests/
agent-transcripts/
```

## Manual UI test plan

1. Create a new chat.
2. Ask: "What does Lenny's content say about improving activation?"
3. Confirm sources are shown.
4. Ask a follow-up question.
5. Ask an unsupported/specific question and verify the assistant can say evidence is insufficient.
6. Ask: "Turn that into a Ship 30 for 30 essay."
7. Generate a Markdown or HTML artifact.
8. Confirm the artifact appears in the right-hand viewer.
9. Restart Docker and confirm sessions remain in PostgreSQL.
10. Switch provider configuration and verify the UI provider indicator changes.

## Demo video

Recommended 2–3 minute flow:
- 20 sec: problem
- 40 sec: grounded question + sources
- 20 sec: follow-up
- 40 sec: Ship 30 essay
- 20 sec: artifact viewer
- 20 sec: Ollama/local model
- 20 sec: one architecture/security trade-off
