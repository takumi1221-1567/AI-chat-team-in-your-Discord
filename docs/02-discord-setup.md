# 02 · Discord bot setup

You need a bot token and the bot in your server with the right intent. ~5 minutes.

## 1. Create the application & bot
1. Go to the [Discord Developer Portal](https://discord.com/developers/applications) → **New Application**.
2. Open **Bot** → **Add Bot** → **Reset Token** → copy the token. Put it in `.env`:
   ```
   DISCORD_BOT_TOKEN=paste-token-here
   ```
3. Still on **Bot**, enable **Privileged Gateway Intents → MESSAGE CONTENT INTENT**.
   (Without this the bot cannot read message text.)

## 2. Invite the bot to your server
1. **OAuth2 → URL Generator** → scopes: `bot`.
2. Bot permissions: `View Channels`, `Send Messages`, `Read Message History`, `Embed Links`.
3. Open the generated URL, pick your server, authorize.

## 3. (Optional) Restrict to one channel
Right-click the channel → **Copy Channel ID** (enable Developer Mode in Discord settings first),
then in `.env`:
```
DISCORD_CHANNEL_ID=123456789012345678
```
Leave `0` to listen on every channel.

## 4. Run
```bash
pip install -r requirements.txt
python bot/discord_team_bot.py
```
You should see `✅ Logged in as <bot> | team: [...]`. Type a message in the channel.

## Keeping it running (macOS, launchd)
Create `~/Library/LaunchAgents/com.aichatteam.bot.plist` (adjust paths):
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.aichatteam.bot</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/python3</string>
    <string>/full/path/AI-chat-team-in-your-Discord/bot/discord_team_bot.py</string>
  </array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>/tmp/aichatteam.log</string>
  <key>StandardErrorPath</key><string>/tmp/aichatteam.err.log</string>
</dict></plist>
```
```bash
launchctl load ~/Library/LaunchAgents/com.aichatteam.bot.plist
launchctl kickstart -k gui/$(id -u)/com.aichatteam.bot   # restart after edits
```
On Linux, use a `systemd --user` service or `docker run` instead.

Next: **[03-define-your-team.md](03-define-your-team.md)**.
