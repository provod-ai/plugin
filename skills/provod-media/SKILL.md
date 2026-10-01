---
name: provod-media
description: Use when retrieving and presenting Provod media results.
version: 0.1.0
author: provod.ai
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [provod, media, retrieval]
    related_skills: [provod-provider, provod-mcp]
---

# Provod Media Outcomes

Turn asynchronous generation jobs into verified, display-ready outcomes. Keep media identifiers stable and treat temporary URLs as secrets with an expiry.

## When to Use

- A generation tool returned a job or generation identifier.
- The user asks to retrieve, display, or reuse generated media.
- Do not claim a media result from submission metadata alone.

## Procedure

1. For one active job, call `jobs_wait` with a bounded timeout. If it is still non-terminal, use `job_status` or wait again rather than declaring failure.
2. Use `job_display` for one display-ready outcome. Use `show_generation_by_ids` for known identifiers or `show_generations` only when discovery of recent outcomes is intended.
3. Inspect the terminal state. Report failed or cancelled outcomes as such, including safe error details but no credentials or signed URLs.
4. Present every successful output the tool returns. Preserve media type, order, and identifiers; do not replace an output with a thumbnail unless labeled.
5. When another generation needs an output as input, prefer its stable media identifier. Use `show_medias` to verify reusable media rather than persisting a temporary URL.

Completion means the job is terminal and each reported output is backed by a retrieval response.

## Upload Inputs

Prefer `media_import_url` for an already reachable URL. For local bytes, call `media_upload` with operation "create". For each part, call `media_upload` again with operation "part", the returned "media_id", and its "part_number" to obtain that part's upload URL; upload the bytes to that URL and retain its ETag. Finish with `media_confirm`, supplying `{ "media_id": "<returned media_id>", "parts": [{ "partNumber": 1, "etag": "<etag>" }] }` for every uploaded part. Use `media_upload_widget` when the client cannot perform the returned URL transfer. Abort an incomplete multipart upload with the `media_upload` "abort" operation and its "media_id".

## Pitfalls

- Submission accepted is not generation completed.
- Signed URLs can expire and can grant access; do not log or save them as canonical references.
- Poll with bounded waits; do not create an unbounded loop.
- Do not discard additional outputs from batch or multi-output generations.

## Verification

Match the retrieved job or generation identifier to the submitted identifier, confirm a terminal success state before presenting success, and account for every returned output.
