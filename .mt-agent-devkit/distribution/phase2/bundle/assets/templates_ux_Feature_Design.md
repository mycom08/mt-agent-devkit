# UI/UX Design — {feature name}

Status: Draft
Approved-by:
Approved-at:

**Doc type:** feature design doc (one feature, frozen once it ships). **Promotion:** at feature closure the UI/UX Designer proposes reusable pieces for the project UX standard, and both TL and PO accept.

How to use: copy this blank template to `docs/feature/<feature-slug>/ui-ux/<Feature_Name>_Design.md` and fill every section. Write "None" where a section does not apply.

---

## 1. Standard Reference

Follows the project UX standard at the path registered in the "UX Quality Standard" row of the document index: {path, or "not registered"}. Do not repeat its rules here; record only what is specific to this feature.

## 2. Screens

| Screen | Purpose | Entry point |
|---|---|---|
| {screen} | {what the user does here} | {how the user arrives} |

## 3. Flows

For each flow: the trigger, the steps across screens, and the outcome, including the failure path.

- **{flow name}:** {trigger} → {steps} → {outcome}; on failure: {what happens}

## 4. Layouts

For each screen: the structure, content order and how it changes across the standard's breakpoints. Link wireframes or the prototype route.

- **{screen}:** {layout}

## 5. Shared Components

| Component | Used on | Existing or new | Notes |
|---|---|---|---|
| {component} | {screens} | {existing / new} | {variants or behaviour} |

## 6. States per Screen

One row per screen. Describe every state; write "Not possible" with the reason rather than leaving a cell blank.

| Screen | Loading | Empty | Error | Success | Other states |
|---|---|---|---|---|---|
| {screen} | {loading} | {empty} | {error} | {success} | {validation, disabled, partial, no permission} |

## 7. Deviations from the Standard

Each deviation either updates the standard or stays local to this feature.

| Standard rule | What this feature does instead | Reason | Outcome |
|---|---|---|---|
| {rule} | {deviation} | {why} | {update the standard / local to this feature} |

## 8. Promotion Candidates

Pieces of this design that other features can reuse. Reviewed at feature closure.

| Piece | Why reusable | TL decision | PO decision |
|---|---|---|---|
| {component, pattern or rule} | {reason} | {accept / reject} | {accept / reject} |
