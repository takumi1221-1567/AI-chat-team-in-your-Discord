# 00 · Spec & troubleshooting reference (read this when fixing)

The authoritative contract for the bot. When something misbehaves, reconcile against this.

## Components & responsibilities

| File | Responsibility |
|---|---|
| `bot/discord_team_bot.py` | Load config, route Discord messages, run chat/meeting, call backends |
| `agents.yaml` (from `agents.example.yaml`) | The team: teammates + summarizer + meeting + knowledge |
| `.env` (from `config.example.env`) | Secrets & runtime config (token, channel, ollama host) |
| `docs/`, `skills/` | Human + AI guidance |

## Configuration contract (`agents.yaml`)
- `team[]`: each has `name`, `backend` (`ollama`|`http`), optional `persona`, `angle`, `color`.
  - `ollama`: `model` (must be pulled).
  - `http`: `endpoint`; optional `request_key` (default `message`), `response_key` (default `reply`),
    `headers` (supports `${ENV}`), `extra_body`.
- `summarizer`: `name`, `backend`, `model` (used for the meeting wrap-up).
- `meeting`: `rounds` (int), `start`/`end` (trigger word lists).
- `knowledge`: `enabled` (bool), `dirs` (list), optional `folder` (path-substring filter).

## Runtime contract (env)
`DISCORD_BOT_TOKEN` (required), `DISCORD_CHANNEL_ID` (0=all), `OLLAMA_HOST`, `AGENTS_FILE`.
`http` teammate secrets are arbitrary `${VAR}` names referenced in `headers`.

## Backend contracts
- **ollama**: `POST {OLLAMA_HOST}/api/chat` with `{model, messages:[{role,content}], stream:false}` →
  read `message.content`.
- **http (your agent)**: `POST endpoint` with `{request_key: text, ...extra_body}` and `headers` →
  read `data[response_key]`. Must tolerate non-200/timeout by returning empty (skip the turn).

## Invariants (must stay true)
1. `bot.run()` only under `if __name__ == "__main__":` so the module can be imported for tests.
2. A failing/slow teammate is **skipped**, never crashes `on_message`.
3. Secrets never enter git or get echoed back in full.
4. Meeting turns receive prior turns as **plain text in the prompt**, not as assistant messages.
5. Each teammate speaks from its `angle` only and is told **not to repeat** others.
6. Replies are cleaned of leaked `[Name]:` / `【Name】` prefixes.

## Troubleshooting (symptoms → cause → fix)

| Symptom | Cause | Fix |
|---|---|---|
| Bot online, never replies | Message Content Intent off / channel filter mismatch | Enable intent in Dev Portal; set `DISCORD_CHANNEL_ID=0` or the right id |
| One teammate always silent | `http` endpoint errors, or `ollama` model not pulled | `curl` the endpoint; `ollama pull <model>`; check the model name exists in `ollama list` |
| **Empty replies from a model you "have"** | Model name in `agents.yaml` not actually installed (e.g. `gemma2:2b`) | `ollama list`; pull it or switch the teammate to an installed model |
| Everyone parrots the first speaker | personas too long / angles too similar / history fed as chat turns | Shorten personas; sharpen `angle`; keep transcript as plain text (invariant #4) |
| Small model drifts to English | weak language steering | Put the language rule at the **end** of the persona ("Answer in Japanese only. No English."); keep injected context in the target language |
| RAG returns useless `tags:` snippets | YAML frontmatter not stripped | Strip frontmatter, snippet around the keyword hit (see `skills/local-knowledge-rag`) |
| RAG/folder filter matches nothing (macOS, non-ASCII) | filenames are NFD, your string is NFC | `unicodedata.normalize("NFC", path)` on load |
| `http` agent returns but field is empty | wrong `response_key` (e.g. API returns `answer` not `reply`) | set `response_key` to the actual field; verify with `curl` |
| `ModuleNotFoundError: yaml` | PyYAML missing | `pip install pyyaml` (or use a `.json` agents file) |
| Deployed agent (Cloudflare Pages) ignores a newly set secret | Pages applies secrets to **new** deployments | redeploy after `wrangler pages secret put` |
| Image/heavy model 429 | free tier / billing | use a text model; for Gemini set `thinkingConfig.thinkingBudget=0` to cut latency |

## Performance notes
- Meeting LLM calls ≈ `teammates × rounds (+1 summary)`. Keep `rounds` 2–3 if any teammate is metered.
- Local Ollama meetings are free; `http` teammates cost per call.
