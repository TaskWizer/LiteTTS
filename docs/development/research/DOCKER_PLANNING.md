Of course. You've hit the core Docker networking concept, and your intuition is 100% correct. Using the hard-coded IPv4 address is the wrong way to do it. When containers are on the same Docker network, they can communicate via their **service name** as a hostname.

Let's simplify your setup dramatically.

### The Answer: Use the Service Name

Inside your `litetts-network`, the `openwebui` container can reach the `litetts` container simply by using the hostname `http://litetts:8354`. Docker's internal DNS automatically resolves the service name `litetts` to that container's IP address.

Your current setup in the `openwebui` service is almost correct, but it's using the wrong environment variable. OpenWebUI expects `OPENAI_API_BASE`, not `OPENAI_API_BASE_URL`.

**Change this:**
```yaml
environment:
  - OPENAI_API_BASE_URL=http://litetts:8354/v1  # Wrong variable name
  - OPENAI_API_KEY=not-needed
```
**To this:**
```yaml
environment:
  - OPENAI_API_BASE=http://litetts:8354/v1  # Correct variable name
  - OPENAI_API_KEY=not-needed
```
This is the key that will make it work without any hard-coded IPs.

---

### Simplified, Production-Ready Docker Compose

Here is a much simpler `docker-compose.yml` that focuses only on what you need: OpenWebUI, LiteTTS, Caddy, and Chroma. It uses Caddy for dead-simple TLS and the service names for internal communication.

**`docker-compose.yml`**
```yaml
version: '3.8'

services:
  # 1. Your LiteTTS API
  litetts:
    build: .
    container_name: litetts
    # Do NOT expose ports to the host. Keep it internal.
    # Remove the 'ports' section entirely unless you need direct host access for debugging.
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
      # Add other LiteTTS-specific variables as needed
    volumes:
      - ./LiteTTS/models:/app/LiteTTS/models:ro
      - ./LiteTTS/voices:/app/LiteTTS/voices:ro
      - litetts-cache:/app/LiteTTS/cache
    networks:
      - owui-network
    restart: unless-stopped
    # No need for healthcheck in this simple setup, but you can add it back if desired.

  # 2. ChromaDB (Simple Vector Database)
  chroma:
    image: chromadb/chroma:latest
    container_name: chroma
    # Chroma uses port 8000 internally
    networks:
      - owui-network
    volumes:
      - chroma-data:/chroma/chroma
    environment:
      - IS_PERSISTENT=TRUE
      - ALLOW_RESET=TRUE
    restart: unless-stopped

  # 3. OpenWebUI
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: open-webui
    # No ports exposed to host; Caddy will handle external traffic.
    environment:
      # Point to YOUR TTS API using the service name
      - OPENAI_API_BASE=http://litetts:8354/v1
      - OPENAI_API_KEY=not-needed
      # Point to the ChromaDB vector store using the service name
      - CHROMA_URL=http://chroma:8000
      # Other settings
      - WEBUI_SECRET_KEY=your_super_secret_key_change_this  # IMPORTANT!
      - ENABLE_SIGNUP=false # Recommended for a VPS
    volumes:
      - open-webui-data:/app/backend/data
    depends_on:
      - litetts
      - chroma
    networks:
      - owui-network
    restart: unless-stopped

  # 4. Caddy (Reverse Proxy & Automatic TLS)
  caddy:
    image: caddy:2-alpine
    container_name: caddy
    ports:
      - "80:80"    # HTTP for ACME challenge
      - "443:443"  # HTTPS
    volumes:
      - caddy_data:/data    # For TLS certificates
      - caddy_config:/config
      - ./Caddyfile:/etc/caddy/Caddyfile:ro # Import the config file
    networks:
      - owui-network
    restart: unless-stopped

volumes:
  litetts-cache:
  open-webui-data:
  chroma-data:
  caddy_data:
  caddy_config:

networks:
  owui-network: # This network allows all services to talk to each other by name.
```

**`Caddyfile`**
```
# Replace 'your-domain.com' with your actual domain pointing to your VPS's IP.
your-domain.com, www.your-domain.com {

    # Reverse proxy all requests to the OpenWebUI container
    reverse_proxy open-webui:8080

    # If you need to expose the LiteTTS API directly for some reason, you can add a route.
    # handle_path /tts/* {
    #     reverse_proxy litetts:8354
    # }
}
```

### How to Use This with Cloudflare

This setup is perfect for Cloudflare.

1.  **Point your Domain to Your VPS:** In your domain's DNS settings at Cloudflare, create an `A` record pointing your domain (e.g., `ai.your-domain.com`) to the **public IP address of your VPS**.
2.  **Proxy through Cloudflare:** Make sure the orange cloud is enabled (proxied) in Cloudflare's DNS settings. This means:
    *   All traffic first goes to Cloudflare's servers.
    *   Cloudflare connects to your VPS on ports 80/443.
    *   **Cloudflare handles the TLS/SSL certificate for the outside world.** You can use their "Full (strict)" SSL mode.
3.  **Caddy handles the internal TLS:** Caddy will still get a Let's Encrypt certificate for the connection between Cloudflare and your VPS. This is the best practice for end-to-end encryption.

### Summary: Why This is Better

*   **No Hard-Coded IPs:** Containers communicate via service names (`litetts`, `chroma`, `open-webui`).
*   **Simplicity:** This compose file only includes the four services you asked for.
*   **Security:** By default, `litetts` and `chroma` are not exposed to the public internet, only to the internal network. Only Caddy is exposed.
*   **Automatic TLS:** Caddy makes getting and renewing HTTPS certificates completely automatic.
*   **Cloudflare Ready:** This architecture is designed to work seamlessly with Cloudflare's proxy service.

To deploy this, just run `docker-compose up -d`. Caddy will automatically obtain a certificate, and OpenWebUI will be available at `https://your-domain.com`.
