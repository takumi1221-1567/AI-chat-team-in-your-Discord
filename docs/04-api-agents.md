# 04 · API-ize your own agent

The `http` backend is the heart of this template: a teammate can be **any agent you built and
deployed**, as long as it speaks a tiny HTTP contract.

## The contract

```
POST <endpoint>
Content-Type: application/json

{ "message": "<the user or meeting prompt>" }
        ↓
{ "reply": "<the agent's answer>" }
```

That's it. Field names are configurable per teammate (`request_key` / `response_key`), so you can
adapt to an existing API without changing it.

## Minimal reference implementation (Cloudflare Pages Function)

`functions/api/chat.js` — deploy with `wrangler pages deploy`:

```js
export async function onRequest({ request, env }) {
  if (request.method !== "POST") return new Response("Method Not Allowed", { status: 405 });
  const { message } = await request.json();

  // call whatever model/logic your agent uses…
  const res = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent?key=${env.GEMINI_API_KEY}`,
    { method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        systemInstruction: { parts: [{ text: "You are Strat, a calm strategist. 1-3 sentences." }] },
        contents: [{ role: "user", parts: [{ text: message }] }],
        generationConfig: { thinkingConfig: { thinkingBudget: 0 } },
      }) });
  const data = await res.json();
  const reply = (data?.candidates?.[0]?.content?.parts || []).map(p => p.text).join("").trim();

  return new Response(JSON.stringify({ reply }), { headers: { "Content-Type": "application/json" } });
}
```

Any stack works (FastAPI, Express, a Worker, a Lambda) — return `{"reply": "..."}`.

## Wire it into the team

```yaml
- name: Strat
  backend: http
  endpoint: "https://agent.example.workers.dev/api/chat"
  request_key: message      # change if your API expects e.g. "query"
  response_key: reply       # change if your API returns e.g. "answer"
  headers:
    Authorization: "Bearer ${AGENT_TOKEN}"   # put AGENT_TOKEN in .env
```

## Adapting to a different shape

Already have an API like `{"query": "..."} → {"answer": "..."}`? No code change:

```yaml
  request_key: query
  response_key: answer
```

Need a fixed extra field (session id, model name)? Use `extra_body`:

```yaml
  extra_body:
    user_id: discord-team
```

## Notes

- **Secrets stay out of git.** Reference them as `${VAR}` in `headers`; define `VAR` in `.env`.
- **Timeouts/errors are swallowed** so one slow agent never freezes the room — it's just skipped that turn.
- **Streaming isn't required.** The bot reads a single JSON response (blocking is simplest and robust).

Next: **[05-meeting-mode.md](05-meeting-mode.md)**.
