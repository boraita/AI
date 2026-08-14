---
name: ultracode-qa
description: Full-site QA + UX audit of a running web app, orchestrated as an "ultracode" (parallel Workflow of QA agents). Acts as an expert QA engineer that navigates and exercises EVERY feature to confirm it works, plus a UX expert that flags user pitfalls, then produces a severity-ranked Artifact HTML report. Access is via a throwaway test user created through the app's dev-login (the ONE allowed backend touch); the normal login flow is explicitly out of scope. Use when the user asks to "test the whole web app", "QA the entire site", "audit every feature", "run a full UX/QA pass", "ultracode QA", or wants a comprehensive functionality + usability report of a live site they can reach via dev-login.
---

# Ultracode QA

Drive a complete QA + UX audit of a live web app and deliver a ranked Artifact
HTML report. QA-expert rigor (does every feature actually work) plus UX-expert
judgment (where does the user trip). Built to run as an "ultracode": many QA
agents in parallel via the `Workflow` tool, with collision control and the right
model per agent.

## Ground rules (non-negotiable)

- **Backend is off-limits except one step**: creating/authenticating a throwaway
  test user through the app's **dev-login**. Do that first, save the session, and
  never touch the backend again.
- **Do NOT test the normal login flow** — a real user cannot reach dev-login, so
  the login experience is out of scope. Everything else IS in scope.
- **The environment is assumed running** — do not try to start or build it unless
  the user says otherwise.
- **Plan, then parallelize, avoiding collisions** — isolate test data per agent
  and forbid globally destructive actions in parallel lanes.

## Prerequisites

Two things must be known before starting — ask the user if missing:
1. **Base URL** of the running app.
2. **How to invoke dev-login** (a URL/token, or an endpoint + payload).

Playwright must be installed (`python3 -m playwright install chromium`). The
mechanics of navigation reuse the **webapp-testing** skill — read it for the
robust-waiting and screen-by-screen capture patterns rather than reinventing them.

## Workflow

Run phases 0–1 and 4 in the main thread; phases 2–3 are the parallel Workflow.

1. **Provision** (once, sequential) — run `scripts/provision_session.py` with the
   base URL and dev-login details to create the test user and save
   `storage_state.json`. This is the only backend touch. Confirm it landed on an
   authenticated screen. See `--help`.
2. **Map** — load the session and crawl one level deep to discover routes, then
   group them into coherent AREAS (an area = one agent's turf). Areas, not raw
   URLs, are the unit of parallelism.
3. **Test (parallel)** — one agent per area exercises every interactive element
   (functional) and applies the UX pitfalls checklist (`references/ux-pitfalls.md`).
   Findings are structured (see schema in the recipe).
4. **Verify** — each blocker/major finding is adversarially re-checked by a
   stronger model before it survives into the report.
5. **Report** — synthesize into the Artifact HTML using
   `assets/report-template.html`.

**Read `references/workflow-recipe.md` before writing the Workflow script** — it
holds the phase model, the collision-control rules, the per-agent model/effort
table, the finding schema, and a ready-to-adapt `Workflow` skeleton (uses
`pipeline` so each area verifies as it finishes).

## Collision control (summary — details in the recipe)

- Each agent gets its own browser context from the shared `storage_state.json`
  (same identity, separate cookies): `browser.new_context(storage_state=...)`.
- Read-only areas run fully parallel; write areas namespace every created record
  with their area slug (`qa-<area>-*`) and clean up after.
- Globally destructive actions (delete-all, account settings, logout,
  password/email change on the shared user) are forbidden in parallel lanes —
  serialize them last or log for a manual pass.

## Right model per agent (summary — full table in the recipe)

- Crawl / mechanical capture → `haiku`, low effort.
- Per-area functional + UX test → `sonnet`, medium effort.
- Verify a blocker/major → `opus`, high effort (adversarial).
- Final synthesis → the main thread (you).

Keep the fan-out within the session's workflow size guideline; batch areas if
there are many.

## Report

The report is an **Artifact HTML** page. Load the `artifact-design` skill first,
render `assets/report-template.html` (replace the `{{...}}` placeholders and the
example cards), and publish with the Artifact tool. Lead with an executive
summary (counts by severity, top blockers, one-line health verdict), then group
findings by area, sorted blocker→polish, each with screenshot, repro steps, and
expected-vs-actual. Findings that failed the adversarial re-check go in a dimmed
"Unconfirmed" section, not the main counts.

## Resources

- `scripts/provision_session.py` — dev-login → `storage_state.json`. The only
  backend touch. Parametrized; adapt if the app's dev-login is unusual.
- `references/workflow-recipe.md` — the ultracode orchestration blueprint.
- `references/ux-pitfalls.md` — what each agent hunts for + severity rubric.
- `assets/report-template.html` — theme-aware Artifact report template.
