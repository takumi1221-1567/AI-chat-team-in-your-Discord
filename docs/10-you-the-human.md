# 10 · You, the human — what only you can do

Claude Code (or any AI) can write all the code and wire everything up. But a few things require **you**
— an account, a browser login, a payment method, or running software on your own machine. This is your
short, complete checklist, with how to obtain each.

## Your checklist

- [ ] **Discord bot token** — only you can create it (it's tied to your Discord account).
- [ ] **Enable Message Content Intent** — a toggle in your Developer Portal.
- [ ] **Invite the bot to your server** — you must authorize it.
- [ ] **Install & run Ollama** (only if you use `backend: ollama` teammates).
- [ ] **Endpoints for your `http` teammates** — the agents *you* built and deployed.
- [ ] **API keys** those endpoints need — paste into `.env`.
- [ ] **Run the bot on your machine** (and optionally keep it alive).

---

## How to obtain each

### 1. Discord bot token (required)
1. https://discord.com/developers/applications → **New Application** → name it.
2. **Bot** tab → **Reset Token** → **Copy**. Paste into `.env`:
   `DISCORD_BOT_TOKEN=...`
3. Same tab → **Privileged Gateway Intents** → turn ON **MESSAGE CONTENT INTENT**. (Without this the bot
   can't read messages and looks dead.)
> Treat the token like a password. If it leaks, click **Reset Token** to invalidate it.

### 2. Invite the bot (required)
**OAuth2 → URL Generator** → scope `bot` → permissions: *View Channels, Send Messages, Read Message
History, Embed Links* → open the generated URL → pick your server → **Authorize**.

### 3. Ollama (only for local teammates)
- Install: https://ollama.com/download (macOS app, or `curl -fsSL https://ollama.com/install.sh | sh` on Linux).
- Start it (the app, or `ollama serve`).
- Pull each model your team uses: `ollama pull llama3` (and any others in `agents.yaml`).
- Verify: `ollama list` shows them; `curl -s localhost:11434/api/tags` responds.

### 4. Your `http` teammates' endpoints (only if you use them)
Each `backend: http` teammate is **an agent you built and deployed yourself** — any URL that answers
`POST {"message": "..."} → {"reply": "..."}` (field names configurable). To create one, see
[04-api-agents.md](04-api-agents.md) (copy-paste Cloudflare Pages Function). You provide Claude Code with:
- the **endpoint URL**, and
- the **request/response field names** if they differ (e.g. `query` / `answer`), and
- any **API key** the endpoint needs → put it in `.env` (e.g. `X_AGENT_TOKEN=...`) and reference it in
  `agents.yaml` as `headers: { Authorization: "Bearer ${X_AGENT_TOKEN}" }`.
> Don't have any yet? Start with all `backend: ollama` teammates — no endpoints needed.

### 5. Run it
```bash
pip install -r requirements.txt
python bot/discord_team_bot.py     # expect: ✅ Logged in …
```
Keep it running 24/7 (optional): launchd / systemd / Docker — see [02-discord-setup.md](02-discord-setup.md).

---

## What you do NOT need to do
- Write any Python — Claude Code handles the bot and config.
- Set up a database or vector store — local knowledge is just a folder of files (optional).
- Pay for a cloud LLM — a fully-local team (Ollama) has no per-call cost.

## Handing it to Claude Code
Paste this once, in the repo:
> *"Read CLAUDE.md and build this project. I want a team called [names + what each is good at].
> Ask me for the Discord token and any agent endpoints when you reach those steps."*

Claude will do the rest and stop to ask you for the items above when it needs them.
