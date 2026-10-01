# Provod hosted MCP integration

The plugin uses the hosted Streamable HTTP MCP endpoint:

- Endpoint: `https://api.provod.ai/mcp`
- Authentication policy: `ON_INSTALL`
- OAuth client ID: `REPLACE_WITH_PROVOD_OAUTH_CLIENT_ID` (public placeholder only)

`mcp.json` is the portable Agent Plugins MCP manifest. `oauth.json` carries the
installation policy and public OAuth client metadata until the real client ID is
issued. Do not add a client secret, access token, refresh token, or private key.

Before marketplace submission, replace the client ID placeholder with the
registered public OAuth client ID and keep the authentication policy as
`ON_INSTALL`. The OAuth endpoints must be discovered from the MCP server's
standard authorization metadata rather than hard-coded here.
