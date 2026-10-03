import { NextResponse } from "next/server";
import type { ReportData } from "@/types/report";

export const runtime = "nodejs";

type Msg = { role: "user" | "assistant"; content: string };

const GROQ_URL = "https://api.groq.com/openai/v1/chat/completions";
const DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile";

function buildContext(report: ReportData): string {
  const sources = report.sources
    .map((s) => `[${s.id}] ${s.title} (${s.publisher}, type=${s.sourceType}, quality=${Math.round(s.qualityScore * 100)}%)`)
    .join("\n");
  const evidence = report.evidence
    .map((e) => `[${e.id}] (${e.type}, from ${e.sourceId}, confidence=${Math.round(e.confidence * 100)}%) ${e.text}`)
    .join("\n");
  const conflicts = report.conflicts
    .map((c) => `[${c.id}] ${c.evidenceAId} vs ${c.evidenceBId} (${c.type}, severity=${Math.round(c.severity * 100)}%): ${c.explanation}`)
    .join("\n");

  return [
    `CLAIM: ${report.claimText}`,
    `VERDICT: ${report.verdict.label} | confidence ${Math.round(report.verdict.confidence * 100)}% | uncertainty ${Math.round(report.verdict.uncertainty * 100)}% | human review required: ${report.verdict.reviewRequired}`,
    `VERDICT REASONING: ${report.verdict.explanation}`,
    `SUMMARY: ${report.summary}`,
    `SOURCES:\n${sources || "none"}`,
    `EVIDENCE:\n${evidence || "none"}`,
    `CONFLICTS:\n${conflicts || "none"}`,
  ].join("\n\n");
}

const SYSTEM_PROMPT = `You are the ClaimLens report assistant. You explain a fact-checking report to the user.
Rules:
- Answer ONLY from the report below. If the report does not contain the answer, say so plainly. Never invent sources, numbers or facts.
- Cite the report items you rely on using their ids in square brackets, e.g. [ev-1], [src-2], [conf-1].
- Be honest about uncertainty: mention the confidence/uncertainty values when explaining the verdict.
- If the user asks "why is it fake/false", explain what the evidence actually shows, even if the verdict is not "false".
- Keep answers short (under 150 words), clear, and in the user's language.`;

function fallbackAnswer(report: ReportData, question: string): string {
  const v = report.verdict;
  const reason = v.explanation || "The verdict is based on the report evidence and confidence scores.";

  return (
    `The verdict is "${v.label}" with ${Math.round(v.confidence * 100)}% confidence and ${Math.round(v.uncertainty * 100)}% uncertainty. ` +
    `${reason} ` +
    `This response is a local fallback because the Groq key/model is not configured yet. Question: "${question.slice(0, 120)}".`
  );
}

export async function POST(req: Request) {
  let body: { report?: ReportData; messages?: Msg[] };
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  const report = body.report;
  const messages = (body.messages ?? [])
    .filter((m) => (m.role === "user" || m.role === "assistant") && typeof m.content === "string")
    .slice(-10)
    .map((m) => ({ role: m.role, content: m.content.slice(0, 1500) }));

  if (!report || !messages.length) {
    return NextResponse.json({ error: "Missing report or messages" }, { status: 400 });
  }

  const apiKey = process.env.GROQ_API_KEY?.trim();
  const lastQuestion = messages[messages.length - 1].content;
  const model = process.env.GROQ_MODEL?.trim() || DEFAULT_GROQ_MODEL;

  if (!apiKey) {
    return NextResponse.json({ answer: fallbackAnswer(report, lastQuestion), mock: true });
  }

  try {
    const res = await fetch(GROQ_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${apiKey}` },
      body: JSON.stringify({
        model,
        temperature: 0.2,
        max_tokens: 500,
        messages: [
          { role: "system", content: `${SYSTEM_PROMPT}\n\n--- REPORT ---\n${buildContext(report)}` },
          ...messages,
        ],
      }),
    });

    if (!res.ok) {
      const detail = await res.text();
      console.error("Groq error", res.status, detail.slice(0, 300));

      return NextResponse.json({
        answer: fallbackAnswer(report, lastQuestion),
        mock: true,
        warning: `Groq request failed (${res.status}). Set GROQ_API_KEY and GROQ_MODEL to enable live answers.`,
      });
    }

    const data = await res.json();
    const answer: string = data?.choices?.[0]?.message?.content?.trim() || "No answer returned.";
    return NextResponse.json({ answer });
  } catch (err) {
    console.error("Chat route error", err);
    return NextResponse.json({
      answer: fallbackAnswer(report, lastQuestion),
      mock: true,
      warning: "Could not reach Groq. Falling back to a local explanation.",
    });
  }
}
