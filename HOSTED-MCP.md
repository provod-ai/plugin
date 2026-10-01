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

## Follow-up replacement task

Create a release-blocking follow-up task to replace
`REPLACE_WITH_PROVOD_OAUTH_CLIENT_ID` in `.codex-plugin/plugin.json`,
`plugins/provod/.claude-plugin/plugin.json`, and `oauth.json` with the
registered public OAuth client ID. The follow-up must verify that the three
files still point to `https://api.provod.ai/mcp`, retain OAuth `on_install`
authentication, and contain no `client_secret`, access token, refresh token,
or CLI/stdio fallback. Do not replace the placeholder until the provider has
issued and approved the public client registration.
