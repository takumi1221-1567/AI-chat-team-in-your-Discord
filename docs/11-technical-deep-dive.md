# 11 · Technical deep dive — the meeting algorithm

The hard part of a multi-agent "meeting" isn't calling N models — it's getting a **real discussion** out of
them instead of N paraphrases of the same answer. This is how `run_meeting()` does it, with the actual code.

## The core problem: the parrot effect

Ask several LLMs the same question and they converge — especially small local models, which will happily
restate the previous speaker almost verbatim. A meeting that just concatenates answers is theatre, not a
discussion. Two failure modes specifically:

1. **Convergence** — every agent says the same thing from the same angle.
2. **Imitation** — if you feed prior turns as *chat messages*, the model continues the last speaker's voice
   and copies it (we observed the literal `[Name]:` prefix leaking into replies).

## The solution: angle-constrained, turn-taking generation

Three design choices, all visible in `bot/discord_team_bot.py` → `run_meeting()`:

```python
for _ in range(MEETING_ROUNDS):
    for agent in TEAM:                                   # (1) sequential turn-taking
        transcript = "\n".join(f"- {h['agent']}: {h['text']}" for h in history[-8:]) or "(no remarks yet)"
        angle = agent.get("angle", "your own expertise")
        prompt = (f"Topic: \"{topic}\"\nDiscussion so far:\n{transcript}\n\n"   # (2) transcript as plain text
                  f"You are \"{agent.get('name')}\". From the angle of {angle} only, add a NEW point, "
                  "rebuttal, or concrete proposal that does not repeat what others said. 1-2 sentences. "
                  "No speaker labels, content only.")                            # (3) per-turn anti-repeat
        reply = await loop.run_in_executor(None, ask_agent, agent, prompt, [], ctx)
        if not reply:
            continue
        await post(ch, agent.get("name", "Agent"), reply)
        history.append({"agent": agent.get("name", "Agent"), "text": reply})
```

1. **Sequential turn-taking (not parallel).** Within a round, agents speak **one after another**, and each
   one receives everyone's prior turns. This is deliberate: parallel `asyncio.gather` would be faster but
   every agent would answer blind, re-converging. The latency cost buys genuine build-on-the-last-point
   behaviour. (It also means a teammate can directly rebut the one before it.)

2. **Transcript injected as plain text, not as chat turns.** Prior turns go into the *user prompt* as a
   bulleted list — they are never passed as `assistant` messages. This is the single most important trick:
   it stops the model from imitating the previous speaker's voice/format. (See `ask_agent`: `history` is
   passed as `[]` here precisely so the model has nothing to imitate.)

3. **A fixed `angle` per teammate + an explicit "do NOT repeat" instruction every turn.** The angle
   (`risk`, `execution`, `cost`, …) pulls each agent in a different direction; the instruction caps length to
   1–2 sentences and forbids restating others. Leaked `[Name]:` prefixes are stripped defensively
   (`_strip_name_prefix`).

## Context-window management

History is **windowed to the last 8 turns** (`history[-8:]`) when building each prompt, so prompt size stays
bounded regardless of round count — the meeting can run long without the context growing without limit. The
**summary** step reads the *full* log once at the end:

```python
sys = ("You are the meeting facilitator. Read the log and produce a concise summary as:\n"
       "[Summary] 3-5 bullets\n[Decisions] bullets (or 'none')\n[Next actions] bullets (or 'none').\nNo preamble.")
summary = await loop.run_in_executor(None, call_ollama, SUMMARIZER.get("model","llama3"), sys, convo or topic, [], 150)
```

## Backend independence

Each turn calls `ask_agent`, which dispatches to either a **local Ollama model** or **your HTTP API agent**
(`backend: ollama | http`). The meeting loop doesn't know or care which — so a single meeting can mix a local
`llama3`, your deployed Gemini-backed endpoint, and a Claude-backed endpoint. "Model diversity" is therefore a
config choice, not a code change. A teammate that errors or times out returns `""` and is simply skipped that
turn (fail-soft), so one slow backend never deadlocks the room.

## Trade-offs (stated honestly)

- **Latency vs. discussion quality.** Sequential turn-taking is `O(n·m)` *serial* model calls (n teammates ×
  m rounds), so wall-clock time is the **sum** of per-call latencies, not the max. Parallelism would cut
  latency but kill the turn-taking that makes it a discussion. This is the central trade-off; if you need
  speed over debate, drop to `rounds: 1` or fewer teammates.
- **Small models drift.** Angle + "don't repeat" + plain-text transcript mitigate it but don't eliminate it;
  stronger models (via an `http` teammate) debate more crisply.
- **No formal conflict resolution.** The facilitator *summarizes* disagreement; it does not vote or weight.
  Consensus is editorial, not algorithmic. If you need voting/weighted consensus, it's a clean extension
  point in the summary step.

## Research grounding

The "have models disagree across rounds, then reconcile" pattern is the production form of **multi-agent
debate** — e.g. Du et al., *"Improving Factuality and Reasoning in Language Models through Multiagent Debate"*
(2023), which shows that several models critiquing each other across rounds improves factuality and reasoning
over a single pass. This repo operationalizes that idea with Discord as the interface and a fixed-angle,
turn-taking schedule instead of free-form debate.

See also: [05-meeting-mode.md](05-meeting-mode.md) (user-facing), [12-scalability.md](12-scalability.md) (cost & deployment).
