# Provod marketplace application packet

Status: draft for owner review; do not submit while any item marked TODO remains.
Evidence checked: 2026-10-01 UTC.

## 1. Listing identity

- Display name: Provod AI
- Suggested slug: provod-ai
- Publisher: provod.ai, operated through TRAFFIC AGGREGATOR LLC
- Category: Productivity (secondary: Developer tools / Image and video generation)
- Repository: https://github.com/provod-ai/plugin
- Canonical skills source: https://github.com/provod-ai/skills
- Hosted MCP endpoint: https://api.provod.ai/mcp
- Public website: https://provod.ai
- Support: https://provod.ai/ru/contact; Telegram https://t.me/provodai; email info@provod.ai

Owner confirmation required: exact marketplace display name and whether the legal publisher should be shown as “provod.ai” or “TRAFFIC AGGREGATOR LLC (provod.ai)”.

## 2. Short description (<= 200 characters)

Access Provod’s live AI model catalog, image/video generation, media workflows, account visibility, and confirmed billing actions from your AI assistant.

## 3. Long description

Provod connects an AI assistant to the hosted Provod MCP service. Discover currently available models and capabilities, submit image or video jobs, upload or import source media, wait for completed jobs, and retrieve display-ready outputs. The integration also exposes account balance, transactions, workspaces, and plans/credits for visibility. Any billing purchase is a separate mutation that requires the user’s explicit confirmation.

The integration uses the live Provod catalog rather than a bundled list of model names. Generation is asynchronous: a submitted job is not reported as complete until the service returns a terminal result. Temporary signed media URLs are treated as expiring delivery references, not durable identifiers.

The plugin does not require a local CLI, provider API key, or model-specific credential. It connects to the hosted Streamable HTTP MCP endpoint and uses the client’s OAuth authorization flow.

## 4. Capabilities and tool inventory

Exact hosted tool names are listed below; no aliases should be advertised:

- Discovery: `models_explore`
- Generation: `generate_image`, `generate_video`, `generate_image_batch`, `generate_video_batch`
- Job/result retrieval: `show_generations`, `job_status`, `job_display`, `jobs_wait`, `show_generation_by_ids`
- Media input: `media_upload`, `media_import_url`, `media_confirm`, `media_upload_widget`, `show_medias`
- Account visibility: `balance`, `transactions`, `list_workspaces`, `show_plans_and_credits`
- Billing mutation: `confirm_billing_purchase`

Do not claim text chat, arbitrary web browsing, or access to a user’s files unless those capabilities are separately exposed by the live MCP manifest.

## 5. Data sent and destinations

| Data | Why it is sent | Destination | User control / handling |
| --- | --- | --- | --- |
| User prompt and generation parameters (model identifier, dimensions, duration, etc.) | Submit and monitor a generation | Provod hosted MCP at `api.provod.ai`; Provod routes the request to the selected model/provider | Sent only when the user asks for the operation; model selection is verified against live discovery |
| Source media bytes or an import URL | Use reference media in a generation | Provod media service via MCP upload/import flow | Upload/import is user-initiated; use stable media IDs after upload; do not persist signed URLs |
| Job, generation, and media identifiers | Retrieve status and outputs | Provod hosted MCP | Opaque identifiers are retained only as needed for the conversation/workflow |
| Account, balance, transaction, workspace, plan, and credit queries | Show account information | Provod hosted MCP | Read-only visibility calls are initiated by the user/assistant request |
| Billing amount/plan and idempotency key for a purchase | Execute a purchase after confirmation | Provod hosted MCP and Provod billing system | `confirm_billing_purchase` must never be called without explicit user confirmation; never silently retry |
| OAuth authorization data | Authenticate the MCP connection | Provod authorization service and client credential store | No token or secret is placed in prompts, logs, repository files, or listing text |

The packet must not claim that Provod or downstream model providers retain no prompts, train on prompts, or guarantee a particular geographic processing location unless the current legal/privacy documentation explicitly confirms it.

## 6. Authentication explanation

Authentication mode: OAuth on install (`ON_INSTALL`). The client connects to `https://api.provod.ai/mcp`, discovers the service metadata, and opens the provider authorization flow. The user signs in/consents in the provider’s authorization UI; the client stores the resulting credentials in its protected credential store. The plugin has no embedded API key and does not ask users to paste tokens into chat.

Owner verification before submission:

- [ ] Confirm OAuth metadata and redirect/client registration are live in the marketplace client.
- [ ] Confirm scopes shown to the user (expected MCP access scopes include `mcp:tools` and `offline_access`; use the live metadata as authoritative).
- [ ] Confirm disconnect/revoke behavior and account-switch behavior.

## 7. Billing behavior

- Model generation can consume the user’s Provod balance/credits according to the selected model and current catalog pricing.
- `balance`, `transactions`, and `show_plans_and_credits` are visibility operations.
- `confirm_billing_purchase` is the only listed purchase mutation and requires explicit user confirmation immediately before invocation.
- The assistant must show the purchase details returned by the service, preserve the idempotency key unchanged, and never silently retry a failed or ambiguous purchase.
- The listing must not promise fixed prices; pricing and availability are live data.

## 8. Legal and support URLs

- Privacy policy: https://provod.ai/ru/legal/privacy
- Terms / public offer: https://provod.ai/ru/legal/terms
- Cookie policy: https://provod.ai/ru/legal/cookies (verify route before submission)
- Security information: https://provod.ai/ru/security
- 152-FZ information: https://provod.ai/ru/legal/152-fz
- Company details: https://provod.ai/ru/legal/requisites
- Contact/support: https://provod.ai/ru/contact; https://t.me/provodai; mailto:info@provod.ai

The authoritative terms document is the Russian public-offer PDF linked by the site. The English page, if presented, is informative and does not replace the authoritative document.

## 9. Publisher identity

Public company information currently identifies the licensor as TRAFFIC AGGREGATOR LLC. Site content lists Tax ID 9707022118, registration reason code 772801001, registration number 1237700937429, and registered address 117279, Moscow, KonKovo municipal district, 22 Vvedenskogo St., bldg. 1, premises 5N. Copy these details into the marketplace only after legal-owner approval and current-site recheck.

## 10. Assets

Logo/icon:

- Preferred source: official provod.ai brand mark from the public site (owner must export a square PNG/SVG accepted by the marketplace).
- Existing brand component: `/Users/goodok/git/altrouter/apps/site/src/components/brand/provod-logo.tsx` (source reference only; not a submission asset).
- Do not reuse OpenCode assets or submit an unapproved generated logo.

Screenshots required (TODO; capture from the actual marketplace-compatible client, with test account and no personal data):

1. OAuth install/consent screen showing Provod connection.
2. Live model discovery followed by a generation request.
3. Completed job with retrieved image/video output.
4. Account balance/credits visibility, with all identifiers and amounts redacted unless intentionally demo data.
5. Explicit confirmation screen immediately before a billing purchase (prefer a static test/sandbox state; do not perform a real purchase for screenshots).

Public, non-authenticated product imagery can be referenced from https://provod.ai, but it is not a substitute for integration screenshots.

## 11. Demo prompts

- “Explore the currently available image models for a photorealistic 16:9 landscape, compare price and limits, then ask me before generating.”
- “Generate a square editorial illustration of a red fox reading beside a rainy window. Wait for the job to finish and show every returned output.”
- “Use this image as a reference and create three independent variations; do not start until the upload is confirmed.”
- “Show my current balance, recent transactions, and available plans. Do not purchase anything.”
- “Prepare a purchase of the plan I selected, summarize the exact amount and idempotency key, and wait for my explicit confirmation.”

## 12. Security disclosures

- Hosted endpoint: HTTPS only, `https://api.provod.ai/mcp`.
- Credentials: OAuth/client credential store; no secrets in skill files, prompts, screenshots, or repository.
- Authorization boundary: user authorization is required; billing is a separate explicitly confirmed mutation.
- Data minimization: send only prompt/parameters/media/account fields needed for the requested operation.
- Async integrity: match returned job/generation IDs and verify terminal state before reporting success.
- Signed URLs: treat as temporary access grants; never log or persist them as canonical references.
- Model safety: use the live catalog; never maintain a static availability list.
- Security contact: info@provod.ai.

Known disclosure boundary: the public security page does not add claims about certifications, SLAs, or data residency. Those claims must not appear in the application without separately verified evidence.

## 13. Submission gate

- [ ] Owner approved display name/category/descriptions.
- [ ] Repository and publisher ownership verified.
- [ ] OAuth metadata, scopes, redirect, and revoke flow tested in target client.
- [ ] Live MCP tool list matches the inventory above.
- [ ] Privacy, terms, support, security, and company URLs return 200 and are public.
- [ ] Approved square icon and five integration screenshots attached.
- [ ] Demo prompts tested with a non-production/test account.
- [ ] Billing confirmation tested without an actual unintended charge.
- [ ] Secret scan and prompt/media redaction completed.
- [ ] Marketplace reviewer notes prepared for any placeholder or unsupported capability.
