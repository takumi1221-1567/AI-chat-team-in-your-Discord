#!/usr/bin/env python3
"""
AI chat team in your Discord — a pluggable multi-agent meeting bot.

Define your team in `agents.yaml`. Each teammate is backed by either:
  - a local Ollama model ("ollama"), or
  - your own HTTP API agent ("http") — any POST endpoint that returns JSON.

So you can drop in agents *you* built and "API-ized" yourself (e.g. a
Cloudflare Pages Function exposing POST /api/chat -> {"reply": "..."}),
mix them with local models, and have them hold autonomous meetings in Discord.

Quick start:
    pip install -r requirements.txt
    cp config.example.env .env          # put DISCORD_BOT_TOKEN
    cp agents.example.yaml agents.yaml  # define your team
    python bot/discord_team_bot.py

Commands in Discord:
    (any message)        -> teammates reply in character
    meeting <topic>      -> teammates auto-discuss for N rounds, then a summary
    done                 -> the summarizer wraps up and clears the log
"""
import os
import re
import json
import asyncio
import requests
import discord
from discord.ext import commands

try:
    import yaml
except ImportError:
    yaml = None

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ─────────────────────────────────────────────────────────────────────────
# Config & team definition
# ─────────────────────────────────────────────────────────────────────────
def _load_dotenv() -> None:
    """Minimal .env loader (no extra dependency)."""
    path = os.path.join(ROOT, ".env")
    if not os.path.exists(path):
        return
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_dotenv()

BOT_TOKEN   = os.environ.get("DISCORD_BOT_TOKEN", "")
CHANNEL_ID  = int(os.environ.get("DISCORD_CHANNEL_ID", "0"))   # 0 = all channels
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
AGENTS_FILE = os.environ.get("AGENTS_FILE", os.path.join(ROOT, "agents.yaml"))


def load_team() -> dict:
    path = AGENTS_FILE if os.path.exists(AGENTS_FILE) else os.path.join(ROOT, "agents.example.yaml")
    with open(path, encoding="utf-8") as f:
        if path.endswith((".yaml", ".yml")):
            if not yaml:
                raise SystemExit("Install PyYAML (pip install pyyaml) or use a .json agents file.")
            return yaml.safe_load(f)
        return json.load(f)


CFG            = load_team()
TEAM           = CFG.get("team", [])
SUMMARIZER     = CFG.get("summarizer") or {"name": "Summary", "backend": "ollama", "model": "llama3"}
MEETING_ROUNDS = int((CFG.get("meeting") or {}).get("rounds", 3))
KNOW           = CFG.get("knowledge") or {}

# Trigger words (override in agents.yaml: meeting.start / meeting.end)
MEETING_START = tuple((CFG.get("meeting") or {}).get("start", ["meeting", "会議", "ミーティング"]))
MEETING_END   = tuple((CFG.get("meeting") or {}).get("end",   ["done", "終わり", "おわり", "終了"]))

NOISE_MARKERS = ("api key", "quota", "rate limit", "未設定", "not configured", "RESOURCE_EXHAUSTED")


def _is_noise(text: str) -> bool:
    low = (text or "").lower()
    return any(m.lower() in low for m in NOISE_MARKERS)


def _strip_name_prefix(text: str) -> str:
    """Remove a leaked speaker label like '[Name]:' or '【Name】' at the start."""
    return re.sub(r'^\s*[\[【][^\]】]{1,16}[\]】]\s*[:：]?\s*', '', text or '').strip()


# ─────────────────────────────────────────────────────────────────────────
# Backends: a teammate is either a local Ollama model or your HTTP API agent
# ─────────────────────────────────────────────────────────────────────────
def call_ollama(model: str, system: str, message: str, history=None, timeout=60) -> str:
    msgs = [{"role": "system", "content": system}]
    for h in (history or []):
        if h.get("text"):
            msgs.append({"role": "assistant", "content": f"{h['agent']}: {h['text']}"})
    msgs.append({"role": "user", "content": message})
    try:
        r = requests.post(f"{OLLAMA_HOST}/api/chat",
                          json={"model": model, "messages": msgs, "stream": False}, timeout=timeout)
        r.raise_for_status()
        return (r.json().get("message", {}).get("content") or "").strip()
    except Exception:
        return ""


def _subst_env(value: str) -> str:
    """Replace ${ENV_VAR} in a string with the environment value (for API keys in headers)."""
    return re.sub(r"\$\{(\w+)\}", lambda m: os.environ.get(m.group(1), ""), str(value))


def call_http(agent: dict, message: str, timeout=60) -> str:
    """Call your own API-ized agent. Body/response field names are configurable."""
    body = {agent.get("request_key", "message"): message}
    for k, v in (agent.get("extra_body") or {}).items():
        body[k] = v
    headers = {"Content-Type": "application/json"}
    for k, v in (agent.get("headers") or {}).items():
        headers[k] = _subst_env(v)   # supports ${MY_TOKEN}
    try:
        r = requests.post(agent["endpoint"], json=body, headers=headers, timeout=timeout)
        r.raise_for_status()
        data = r.json()
    except Exception:
        return ""
    if isinstance(data, dict):
        return (str(data.get(agent.get("response_key", "reply"), "")) or "").strip()
    return str(data).strip()


def ask_agent(agent: dict, message: str, history=None, context: str = "") -> str:
    """Generate one teammate's reply via its configured backend."""
    persona = (agent.get("persona", "") + (context or "")).strip()
    if agent.get("backend") == "http":
        # Deployed agents usually own their own system prompt; we prepend any steering.
        msg = f"{persona}\n\n{message}" if persona else message
        reply = call_http(agent, msg)
    else:
        system = persona or "You are a helpful assistant. Answer concisely."
        reply = call_ollama(agent.get("model", "llama3"), system, message, history)
    reply = _strip_name_prefix(reply)
    if not reply or "(応答なし)" in reply or "(no response)" in reply.lower() or _is_noise(reply):
        return ""
    return reply


# ─────────────────────────────────────────────────────────────────────────
# Optional: local knowledge (RAG) from a folder of .md/.txt files — no cloud
# ─────────────────────────────────────────────────────────────────────────
_VAULT_CACHE: dict = {"ts": 0.0, "docs": []}


def _know_dirs() -> list:
    return [os.path.expanduser(d) for d in (KNOW.get("dirs") or []) if os.path.isdir(os.path.expanduser(d))]


def _load_docs(force: bool = False) -> list:
    import time
    import unicodedata
    if not KNOW.get("enabled"):
        return []
    now = time.time()
    if not force and _VAULT_CACHE["docs"] and now - _VAULT_CACHE["ts"] < 300:
        return _VAULT_CACHE["docs"]
    docs = []
    for root in _know_dirs():
        for dp, _d, files in os.walk(root):
            if "/.obsidian" in dp or "/.git" in dp:
                continue
            for fn in files:
                if not fn.endswith((".md", ".txt")):
                    continue
                try:
                    with open(os.path.join(dp, fn), encoding="utf-8") as f:
                        # macOS filenames are NFD; normalize to NFC so folder/title matching works.
                        rel = unicodedata.normalize("NFC", os.path.relpath(os.path.join(dp, fn), root))
                        docs.append((rel, f.read()))
                except Exception:
                    continue
    _VAULT_CACHE.update(ts=now, docs=docs)
    return docs


def _keywords(text: str) -> list:
    terms = set()
    for w in re.findall(r"[A-Za-z0-9]{2,}", text):     terms.add(w.lower())
    for w in re.findall(r"[ァ-ヶー]{2,}", text):        terms.add(w)
    for w in re.findall(r"[一-龥々〆ヶ]{2,}", text):     terms.add(w)
    return list(terms)[:12]


def _strip_frontmatter(text: str) -> str:
    t = text.lstrip()
    if t.startswith("---"):
        m = re.search(r"^---\s*\n.*?\n---\s*\n", t, re.S)
        if m:
            t = t[m.end():]
    return t.lstrip()


def knowledge_context(query: str, limit: int = 4) -> str:
    docs = _load_docs()
    if not docs:
        return ""
    terms = _keywords(query)
    if not terms:
        return ""
    folder = KNOW.get("folder", "")   # optional: restrict to a subfolder substring
    scored = []
    for path, content in docs:
        if folder and folder not in path:
            continue
        pl, cl = path.lower(), content.lower()
        score = sum((3 if t.lower() in pl else (1 if t.lower() in cl else 0)) for t in terms)
        if score:
            body = _strip_frontmatter(content)
            cl2 = body.lower()
            pos = min([cl2.find(t.lower()) for t in terms if t.lower() in cl2] or [0])
            seg = " ".join(body[max(0, pos - 120): max(0, pos - 120) + 480].split())
            title = os.path.splitext(os.path.basename(path))[0]
            scored.append((score, f"【{title}】{seg}"))
    scored.sort(key=lambda x: x[0], reverse=True)
    snips = [s for _, s in scored[:limit]]
    if not snips:
        return ""
    return ("\n\n=== Reference (your own memory; use it naturally, cite specifics) ===\n"
            + "\n\n".join(snips)
            + "\n=== end ===\nGround your answer in the specifics above (names/dates/facts); avoid vague generalities.")


# ─────────────────────────────────────────────────────────────────────────
# Discord bot
# ─────────────────────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


def agent_color(name: str) -> int:
    for a in TEAM + [SUMMARIZER]:
        if a.get("name") == name and a.get("color"):
            try:
                return int(str(a["color"]), 16) if isinstance(a["color"], str) else int(a["color"])
            except Exception:
                return 0x5865F2
    return 0x5865F2


async def post(channel, name: str, text: str) -> None:
    for chunk in [text[i:i + 3900] for i in range(0, len(text), 3900)] or [text]:
        embed = discord.Embed(description=chunk, color=agent_color(name))
        embed.set_author(name=name)
        await channel.send(embed=embed)


async def run_chat(message, text: str, loop) -> None:
    """Each teammate replies in character (grounded in local knowledge if enabled)."""
    ctx = await loop.run_in_executor(None, knowledge_context, text)
    for agent in TEAM:
        reply = await loop.run_in_executor(None, ask_agent, agent, text, None, ctx)
        if reply:
            await post(message.channel, agent.get("name", "Agent"), reply)
            await asyncio.sleep(0.4)


async def run_meeting(message, topic: str, loop) -> None:
    """Teammates auto-discuss the topic for N rounds, then the summarizer wraps up."""
    ch = message.channel
    if not topic:
        await post(ch, SUMMARIZER.get("name", "Summary"), "Give me a topic, e.g. `meeting roadmap for Q3`.")
        return
    ctx = await loop.run_in_executor(None, knowledge_context, topic)
    note = " (with reference notes)" if ctx else ""
    await post(ch, SUMMARIZER.get("name", "Summary"),
               f"🗣️ Meeting started — topic: **{topic}**{note}\n"
               f"Participants: {', '.join(a.get('name','?') for a in TEAM)} · {MEETING_ROUNDS} rounds")
    history: list = []
    for _ in range(MEETING_ROUNDS):
        for agent in TEAM:
            transcript = "\n".join(f"- {h['agent']}: {h['text']}" for h in history[-8:]) or "(no remarks yet)"
            angle = agent.get("angle", "your own expertise")
            prompt = (f"Topic: \"{topic}\"\nDiscussion so far:\n{transcript}\n\n"
                      f"You are \"{agent.get('name')}\". From the angle of {angle} only, add a NEW point, "
                      "rebuttal, or concrete proposal that does not repeat what others said. 1-2 sentences. "
                      "No speaker labels, content only.")
            reply = await loop.run_in_executor(None, ask_agent, agent, prompt, [], ctx)
            if not reply:
                continue
            await post(ch, agent.get("name", "Agent"), reply)
            history.append({"agent": agent.get("name", "Agent"), "text": reply})
            await asyncio.sleep(0.4)
    # summary
    convo = "\n".join(f"{h['agent']}: {h['text']}" for h in history)
    sys = ("You are the meeting facilitator. Read the log and produce a concise summary as:\n"
           "[Summary] 3-5 bullets\n[Decisions] bullets (or 'none')\n[Next actions] bullets (or 'none').\n"
           "No preamble.")
    summary = await loop.run_in_executor(
        None, call_ollama, SUMMARIZER.get("model", "llama3"), sys, convo or topic, [], 150)
    await post(ch, SUMMARIZER.get("name", "Summary"), f"📋 Meeting summary\n\n{summary or '(no summary)'}")


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}  |  team: {[a.get('name') for a in TEAM]}")


@bot.event
async def on_message(message: discord.Message):
    if message.author.id == bot.user.id:
        return
    if CHANNEL_ID and message.channel.id != CHANNEL_ID:
        return
    await bot.process_commands(message)
    if message.content.startswith("!"):
        return
    text = message.content.strip()
    if not text:
        return
    loop = asyncio.get_running_loop()
    norm = text.replace(" ", "").replace("　", "")

    if any(norm.startswith(k) for k in MEETING_START):
        topic = text
        for k in MEETING_START:
            if text.lower().startswith(k.lower()):
                topic = text[len(k):].strip(" 　:：・").strip()
                break
        await run_meeting(message, topic, loop)
        return

    thinking = await message.channel.send("…")
    try:
        await run_chat(message, text, loop)
    finally:
        try:
            await thinking.delete()
        except Exception:
            pass


if __name__ == "__main__":
    if not BOT_TOKEN:
        raise SystemExit("Set DISCORD_BOT_TOKEN in your environment or .env file.")
    if not TEAM:
        raise SystemExit("Define at least one teammate in agents.yaml (see agents.example.yaml).")
    bot.run(BOT_TOKEN)
