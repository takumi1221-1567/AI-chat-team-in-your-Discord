# 07 · Optional — a Google Apps Script hub

You don't need this to run the team. But if you want a **zero-infra web dashboard** and a free,
always-on place to **log and read meeting transcripts**, a Google Apps Script (GAS) Web App is a handy
companion. This is the pattern this template grew out of.

## What a GAS hub gives you

- A public `…/exec` Web App URL you can `POST` to from the bot (fire-and-forget logging).
- A spreadsheet as a free datastore for transcripts / decisions.
- A simple HTML dashboard (served by the same script) to browse meetings.

## Shape of it

```javascript
// Code.gs  (Extensions → Apps Script, then Deploy → Web App)
function doPost(e) {
  const body = JSON.parse(e.postData.contents || "{}");
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("log");
  sheet.appendRow([new Date(), body.speaker || "", body.text || "", body.type || ""]);
  return ContentService.createTextOutput(JSON.stringify({ ok: true }))
                       .setMimeType(ContentService.MimeType.JSON);
}

function doGet() {                       // optional dashboard
  return HtmlService.createHtmlOutputFromFile("index");
}
```

Deploy as **Web App** (Execute as: *me*, Access: *anyone*), copy the `/exec` URL.

## Hook it into the bot (optional)

The template bot doesn't log to GAS by default (to stay dependency-free and private). To add it,
record each posted message inside `post()`:

```python
import requests, os
GAS_URL = os.environ.get("GAS_URL", "")
def record_to_gas(speaker, text, kind="msg"):
    if not GAS_URL:
        return
    try:
        requests.post(GAS_URL, json={"speaker": speaker, "text": text, "type": kind}, timeout=10)
    except Exception:
        pass
```

Put `GAS_URL=` in `.env`. Logging failures are ignored so they never block the chat.

> Keep the spreadsheet private if transcripts contain anything sensitive — a GAS Web App set to
> "anyone" exposes only the script's endpoints, but treat the `/exec` URL itself as a secret.

Next: **[08-testing.md](08-testing.md)**.
