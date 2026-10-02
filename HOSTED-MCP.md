# Provod hosted MCP integration

The plugin uses the hosted Streamable HTTP MCP endpoint:

- Endpoint: `https://api.provod.ai/mcp`
- Authentication policy: `ON_INSTALL`
- OAuth client registration: CIMD when advertised, otherwise DCR

`mcp.json` is the portable Agent Plugins MCP manifest. OAuth client
registration is deliberately not hard-coded in the marketplace package. The
authorization server advertises its registration capabilities; clients should
use CIMD when supported and DCR otherwise. Keep OAuth authorization and token
endpoints discovered from standard metadata rather than hard-coded here.

The package retains OAuth `ON_INSTALL` authentication and must not contain a
`client_secret`, access token, refresh token, private key, or CLI/stdio
fallback. A static client ID is not required for this package: OpenAI documents
CIMD and DCR as supported client-registration paths, with DCR returning and
reusing a generated client ID per MCP connection.
