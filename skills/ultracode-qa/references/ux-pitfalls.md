# UX Pitfalls Checklist

What each QA agent hunts for beyond "does it work". A feature can be
functionally correct and still fail the user. Rate each finding
`blocker | major | minor | polish` and attach a screenshot + the exact
route/selector.

## Severity rubric

- **blocker** — user cannot complete a core task; data loss; dead-end with no
  recovery; broken on a primary path.
- **major** — task completable but with real friction, confusion, or a wrong
  mental model; silent failure; missing feedback on a destructive action.
- **minor** — noticeable rough edge; inconsistent but recoverable.
- **polish** — cosmetic, copy, spacing, micro-interaction.

## Functional checks (per interactive element)

- Every button/link/form does what its label promises, and reaches a real state.
- Forms: validation fires on bad input, error messages are specific and near the
  field, valid input submits, and success is confirmed.
- Required vs optional fields are honest; server errors surface to the user.
- Destructive actions (delete, cancel, overwrite) confirm first and are reversible
  or clearly warned.
- Pagination, search, filters, sort: change the result set correctly and are
  combinable without breaking.
- Empty states, zero-results, and first-run states render (not a blank void).
- Loading states exist for anything async (no frozen-looking UI).
- Error states are handled (network fail, 4xx/5xx) with a recovery path, not a
  white screen.

## UX / cognitive pitfalls

- **No feedback**: an action fires but nothing visibly changes → user repeats it.
- **Ambiguous affordance**: looks clickable but isn't, or vice versa.
- **Hidden state**: the app remembers something the user can't see (silent filter
  still applied, stale selection).
- **Irreversible-by-surprise**: destructive action with no undo and no warning.
- **Dead ends**: a screen with no way back/forward for the task at hand.
- **Inconsistent patterns**: same concept, different UI in two places → relearning.
- **Premature disable**: buttons disabled with no explanation of what to fix.
- **Focus/keyboard traps**: modal can't be closed by keyboard; tab order jumps.
- **Unlabeled icons**: icon-only controls with no accessible name or tooltip.
- **Copy that lies or confuses**: jargon, mismatched labels, error text that
  doesn't say how to fix it.
- **Layout breakage**: overflow, overlap, or cut-off content at mobile width
  (test 390×844) and at desktop.
- **Slow-path defaults**: the common task takes more steps than it should.

## Accessibility quick pass (not a full audit)

- Interactive elements reachable and operable by keyboard (Tab/Enter/Esc).
- Visible focus ring present.
- Images/icons have accessible names; form fields have labels.
- Text contrast looks adequate (flag obvious low-contrast; a full WCAG audit is a
  separate task — see the accessibility-testing skill).

## What NOT to test

- The normal login flow (out of scope — access is via dev-login only).
- Anything requiring real backend mutation you can't isolate (see collision rules
  in the workflow recipe).
