---
name: testing-the-team
description: Test a multi-agent Discord bot without a live Discord connection by importing the module and exercising backends, chat, and meetings. Use to verify agents/meetings before going live.
---

# Testing the team

Verify backends and orchestration offline before relying on Discord.

## Backend smoke tests
```bash
curl -s http://localhost:11434/api/tags | grep name          # Ollama up + model present
curl -s -X POST <endpoint> -H 'Content-Type: application/json' \
     -d '{"message":"hi"}'                                    # http agent -> {"reply": ...}
```

## Import the bot without running it
`bot.run()` must be guarded by `if __name__ == "__main__":` so the module imports cleanly:
```python
import importlib.util, os
os.environ.setdefault("DISCORD_BOT_TOKEN", "x")
spec = importlib.util.spec_from_file_location("bot", "bot/discord_team_bot.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
for a in m.TEAM:
    print(a["name"], "->", m.ask_agent(a, "one improvement to our plan?"))
```

## Dry-run a meeting round
Loop the team with a plain-text transcript and each agent's angle; confirm replies are (a) in the right
language, (b) distinct, (c) non-empty. If an agent is always empty, curl its endpoint or `ollama pull`
its model.

## Triage table
| Symptom | Cause / fix |
|---|---|
| Bot online, no replies | Message Content Intent off, or channel filter mismatch |
| One agent silent | endpoint error / model missing |
| All replies identical | personas too long, angles too similar |
| Wrong language | add explicit final language instruction to persona |
| `ModuleNotFoundError: yaml` | `pip install pyyaml` |

## Done when
A message yields per-agent replies, and `meeting <topic>` yields multiple distinct rounds plus a
structured summary.
