# AI chat team in your Discord

> Turn the AI agents **you** build into a **team** that lives in your Discord —
> they chat, **hold autonomous meetings**, and a facilitator summarizes the outcome.
> Each teammate is backed by **your own HTTP API agent** or a **local model** — mix freely.

This is a **template**. Clone it, define your team in one YAML file, set a Discord token,
and you have a running multi-agent room. No vendor lock-in, runs on your machine.

```
You: meeting How should we launch the new feature?

🗣️ Chair   Meeting started — topic: How should we launch the new feature? · 3 rounds
Ada      Lock the scope first and gate the rollout behind a staged release to limit risk.
Quill       I'll line up the schedule: a one-week QA window, then a phased open to 10% of users.
Strat     Strategically, ship the API behind a flag and measure error rates before widening.
Dash      Let's not over-plan — pick a date, run a smoke test today, and commit to it!
…(2 more rounds)…
📋 Chair   [Summary] • staged rollout • flag + metrics • fixed launch date  [Decisions] … [Next actions] …
```

---

## Why this exists

Most "AI agent" demos are a single bot answering a single prompt. Real work happens in a
**team** that argues, builds on each other, and lands a decision. This template gives you:

- 🧩 **Pluggable backends** — a teammate is either your **HTTP API agent** (the "API-ize your
  agent" path) or a **local Ollama** model. Same team, different engines.
- 🗣️ **Autonomous meetings** — `meeting <topic>` runs several rounds where each teammate speaks
  from its **own angle** (so they don't parrot each other), then a facilitator summarizes.
- 🧠 **Optional local knowledge (RAG)** — ground replies in a folder of your own `.md`/`.txt`
  notes, fully offline. No cloud, no quota.
- 🔒 **Template-safe** — secrets live in `.env`; nothing personal is committed.

---

## How it's different

There are excellent multi-agent frameworks. This one makes a specific, narrow bet:

- **Backend mixing as a first-class feature.** A single team can run a local `ollama` model, *your* deployed
  HTTP agent, and a Claude/Gemini-backed endpoint side by side — switch one teammate's backend by editing one
  YAML field. No SDK rewrite.
- **Discussion, not fan-out.** Agents take turns *in sequence*, each reading the prior turns and constrained to
  a fixed **angle**, with an explicit "don't repeat" rule — so you get build-and-rebut, then a structured
  facilitator summary. The anti-parrot mechanics are documented in
  [docs/11-technical-deep-dive.md](docs/11-technical-deep-dive.md).
- **Offline-capable & vendor-neutral.** All-`ollama` teams run with no cloud and no quota. MIT.
- **Discord-native, 1-file config.** It lives where teams already talk; the whole team is one `agents.yaml`.

| | this template | LangChain | AutoGen | CrewAI |
|---|---|---|---|---|
| Mix local + HTTP + hosted backends per agent | ✅ one YAML field | via code | ✅ | partial |
| Runs fully offline (no cloud) | ✅ all-`ollama` | ❌ | partial | ❌ |
| Turn-taking debate → summary, built in | ✅ | build it | ✅ | ✅ |
| Discord as the interface | ✅ native | ❌ | ❌ | ❌ |
| Setup to first meeting | minutes, 1 file | more involved | more involved | more involved |
| License | MIT | MIT | MIT/CC | proprietary core |

> Characteristics as of 2026 and necessarily simplified — these frameworks are broader and evolve. Use
> LangChain/AutoGen/CrewAI for general-purpose or research-grade orchestration; use **this** when you want a
> Discord-native, offline-capable team that mixes your own agents and reaches a decision. They're complementary —
> an `http` teammate here can itself be a LangChain/AutoGen agent behind `POST {message} → {reply}`.

---

## 60-second quick start

```bash
git clone https://github.com/<you>/AI-chat-team-in-your-Discord
cd AI-chat-team-in-your-Discord
pip install -r requirements.txt

cp config.example.env .env          # paste your DISCORD_BOT_TOKEN
cp agents.example.yaml agents.yaml  # define your team (see below)

# (optional, for local teammates)  ollama pull llama3
python bot/discord_team_bot.py
```

Then in Discord: type anything to chat, or `meeting <topic>` to start a discussion.

> New to Discord bots? See **[docs/02-discord-setup.md](docs/02-discord-setup.md)** for the
> token + invite + "Message Content Intent" steps.

---

## 🤖 Or: hand it to Claude Code and let it build

This repo ships a build brief (**[CLAUDE.md](CLAUDE.md)**) that an AI coding agent reads automatically.
Clone the repo, open it in Claude Code, and paste:

> *"Read CLAUDE.md and build this project. I want a team called **Ada** (calm, risk & discipline),
> **Quill** (scheduling & coordination), and **Strat** (strategy) — Ada and Quill local, Strat is my API agent.
> Ask me for the Discord token and Strat's endpoint when you reach those steps."*

Claude will install deps, write `agents.yaml`, verify each teammate offline, and stop to ask you for the
few things only you can provide (token, endpoints, keys). What it can't do is yours, listed in one place:
**[docs/10-you-the-human.md](docs/10-you-the-human.md)**. The contract it builds against (and consults when
fixing) is **[docs/00-spec.md](docs/00-spec.md)**.

---

## Define your team (`agents.yaml`)

```yaml
team:
  - name: Ada                       # local model teammate
    backend: ollama
    model: llama3
    angle: discipline and risk
    persona: "You are Ada, a calm secretary AI. 1-3 sentences."

  - name: Strat                          # YOUR agent, exposed as an HTTP API
    backend: http
    endpoint: "https://your-agent.example.com/api/chat"
    request_key: message             # body field for the user text
    response_key: reply              # JSON field to read back
    angle: strategy and judgement

summarizer: { name: Chair, backend: ollama, model: llama3 }
meeting:  { rounds: 3 }
```

The `http` backend is how you plug in an agent you built and deployed yourself — any endpoint
that accepts `{"message": "..."}` and returns `{"reply": "..."}`. Field names are configurable,
and headers support `${ENV_VAR}` substitution for API keys. See
**[docs/04-api-agents.md](docs/04-api-agents.md)**.

---

## The journey, end to end

This template is the "team" half of a larger build. The full path — **build an agent → expose it
as an API → assemble a team → run it in Discord → test it** — is documented so anyone can
reproduce it:

| Step | Doc |
|---|---|
| Build brief for Claude Code | [CLAUDE.md](CLAUDE.md) |
| Spec, invariants & troubleshooting | [docs/00-spec.md](docs/00-spec.md) |
| What only you (the human) must do | [docs/10-you-the-human.md](docs/10-you-the-human.md) |
| What you're building | [docs/01-concept.md](docs/01-concept.md) |
| Discord bot: token, invite, intents | [docs/02-discord-setup.md](docs/02-discord-setup.md) |
| Define your team | [docs/03-define-your-team.md](docs/03-define-your-team.md) |
| API-ize your own agent | [docs/04-api-agents.md](docs/04-api-agents.md) |
| Autonomous meeting mode | [docs/05-meeting-mode.md](docs/05-meeting-mode.md) |
| Local knowledge (RAG) | [docs/06-local-knowledge-rag.md](docs/06-local-knowledge-rag.md) |
| Optional: a Google Apps Script hub | [docs/07-gas-hub-optional.md](docs/07-gas-hub-optional.md) |
| Test the team | [docs/08-testing.md](docs/08-testing.md) |
| Reproduce from scratch | [docs/09-reproduce-from-scratch.md](docs/09-reproduce-from-scratch.md) |
| **Technical deep dive** (meeting algorithm) | [docs/11-technical-deep-dive.md](docs/11-technical-deep-dive.md) |
| **Scalability, cost & deployment** | [docs/12-scalability.md](docs/12-scalability.md) |

> **Building the individual agents** (each character's own design and deployment) is covered in a
> companion guide on building a single agent. This repo focuses on turning agents into a *team*.

Reusable, copy-pasteable **skills** for an AI coding assistant live in [`skills/`](skills/).

---

## Example team setups

These are **example configurations** to copy into `agents.yaml` — illustrative, not case studies.

### Product launch decision
A team that reaches a go/no-go with explicit trade-offs.
```yaml
team:
  - name: Ada
    backend: ollama
    model: llama3
    angle: "risk, compliance, what can go wrong"
  - name: Quill
    backend: ollama
    model: llama3
    angle: "scheduling and execution feasibility"
  - name: Strat
    backend: http
    endpoint: "https://your-strategist.example.com/api/chat"
    angle: "business strategy and differentiation"
summarizer: { name: Chair, backend: ollama, model: llama3 }
meeting: { rounds: 3 }
```
```
You: meeting How should we launch the new feature?
🗣️ Chair  Meeting started — topic: How should we launch the new feature? · 3 rounds
Ada      Gate the rollout behind a staged release; lock scope first to limit risk.
Quill    Plan a one-week QA window, then open to 10% of users before full release.
Strat    Ship behind a flag and measure error rates before widening — protects the brand.
…(more rounds)…
📋 Chair  [Summary] staged rollout · flag + metrics · fixed date  [Decisions] … [Next actions] …
```

### Research-paper review
Three reviewers with opposing mandates, then a synthesized verdict.
```yaml
team:
  - name: Skeptic
    backend: ollama
    model: llama3
    angle: "methodological weaknesses and threats to validity"
  - name: Enthusiast
    backend: ollama
    model: llama3
    angle: "novelty and what it unlocks"
  - name: Methodologist
    backend: http
    endpoint: "https://your-agent.example.com/api/chat"
    angle: "rigor, baselines, and reproducibility"
summarizer: { name: Chair, backend: ollama, model: llama3 }
meeting: { rounds: 2 }
```
Paste the abstract as the topic (`meeting <abstract>`) to get strengths, weaknesses, and a verdict.

---

## Architecture

```
Discord channel
   │  message  /  "meeting <topic>"
   ▼
discord_team_bot.py
   ├─ for each teammate in agents.yaml:
   │     ├─ backend: ollama  → local model (offline)
   │     └─ backend: http    → YOUR deployed API agent  (POST {message} → {reply})
   ├─ meeting mode: N rounds, each speaks from its own angle → facilitator summary
   └─ optional: inject context from a local folder of notes (RAG, offline)
```

No database required. No cloud LLM required. Bring your own agents.

---

## License

MIT — see [LICENSE](LICENSE). Use it, fork it, ship your own team.
