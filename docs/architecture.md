# Architecture — The Lenny Growth Assistant

## 1. System Overview

The Lenny Growth Assistant is a local-first AI application composed of:

- Next.js / React frontend
- FastAPI backend
- PostgreSQL with pgvector
- Ollama for local LLM inference
- Claude Agent SDK as an optional cloud provider
- Docker Compose for local deployment

The architecture separates the user interface, application/agent logic, retrieval layer, model providers, and persistence layer.

```text
                         ┌──────────────────────┐
                         │      Next.js UI      │
                         │                      │
                         │ Chat / Sources /     │
                         │ Artifact Viewer      │
                         └──────────┬───────────┘
                                    │ HTTP
                                    ▼
                         ┌──────────────────────┐
                         │      FastAPI         │
                         │       API            │
                         └──────────┬───────────┘
                                    │
                         ┌──────────▼───────────┐
                         │   Agent / Skills     │
                         │                      │
                         │ QA / Ship30 /        │
                         │ Artifact generation  │
                         └───────┬───────┬──────┘
                                 │       │
                    ┌────────────┘       └──────────────┐
                    ▼                                   ▼
          ┌──────────────────┐                ┌──────────────────┐
          │    Retrieval     │                │   LLM Provider   │
          │                  │                │                  │
          │ Embeddings +     │                │ Ollama           │
          │ pgvector search  │                │ Claude Agent SDK │
          └────────┬─────────┘                └──────────────────┘
                   │
                   ▼
          ┌──────────────────┐
          │   PostgreSQL     │
          │   + pgvector     │
          │                  │
          │ Sessions         │
          │ Messages         │
          │ Documents        │
          │ Chunks           │
          └──────────────────┘
2. Frontend Architecture
The frontend is implemented using Next.js and React.
The main application provides:
Conversation Sidebar
Displays persisted conversations and allows users to create or reopen sessions.
Chat Interface
Allows users to submit product and growth questions.
Sources Panel
Displays the transcript sources returned by the retrieval pipeline.
Artifact Viewer
Displays generated artifacts.
Markdown artifacts are rendered as Markdown.
HTML artifacts are displayed in a sandboxed iframe using srcDoc.
3. Backend Architecture
The FastAPI application exposes REST endpoints for:
POST /api/sessions
GET  /api/sessions
GET  /api/sessions/{session_id}/messages
POST /api/sessions/{session_id}/messages
POST /api/sessions/{session_id}/artifacts
The API layer is responsible for:
- Request validation
- Session management
- Message persistence
- Agent invocation
- Source formatting
- Artifact responses
- Error handling
4. Agent Layer
The agent layer coordinates retrieval and generation.
Grounded Q&A
Question
   ↓
Retrieve transcript evidence
   ↓
Build grounded prompt
   ↓
Selected LLM provider
   ↓
Answer + sources
Ship 30 for 30
Conversation
   ↓
Retrieve relevant transcript evidence
   ↓
Ship 30 for 30 writing skill
   ↓
LLM
   ↓
~1,250 word Markdown essay
Artifact Generation
Artifact request
   ↓
Retrieve relevant evidence
   ↓
Artifact generation skill
   ↓
LLM
   ↓
Markdown / HTML
   ↓
Sanitization for HTML
   ↓
Artifact Viewer
5. Retrieval Architecture
The retrieval pipeline uses the Lenny Podcast transcript corpus.
Ingestion
Transcript Markdown
        ↓
Metadata extraction
        ↓
Text chunking
        ↓
Ollama embedding model
        ↓
Vector representation
        ↓
PostgreSQL / pgvector
Query
User question
        ↓
Question embedding
        ↓
Vector similarity search
        ↓
Top relevant chunks
        ↓
Grounded generation
The embedding model used locally is:
nomic-embed-text
6. Data Model
The primary persisted entities are:
Session
Represents a conversation.
Important fields include:
- ID
- Title
- Created timestamp
- Updated timestamp
Message
Represents a user or assistant message.
Important fields include:
- ID
- Session ID
- Role
- Content
- Metadata
- Created timestamp
Message metadata can include the retrieved source information and selected provider.
Document
Represents an ingested transcript.
Chunk
Represents a searchable portion of a transcript and its vector embedding.
7. Model Provider Architecture
The model layer provides a provider-independent interface.
Local Provider
FastAPI
   ↓
LLM layer
   ↓
Ollama
   ↓
llama3.2:3b
This is the default local demonstration path.
Cloud Provider
FastAPI
   ↓
LLM layer
   ↓
Claude Agent SDK
   ↓
Anthropic Claude
The cloud provider is optional and requires the user's own Anthropic credentials.
The application is designed so that the retrieval and agent layers do not need to change when switching model providers.
8. Claude Agent SDK Integration
The application includes the Python Claude Agent SDK.
The SDK is isolated behind the LLM provider layer.
Conceptually:
generate()
    │
    ├── provider=ollama
    │       └── Ollama HTTP API
    │
    └── provider=anthropic
            └── Claude Agent SDK
This keeps provider-specific implementation details out of the core agent logic.
9. Artifact Security
Generated HTML is treated as untrusted content.
Before HTML is returned to the frontend:
1. The model response is parsed to extract the HTML document.
2. Dangerous HTML elements and attributes are removed.
3. Unsafe URL protocols are removed.
4. JavaScript event handlers are removed.
5. The sanitized HTML is returned to the frontend.
The frontend then renders HTML artifacts inside a sandboxed iframe.
Generated HTML
      ↓
Extract HTML
      ↓
Bleach sanitization
      ↓
Sandboxed iframe
      ↓
Artifact Viewer
The system does not execute generated JavaScript.
10. Error Handling
The backend catches model and artifact generation failures and converts them into controlled HTTP errors.
For example:
LLM failure
   ↓
Exception logged
   ↓
HTTP 503
   ↓
Frontend displays controlled error
LLM requests also use explicit timeouts.
The local Ollama generation timeout is intentionally longer because CPU-based local inference can be slower than cloud inference.
11. Persistence
Conversation state is persisted in PostgreSQL.
This means:
Browser refresh
      ↓
GET session messages
      ↓
PostgreSQL
      ↓
Conversation restored
The system does not rely solely on browser state for conversation persistence.
12. Docker Architecture
Docker Compose runs the primary services:
┌────────────────────────────────────────────┐
│              Docker Compose                │
│                                            │
│  ┌───────────┐      ┌──────────────┐       │
│  │ Frontend  │ ───► │   Backend    │       │
│  │   :3000   │      │    :8000     │       │
│  └───────────┘      └──────┬───────┘       │
│                             │               │
│              ┌──────────────┼───────────┐   │
│              ▼              ▼           │   │
│        ┌──────────┐   ┌────────────┐   │   │
│        │ Postgres │   │   Ollama   │   │   │
│        │  :5432   │   │   :11434   │   │   │
│        └──────────┘   └────────────┘   │   │
│                                        │   │
└────────────────────────────────────────────┘
13. Deployment
The intended local startup flow is:
docker compose up -d
The application can then be accessed at:
Frontend: http://localhost:3000
Backend:  http://localhost:8000
Ollama:   http://localhost:11434
PostgreSQL is internal to the Docker Compose environment.
14. Design Principles
Ground First
Transcript evidence is retrieved before grounded answers or artifacts are generated.
Provider Independence
Application logic should not depend on a single LLM provider.
Local First
The default setup should work without requiring a paid cloud AI API.
Safe Rendering
Generated HTML is considered untrusted and is sanitized before rendering.
Persistent State
Conversations are stored in PostgreSQL rather than relying only on frontend state.
Explicit Skills
Different tasks use dedicated prompts/skills rather than one generic generation prompt.
15. Current Limitations
The current implementation intentionally does not provide:
- Authentication
- Multi-user authorization
- Production-scale horizontal scaling
- Streaming generation
- Advanced reranking
- Hybrid retrieval
- Full cloud deployment
- Artifact version history
These can be added as future iterations.
16. Architectural Trade-offs
Ollama vs Cloud-only
Ollama provides a reproducible local demonstration and avoids mandatory cloud API costs, but smaller local models can have lower quality and higher latency.
PostgreSQL + pgvector
Using PostgreSQL for both application persistence and vector search keeps the system relatively simple and reduces infrastructure complexity.
REST vs Streaming
REST endpoints simplify the initial implementation. Streaming would improve perceived latency and is a future improvement.
Sandboxed iframe
The sandboxed iframe adds isolation for generated HTML while keeping the Artifact Viewer simple to implement.