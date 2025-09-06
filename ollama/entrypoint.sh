#!/bin/sh
set -e

# Start the Ollama server in the background
ollama serve &
SERVER_PID=$!

# Wait for the server to be ready
echo "Waiting for Ollama server to start..."
until curl -s http://localhost:11434/api/version >/dev/null 2>&1; do
  sleep 2
done

# Pull the desired model (change 'llama2' to whatever model you need)
MODEL_NAME="${OLLAMA_MODEL:-gemma3:1b}"
echo "Pulling model: $MODEL_NAME"
ollama pull "$MODEL_NAME"

# Bring the Ollama server back to foreground
wait $SERVER_PID