#!/usr/bin/env python3
"""Offline validation for the public Provod Codex/Claude plugin package."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT_REQUIRED = (
    "README.md", "LICENSE", "SECURITY.md",
    ".codex-plugin/plugin.json", ".claude-plugin/marketplace.json",
    "plugins/provod/.claude-plugin/plugin.json",
)
ENDPOINT = "https://api.provod.ai/mcp"
PLACEHOLDER = "REPLACE_WITH_PROVOD_OAUTH_CLIENT_ID"
SECRET_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z ]+ PRIVATE KEY-----"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    re.compile(r"(?i)\b(?:client_secret|access_token|refresh_token)\s*[:=]"),
)
MCP_CONFIGS = ("mcp.json", "oauth.json")
MANIFESTS = (".codex-plugin/plugin.json", "plugins/provod/.claude-plugin/plugin.json", ".agents/plugins/marketplace.json", ".claude-plugin/marketplace.json")


def _require(mapping: dict[str, Any], key: str, kind: type, errors: list[str], path: str) -> Any:
    value = mapping.get(key)
    if not isinstance(value, kind):
        errors.append(f"{path}.{key} must be {kind.__name__}")
    return value


def _validate_manifest_schema(rel: str, value: Any, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{rel} must be a JSON object")
        return
    if rel in (".codex-plugin/plugin.json", "plugins/provod/.claude-plugin/plugin.json", ".agents/plugins/marketplace.json"):
        for key in ("name", "version", "description"):
            _require(value, key, str, errors, rel)
        _require(value, "mcp", dict, errors, rel)
        capabilities = _require(value, "capabilities", list, errors, rel)
        if isinstance(capabilities, list) and not all(isinstance(item, str) for item in capabilities):
            errors.append(f"{rel}.capabilities must contain only strings")
    if rel == ".claude-plugin/marketplace.json":
        plugins = _require(value, "plugins", list, errors, rel)
        if isinstance(plugins, list) and not plugins:
            errors.append(f"{rel}.plugins must not be empty")


def _validate_mcp_config(rel: str, value: Any, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{rel} must be a JSON object")
        return
    if rel == "mcp.json":
        servers = _require(value, "mcpServers", dict, errors, rel)
        server = servers.get("provod") if isinstance(servers, dict) else None
        if not isinstance(server, dict):
            errors.append("mcp.json.mcpServers.provod must be an object")
        else:
            if server.get("type") != "streamable-http":
                errors.append("mcp.json provod type must be 'streamable-http'")
            if server.get("url") != ENDPOINT:
                errors.append(f"mcp.json provod url must be {ENDPOINT!r}")
    else:
        if value.get("mcp_server") != "provod":
            errors.append("oauth.json mcp_server must be 'provod'")
        if value.get("authentication") != "ON_INSTALL":
            errors.append("oauth.json authentication must be 'ON_INSTALL'")
        oauth = value.get("oauth")
        if not isinstance(oauth, dict) or oauth.get("client_id") != PLACEHOLDER:
            errors.append("oauth.json oauth.client_id must be the documented placeholder")


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
    for rel in MANIFESTS:
        if rel in docs:
            _validate_manifest_schema(rel, docs[rel], errors)
    for rel in MCP_CONFIGS:
        if rel in docs:
            _validate_mcp_config(rel, docs[rel], errors)
    codex = docs.get(".codex-plugin/plugin.json")
    if isinstance(codex, dict):
        mcp = codex.get("mcp", {})
        expected = {"transport": "streamable_http", "url": ENDPOINT, "auth": "oauth", "install": "on_install", "client_id": PLACEHOLDER}
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
        for key, value in (("type", "oauth"), ("install", "on_install"), ("client_id", PLACEHOLDER)):
            if not isinstance(auth, dict) or auth.get(key) != value:
                errors.append(f"Claude OAuth {key} must be {value!r}")
    for path in root.rglob("*"):
        if not path.is_file() or ".git" in path.parts or path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".ico"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
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
    errors = check(root)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"validated Provod plugin at {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
