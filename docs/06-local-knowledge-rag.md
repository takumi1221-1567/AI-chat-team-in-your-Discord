# 06 · Local knowledge (RAG), offline

Ground your team's replies in **your own notes** — a folder of `.md` / `.txt` files — with no cloud,
no database, and no embeddings service. Off by default.

## Enable it

```yaml
knowledge:
  enabled: true
  dirs:
    - "~/notes"                       # one or more folders
    - "~/Documents/research"
  folder: ""                          # optional: only notes whose path contains this substring
```

Restart the bot. Now both chat and meetings inject relevant note snippets as **reference context**,
and teammates are told to cite the specifics (names, dates, facts) instead of speaking in generalities.

## How it works (simple on purpose)

1. **Load** — all `.md`/`.txt` under `dirs` are read into memory (cached ~5 min). `.obsidian`/`.git`
   are skipped. File paths are **NFC-normalized** so non-ASCII folder/title matching works on macOS.
2. **Search** — the query is reduced to keywords (ASCII words, katakana runs, kanji runs). Each note is
   scored by keyword hits; a hit in the **path/title counts triple** (titles are strong signals).
3. **Snippet** — YAML frontmatter is stripped and a window around the first keyword hit is extracted,
   whitespace collapsed — so the model gets real body text, not a `tags:` header.
4. **Inject** — the top snippets become a `=== Reference ===` block appended to each teammate's prompt.

## Restrict to a topic area

`folder` lets you keep meetings on-theme. If your notes are under
`Knowledge/cases/...`, set `folder: "cases"` and only those notes are used.

## Scaling notes

This loads every file into memory, which is perfect up to a few thousand small notes. For large corpora,
swap `knowledge_context()` for a vector store (e.g. a local FAISS/Chroma index) — the rest of the bot is
unchanged because it only consumes the returned context string.

Next: **[07-gas-hub-optional.md](07-gas-hub-optional.md)**.
