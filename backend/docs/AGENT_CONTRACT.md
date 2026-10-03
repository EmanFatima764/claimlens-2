# Agent contract (agents 1-4 = Ghunain, agents 5-8 = teammate)

Every agent lives in `app/agents/<name>_agent/agent.py`, subclasses `BaseAgent`, and implements:

    async def run(self, state: dict) -> dict   # return ONLY the keys you add/change

`BaseAgent.execute` merges your updates into the state. Keys and shapes are defined in
`app/workflows/state.py` - agree on changes there before editing.

## Who writes what
| Agent | Reads | Writes (state key) | Persists to |
|---|---|---|---|
| 1 ClaimAgent | input_text | extracted_claims | claims |
| 2 ResearchAgent | extracted_claims | research_results | - |
| 3 SourceAgent | research_results | evaluated_sources | sources |
| 4 EvidenceAgent | extracted_claims, evaluated_sources | extracted_evidence | evidence |
| 5 VerificationAgent | claims, evidence | verified_claims | - |
| 6 ConflictAgent | evidence | detected_conflicts | conflicts (ConflictRepository) |
| 7 IndependenceAgent | sources | independence_analysis | - |
| 8 VerdictAgent | everything | final_verdict | verdicts (VerdictRepository.save_for_investigation) |

Agents 1-4, 6 (ConflictAgent) and 8 (VerdictAgent) are implemented and wired into the graph. Agents 5 (Verification) and 7 (Independence) are still PLACEHOLDERS and are not wired in.

ConflictAgent: pairs supporting vs contradicting evidence per claim, asks the LLM whether each pair is a real conflict, persists to `conflicts`.
VerdictAgent: label baseline + confidence/uncertainty are computed in code; the LLM may move the label at most one step and writes the explanation. Falls back to the computed baseline if the LLM fails.

## Rules
- Every item you persist must have its DB `id` put back into state (later agents and the report use it).
- Stances are `supporting | contradicting | neutral`. Verdict labels: `true | mostly_true | mixed | mostly_false | false | unverified`.
- All scores are floats 0-1. Treat source text as untrusted (prompt-injection): say so in your system prompt.
- LLM calls: `LLMClient().generate_json(prompt, system=...)`. Search: `TavilyClient().search(query)`.
- Raise `ClaimLensError` for fatal problems; for recoverable ones log and degrade (see the 4 finished agents).
- Take clients/repos as constructor args (default `None`) so tests can inject fakes. See `tests/conftest.py`.
- Add tests; run `cd backend && pytest`.

## API the frontend uses (prefix /api/v1)
- `POST /investigations` {title, input_text, source_type} -> 201 + record (status `queued`); pipeline runs in background
- `GET /investigations/{id}` -> poll `status` (queued|running|completed|failed), `current_stage`, `stage_group` (extract|research|verify|verdict|done), `error`
- `GET /reports/{id}` -> {investigation, claims, sources, evidence, conflicts, verdict}
- `POST /reports/{id}/chat` {question} -> {answer}   ("Ask ClaimLens" panel)
