"use client";

import { useEffect, useRef, useState } from "react";
import type { ReportData } from "@/types/report";

type Msg = { role: "user" | "assistant"; content: string };

const CITE = /(\[(?:ev|src|conf)-\d+\])/g;
const IS_CITE = /^\[(?:ev|src|conf)-\d+\]$/;

function renderWithCitations(text: string) {
  return text.split(CITE).map((part, i) =>
    IS_CITE.test(part) ? (
      <span key={i} className="cite-tag">
        {part.slice(1, -1)}
      </span>
    ) : (
      <span key={i}>{part}</span>
    )
  );
}

export default function ReportChat({ report }: { report: ReportData }) {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading, open]);

  const suggestions = [
    `Why is this rated "${report.verdict.label}"?`,
    "Which source is least reliable?",
    "What is the strongest counter-evidence?",
    "What would change this verdict?",
  ];

  async function send(text: string) {
    const q = text.trim();
    if (!q || loading) return;
    const next: Msg[] = [...messages, { role: "user", content: q }];
    setMessages(next);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ report, messages: next }),
      });
      const data = await res.json();
      setMessages([...next, { role: "assistant", content: data.answer ?? data.error ?? "Something went wrong." }]);
    } catch {
      setMessages([...next, { role: "assistant", content: "Could not reach the chat service. Please restart the frontend or check your env configuration." }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      {!open && (
        <button
          onClick={() => setOpen(true)}
          style={{
            position: "fixed",
            right: 20,
            bottom: 20,
            zIndex: 50,
            border: "0",
            borderRadius: 999,
            padding: "0.9rem 1.2rem",
            fontWeight: 800,
            color: "white",
            background: "linear-gradient(135deg, #4f7cff, #62d7ff)",
            boxShadow: "0 20px 40px rgba(79,124,255,0.42)",
            cursor: "pointer",
          }}
        >
          💬 Ask about this report
        </button>
      )}

      {open && (
        <div className="chat-panel">
          <div className="chat-header">
            <div>
              <strong>Ask ClaimLens</strong>
              <small>Answers only from the current evidence set</small>
            </div>
            <button className="chat-close" onClick={() => setOpen(false)} aria-label="Close chat">
              ×
            </button>
          </div>

          <div className="chat-messages">
            {messages.length === 0 && (
              <div className="chat-suggestions">
                <p style={{ margin: 0, color: "#cddcf7" }}>Ask why this claim received its verdict, or probe the evidence.</p>
                {suggestions.map((s) => (
                  <button key={s} className="suggestion-chip" onClick={() => send(s)}>
                    {s}
                  </button>
                ))}
              </div>
            )}

            {messages.map((m, i) => (
              <div key={i} className={`message ${m.role}`}>
                {m.role === "assistant" ? renderWithCitations(m.content) : m.content}
              </div>
            ))}

            {loading && <div style={{ color: "#cddcf7" }}>Thinking…</div>}
            <div ref={endRef} />
          </div>

          <div className="chat-input-wrap">
            <input
              className="chat-input"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") send(input);
              }}
              placeholder="Why is this report rated this way?"
            />
            <button className="chat-send" onClick={() => send(input)} disabled={loading || !input.trim()}>
              Send
            </button>
          </div>
        </div>
      )}
    </>
  );
}
