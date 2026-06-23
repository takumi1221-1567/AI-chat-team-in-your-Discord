# AI chat team in your Discord — container image
# Build:  docker build -t ai-chat-team .
# Run:    docker run --rm -e DISCORD_BOT_TOKEN=... \
#           -v "$PWD/agents.yaml:/app/agents.yaml:ro" \
#           --add-host=host.docker.internal:host-gateway \
#           -e OLLAMA_HOST=http://host.docker.internal:11434 ai-chat-team
FROM python:3.12-slim

WORKDIR /app

# Install deps first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App code + example config (mount your real agents.yaml at runtime)
COPY bot/ ./bot/
COPY agents.example.yaml ./agents.example.yaml

# Secrets come from the environment / -e flags, never baked into the image.
ENV PYTHONUNBUFFERED=1
CMD ["python", "bot/discord_team_bot.py"]
