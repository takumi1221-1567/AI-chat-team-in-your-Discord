---
name: discord-bot-setup
description: Create a Discord bot (token, invite, Message Content Intent) and run/keep alive a Python discord.py bot. Use when wiring any agent or team into Discord.
---

# Discord bot setup

Use this when the user wants an agent/team to live in Discord.

## Steps
1. **App + bot + token** — Discord Developer Portal → New Application → Bot → Reset Token. Store the
   token in `.env` as `DISCORD_BOT_TOKEN` (never in code or git).
2. **Enable MESSAGE CONTENT INTENT** under Bot → Privileged Gateway Intents. Without it, `message.content`
   is empty and the bot appears "dead."
3. **Invite** — OAuth2 → URL Generator → scope `bot`, permissions: View Channels, Send Messages, Read
   Message History, Embed Links. Open URL, authorize into the server.
4. **Minimal bot** (`discord.py>=2.3`):
   ```python
   import discord
   intents = discord.Intents.default(); intents.message_content = True
   client = discord.Client(intents=intents)
   @client.event
   async def on_message(m):
       if m.author == client.user: return
       await m.channel.send("pong")
   client.run(TOKEN)
   ```
5. **Keep alive** — macOS: a `launchd` plist with `RunAtLoad` + `KeepAlive`; Linux: `systemd --user`
   or Docker. Restart with `launchctl kickstart -k gui/$(id -u)/<label>`.

## Checks / pitfalls
- Bot online but silent → intent not enabled, or channel filter excludes the channel.
- Long messages → Discord caps at 2000 chars (4096 in embeds); chunk before sending.
- Never commit the token; rotate it if it leaks (Reset Token).
