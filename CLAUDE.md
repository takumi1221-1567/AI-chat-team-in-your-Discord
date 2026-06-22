# CLAUDE.md — build brief for Claude Code

You are an AI engineer. This repository is a **template** for running a team of AI agents in Discord.
Your job: take it from "cloned template" to "a working team in the user's Discord," **autonomously**,
pausing only to ask the human for the few things only they can provide.

Read this file first. Then read `docs/00-spec.md` (the contract) and `README.md`.

## Mission
Stand up `bot/discord_team_bot.py` with a real `agents.yaml`, verify it offline, and get it replying in
the user's Discord channel — including `meeting <topic>` producing multiple rounds + a summary.

## Build order (do these in sequence; verify each before moving on)
1. **Install deps**: `pip install -r requirements.txt`. If `ollama` is needed (any `backend: ollama`
   teammate), confirm Ollama is running (`curl -s localhost:11434/api/tags`) and `ollama pull` each model.
2. **Create config**: `cp config.example.env .env` and `cp agents.example.yaml agents.yaml`.
3. **Define the team** in `agents.yaml` from what the user wants (names, personas, angles, backends).
   For `http` teammates you need each endpoint — **ask the human** (see "Ask the human" below).
4. **Offline verify** (no Discord needed): follow `docs/08-testing.md` — import the module and call
   `ask_agent` for each teammate; dry-run one meeting round. Fix issues using `docs/00-spec.md`.
5. **Discord**: the human must create the bot + token + enable Message Content Intent + invite it
   (`docs/02-discord-setup.md`). Once `DISCORD_BOT_TOKEN` is in `.env`, run `python bot/discord_team_bot.py`
   and confirm `✅ Logged in …`.
6. **Acceptance**: a normal message yields per-teammate replies; `meeting <topic>` yields distinct rounds
   + a `[Summary]/[Decisions]/[Next actions]` embed. See "Definition of done."

## Ask the human (you cannot do these — request them explicitly, then continue)
- **Discord bot token** + enabling **Message Content Intent** + inviting the bot (guide them with `docs/02`).
- **Endpoints for any `http` teammates** (their own deployed agents answering `{message}→{reply}`), and any
  **API keys** those need (they go in `.env`, referenced as `${VAR}` in `agents.yaml` headers).
- **Permission/credentials to install or run things on their machine** (Ollama, running the bot, launchd).
- Anything requiring a browser login, a paid account, or a payment method.
If a step is blocked on one of these, state exactly what you need and how to get it, then proceed with
everything else that is unblocked.

## Guardrails (do not violate)
- **Never commit secrets.** `.env` and the real `agents.yaml` are git-ignored — keep them that way. Only
  `*.example.*` files are committed. Never print a full token/key back to the user.
- **Don't invent endpoints.** If you don't have a teammate's URL, leave a `backend: ollama` placeholder or
  ask; never hardcode a guessed URL.
- **Keep it runnable at every step.** Prefer small, verified changes. Don't break the example so a fresh
  clone still works.
- **Fail soft.** A teammate that errors or times out must be skipped, never crash the bot.
- If this repo is under git and you commit, set the author to the human (their `git config`), and do not
  add any third party as a contributor.

## Definition of done
- [ ] `agents.yaml` exists with ≥1 teammate; every `http` endpoint verified with `curl` (`{message}→{reply}`).
- [ ] Every `backend: ollama` model is pulled and responds.
- [ ] Offline test (`docs/08`) shows each teammate returns a non-empty, in-language, distinct reply.
- [ ] Bot prints `✅ Logged in …` and replies to a message in the channel.
- [ ] `meeting <topic>` runs `meeting.rounds` rounds with distinct voices + a structured summary.
- [ ] No secret is committed; a fresh clone + `pip install` + `.env` still runs.

## Where things live
- Contract & invariants & troubleshooting → `docs/00-spec.md`
- What the human must provide/obtain → `docs/10-you-the-human.md`
- Each topic (setup, team, API agents, meetings, RAG, GAS, testing, reproduce) → `docs/01`–`09`
- Reusable how-to for sub-tasks → `skills/*/SKILL.md`
