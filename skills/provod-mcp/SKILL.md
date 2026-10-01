---
name: provod-mcp
description: Use when routing work through the hosted Provod MCP.
version: 0.1.0
author: provod.ai
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [provod, mcp, routing]
    related_skills: [provod-provider, provod-media]
---

# Provod Hosted MCP Routing

Route each operation to the public hosted MCP contract. Tool names are exact; do not create aliases or infer additional tools.

## When to Use

- An agent needs model discovery, generation, media transfer, account visibility, or billing confirmation through Provod MCP.
- Do not use provider chat/completions endpoints as substitutes for MCP tools.

## Tool Routing

- Discovery: `models_explore`.
- Single generation: `generate_image`, `generate_video`.
- Batch generation: `generate_image_batch`, `generate_video_batch`.
- Generation retrieval: `show_generations`, `job_status`, `job_display`, `jobs_wait`, `show_generation_by_ids`.
- Media input: `media_upload`, `media_import_url`, `media_confirm`, `media_upload_widget`, `show_medias`.
- Account visibility: `balance`, `transactions`, `list_workspaces`, `show_plans_and_credits`.
- Billing mutation: `confirm_billing_purchase`.

## Procedure

1. Use `models_explore` for current model capabilities; never route from a static model catalog.
2. Upload or import required source media and retain only returned media identifiers in subsequent generation requests.
3. Use a single-generation tool for one prompt and a batch tool only for multiple independent prompts.
4. Treat generation submission as asynchronous. Follow its returned identifier with `jobs_wait`, `job_status`, or the retrieval tools; do not assume submission returns final media.
5. Require the user's explicit confirmation before `confirm_billing_purchase`. Preserve the confirmation capability and idempotency key exactly.
6. Return a display-ready result using the outcome workflow in [Provod media](../provod-media/SKILL.md).

Completion means every call uses one exact public tool name and the final response is retrieved rather than inferred.

## Pitfalls

- Never invent a tool name, silently retry a billing mutation, or pass provider credentials as tool arguments.
- Keep identifiers opaque and unchanged.
- A successful tool transport does not prove a generation succeeded; inspect the returned state.
- Never expose signed upload/download URLs in logs or durable rule files.

## Verification

Check each invoked name against Tool Routing, confirm current model discovery preceded implicit selection, and verify that any asynchronous job reached a terminal state before reporting completion.
