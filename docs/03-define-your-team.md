# 03 · Define your team

Everything about who is on the team lives in **`agents.yaml`** (copy it from
`agents.example.yaml`). No code changes needed to add, remove, or re-tune a teammate.

## Teammate fields

| Field | Required | Meaning |
|---|---|---|
| `name` | ✅ | Display name (shown as the embed author) |
| `backend` | ✅ | `ollama` (local model) or `http` (your API agent) |
| `persona` | – | System prompt / steering for this teammate |
| `angle` | – | The one perspective they speak from in meetings (prevents parroting) |
| `color` | – | Hex (e.g. `"2962ff"`) for the Discord embed stripe |
| **ollama:** `model` | for ollama | Ollama model name, e.g. `llama3` |
| **http:** `endpoint` | for http | URL of your agent |
| **http:** `request_key` | – | Body field for the user text (default `message`) |
| **http:** `response_key` | – | JSON field to read back (default `reply`) |
| **http:** `headers` | – | Extra headers; `${ENV_VAR}` is substituted from the environment |
| **http:** `extra_body` | – | Extra JSON fields to send (e.g. a fixed `user_id`) |

## Example: a mixed team

```yaml
team:
  - name: Ada
    backend: ollama
    model: llama3
    angle: discipline, accountability, risk
    persona: "You are Ada, a calm secretary AI. 1-3 sentences, no preamble."

  - name: Strat
    backend: http
    endpoint: "https://your-agent.example.com/api/chat"
    request_key: message
    response_key: reply
    headers:
      Authorization: "Bearer ${AGENT_TOKEN}"   # AGENT_TOKEN comes from .env
    angle: strategy, technology, risk assessment

summarizer:
  name: Chair
  backend: ollama
  model: llama3

meeting:
  rounds: 3
  start: ["meeting", "会議"]
  end:   ["done", "終わり"]
```

## Tips

- **Keep personas short.** 2-3 sentences. Long personas make small local models drift.
- **Give every teammate a distinct `angle`.** This is what makes meetings feel like a real discussion.
- **Language:** tell the persona which language to answer in (e.g. "Answer in Japanese only.") if you
  want a non-English team. Small models honor a final, explicit instruction best.
- **Silence is fine.** If a teammate returns nothing useful (or your API errors), it's skipped — the
  conversation continues.

Next: **[04-api-agents.md](04-api-agents.md)**.
