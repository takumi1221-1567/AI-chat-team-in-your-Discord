---
name: agent-api-wrapper
description: Expose any AI agent as a tiny HTTP API (POST {message} -> {reply}) and plug it into a team as a pluggable backend. Use when "API-izing" an agent or connecting one to the bot.
---

# Agent API wrapper

Turn an agent into a network-callable teammate with a minimal, stable contract.

## The contract
```
POST <endpoint>   Content-Type: application/json
{ "message": "<text>" }  ->  { "reply": "<text>" }
```
Keep it blocking (single JSON response). Field names may differ; make them configurable on the caller
side (`request_key` / `response_key`) instead of changing the API.

## Reference (Cloudflare Pages Function)
```js
export async function onRequest({ request, env }) {
  if (request.method !== "POST") return new Response("405", { status: 405 });
  const { message } = await request.json();
  const reply = await yourModel(message, env);     // any backend
  return new Response(JSON.stringify({ reply }), { headers: { "Content-Type": "application/json" } });
}
```
Equivalent in FastAPI/Express/Lambda is fine — just return `{"reply": "..."}`.

## Plug into a team (agents.yaml)
```yaml
- name: Strat
  backend: http
  endpoint: "https://agent.example.workers.dev/api/chat"
  request_key: message       # adapt to your API (e.g. "query")
  response_key: reply        # adapt to your API (e.g. "answer")
  headers: { Authorization: "Bearer ${AGENT_TOKEN}" }   # ${VAR} from .env
```

## Rules
- **Secrets** go in server env or as `${VAR}` headers — never in the repo.
- **Fail soft**: callers should treat timeouts/non-200 as "no reply this turn," not a crash.
- **CORS** only matters for browsers; server-to-server calls don't need it (but add `*` if testing from a page).
- Keep latency sane (a few seconds); meetings call this N×R times.
