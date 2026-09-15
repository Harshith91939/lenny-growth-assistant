# Product Requirements Document
# The Lenny Growth Assistant

## 1. Product Overview

The Lenny Growth Assistant is a grounded AI product and growth assistant that helps founders, product managers, and growth practitioners learn from Lenny's Podcast conversations.

Users can ask product and growth questions in natural language. The system retrieves relevant passages from the available Lenny Podcast transcript corpus and uses those passages as grounding context for the AI response.

The product can also transform a grounded discussion into useful artifacts such as:

- Ship 30 for 30 style essays
- Product-market-fit playbooks
- Growth plans
- HTML landing pages

The application supports a local-first AI workflow using Ollama and provides an optional Cloud Claude provider through the Claude Agent SDK.

---

## 2. Problem

Product and growth practitioners often have questions such as:

- How should we improve activation?
- How do successful companies approach growth?
- When should a company invest in acquisition?
- How should a growth team be structured?
- What product principles repeatedly appear in conversations with experienced operators?

Lenny's Podcast contains a large amount of relevant product and growth knowledge, but finding and applying the relevant insights manually is time-consuming.

A generic LLM can answer these questions, but it may hallucinate information or provide advice that cannot be traced back to the source material.

The Lenny Growth Assistant addresses this by combining:

1. Transcript retrieval
2. Vector search
3. Grounded generation
4. Source citations
5. Persistent conversations
6. Reusable writing and artifact skills

---

## 3. Target Users

### Primary Users

- Product managers
- Growth practitioners
- Startup founders
- Product leaders
- Entrepreneurs

### Secondary Users

- Students learning product management
- Researchers studying product and growth strategies
- Teams looking for structured product-development insights

---

## 4. Jobs To Be Done

### Core JTBD

"When I have a product or growth problem, I want to quickly discover what experienced product leaders have said about similar problems so that I can make a better decision."

### Artifact JTBD

"When I have a grounded discussion, I want to transform it into a useful document or artifact so that I can share or act on the insights."

---

## 5. Goals

### Primary Goals

1. Provide grounded answers using podcast transcript evidence.
2. Show the sources used for each answer.
3. Preserve conversations across browser refreshes.
4. Support local AI inference using Ollama.
5. Provide an optional Claude Agent SDK integration.
6. Transform conversations into useful artifacts.
7. Safely render generated HTML artifacts.
8. Provide a reproducible Docker-based deployment.

### Secondary Goals

1. Keep the architecture simple enough for local development.
2. Make failures observable through application logs.
3. Provide tests for important application behavior.
4. Document design decisions and operational setup.

---

## 6. Non-Goals

The following are intentionally outside the initial scope:

- User authentication
- Multi-tenant access control
- Billing
- Production-scale Kubernetes deployment
- Editing or modifying original podcast transcripts
- Replacing a human product manager
- Autonomous product decisions

---

## 7. Core Features

### 7.1 Grounded Chat

Users can ask natural-language product and growth questions.

The system:

1. Embeds the question.
2. Searches the transcript vector database.
3. Retrieves relevant passages.
4. Provides the passages to the selected LLM.
5. Generates a grounded response.
6. Returns source information.

---

### 7.2 Source Citations

Responses expose the transcript sources used during generation.

Each source includes:

- Episode title
- Guest
- Source URL
- Retrieved passage

This allows users to inspect the evidence behind an answer.

---

### 7.3 Persistent Conversations

Sessions and messages are stored in PostgreSQL.

Users can:

- Create a new chat
- Return to previous chats
- Refresh the browser without losing conversations
- Continue an existing discussion

---

### 7.4 Local Ollama Provider

The application supports local inference using:

- Ollama
- `llama3.2:3b`

This provides a local demonstration mode without requiring a paid cloud LLM API.

Embeddings use:

- `nomic-embed-text`

---

### 7.5 Claude Agent SDK Provider

The application includes an optional Claude Agent SDK integration.

The provider can be selected when valid Anthropic credentials are available.

The local Ollama provider remains the default demonstration path.

---

### 7.6 Ship 30 for 30 Skill

The assistant includes a dedicated writing skill for transforming grounded conversations into approximately 1,250-word essays.

The skill emphasizes:

- Strong hooks
- One clear central idea
- Narrative progression
- Specific examples
- Skimmable structure
- Practical takeaways
- Human writing style
- Grounding in transcript evidence

The system avoids inventing unsupported facts, quotations, or statistics.

---

### 7.7 Artifact Generation

Users can request artifacts such as:

- Essays
- Playbooks
- Plans
- HTML landing pages
- Markdown documents

The artifact generation system uses retrieved transcript evidence as grounding context.

---

### 7.8 Artifact Viewer

Generated Markdown is rendered inside the application.

Generated HTML is rendered inside a sandboxed iframe.

The backend sanitizes generated HTML before returning it to the frontend.

This reduces the risk of generated HTML executing unwanted scripts or unsafe content.

---

## 8. Technical Architecture

### Frontend

- Next.js
- React
- JavaScript
- Marked

### Backend

- FastAPI
- Python
- SQLAlchemy
- Pydantic

### Database

- PostgreSQL
- pgvector

### AI

- Ollama
- Llama 3.2 3B
- Nomic Embed Text
- Claude Agent SDK (optional cloud provider)

### Deployment

- Docker
- Docker Compose

---

## 9. RAG Pipeline

```text
Podcast Transcripts
        |
        v
Metadata Parsing
        |
        v
Chunking
        |
        v
Ollama Embeddings
        |
        v
PostgreSQL + pgvector
        |
        |
User Question
        |
        v
Question Embedding
        |
        v
Vector Similarity Search
        |
        v
Relevant Transcript Chunks
        |
        v
LLM Prompt
        |
        v
Grounded Response
        |
        v
Sources / Citations
10. Success Metrics
Grounded Answer Quality
Target:
≥90% useful retrieval on a curated answerable evaluation set.
Session Persistence
Target:
100% of successfully created sessions and messages persist across refreshes.
Artifact Generation
Target:
≥95% successful artifact generation for supported requests.
Local Startup
Target:
The application should start using Docker Compose with the documented startup command.
Source Coverage
Target:
≥90% of answerable questions should return at least one useful transcript source.
11. Functional Requirements
FR-1 Chat
The system must accept natural-language questions.
FR-2 Retrieval
The system must retrieve relevant transcript chunks before generating grounded answers.
FR-3 Sources
The system must expose retrieved source information.
FR-4 Persistence
The system must persist sessions and messages in PostgreSQL.
FR-5 Local Model
The system must support local Ollama inference.
FR-6 Cloud Model
The system should support Claude through the Claude Agent SDK when credentials are available.
FR-7 Essay Skill
The system must support generation of Ship 30 for 30 style essays.
FR-8 Artifacts
The system must support Markdown and HTML artifact generation.
FR-9 HTML Safety
Generated HTML must be sanitized before rendering.
FR-10 Docker
The application must be runnable through Docker Compose.
12. Non-Functional Requirements
Performance
The UI should provide a visible loading state while generation is running.
Reliability
LLM failures should return a controlled API error rather than crashing the application.
Security
Generated HTML must be sanitized and rendered in a sandboxed iframe.
Observability
Application failures should be recorded through structured application logs.
Reproducibility
The application should provide a documented Docker-based startup process.
13. Risks
Hallucination
Risk:
The model may generate unsupported information.
Mitigation:
Use transcript retrieval and explicitly instruct the model to remain grounded.
Local Model Quality
Risk:
Small local models may produce lower-quality responses than cloud models.
Mitigation:
Keep the system provider-agnostic and support an optional cloud provider.
Latency
Risk:
Local inference can be slow on CPU-only machines.
Mitigation:
Use loading states, request timeouts, and configurable model settings.
Unsafe Generated HTML
Risk:
Generated HTML could contain malicious JavaScript or unsafe URLs.
Mitigation:
Backend HTML sanitization plus sandboxed iframe rendering.
Transcript Rights
Risk:
Podcast transcript content may have usage restrictions.
Mitigation:
Use the transcript repository according to its stated usage terms and clearly attribute source material.
14. Acceptance Criteria
The product is considered successful when:
- Users can create conversations.
- Users can send product/growth questions.
- Transcript retrieval provides grounded evidence.
- Sources are shown in the UI.
- Conversations persist in PostgreSQL.
- Ollama works locally.
- Claude Agent SDK integration exists as an optional provider.
- Ship 30 for 30 essay generation works.
- Markdown artifacts render in the Artifact Viewer.
- HTML artifacts render in the Artifact Viewer.
- Generated HTML is sanitized.
- HTML is displayed inside a sandboxed iframe.
- Docker Compose starts the application.
- Application errors are logged.
- Full production-scale authentication.
- Production cloud deployment.
15. Future Improvements
Potential future improvements include:
- Streaming responses
- Better retrieval evaluation
- Reranking
- Hybrid keyword + vector search
- More sophisticated transcript metadata filtering
- Authentication
- Multi-user workspaces
- Artifact history
- Artifact export/download
- Cloud deployment
- Larger local models
- Automated evaluation datasets
- Conversation summarization
16. Product Principle
The central product principle is:
Ground first, generate second.

The assistant should prioritize trustworthy transcript evidence before producing recommendations or artifacts.

