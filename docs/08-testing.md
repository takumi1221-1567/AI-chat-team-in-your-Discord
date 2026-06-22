# 08 · Test the team

You can test most things **without Discord** by importing the bot module and calling its functions.

## 1. Smoke-test the backends

```bash
# Is Ollama up and is the model present?
curl -s http://localhost:11434/api/tags | python3 -m json.tool | grep name

# Does your HTTP agent honor the contract?
curl -s -X POST https://your-agent.example.com/api/chat \
  -H "Content-Type: application/json" -d '{"message":"hello"}'
# expect: {"reply":"..."}
```

## 2. Test teammates offline (no Discord token needed)

```python
# test_team.py — run: python test_team.py
import importlib.util, os
os.environ.setdefault("DISCORD_BOT_TOKEN", "x")   # bot.run() is never called here
spec = importlib.util.spec_from_file_location("bot", "bot/discord_team_bot.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

print("team:", [a["name"] for a in m.TEAM])
for agent in m.TEAM:
    print(f"\n[{agent['name']}] ->", m.ask_agent(agent, "Suggest one improvement to our launch plan."))
```

Importing the module is safe: `bot.run()` only executes under `__main__`.

## 3. Dry-run a meeting locally

```python
ctx = m.knowledge_context("launch plan")          # "" unless knowledge.enabled
hist = []
for agent in m.TEAM:
    tr = "\n".join(f"- {h['agent']}: {h['text']}" for h in hist) or "(none)"
    prompt = (f'Topic: "launch plan"\nDiscussion so far:\n{tr}\n\n'
              f'You are "{agent["name"]}". From {agent.get("angle","your angle")} only, add a new point in 1-2 sentences.')
    r = m.ask_agent(agent, prompt, [], ctx)
    print(f"[{agent['name']}] {r}")
    if r: hist.append({"agent": agent["name"], "text": r})
```

## 4. Common issues

| Symptom | Likely cause / fix |
|---|---|
| Bot connects but never replies | Message Content Intent not enabled, or `DISCORD_CHANNEL_ID` points elsewhere |
| A teammate is always silent | `http` endpoint erroring (test with curl) or model not pulled (`ollama pull <model>`) |
| Everyone parrots each other | Personas too long / angles too similar — shorten personas, sharpen `angle` |
| Replies drift to the wrong language | Add an explicit final instruction to the persona (e.g. "Answer in Japanese only.") |
| `ModuleNotFoundError: yaml` | `pip install pyyaml` (or use a `.json` agents file) |

## 5. In Discord

Type a message → expect each teammate to reply.
Type `meeting <topic>` → expect rounds of discussion + a final summary embed.

Next: **[09-reproduce-from-scratch.md](09-reproduce-from-scratch.md)**.
