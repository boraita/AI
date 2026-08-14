# Ultracode Workflow Recipe

How to orchestrate the full-site QA/UX audit with the `Workflow` tool. This is
the "ultracode" the skill produces. Adapt the skeleton — do not run it blind.

## Phase model

```
Phase 0  Provision   (sequential, once)   — dev-login → storage_state.json
Phase 1  Map         (1 agent)            — crawl routes → work-list of areas
Phase 2  Test        (parallel, capped)   — one agent per area: function + UX
Phase 3  Verify      (pipeline stage)     — re-check each blocker/major finding
Phase 4  Report      (main thread)        — synthesize → Artifact HTML
```

Phases 0–1 run in the main thread BEFORE calling Workflow (scout first, then
fan out). Phases 2–3 are the Workflow script. Phase 4 is back in the main thread
so you can call the Artifact tool.

## Phase 0 — Provision (main thread, once)

Run `scripts/provision_session.py` to create the throwaway test user via
dev-login and save `storage_state.json`. This is the only backend touch. Verify
it landed on an authenticated screen before continuing. Do NOT test the normal
login flow.

## Phase 1 — Map the app (main thread)

Discover the work-list; don't hardcode it. Load the authenticated session and
crawl one level deep from the entry point, collecting same-origin routes and the
major interactive areas per route. Reuse the **webapp-testing** skill's
screen-by-screen capture for the mechanics. Group routes into coherent AREAS
(e.g. "dashboard", "settings", "checkout") — areas, not raw URLs, are the unit
of parallelism, because one agent owning one area avoids two agents fighting over
the same widgets.

## Phase 2 — Parallel testing with collision control

Each area gets one agent. To avoid collisions:

- **Read-heavy areas** run fully parallel — no shared write state.
- **Write areas** (create/edit/delete) get an ISOLATED data namespace per agent:
  prefix every record the agent creates with its area slug + index
  (`qa-checkout-01-*`) so two agents never edit the same row. The agent cleans up
  what it created, or leaves it clearly tagged as disposable.
- **Globally destructive actions** (delete-all, account-level settings, logout,
  password/email change on the shared test user) are FORBIDDEN in parallel lanes.
  Route them to a single serialized lane that runs after everything else, or skip
  and log them for a manual pass.
- Each agent gets its OWN browser context from the same `storage_state.json`
  (`browser.new_context(storage_state=...)`) — separate contexts, shared identity,
  no cookie stomping.

## Model & effort per agent (use the right model for the job)

| Agent role | model | effort | why |
|---|---|---|---|
| Route crawl / mechanical capture | `haiku` | low | high volume, low judgment |
| Per-area functional + UX test | `sonnet` | medium | most of the work; needs judgment on pitfalls |
| Verify a blocker/major finding | `opus` | high | adversarial, must not pass a false positive |
| Final synthesis (main thread) | inherit | — | you, holding the whole picture |

Set these via `agent(prompt, {model, effort, phase, schema})`. Omit `model` to
inherit when unsure. Keep the workflow within the session's size guideline
(default: <15 agents) — batch areas if there are many.

## Finding schema (force structured output)

```js
const FINDING = {
  type: "object",
  properties: {
    area: { type: "string" },
    route: { type: "string" },
    title: { type: "string" },
    category: { type: "string", enum: ["functional", "ux", "a11y", "visual"] },
    severity: { type: "string", enum: ["blocker", "major", "minor", "polish"] },
    steps: { type: "string" },        // how to reproduce
    expected: { type: "string" },
    actual: { type: "string" },
    screenshot: { type: "string" },   // path
  },
  required: ["area", "route", "title", "category", "severity", "actual"],
}
const AREA_RESULT = {
  type: "object",
  properties: { area: { type: "string" },
    findings: { type: "array", items: FINDING } },
  required: ["area", "findings"],
}
```

## Workflow skeleton

```js
export const meta = {
  name: 'ultracode-qa-audit',
  description: 'Full-site QA + UX audit of an authenticated web app',
  phases: [{ title: 'Test' }, { title: 'Verify' }],
}
// args = { areas: [{slug, routes:[...]}], storageState: 'storage_state.json' }
const AREA = (a) => `You are an expert QA + UX engineer. Test EVERY interactive
element in the "${a.slug}" area (routes: ${a.routes.join(', ')}). Load the
session with browser.new_context(storage_state='${args.storageState}'). Follow
the ux-pitfalls checklist. Isolate any data you create under the prefix
"qa-${a.slug}-". NEVER run globally destructive actions. Return findings.`

const results = await pipeline(
  args.areas,
  a => agent(AREA(a), { label: `test:${a.slug}`, phase: 'Test',
                        model: 'sonnet', effort: 'medium', schema: AREA_RESULT }),
  (res) => parallel((res?.findings || [])
    .filter(f => f.severity === 'blocker' || f.severity === 'major')
    .map(f => () => agent(
      `Adversarially reproduce this finding; mark real=false if you cannot: ${JSON.stringify(f)}`,
      { label: `verify:${f.area}`, phase: 'Verify', model: 'opus', effort: 'high',
        schema: { type:'object', properties:{ real:{type:'boolean'}, note:{type:'string'} },
                  required:['real'] } })
      .then(v => ({ ...f, verified: v?.real, note: v?.note }))))
)
// minor/polish pass through unverified; blocker/major carry a verified flag
return results
```

`pipeline` (not `parallel`) so each area's findings start verifying the moment
that area finishes — no barrier wasting the fast areas' wall-clock.

## Phase 4 — Report (main thread)

Collect the workflow return value, drop `verified === false` findings from the
blocker/major set (keep them in an "unconfirmed" appendix), then render
`assets/report-template.html` into an Artifact via the Artifact tool. Load the
`artifact-design` skill first. Sort by severity, group by area, one card per
finding with screenshot, steps, expected vs actual. Lead with an executive
summary: counts by severity, top 3 blockers, overall health verdict.
