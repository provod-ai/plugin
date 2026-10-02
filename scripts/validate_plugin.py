#!/usr/bin/env python3
"""Offline validation for the public Provod Codex/Claude plugin package."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT_REQUIRED = (
    "README.md", "LICENSE", "SECURITY.md",
    ".codex-plugin/plugin.json", ".claude-plugin/marketplace.json",
    "plugins/provod/.claude-plugin/plugin.json",
)
ENDPOINT = "https://api.provod.ai/mcp"
FORBIDDEN_PLACEHOLDER = "REPLACE_WITH_PROVOD_OAUTH_CLIENT_ID"
SECRET_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z ]+ PRIVATE KEY-----"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    re.compile(r"(?i)\b(?:client_secret|access_token|refresh_token)\s*[:=]"),
)


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    for rel in ROOT_REQUIRED:
        if not (root / rel).is_file():
            errors.append(f"missing required file: {rel}")
    docs: dict[str, object] = {}
    for path in root.rglob("*.json"):
        if ".git" in path.parts:
            continue
        try:
            docs[str(path.relative_to(root))] = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"invalid JSON {path.relative_to(root)}: {exc}")
    codex = docs.get(".codex-plugin/plugin.json")
    if isinstance(codex, dict):
        mcp = codex.get("mcp", {})
        expected = {"transport": "streamable_http", "url": ENDPOINT, "auth": "oauth", "install": "on_install"}
        for key, value in expected.items():
            if not isinstance(mcp, dict) or mcp.get(key) != value:
                errors.append(f"Codex MCP {key} must be {value!r}")
        if isinstance(mcp, dict) and any(key in mcp for key in ("client_secret", "access_token", "refresh_token")):
            errors.append("Codex MCP contains forbidden credential fields")
    marketplace = docs.get(".claude-plugin/marketplace.json")
    if isinstance(marketplace, dict):
        plugins = marketplace.get("plugins")
        if not isinstance(plugins, list) or not plugins or plugins[0].get("source") != "./plugins/provod":
            errors.append("Claude marketplace must contain source ./plugins/provod")
    claude = docs.get("plugins/provod/.claude-plugin/plugin.json")
    if isinstance(claude, dict):
        mcp = claude.get("mcp", {})
        auth = mcp.get("auth", {}) if isinstance(mcp, dict) else {}
        expected = (("type", "streamable_http"), ("url", ENDPOINT))
        for key, value in expected:
            if not isinstance(mcp, dict) or mcp.get(key) != value:
                errors.append(f"Claude MCP {key} must be {value!r}")
        for key, value in (("type", "oauth"), ("install", "on_install")):
            if not isinstance(auth, dict) or auth.get(key) != value:
                errors.append(f"Claude OAuth {key} must be {value!r}")
    portable = docs.get("mcp.json")
    if isinstance(portable, dict):
        servers = portable.get("mcpServers")
        server = servers.get("provod") if isinstance(servers, dict) else None
        if not isinstance(server, dict):
            errors.append("portable MCP manifest must define the provod server")
        else:
            if server.get("type") != "streamable-http":
                errors.append("portable MCP transport must be streamable-http; CLI/stdio fallback is forbidden")
            if server.get("url") != ENDPOINT:
                errors.append(f"portable MCP url must be {ENDPOINT!r}")
            if server.get("type") == "stdio" or "command" in server:
                errors.append("portable MCP must not contain a CLI/stdio fallback")
    for path in root.rglob("*"):
        if (
            not path.is_file()
            or ".git" in path.parts
            or "__pycache__" in path.parts
            or path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".ico", ".pyc", ".pyo"}
        ):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if path.parent.name not in {"tests", "scripts"} and FORBIDDEN_PLACEHOLDER in text:
            errors.append(f"stale OAuth client placeholder in {path.relative_to(root)}")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                errors.append(f"possible credential in {path.relative_to(root)}")
                break
    return errors


def check(root: Path) -> list[str]:
    errors = validate(root)
    private_names = {".env", ".env.local", ".env.production", "id_rsa", "id_ed25519"}
    for path in root.rglob("*"):
        if path.is_file() and path.name in private_names:
            errors.append(f"private credential-like path: {path.relative_to(root)}")
    return errors


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    errors = validate(root)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"validated Provod plugin at {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
