# Provod Plugin
Public Codex and Claude integration for provod.ai.

The integrations use the hosted Streamable HTTP MCP endpoint with OAuth
authorization on install. OAuth client registration uses CIMD when the server
advertises it and DCR otherwise; no static client ID or secret is bundled.
See `HOSTED-MCP.md` for the authentication contract.
