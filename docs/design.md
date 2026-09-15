# Product & UX Design — The Lenny Growth Assistant

## 1. Design Goal

The product should feel like a focused AI research and thinking workspace rather than a generic chatbot.

The interface is designed around three activities:

1. Ask a product or growth question.
2. Inspect the transcript evidence behind the answer.
3. Turn the discussion into a reusable artifact.

The design prioritizes clarity, trust, and fast movement from question to action.

---

## 2. Primary User Flow

```text
Open application
      |
      v
Create / select conversation
      |
      v
Ask product or growth question
      |
      v
Grounded AI response
      |
      +--------------------+
      |                    |
      v                    v
Inspect sources       Continue discussion
      |                    |
      +---------+----------+
                |
                v
        Create artifact
                |
        +-------+-------+
        |               |
        v               v
     Markdown         HTML
        |               |
        v               v
 Artifact Viewer   Sandboxed Viewer
 3. Layout
The application uses a three-column workspace.
Left — Conversation Sidebar
Contains:
- Product name
- New Chat button
- Conversation history
- LLM provider indicator
Purpose:
Allow users to quickly switch between ongoing research conversations.
Center — Chat Workspace
Contains:
- Application title
- Short product description
- Ship 30 for 30 action
- Conversation messages
- Composer
- Send button
Purpose:
This is the primary thinking and interaction surface.
Right — Evidence & Artifact Panel
Contains:
- Retrieved transcript sources
- Source links
- Artifact Viewer
Purpose:
Keep evidence and generated outputs visible without forcing users to leave the conversation.
4. Trust & Grounding
AI-generated answers can be difficult to trust when users cannot determine where the information came from.
The design therefore makes retrieved evidence visible next to the conversation.
Each source displays:
- Episode title
- Guest
- Source link
This gives the user a clear path from:
AI answer
    ↓
Retrieved evidence
    ↓
Original episode
The assistant is instructed to remain grounded in retrieved transcript evidence.
5. Conversation Design
User Messages
User messages are visually separated from assistant responses.
Assistant Messages
Assistant responses support Markdown rendering.
This allows the model to use:
- Headings
- Lists
- Bold text
- Emphasis
- Links
- Structured explanations
Loading State
During generation the interface displays:
Assistant

Thinking…
This prevents the interface from appearing unresponsive during slower local Ollama inference.
6. Artifact Design
Artifacts are treated as first-class outputs rather than ordinary chat messages.
When a user requests an artifact, the chat displays a concise confirmation:
I've created the requested artifact.
You can view it in the Artifact Viewer on the right.
The actual artifact appears in the dedicated viewer.
This prevents long generated documents or HTML source code from overwhelming the conversation.
7. Markdown Artifacts
Markdown artifacts are rendered into formatted content inside the Artifact Viewer.
Typical outputs include:
- Product-market-fit playbooks
- Growth plans
- Ship 30 for 30 essays
- Structured notes
The viewer supports readable headings, paragraphs, lists, and other Markdown structures.
8. HTML Artifacts
HTML artifacts are treated as untrusted generated content.
The flow is:
LLM-generated HTML
       |
       v
HTML extraction
       |
       v
Bleach sanitization
       |
       v
Sandboxed iframe
       |
       v
Artifact Viewer
The frontend uses:
<iframe sandbox="">
The backend sanitizes generated HTML before returning it.
The HTML generator is instructed to return a self-contained document with embedded CSS rather than relying on external files.
9. Visual Design Principles
Clear Hierarchy
Important actions should be visually obvious.
Primary actions include:
- New Chat
- Send
- Create 30 for 30
Evidence Visibility
Sources should remain accessible without disrupting the conversation.
Focused Workspace
The three-column layout keeps:
- conversations
- reasoning
- evidence
- artifacts
available simultaneously.
Progressive Disclosure
The main conversation remains concise while detailed evidence and generated artifacts are available in dedicated panels.
10. Provider UX
The application supports two provider options:
Local Ollama
Local Ollama
llama3.2:3b
This is the default local demonstration provider.
Cloud Claude
Cloud Claude
Claude Agent SDK
This is an optional provider requiring the user's own Anthropic credentials.
The provider selector communicates which model path is active.
11. Empty State
When a conversation has no messages, the application displays a simple starting prompt:
Ask a product or growth question.

Try:
"What are practical ways to improve activation?"
The goal is to communicate immediately what the product is designed to answer.
12. Error States
Errors should be understandable rather than exposing raw stack traces.
For example:
Error: AI service unavailable
Detailed errors remain available in backend logs for debugging.
13. Responsive Behavior
The primary target is desktop usage because the application is designed as a research workspace.
On smaller screens, the layout can progressively collapse the secondary panels so that the conversation remains usable.
Future improvements could include:
- Mobile navigation
- Collapsible sources
- Full-screen artifact viewer
- Responsive conversation sidebar
14. Accessibility Considerations
The interface should use:
- Semantic HTML
- Descriptive button labels
- Visible focus states
- Readable text contrast
- Form labels/placeholders
- Accessible iframe titles
Generated HTML artifacts are isolated from the main application using a sandboxed iframe.
15. Interaction Principles
Ask → Ground → Create
The core product loop is:
ASK
"What should we improve?"

       ↓

GROUND
"What does the transcript evidence say?"

       ↓

CREATE
"Turn those insights into something useful."
This loop differentiates the product from a generic chatbot.
16. Ship 30 for 30 Experience
The "Create 30 for 30" action transforms the current grounded discussion into an approximately 1,250-word essay.
The generated essay should have:
- A strong title
- A compelling opening
- One central idea
- Narrative progression
- Specific examples
- Short paragraphs
- Useful section headings
- A practical closing takeaway
The output should feel like a publishable online essay rather than a chatbot response.
17. Artifact Request Experience
Users can request artifacts naturally through chat.
Examples:
Create a product-market-fit playbook.
Turn this discussion into a Ship 30 for 30 essay.
Create an HTML landing page for this playbook.
The application detects supported artifact requests and routes them to the Artifact Viewer.
18. Security UX
Generated content should never be implicitly trusted.
HTML is:
1. Extracted from the model response.
2. Sanitized on the backend.
3. Rendered in an isolated iframe.
The product intentionally does not execute arbitrary model-generated JavaScript.
19. Future UX Improvements
Potential improvements include:
- Streaming responses
- Citation highlighting
- Expandable transcript passages
- Search/filter across episodes
- Artifact download
- Artifact history
- Copy/share controls
- Conversation rename
- Dark mode
- Mobile layout
- Model latency indicators
- Retrieval confidence indicators
20. Design Summary
The interface is built around a simple principle:
Keep the question, evidence, and resulting artifact in the same workspace.

This allows users to move from product uncertainty to grounded insight and finally to a reusable output without switching tools.