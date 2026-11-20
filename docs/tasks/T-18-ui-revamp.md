# T-18. UI revamp: one consistent, polished visual system

- Owner: cloud session (Sonnet lead, Haiku auditor)
- Depends on: `main` at or after `3f528d2`. Branch from `main`, not from any feature branch.
- Estimate: L (run as three phases below; each phase is one or more commits)

## Goal

Every public and reviewer screen looks like one product: one type scale, one spacing rhythm, one token set, less clutter, and it holds up from 360 px to 1440 px.

## Context

Read first, in this order: root `AGENTS.md`, `apps/web/AGENTS.md`, `docs/DESIGN.md`, `apps/web/src/styles.css`, `apps/web/src/components/ui/`, `apps/web/src/router.tsx`.

Known drift to resolve (confirm with the audit):

- **Two token names for each role in `styles.css`.** `surface`/`paper`, `border`/`line`, `border-strong`/`line-strong`, `foreground`/`ink`, `muted`/`faint`, `brand-accent`/`beacon`/`brand-500`, `surface-muted`/`sunken`. Pick one name per role, migrate every usage, delete the other. `unknown` and `no-official-statement` also need a single name.
- **`Card` is defined twice**: `components/ui/surface.tsx` and `components/ui/card.tsx`. Keep one.
- **`components/ui/surface.tsx` holds most primitives** (`PageHeader`, `PageTitle`, `SectionTitle`, `Pill`, `Notice`, `Loading`, `controlClass`). `DESIGN.md` describes them but not where they live. Either split `surface.tsx` by component or document it as is.
- **`DESIGN.md` still describes a serif voice for claims and sources.** The code uses the sans display stack. Sonnet decides the typography (see Phase 2, step 2). Any font must be a system stack: no web font without an ADR.

## Roles and handover

The work is split so the expensive model only does judgment.

| Phase | Who | Does | Writes |
| --- | --- | --- | --- |
| 1. Audit | Haiku subagent (`Agent` with `model: "haiku"`) | Runs the app, screenshots every route, extracts measurements. No design opinions, no code edits. | `docs/design/audit/AUDIT.md` and `docs/design/audit/shots/` |
| 2. Design and build | Sonnet (main session) | Reads `AUDIT.md`, decides tokens and scale, edits code | Code, `docs/DESIGN.md`, `docs/design/audit/DECISIONS.md` |
| 3. Check | Haiku subagent, then Sonnet | Haiku re-shoots changed routes only; Sonnet compares and fixes | `docs/design/audit/AFTER.md` |

The handover between models is the files above, never chat. Sonnet must not re-screenshot routes the audit already covered unless it changed them.

### Phase 1 audit (Haiku)

1. Install Playwright in a scratch directory **outside the repo** (for example `/tmp/shots`). Do not add it to `package.json`; this task adds no dependency.
2. Start the stack with `make dev` (web, API and worker). Seed known data with `make demo-reset CONFIRM=1`, which needs `REPOSITORY_BACKEND=sql` and must never run against production. If a reviewer login is needed, ask the user for the local dev credentials first. Never write credentials into any file, screenshot or log.
3. Routes: `/`, `/check`, `/guide`, `/subscribe`, `/information`, one `/information/:slug`, `/fact-checks`, one `/fact-checks/:slug`, one `/c/:messageId`, `/dashboard`, `/dashboard/claims`, `/dashboard/verification`, one `/dashboard/verification/:messageId` (in each step: review, approve, seal, send), `/dashboard/evidence`, `/dashboard/board`. Also capture the empty, loading and error state where one is reachable.
4. Widths: 360, 768, 1440. Full page PNGs named `<route-slug>@<width>.png`.
5. For each page, extract with a script (not by eye) the computed `font-size`, `font-weight`, `line-height`, `color`, `background-color`, `padding`, `margin`, `gap`, `border-radius`, `box-shadow` of visible elements, and summarise the distinct values. Flag raw hex or Tailwind palette classes in `apps/web/src` with `grep`.
6. Record per route: horizontal overflow, text under 4.5:1 contrast, touch targets under 40 px, more than one `h1`, console errors.
7. `AUDIT.md` format: one section per route with screenshot paths, a bullet list of facts (each with a `file:line` pointer when known), then a global inventory table: distinct font sizes, spacings, radii, shadows, colours, with counts. Facts only, no recommendations. Keep it under 600 lines.

### Phase 2 design and build (Sonnet)

1. Read `AUDIT.md` and a sample of screenshots (all three widths of the homepage, verification page and board; others only when the audit flags a problem).
2. Make the design decisions yourself; do not wait for the user. This is refinement, not redesign. Keep the existing identity in `DESIGN.md`: the forest green brand, the slate neutrals, the existing verdict colours (`confirmed` green, `contradicted` red, `no-official-statement` slate) and the calm, civic personality. Do not introduce new hues, a new accent colour, a different brand colour or a new mood. Consolidate names and tune values only where needed for contrast or consistency, and state each value change in `DECISIONS.md`. Choose:
   - the typography: the font stacks for display, UI and data (system stacks only), the type scale, weights and line heights;
   - the token set: one name per colour role, the spacing scale, radii, shadows and layout widths;
   - the clutter cuts.

   Record each choice with a one line reason in `DECISIONS.md`. Then lock the final spec in `docs/DESIGN.md`: the typography, token and scale tables, marked as the locked specification. Later changes to these need an explicit update to `DESIGN.md` in the same commit.
3. Implement in this order, committing after each: tokens in `styles.css`; primitives in `components/ui/`; the two shells (`public-layout`, `dashboard-layout`); then pages and features. Features compose primitives; they do not restyle them.
4. Clutter: remove repeated explanations, decorative boxes inside boxes, competing shadows and redundant labels. Do not remove the official source citation, the human approval signal or the fingerprint check: `DESIGN.md` requires them to stay visible.
5. Update `docs/DESIGN.md` to match the code in the same commit as the change it describes.

### Phase 3 check

Haiku re-shoots only the changed routes at the three widths into `shots/after/` and re-runs the measurement script. Sonnet compares the before and after inventories, fixes regressions, and writes `AFTER.md`: what changed, the remaining known issues.

## Guardrails (do not cross)

- No palette redesign. The brand stays forest green, neutrals stay slate, and verdict colours keep their meaning. Any colour value change must be small, justified by contrast or consistency, and listed in `DECISIONS.md`.
- Verdict has exactly three values: `confirmed`, `contradicted`, `no_official_statement`. Labels come from `features/claims/verdict.ts` and are shown only through `VerdictBadge`. No "true", "false", "misleading" or opinion words, in copy or colour names.
- Do not touch the approval gate in `domain/` or any send path. This task is `apps/web` and `docs` only. If a fix seems to need an API change, stop and write it under Questions.
- No raw hex or Tailwind palette colours in components; tokens only. Colour is never the only signal.
- No web font, icon library, CSS framework or UI kit. Icons come from `components/icons.tsx`.
- No vendor names in core code, no secrets anywhere, including screenshots of settings pages.
- Accessibility checklist in `DESIGN.md` still holds: 360 px, 200 percent zoom, 40 px targets, labelled controls, one `h1`, skip link, visible focus, `prefers-reduced-motion`.
- Existing tests keep passing. If markup changes break a test, update the test to the new markup, not the behaviour it checks.
- Line endings: `main` now has `* text=auto eol=lf`. Do not change line-ending config in this task.

## Cost controls

- Haiku does all screenshotting and measurement. Sonnet reads files, not raw DOM dumps.
- One audit pass, at most two correction passes after it. Then stop and report, even if minor issues remain; list them in `AFTER.md`.
- Screenshots stay in `docs/design/audit/shots/`, which is git ignored; commit only the markdown.
- Do not run `make verify` after every edit. Run `make -C apps/web verify` (lint, typecheck, test, build) per phase, and the full `make verify` once at the end.

## Acceptance criteria

- [ ] `styles.css` has one token name per role; no usage of the removed names remains (`grep` shows none)
- [ ] One `Card` component remains
- [ ] Every page uses the same type scale and spacing scale recorded in `DECISIONS.md`; the after inventory shows fewer distinct font sizes, spacings and shadows than the before inventory
- [ ] No horizontal overflow at 360 px on any route; no meaningful text under 4.5:1
- [ ] `docs/DESIGN.md` matches the code: primitives and their files, colours, typography
- [ ] Guardrails above hold; no files outside `apps/web`, `docs`, and the `.gitignore` entry for the shots folder changed
- [ ] `make verify` passes; paste its last lines in the PR

## Delivery

- Branch `task/T-18-ui-revamp` from `main`. Conventional Commits with scope `web` or `docs`. No `Co-Authored-By` or AI attribution lines in commits or the PR.
- Open the PR as a draft with before and after screenshots of the homepage, verification page and board at 360 and 1440 attached or linked. Do not merge.

## Files likely touched

`apps/web/src/styles.css`, `apps/web/src/components/**`, `apps/web/src/features/**/*.tsx`, `apps/web/src/pages/*.tsx`, `docs/DESIGN.md`, `docs/design/audit/*.md`, `.gitignore`.

## Questions

None open. Sonnet decides typography and tokens as described in Phase 2 and records them in `DESIGN.md`.

This brief is a cloud session task and is not listed on `docs/tasks/BOARD.md`.
