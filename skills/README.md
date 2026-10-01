# Provod skills

Versioned, auditable instructions for agents using the Provod provider and hosted MCP server.

## Canonical skills

- [Provider selection](skills/provod-provider/SKILL.md)
- [Hosted MCP routing](skills/provod-mcp/SKILL.md)
- [Media outcome retrieval](skills/provod-media/SKILL.md)

Model availability is live data. These skills tell clients to discover models through the CLI or `models_explore`; they intentionally contain no static model catalog. The canonical Markdown is client-neutral, so this release does not generate duplicate Claude, Codex, Hermes, or OpenCode rule fragments.

## Validate and package

Requires Node.js 20 or newer. Install the pinned validator dependency with `npm ci`.

```sh
npm test
npm run validate
npm run build:index
shasum -a 256 index.json
```

`index.json` is generated deterministically from canonical skill bytes. A release publishes that file and its SHA-256 digest; consumers must reject an index whose bytes do not match the trusted digest. Tag publication is fail-closed until the repository is public, `main` has branch protection, and the tagged commit is contained in `main`.

## License

[MIT](LICENSE)
