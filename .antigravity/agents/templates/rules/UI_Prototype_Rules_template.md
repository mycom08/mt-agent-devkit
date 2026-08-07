# UI Prototype Rules

**Applies to:** Any implementer (Developer, Technical Lead, QA, UI/UX Designer)
**Trigger:** This project has (or is paired with) a `<repo-name>-ui-prototype` companion repo — the runnable UI/UX prototype scaffolded by Build Software's UI-bearing companion-repo convention. If this project has no such pairing, nothing below applies.

---

## 1. Why This Exists

A UI/UX prototype repo is a **reference for layout, interaction, and component structure** — nothing more. It exists so Developer builds the real screen against a working example instead of a static picture, and so layout/interaction decisions are made once, up front, by UI/UX Designer, rather than improvised mid-implementation. It is never a source of code, architecture, or data for the real product.

---

## 2. The Reference-Only Rule

The prototype's **layout, interaction flow, and component structure** are the reference. Its **architecture, services, and mock-backend code are never copied out of it** — not as a starting point, not as a "temporary" shortcut, not even with modifications. The real repo's architecture, services, and data layer are designed and implemented independently, per the real repo's own `architecture.md` and technical design — never derived from how the prototype happened to wire its mock backend.

If a piece of prototype code looks reusable, that is a signal to extract the **pattern** (e.g. "this form validates on blur, shows inline errors") into the real implementation by writing it fresh against the real stack — not a signal to copy the file.

---

## 3. The Mock-Case Rule

The prototype is allowed to contain clearly-labeled mock cases — a button that simulates a failed API call, a mock-account login, canned response data for a demo flow. These exist **only** in the prototype, to make every flow named in the story's AC reachable and clickable without a real backend.

The real UI **always** implements against real data and real APIs. If the real backend does not yet support something the prototype mocked:
- **Create a story with a backend dependency** — the real screen's story gets a `**Dependencies:**` entry pointing at the backend work that unblocks it for real.
- **Never port a mock into the real UI** — a hardcoded response, a fake success/failure toggle, or any other mock-only construct from the prototype must not land in the real implementation, even temporarily, even behind a flag.

---

## 4. Per-Role Rules

### Developer

- **Implement from the design, never port prototype code.** Use the prototype (and `ui_design.md`, if present) as your reference for what the screen looks like and how it behaves — write the real implementation fresh, against the real repo's own architecture and the real backend/API.
- If a flow you're implementing depends on backend support the prototype only mocked, stop and confirm a backend-dependency story exists (or create one) before writing a workaround. Do not stub around a missing endpoint by reproducing the prototype's mock.
- A PR that imports, copies, or lightly edits a file from the `-ui-prototype` companion repo is out of scope — implement the real thing instead.

### Technical Lead

- **Request changes on any PR that ports a mock case or copies prototype code.** This includes files copied verbatim, files copied with renamed variables, and hardcoded mock data lifted from the prototype's mock backend.
- Before approving a PR for a screen that has a prototype counterpart, **confirm a backend-dependency story exists** wherever the PR appears to stub around a missing endpoint — a stub with no linked backend story is a change request, not a follow-up note.
- Architecture review for the real repo evaluates the real repo's own design — the prototype's architecture (however it wired its mock backend) is never an approved precedent to cite.

### QA

- **Validate against real API behaviour.** A mock case from the prototype is not a test oracle — do not accept "it matches what the prototype mocked" as evidence an AC passes.
- **Flag any AC that can only pass via a mock.** If a story's AC cannot be verified against the real backend because the real backend doesn't support it yet, that is a blocker to report (tag Dev/TL), not a pass condition to wave through.

### UI/UX Designer

- The prototype you build is the reference artifact, not a deliverable that ships to end users — see `UI_UX_Designer_Rules.md §4` for the runnable-prototype standard itself.
- Keep mock cases clearly labeled (e.g. a visible "mock" badge, an obviously fake account name) so nobody mistakes prototype behavior for real backend behavior later.
- When the real backend later diverges from what you mocked (a different error shape, an extra required field), that is expected — the prototype is a point-in-time layout/interaction reference, not a contract the backend must match.

---

## Version

**Version:** 1.0 — initial version
**Created:** 2026-07-20
