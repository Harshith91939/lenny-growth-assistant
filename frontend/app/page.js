"use client";

import { useEffect, useState } from "react";
import { marked } from "marked";

const API =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Home() {
  const [sessions, setSessions] = useState([]);
  const [sid, setSid] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sources, setSources] = useState([]);
  const [artifact, setArtifact] = useState(null);
  const [loading, setLoading] = useState(false);
  const [provider, setProvider] = useState("ollama");

  async function loadSessions() {
    try {
      const r = await fetch(`${API}/api/sessions`);
      const d = await r.json();

      setSessions(d);

      if (!sid && d[0]) {
        selectSession(d[0].id);
      }
    } catch (e) {
      console.error("Failed to load sessions:", e);
    }
  }

  async function newChat() {
    try {
      const r = await fetch(`${API}/api/sessions`, {
        method: "POST",
      });

      const d = await r.json();

      setSessions((x) => [d, ...x]);
      setSid(d.id);
      setMessages([]);
      setSources([]);
      setArtifact(null);
    } catch (e) {
      console.error("Failed to create session:", e);
    }
  }

  async function selectSession(id) {
    try {
      setSid(id);
      setArtifact(null);

      const r = await fetch(
        `${API}/api/sessions/${id}/messages`
      );

      const d = await r.json();

      setMessages(d);

      setSources(
        d.at(-1)?.metadata?.sources || []
      );
    } catch (e) {
      console.error("Failed to load session:", e);
    }
  }

  async function send() {
    if (!input.trim() || !sid || loading) return;

    const q = input.trim();

    setInput("");

    setMessages((x) => [
      ...x,
      {
        role: "user",
        content: q,
      },
    ]);

    setLoading(true);

    try {
      const r = await fetch(
        `${API}/api/sessions/${sid}/messages`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
               content: q,
               provider: provider,
             }),
        }
      );

      const d = await r.json();

      if (!r.ok) {
        throw new Error(
          d.detail || "Request failed"
        );
      }

      const isArtifactRequest =
        /essay|artifact|document|playbook|plan|html|landing page|web page|markdown/i.test(
          q
        );

      setMessages((x) => [
        ...x,
        {
          role: "assistant",
          content: isArtifactRequest
            ? "I've created the requested artifact. You can view it in the Artifact Viewer on the right."
            : d.content,
        },
      ]);

      setSources(d.sources || []);

      if (isArtifactRequest) {
        await generateArtifact(q);
      }
    } catch (e) {
      setMessages((x) => [
        ...x,
        {
          role: "assistant",
          content: `Error: ${e.message}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  async function generateArtifact(request) {
    if (!sid) return;

    const isHTML =
      /html|landing page|web page/i.test(
        request
      );

    try {
      const r = await fetch(
        `${API}/api/sessions/${sid}/artifacts`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            request,
            type: isHTML
              ? "html"
              : "markdown",
              provider: provider,
          }),
        }
      );

      if (!r.ok) {
        const errorData = await r.json().catch(() => ({}));

        throw new Error(
          errorData.detail ||
            "Artifact generation failed"
        );
      }

      const data = await r.json();

      console.log("ARTIFACT:", data);

      setArtifact(data);
    } catch (e) {
      console.error(
        "Artifact generation failed:",
        e
      );

      setMessages((x) => [
        ...x,
        {
          role: "assistant",
          content: `Artifact generation failed: ${e.message}`,
        },
      ]);
    }
  }

  async function essay() {
    if (!sid || loading) return;

    const q =
      "Turn the current grounded discussion into a Ship 30 for 30 style essay of about 1,250 words.";

    setMessages((x) => [
      ...x,
      {
        role: "user",
        content: q,
      },
    ]);

    setLoading(true);

    try {
      const r = await fetch(
        `${API}/api/sessions/${sid}/messages`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            content: q,
            provider: provider,
          }),
        }
      );

      const d = await r.json();

      if (!r.ok) {
        throw new Error(
          d.detail || "Request failed"
        );
      }

      setMessages((x) => [
        ...x,
        {
          role: "assistant",
          content:
            "I've created a Ship 30 for 30 style essay. You can view it in the Artifact Viewer on the right.",
        },
      ]);

      setSources(d.sources || []);

      await generateArtifact(
        "Create a Ship 30 for 30 style essay of about 1,250 words from the current grounded discussion."
      );
    } catch (e) {
      setMessages((x) => [
        ...x,
        {
          role: "assistant",
          content: `Error: ${e.message}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadSessions();
  }, []);

  return (
    <main className="shell">
      {/* SIDEBAR */}
      <aside className="sidebar">
        <div className="brand">
          Lenny Growth Assistant
        </div>

        <button
          onClick={newChat}
          className="new"
        >
          + New chat
        </button>

        <div className="sideTitle">
          Conversations
        </div>

        {sessions.map((s) => (
          <button
            key={s.id}
            className={`session ${
              sid === s.id ? "active" : ""
            }`}
            onClick={() =>
              selectSession(s.id)
            }
          >
            {s.title}
          </button>
        ))}

        <div className="provider">
  <div className="providerLabel">LLM Provider</div>

  <select
    value={provider}
    onChange={(e) => setProvider(e.target.value)}
    disabled={loading}
  >
    <option value="ollama">
      Local Ollama
    </option>

    <option value="anthropic">
      Cloud Claude
    </option>
  </select>

  <div className="providerStatus">
    {provider === "ollama"
      ? "● Local · llama3.2:3b"
      : "● Cloud · Claude Agent SDK"}
  </div>
</div>
      </aside>

      {/* CHAT */}
      <section className="chat">
        <header>
          <div>
            <h1>
              The Lenny Growth Assistant
            </h1>

            <p>
              Grounded answers from Lenny's
              Podcast transcripts.
            </p>
          </div>

          <button
            onClick={essay}
            disabled={loading}
          >
            Create 30 for 30
          </button>
        </header>

        <div className="messages">
          {!messages.length && (
            <div className="empty">
              <h2>
                Ask a product or growth
                question.
              </h2>

              <p>
                Try: "What are practical ways
                to improve activation?"
              </p>
            </div>
          )}

          {messages.map((m, i) => (
            <div
              key={i}
              className={`msg ${m.role}`}
            >
              <div className="role">
                {m.role === "user"
                  ? "You"
                  : "Assistant"}
              </div>

              <div
                dangerouslySetInnerHTML={{
                  __html:
                    m.role === "assistant"
                      ? marked.parse(
                          m.content
                        )
                      : m.content.replaceAll(
                          "\n",
                          "<br/>"
                        ),
                }}
              />
            </div>
          ))}

          {loading && (
            <div className="msg assistant">
              <div className="role">
                Assistant
              </div>

              Thinking…
            </div>
          )}
        </div>

        {/* COMPOSER */}
        <div className="composer">
          <textarea
            value={input}
            onChange={(e) =>
              setInput(e.target.value)
            }
            onKeyDown={(e) => {
              if (
                e.key === "Enter" &&
                !e.shiftKey
              ) {
                e.preventDefault();
                send();
              }
            }}
            placeholder="Ask about product, growth, or Lenny's advice…"
          />

          <button
            onClick={send}
            disabled={loading}
          >
            {loading ? "Thinking…" : "Send"}
          </button>
        </div>
      </section>

      {/* ARTIFACT / SOURCES PANEL */}
      <aside className="artifact">
        {/* SOURCES */}
        <div className="panelTitle">
          Sources
        </div>

        {!sources.length ? (
          <p className="muted">
            Sources from the latest grounded
            response will appear here.
          </p>
        ) : (
          sources.map((s, i) => (
            <div
              className="source"
              key={i}
            >
              <b>{s.title}</b>

              <small>
                {s.guest ||
                  "Lenny's Podcast"}
              </small>

              {s.url && (
                <a
                  href={s.url}
                  target="_blank"
                  rel="noreferrer"
                >
                  Source ↗
                </a>
              )}
            </div>
          ))
        )}

        {/* ARTIFACT VIEWER */}
        <div className="panelTitle artifactTitle">
          Artifact Viewer
        </div>

        {!artifact ? (
          <p className="muted">
            Ask for an essay, playbook,
            plan, or artifact.
          </p>
        ) : artifact.type === "html" ? (
          <iframe
            title="Generated HTML artifact"
            sandbox=""
            srcDoc={artifact.content}
            style={{
              width: "100%",
              height: "650px",
              border: "1px solid #ddd",
              borderRadius: "12px",
              background: "white",
            }}
          />
        ) : (
          <div
            className="artifactBody"
            dangerouslySetInnerHTML={{
              __html: marked.parse(
                artifact.content
              ),
            }}
          />
        )}
      </aside>
    </main>
  );
}