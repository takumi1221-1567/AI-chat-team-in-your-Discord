# 05 · Autonomous meeting mode

Type `meeting <topic>` (or any word in `meeting.start`) and the team runs a self-driven discussion.

## How a meeting runs

```
meeting Launch plan for the new feature
```

1. The facilitator announces the topic and participants.
2. For `meeting.rounds` rounds (default 3), **each teammate speaks once**, in order.
   - It sees the running transcript and is told to contribute from **its own angle only**,
     adding a new point / rebuttal / concrete proposal, **without repeating** others.
3. The facilitator reads the whole log and posts a structured summary:
   ```
   [Summary]  3-5 bullets
   [Decisions]  bullets (or "none")
   [Next actions]  bullets (or "none")
   ```

## Why it doesn't turn into an echo chamber

Two deliberate choices:
- **Angles.** Each teammate has a fixed `angle` (e.g. *risk* vs *execution*), so they pull the topic in
  different directions.
- **Transcript-as-text.** Prior turns are injected as a plain list inside the prompt, not as chat
  messages to imitate. Small models otherwise copy the last speaker verbatim.

## Tuning

| Want | Do |
|---|---|
| Longer/shorter meetings | `meeting.rounds` in `agents.yaml` (or `MEETING_ROUNDS` env) |
| Different trigger words | `meeting.start` / `meeting.end` lists |
| A specific facilitator voice | edit the `summarizer` persona/model |
| More distinct voices | sharpen each teammate's `angle` and keep personas short |

## Cost

With all teammates on `backend: ollama`, a meeting is **fully local and free**. With `http` teammates,
each turn is one request to your endpoint — N teammates × R rounds requests total, so keep `rounds`
modest if those calls are metered.

Next: **[06-local-knowledge-rag.md](06-local-knowledge-rag.md)**.
