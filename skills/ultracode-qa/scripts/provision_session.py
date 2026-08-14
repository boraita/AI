#!/usr/bin/env python3
"""Provision a test-user session via a dev-login mechanism and save Playwright
storage_state so parallel QA agents can reuse the authenticated session WITHOUT
re-running login.

This is the ONE step allowed to touch the backend: it creates/authenticates a
throwaway test user through the app's dev-login. It does NOT exercise the normal
login flow (that is out of scope — a real user cannot reach dev-login).

Dev-login mechanisms vary. Two common shapes are supported out of the box:

  1. URL-token dev-login: visiting a URL sets the session cookie.
     --dev-login-url "https://app.test/dev/login?user=qa_bot"

  2. Endpoint dev-login: a GET/POST to an endpoint returns/sets a session.
     --dev-login-url "https://app.test/api/dev-login" --method POST \
       --body '{"role":"user"}'

If the app's dev-login needs something else (header, form fill), read this
script and adapt — it is meant to be patched per project.

Output: writes storage_state.json (cookies + localStorage) to --out. Parallel
agents load it with browser.new_context(storage_state=...).
"""
import argparse, json, sys
from playwright.sync_api import sync_playwright


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base-url", required=True,
                    help="App base URL, e.g. https://app.test")
    ap.add_argument("--dev-login-url", required=True,
                    help="Full dev-login URL (may include ?user=/token).")
    ap.add_argument("--method", default="GET", choices=["GET", "POST"],
                    help="How to hit the dev-login endpoint (default GET/navigate).")
    ap.add_argument("--body", default=None,
                    help="JSON body for POST dev-login (optional).")
    ap.add_argument("--ready-selector", default="body",
                    help="Selector that confirms an authenticated screen rendered.")
    ap.add_argument("--out", default="storage_state.json",
                    help="Where to write the storage_state (default ./storage_state.json).")
    args = ap.parse_args()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context()
        page = ctx.new_page()

        if args.method == "GET":
            # URL-token / navigate style: visiting sets the session.
            page.goto(args.dev_login_url, wait_until="domcontentloaded")
        else:
            # Endpoint style: call it in the browser context so Set-Cookie sticks.
            body = json.loads(args.body) if args.body else {}
            resp = ctx.request.post(args.dev_login_url, data=body)
            if not resp.ok:
                print(f"[FAIL] dev-login POST {resp.status}: {resp.text()[:300]}",
                      file=sys.stderr)
                sys.exit(1)
            page.goto(args.base_url, wait_until="domcontentloaded")

        # Confirm we landed on an authenticated screen, not a login wall.
        try:
            page.wait_for_selector(args.ready_selector, state="visible", timeout=10000)
        except Exception:
            print("[WARN] ready-selector not found — session may not be authenticated. "
                  "Inspect the saved state before trusting it.", file=sys.stderr)

        ctx.storage_state(path=args.out)
        cookies = ctx.cookies()
        browser.close()

    print(f"[OK] session saved to {args.out} ({len(cookies)} cookie(s)).")
    print("Parallel agents: browser.new_context(storage_state='%s')" % args.out)


if __name__ == "__main__":
    main()
