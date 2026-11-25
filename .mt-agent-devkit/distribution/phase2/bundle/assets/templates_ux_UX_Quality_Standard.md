# UX Quality Standard — {project name}

**Doc type:** project UX standard (long-lived, project-wide). **Promotion:** at feature closure the UI/UX Designer proposes reusable pieces for this standard, and both TL and PO accept.

How to use: copy this blank template to the project path (suggested: `docs/wiki/UX_Quality_Standard.md`), fill the project sections, and register the path in the "UX Quality Standard" row of the document index. The copy is project-owned: later changes to this template do not merge into it.

---

## 1. Baseline for Every UI Screen

### 1.1 Form Validation and Inline Errors

- Show each field error next to its field, in text that says what to fix; colour alone is not enough.
- Validate at a predictable moment (on leaving the field or on submit) and clear the error once the input is valid.
- Keep entered values after a failed submit and move focus to the first invalid field.
- Block double submission while a request is in flight.

### 1.2 Error, Loading, Empty and Success States

- **Loading:** show progress without shifting the layout when content arrives.
- **Empty:** explain why there is nothing to show and offer the next action.
- **Error:** say what failed in plain language and offer a retry or a way out; never expose internal details.
- **Success:** confirm the outcome of every user action that changes data.

### 1.3 Text Overflow

- Long values, long translated strings and unbroken words must wrap or truncate without breaking the layout.
- Truncated text has a way to read the full value.
- Check each screen with strings noticeably longer than the source language.

### 1.4 Responsive Breakpoints

- Each screen works at every breakpoint in section 2, with no horizontal page scroll.
- Content and actions available on a large screen stay reachable on a small one.
- Touch targets are large enough to hit reliably.

### 1.5 Accessibility Basics

- **Labels:** every control has an accessible name; images that carry meaning have a text alternative.
- **Focus:** focus is visible, follows reading order, moves into dialogs and returns to the trigger on close.
- **Keyboard:** every action works without a pointer, and nothing traps focus unintentionally.
- **Contrast:** text, icons and state indicators meet the WCAG AA contrast ratios.

### 1.6 Motion and Transitions

- Use motion to explain a change, with consistent durations and easing across the project.
- Respect the user's reduced-motion setting.
- Never make the user wait for an animation to finish before acting.

### 1.7 Consistency with Existing Components and Styles

- Reuse an existing component before adding a new one.
- Use the component library's tokens for colour, spacing and typography, not hard-coded values.
- Matching actions look, read and behave the same on every screen.

### 1.8 Floating Elements (Tooltips, Popovers, Dropdowns, Menus)

- **Render at page level** through the component library's portalled primitive. Never position the floating element inside the trigger's parent.
- **Click-to-open information uses a popover**, not a tooltip.
- **Solid surface:** use the library's popover or tooltip tokens, never a hard-coded or translucent colour.
- **Check where it breaks:** open it inside a card, near the screen edges and over the next section. It must be fully visible, opaque and on top. An end-to-end test can assert that the element hit at its centre point is the floating element itself.

---

## 2. Breakpoints (project fills in)

| Name | Width range | Layout notes |
|---|---|---|
| {breakpoint name} | {min width to max width} | {notes} |

## 3. Component Library (project fills in)

- **Library:** {name and version}
- **Tokens:** {where colour, spacing and typography tokens live}
- **Portalled primitives:** {tooltip, popover, dropdown and menu components to use}
- **Shared project components:** {list or location}

## 4. Tone and Terminology (project fills in)

- **Tone:** {voice, formality, how errors and confirmations are phrased}

| Use | Instead of | Meaning |
|---|---|---|
| {preferred term} | {terms to avoid} | {definition} |
