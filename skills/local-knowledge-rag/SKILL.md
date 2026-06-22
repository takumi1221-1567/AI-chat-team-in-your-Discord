---
name: local-knowledge-rag
description: Ground LLM replies in a local folder of markdown/text notes with keyword search, no embeddings or cloud. Use to make agents cite real facts from the user's own notes offline.
---

# Local knowledge (RAG), offline

Cheap, dependency-free grounding over a folder of `.md`/`.txt` notes. Good up to a few thousand notes.

## Pipeline
1. **Load** all `.md`/`.txt` under the configured dirs into memory (cache ~5 min). Skip `.obsidian`/`.git`.
   On macOS, **NFC-normalize** file paths (`unicodedata.normalize("NFC", path)`) — filenames are stored
   NFD (decomposed), so non-ASCII folder/title matching silently fails without this.
2. **Keywords** from the query: ASCII words `[A-Za-z0-9]{2,}`, katakana runs `[ァ-ヶー]{2,}`,
   kanji runs `[一-龥々〆ヶ]{2,}`.
3. **Score** each note: keyword in body = 1, **keyword in path/title = 3** (titles are strong signals).
4. **Snippet**: strip YAML frontmatter (`^---\n…\n---\n`), take a window around the first hit, collapse
   whitespace. (Otherwise you inject a useless `tags:` header instead of the body.)
5. **Inject** top-k snippets as a `=== Reference ===` block in the system/user prompt, and instruct the
   model to cite specifics (names/dates) and avoid generalities.

## Gotchas this avoids
- **NFC/NFD mismatch** → folder filters like `"cases" in path` silently match nothing on macOS.
- **Frontmatter snippets** → model gets metadata, answers vaguely. Strip it.
- **Short-keyword false hits** (e.g. "AI") → path-weighting + requiring a real hit mitigates it.

## When to upgrade
Swap the keyword search for a local vector index (FAISS/Chroma) only when the corpus is large; keep the
same "return a context string" interface so callers don't change.
