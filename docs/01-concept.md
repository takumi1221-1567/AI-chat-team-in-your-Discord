# 01 · What you're building

A small, opinionated framework for running **a team of AI agents inside a Discord channel**.

## The mental model

- A **teammate** is one AI persona with a **backend** (a local model, or your own HTTP API agent).
- A **team** is a list of teammates defined in `agents.yaml`.
- A **facilitator** (the `summarizer`) wraps up meetings.
- The **bot** (`bot/discord_team_bot.py`) listens to a Discord channel and routes messages to the team.

## Two interaction modes

1. **Chat** — you type a message; each teammate replies in character (skipping ones with nothing to add).
2. **Meeting** — you type `meeting <topic>`; teammates discuss for several rounds, each from a distinct
   **angle**, building on what others said. Then the facilitator posts a structured summary.

## Design choices (and why)

- **Pluggable backends.** The point of the project is to take agents *you* built and turn them into a
  team. So a teammate can be a deployed HTTP endpoint (`backend: http`) or a local model
  (`backend: ollama`). You can migrate one teammate at a time.
- **Angles prevent parroting.** Small models copy the previous speaker. Giving each teammate a fixed
  "angle" and feeding the running transcript as plain text (not as chat turns to imitate) keeps the
  discussion diverse.
- **Local-first is the default.** With `backend: ollama` and `knowledge.enabled: false → true` over a
  local folder, the whole thing runs offline with no cloud cost or quota.
- **Template-safe.** Secrets live in `.env`; your real team file (`agents.yaml`) is git-ignored so you
  can point it at private endpoints.

## What this repo is *not*

It does not teach you how to build each individual agent (model choice, fine-tuning, deployment of one
character). That belongs to the companion project **My agent**. Here, agents already exist — we make
them a team.

Next: **[02-discord-setup.md](02-discord-setup.md)**.
