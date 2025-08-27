docker run -d \
  -p 3000:8080 \
  -e OPENROUTER_API_KEY="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" \
  -e OPENAI_API_BASE_URL="https://openrouter.ai/api/v1" \
  -e DEFAULT_MODEL="openrouter/auto" \
  -v open-webui:/app/backend/data \
  --name open-webui \
  --restart always \
  ghcr.io/open-webui/open-webui:main
