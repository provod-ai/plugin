---
name: provod-provider
description: Use when selecting a live Provod generation model.
version: 0.1.0
author: provod.ai
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [provod, provider, model-selection]
    related_skills: [provod-mcp, provod-media]
---

# Provod Provider Selection

Select a model from live capabilities rather than remembered names. This skill covers routing policy, not account setup or credential storage.

## When to Use

- A request needs an image or video generation model.
- A model is unavailable, incompatible with the requested media, or explicitly chosen by the user.
- Do not use this skill to invent a model identifier or expose credentials.

## Prerequisites

- A configured Provod provider or hosted MCP connection.
- Authorization supplied by the client credential store, never pasted into prompts or files.

## Procedure

1. Preserve an explicit user model choice and verify it against live discovery before generation.
2. If no model is specified, query the live catalog with the client CLI or `models_explore`, filtering by image or video and the requested capability.
3. Compare only fields returned by live discovery: modality, availability, supported inputs, price, and limits. Do not infer unsupported capabilities from a model name.
4. Choose the least costly available model that satisfies every explicit constraint. Ask the user when quality, speed, or cost preferences would materially change the choice.
5. Pass the returned model identifier unchanged to the generation call. On an availability error, discover again instead of substituting a remembered identifier.

Completion means the selected identifier came from the current catalog or was explicitly supplied and live-verified.

## Pitfalls

- Never maintain a static supported-model list in rules, examples, or generated client files.
- Do not treat a curated recommendation as proof of current availability.
- Do not silently change an explicit model selection.
- Do not log authorization headers, provider keys, MCP tokens, or signed media URLs.

## Verification

Confirm that live discovery returned the chosen model for the required modality immediately before generation, and that no credential or signed URL appears in persisted output.
