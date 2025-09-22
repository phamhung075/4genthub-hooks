1- Install

# Option 1: With uv (recommended)
uv tool install mcp-proxy

# Option 2: With pipx (alternative)
pipx install mcp-proxy


2- Test with terminal
``` bash
mcp-proxy --headers Accept 'application/json, text/event-stream' --headers Authorization 'Bearer <YOUR_API_TOKEN_HERE>' --transport streamablehttp http://localhost:8000/mcp
```

expected:
[I 2025-09-22 14:11:55,193.193 httpx] HTTP Request: POST http://localhost:8000/mcp "HTTP/1.1 200 OK"
[I 2025-09-22 14:11:55,194.194 mcp.client.streamable_http] Negotiated protocol version: 2025-06-18
[I 2025-09-22 14:11:55,198.198 httpx] HTTP Request: POST http://localhost:8000/mcp "HTTP/1.1 202 Accepted"