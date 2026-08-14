---
name: webapp-testing
description: Toolkit for interacting with and testing local web applications using Playwright. Supports verifying frontend functionality, debugging UI behavior, capturing browser screenshots, and viewing browser logs. Also does screen-by-screen audits of a web app or PWA — crawling routes and capturing each screen's visuals, accessibility tree, design tokens, and network/API calls — to document or rebuild it (web/PWA counterpart to decompiling a mobile app).
license: Complete terms in LICENSE.txt
---

# Web Application Testing

To test local web applications, write native Python Playwright scripts.

**Helper Scripts Available**:
- `scripts/with_server.py` - Manages server lifecycle (supports multiple servers)

**Always run scripts with `--help` first** to see usage. DO NOT read the source until you try running the script first and find that a customized solution is abslutely necessary. These scripts can be very large and thus pollute your context window. They exist to be called directly as black-box scripts rather than ingested into your context window.

## Decision Tree: Choosing Your Approach

```
User task → Is it static HTML?
    ├─ Yes → Read HTML file directly to identify selectors
    │         ├─ Success → Write Playwright script using selectors
    │         └─ Fails/Incomplete → Treat as dynamic (below)
    │
    └─ No (dynamic webapp) → Is the server already running?
        ├─ No → Run: python scripts/with_server.py --help
        │        Then use the helper + write simplified Playwright script
        │
        └─ Yes → Reconnaissance-then-action:
            1. Navigate and wait for rendered content (see Robust waiting)
            2. Take screenshot or inspect DOM
            3. Identify selectors from rendered state
            4. Execute actions with discovered selectors
```

If the task is **auditing/understanding a whole app** (a competitor web app or
a PWA) rather than driving one flow, jump to **Screen-by-Screen Capture** below.

## Example: Using with_server.py

To start a server, run `--help` first, then use the helper:

**Single server:**
```bash
python scripts/with_server.py --server "npm run dev" --port 5173 -- python your_automation.py
```

**Multiple servers (e.g., backend + frontend):**
```bash
python scripts/with_server.py \
  --server "cd backend && python server.py" --port 3000 \
  --server "cd frontend && npm run dev" --port 5173 \
  -- python your_automation.py
```

To create an automation script, include only Playwright logic (servers are managed automatically):
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True) # Always launch chromium in headless mode
    page = browser.new_page()
    page.goto('http://localhost:5173') # Server already running and ready
    page.wait_for_load_state('networkidle') # CRITICAL: Wait for JS to execute
    # ... your automation logic
    browser.close()
```

## Reconnaissance-Then-Action Pattern

1. **Inspect rendered DOM**:
   ```python
   page.screenshot(path='/tmp/inspect.png', full_page=True)
   content = page.content()
   page.locator('button').all()
   ```

2. **Identify selectors** from inspection results

3. **Execute actions** using discovered selectors

## Common Pitfall

❌ **Don't** inspect the DOM before the app has rendered on dynamic apps
✅ **Do** wait for the real content, not just the network

### Robust waiting (accuracy)

`networkidle` alone is unreliable on modern SPAs/PWAs — polling, analytics
beacons, websockets, and service workers keep the network busy forever, so it
either hangs or resolves before hydration. Prefer waiting on **rendered
content**:

```python
page.goto(url, wait_until='domcontentloaded')
# Anchor on something the real UI owns:
page.wait_for_selector('main, [role="main"], #root > *', state='visible')
page.wait_for_load_state('networkidle', timeout=8000)  # best-effort, capped
```

- Use `expect(locator).to_be_visible()` over bare `wait_for_timeout()` sleeps.
- Cap every wait with a `timeout=` so a stuck beacon never hangs the run.
- For PWAs, service workers can serve a stale shell: launch with a fresh
  context (`browser.new_context()`) or `service_workers='block'` when you need
  the live network, not the cached shell.

## Best Practices

- **Use bundled scripts as black boxes** - To accomplish a task, consider whether one of the scripts available in `scripts/` can help. These scripts handle common, complex workflows reliably without cluttering the context window. Use `--help` to see usage, then invoke directly. 
- Use `sync_playwright()` for synchronous scripts
- Always close the browser when done
- Use descriptive selectors: `text=`, `role=`, CSS selectors, or IDs
- Add appropriate waits: `page.wait_for_selector()` or `page.wait_for_timeout()`

## Screen-by-Screen Capture (competitive / PWA audit)

Use this when the goal is to **understand every screen** of a web app or PWA —
not just visually, but the code and behavior behind each one — so it can be
documented or rebuilt. This is the web/PWA counterpart to decompiling a mobile
app: same intent, different surface.

For each route/screen, capture four layers so nothing is guessed:

1. **Visual** — full-page screenshot + viewport screenshot at mobile (390×844)
   and desktop widths. PWAs are mobile-first; capture both.
2. **Structure** — accessibility tree (`page.accessibility.snapshot()`) plus the
   rendered DOM. The a11y tree is the cleanest map of what a screen *is*
   (roles, labels, headings) and survives obfuscated class names.
3. **Design tokens** — computed styles of key nodes (color, background,
   font-family, font-size, spacing, radius). This is what lets you rebuild the
   look natively instead of eyeballing it.
4. **Behavior/data** — the network requests the screen fires (XHR/fetch/GraphQL)
   and console logs. This reveals the real API and state model behind the UI.

**Discover routes, don't hardcode them.** Crawl one level from the entry page,
collect same-origin links, and visit each once (dedupe by path). For a PWA also
read the manifest and service worker to learn declared start URLs and scope.

```python
# Per-screen capture skeleton — adapt, don't over-engineer
reqs = []
page.on('request', lambda r: reqs.append((r.method, r.url, r.resource_type)))
page.goto(url, wait_until='domcontentloaded')
page.wait_for_selector('main, [role="main"], #root > *', state='visible')

page.screenshot(path=f'{slug}.full.png', full_page=True)
a11y = page.accessibility.snapshot()               # structure
tokens = page.eval_on_selector_all(                # design tokens
    'h1,h2,button,a,[class*=btn],[class*=card]',
    '''els => els.slice(0,40).map(e => {const s=getComputedStyle(e);
       return {tag:e.tagName, text:e.innerText?.slice(0,40),
       color:s.color, bg:s.backgroundColor, font:s.fontFamily,
       size:s.fontSize, pad:s.padding, radius:s.borderRadius};})'''
)
api = [r for r in reqs if r[2] in ('xhr','fetch')]  # behavior/data
# write {slug}.json with a11y + tokens + api, one file per screen
```

Output one folder per screen (`screens/<slug>/`) holding the screenshot(s) and
a JSON with a11y tree + tokens + API calls. That folder set IS the spec you
rebuild from. Then hand the visual + token layer to the **mobile-app-design**
skill to produce native equivalents, and the API layer to whatever backend work
follows.

**Scope honestly**: only crawl apps you're authorized to (your own, a client's,
or public marketing/PWA surfaces). Don't bypass auth walls or rate limits, and
`log`/note any screens skipped so the audit doesn't read as complete when it
isn't.

## Reference Files

- **examples/** - Examples showing common patterns:
  - `element_discovery.py` - Discovering buttons, links, and inputs on a page
  - `static_html_automation.py` - Using file:// URLs for local HTML
  - `console_logging.py` - Capturing console logs during automation