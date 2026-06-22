---
name: meeting-orchestration
description: Orchestrate a multi-agent discussion that progresses (no parroting) and ends with a structured summary. Use when several AI agents should debate a topic and reach decisions.
---

# Meeting orchestration

Make several agents hold a productive discussion instead of repeating each other.

## Loop
```
context = retrieve(topic)            # optional grounding
history = []
for round in range(ROUNDS):
    for agent in team:
        transcript = render(history[-8:])           # plain text, NOT chat turns
        prompt = f'''Topic: "{topic}"
Discussion so far:
{transcript}

You are "{agent.name}". From the angle of {agent.angle} ONLY, add a NEW point,
rebuttal, or concrete proposal that does not repeat others. 1-2 sentences. Content only.'''
        reply = ask(agent, prompt, context)
        if reply: post(agent.name, reply); history.append({agent, reply})
summary = facilitate(history)        # [Summary]/[Decisions]/[Next actions]
```

## Anti-parroting techniques (important with small models)
- **Distinct angles.** Give each agent one fixed perspective (risk vs execution vs cost…).
- **Transcript as plain text** inside the user prompt — do NOT feed prior turns as assistant
  messages, or the model imitates the last speaker verbatim.
- **"do not repeat" instruction** every turn; cap length to 1-2 sentences.
- **Strip leaked labels** like `[Name]:` from outputs with a regex.

## Summary
A dedicated facilitator reads the full log and emits a fixed structure:
`[Summary]` bullets · `[Decisions]` (or none) · `[Next actions]` (or none). No preamble.

## Cost control
Total LLM calls ≈ agents × rounds (+1 summary). Keep rounds at 2-3 if any agent is metered.
