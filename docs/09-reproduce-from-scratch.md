# 09 · Reproduce from scratch

The whole journey, in order, so anyone can rebuild it. Each step links to the detail doc.

## The path

```
build an agent  →  expose it as an API  →  assemble a team  →  run it in Discord  →  test
   (build one agent)         (this repo · 04)        (03)                (02 · 05)            (08)
```

### Step 0 — Build your agents
Decide who is on the team and what each one is good at. Building each individual agent (its model,
persona, deployment) is covered in a companion guide on building a single agent. For a first run you can skip
this and use local `ollama` teammates with just a `persona`.

### Step 1 — Expose each agent as an API (for `http` teammates)
Give every "remote" teammate a single endpoint:
`POST {message} → {reply}`. See **[04-api-agents.md](04-api-agents.md)** for a copy-paste
Cloudflare Pages Function. Local teammates skip this — they run on Ollama.

### Step 2 — Create the Discord bot
Token + invite + **Message Content Intent**. See **[02-discord-setup.md](02-discord-setup.md)**.
```bash
cp config.example.env .env      # paste DISCORD_BOT_TOKEN
```

### Step 3 — Define the team
```bash
cp agents.example.yaml agents.yaml
```
Add each teammate (`backend: ollama` or `backend: http`), a short `persona`, and a distinct `angle`.
Pick a `summarizer`. See **[03-define-your-team.md](03-define-your-team.md)**.

### Step 4 — (Optional) Wire in local knowledge
Point `knowledge.dirs` at a folder of notes and set `enabled: true` to ground replies offline.
See **[06-local-knowledge-rag.md](06-local-knowledge-rag.md)**.

### Step 5 — Run
```bash
pip install -r requirements.txt
ollama pull llama3            # if you use local teammates
python bot/discord_team_bot.py
```

### Step 6 — Use it
- Chat: type anything → teammates reply.
- Meeting: `meeting <topic>` → rounds of discussion → summary.
See **[05-meeting-mode.md](05-meeting-mode.md)**.

### Step 7 — Test & keep it running
Offline tests and troubleshooting: **[08-testing.md](08-testing.md)**.
Run it 24/7 with launchd / systemd / Docker: **[02-discord-setup.md](02-discord-setup.md)**.

## Checklist

- [ ] `.env` has `DISCORD_BOT_TOKEN`; Message Content Intent enabled
- [ ] `agents.yaml` lists each teammate with a backend + persona + angle
- [ ] `http` endpoints answer `{"message"} → {"reply"}` (verified with curl)
- [ ] `ollama pull <model>` done for every local teammate
- [ ] bot prints `✅ Logged in …` and replies in the channel
- [ ] `meeting <topic>` produces rounds + a summary

That's a reproducible AI chat team in your Discord.
