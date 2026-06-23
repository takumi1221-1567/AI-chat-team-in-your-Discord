# 12 · Scalability, cost & deployment

> The numbers below are a **cost model and rough guidance**, not a published benchmark. Actual latency and
> tokens depend entirely on your models, hardware, and network. Measure your own setup before relying on it.

## The cost model (this you can rely on — it's just counting calls)

A meeting makes a deterministic number of model calls:

```
model calls = (teammates × rounds) + 1 summary
tokens      ≈ Σ over calls of (prompt + completion)
            ≈ (teammates × rounds) × (windowed_transcript + persona + completion) + summary
```

- **Calls scale as `O(n·m)`** — n teammates, m rounds — plus one summary call.
- Calls are **serial** (turn-taking, see [11-technical-deep-dive.md](11-technical-deep-dive.md)), so wall-clock
  time ≈ the **sum** of per-call latencies, not the max.
- Prompt size per call is **bounded**: the transcript is windowed to the last 8 turns, so it does **not** grow
  unboundedly with round count.

## Choosing team size & rounds (guidance, not a benchmark)

| Setting | Suggested | Why |
|---|---|---|
| Teammates | **3–5** for interactive Discord use | Each adds one serial call per round; readability drops past ~6 voices |
| Rounds | **2–3** | Round 1 stakes out angles; 2–3 builds/rebuts; returns diminish after that |
| Larger teams (7+) | async/batch only | Serial latency adds up; consider fewer rounds or a hierarchical setup |

Rules of thumb:
- If meetings feel **slow**, the lever is `rounds` first, then `teammates` — both are linear.
- If any teammate is a **metered API**, remember it's billed `rounds` times per meeting.
- All-`ollama` teams are **free** (local compute only); cost is just your CPU/GPU time.

## Context window

- Per-turn prompt uses `history[-8:]` (last 8 turns) → bounded prompt growth.
- The summary reads the full log once (one call). For very long meetings, summarize-and-truncate the running
  history if you raise the window — the code change is localized to where `transcript` is built.

## Deployment

### Single machine (dev / personal use)
```bash
pip install -r requirements.txt
python bot/discord_team_bot.py
```
- Local Ollama teammates need RAM for each model (roughly ~1 GB+ per small model, model-dependent).
- HTTP teammates need only outbound network; no local model RAM.

### Docker
A `Dockerfile` is included. It runs the bot with your `.env` and `agents.yaml`:
```bash
docker build -t ai-chat-team .
docker run --rm \
  -e DISCORD_BOT_TOKEN=your-token \
  -v "$PWD/agents.yaml:/app/agents.yaml:ro" \
  --add-host=host.docker.internal:host-gateway \
  -e OLLAMA_HOST=http://host.docker.internal:11434 \
  ai-chat-team
```
- `OLLAMA_HOST=http://host.docker.internal:11434` lets the container reach an Ollama running on the host.
- For an all-`http` team you don't need Ollama at all — drop the OLLAMA_HOST line.
- Keep secrets in env / a secrets manager, never baked into the image.

### Keeping it up
- One bot process is enough for one Discord app; it's I/O-bound (waiting on model calls), not CPU-bound.
- Restart-on-crash: `docker run --restart=unless-stopped`, a `systemd --user` unit, or launchd (see
  [02-discord-setup.md](02-discord-setup.md)).
- Scaling out (multiple guilds/high volume) is a process-per-bot or queue concern, not something this template
  prescribes — the meeting logic itself is stateless per channel.
