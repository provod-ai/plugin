# Agent guidance

## MCP App widget UI

Use the official OpenAI repositories as the source of truth:

- Packaging and app surfaces: `openai/plugins` (`README.md`, plugin `.app.json` and `.mcp.json`).
- Widget structure and host integrations: `openai/mcp-extensions`, especially `plugins/bits-and-bolts/src/app/index.html`, `typescript/styles.css`, and `docs/spec.md`.

Treat the widget as a compact, host-native MCP App, not as a standalone SaaS dashboard:

- Use host theme variables such as `--color-background-primary`, `--color-background-secondary`, `--color-text-primary`, `--color-text-secondary`, `--color-border-primary`, and `--font-sans`.
- Start with a small host-style surface: approximately 16px page padding, 14px base text, 19px primary heading, 28px controls, 12px card padding, and restrained corner radii.
- Do not add a permanent product sidebar, large marketing hero, oversized dashboard cards, or excessive empty space. Host navigation and composer remain outside the app.
- Prefer one compact task surface with progressive disclosure: prompt/composer, compact mode/model controls, live loading/empty states, and results only after a real tool response.
- Never render fabricated models, balances, history, progress percentages, or media results. Use `callTool` and explicit loading/empty/error states.
- Keep billing behind an explicit user confirmation and never auto-call purchase tools.
- Verify desktop and narrow layouts, browser console errors, live contract tool names, validator/tests, and screenshots after UI changes.

The local preview is not an MCP host. A preview can verify layout and host-required fallback, but it must not be reported as end-to-end MCP tool verification.
